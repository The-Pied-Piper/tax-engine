"""CA-ON 2025 end to end: return bi, two Form T776 statements on one return."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.artifact import ArtifactRegistry
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import FormInstanceLine
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import NET_RENTAL_INCOME, TOTAL_INCOME
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, compute, run, service

# T776 line 8230 "Other income": the first rental operation has 12,000 of it and no expenses, so its
# line 9946 "Your net income (loss)" is 12,000. The second has no income and advertising (line 8521)
# of 2,000, so its line 9946 is 0 - 2,000 = -2,000: a loss, which no capital cost allowance may
# create or increase.
OPERATION_1: dict[str, Any] = {"rental_other_income": "12000"}
OPERATION_2: dict[str, Any] = {"rental_expenses": {"advertising": ("2000", "0", "0")}}


def bi_inputs(statements: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    """Return BI's inputs, as in `returns/2025_return_bi.yaml`: a landlord with the T776
    `statements` given (none: no rental operation), no business, no farm, no fishing and no other
    income."""
    return {
        "employment_income": "0",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "rental_statements": statements,
        "business_statements": (),
        "farm_statements": (),
        "fish_statements": (),
    }


def return_bi(*statements: dict[str, Any]) -> Worksheet:
    """The return form's worksheet of return BI with the T776 `statements`."""
    return compute(**bi_inputs(statements))


def run_bi(*statements: dict[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return BI with the T776 `statements`."""
    return run(**bi_inputs(statements))


def net_incomes(worksheet: Worksheet) -> list[Any]:
    """Line 9946 of each statement, in statement order, as the return exports it."""
    kind = ArtifactRegistry.shared().kind("ca/t776.net_rental_income")
    value = worksheet.get(kind).value
    assert isinstance(value, RecordList)
    return [record[NET_RENTAL_INCOME] for record in value.records]


def test_two_statements_with_lines_9946_of_12000_and_minus_2000_give_line_12600_of_10000() -> None:
    # T1 line 12600 "Net" adds the lines 9946 of the statements: 12,000.00 + (-2,000.00).
    worksheet = return_bi(OPERATION_1, OPERATION_2)

    assert worksheet.get(NET_RENTAL_INCOME).value == D("10000.00")


def test_line_12600_is_the_whole_of_total_income() -> None:
    worksheet = return_bi(OPERATION_1, OPERATION_2)

    assert worksheet.get(TOTAL_INCOME).value == D("10000.00")


def test_the_return_exports_line_9946_of_each_statement_in_statement_order() -> None:
    worksheet = return_bi(OPERATION_1, OPERATION_2)

    assert net_incomes(worksheet) == [D("12000.00"), D("-2000.00")]


def test_the_order_of_the_statements_does_not_change_the_total() -> None:
    worksheet = return_bi(OPERATION_2, OPERATION_1)

    assert net_incomes(worksheet) == [D("-2000.00"), D("12000.00")]
    assert worksheet.get(NET_RENTAL_INCOME).value == D("10000.00")


def test_one_statement_gives_its_own_line_9946_a_loss_staying_a_loss() -> None:
    assert return_bi(OPERATION_1).get(NET_RENTAL_INCOME).value == D("12000.00")
    assert return_bi(OPERATION_2).get(NET_RENTAL_INCOME).value == D("-2000.00")


def test_a_third_statement_is_added_too() -> None:
    worksheet = return_bi(OPERATION_1, OPERATION_2, OPERATION_1)

    assert worksheet.get(NET_RENTAL_INCOME).value == D("22000.00")


def test_a_return_with_no_statement_has_line_12600_of_zero() -> None:
    worksheet = return_bi()

    assert worksheet.get(NET_RENTAL_INCOME).value == D("0")
    assert worksheet.get(TOTAL_INCOME).value == D("0")
    assert net_incomes(worksheet) == []


def test_each_statement_has_its_own_worksheet_with_its_line_9946() -> None:
    result = run_bi(OPERATION_1, OPERATION_2)

    assert [worksheet.get(NET_RENTAL_INCOME).value for worksheet in result["ca/t776"]] == [
        D("12000.00"),
        D("-2000.00"),
    ]
    assert len(result["ca/t776"]) == 2


def test_a_return_with_no_statement_runs_the_form_on_no_instance() -> None:
    assert run_bi()["ca/t776"] == ()


def test_the_trace_keeps_the_lines_of_each_statement_under_its_position() -> None:
    result = run_bi(OPERATION_1, OPERATION_2)

    groups = [
        line
        for line in service().compose(CA_ON, 2025).trace(result)
        if isinstance(line, FormInstanceLine)
    ]

    # The forms run in the order of their imports: the return reads the forms' exports.
    assert [(group.form, group.position) for group in groups] == [
        ("ca/has_investment_expenses", 1),
        ("ca/schedule_3", 1),
        ("ca/spouse_on_december_31", 1),
        ("ca/t1032", 1),
        ("ca/t1043", 1),
        ("ca/t1206_share_dispositions", 1),
        ("ca/t1212", 1),
        ("ca/t2017", 1),
        ("ca/farm_loss", 1),
        ("ca/t2043", 1),
        ("ca/t1139_return", 1),
        ("ca/schedule_8", 1),
        ("ca/t2205", 1),
        ("ca/t746", 1),
        ("ca/t776", 1),
        ("ca/t776", 2),
        ("ca/t777", 1),
        ("ca/t90", 1),
        ("ca/t936", 1),
        ("ca-on/return", 1),
    ]
    assert all(group.lines for group in groups)
