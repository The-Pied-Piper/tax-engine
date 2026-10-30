"""CA-ON 2025 end to end: return bk, two Form T2042 statements on one return."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.trace import FormInstanceLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FARMING_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, compute, run, service

# T2042 Part 3 "Wheat" (line 9371): the first farming business has 12,000 of it and no expenses, so
# its line 9946 "Your net income (loss)" is 12,000. The second has no income and fertilizers and
# lime (line 9662) of 2,000, so its line 9946 is 0 - 2,000 = -2,000: a loss.
FARM_1: dict[str, Any] = {"farm": {"wheat": "12000"}}
FARM_2: dict[str, Any] = {"farm": {"fertilizers_and_lime": "2000"}}


def bk_inputs(statements: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    """Return BK's inputs, as in `returns/2025_return_bk.yaml`: a sole proprietor with the T2042
    `statements` given (none: no farming business), no business, no fishing, no rental operation
    and no other income."""
    return {
        "employment_income": "0",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "rental_statements": (),
        "business_statements": (),
        "farm_statements": statements,
        "fish_statements": (),
    }


def return_bk(*statements: dict[str, Any]) -> Worksheet:
    """The return form's worksheet of return BK with the T2042 `statements`."""
    return compute(**bk_inputs(statements))


def run_bk(*statements: dict[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return BK with the T2042 `statements`."""
    return run(**bk_inputs(statements))


def net_incomes(result: dict[str, tuple[Worksheet, ...]]) -> list[Any]:
    """Line 9946 of each statement, in statement order, as its own form's worksheet holds it (the
    return no longer carries the list of statements: it reads the profit of each business from
    Form T1139's summary form)."""
    return [worksheet.get(FARMING_INCOME).value for worksheet in result["ca/t2042"]]


def test_two_statements_with_lines_9946_of_12000_and_minus_2000_give_line_14100_of_10000() -> None:
    # T1 line 14100 "Net" adds the lines 9946 of the statements: 12,000.00 + (-2,000.00).
    worksheet = return_bk(FARM_1, FARM_2)

    assert worksheet.get(FARMING_INCOME).value == D("10000.00")


def test_line_14100_is_the_whole_of_net_self_employment_income_and_total_income() -> None:
    worksheet = return_bk(FARM_1, FARM_2)

    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("10000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("10000.00")


def test_the_return_receives_line_9946_of_each_statement_in_statement_order() -> None:
    result = run_bk(FARM_1, FARM_2)

    assert net_incomes(result) == [D("12000.00"), D("-2000.00")]


def test_the_order_of_the_statements_does_not_change_the_total() -> None:
    worksheet = return_bk(FARM_2, FARM_1)
    result = run_bk(FARM_2, FARM_1)

    assert net_incomes(result) == [D("-2000.00"), D("12000.00")]
    assert worksheet.get(FARMING_INCOME).value == D("10000.00")


def test_one_statement_gives_its_own_line_9946_a_loss_staying_a_loss() -> None:
    assert return_bk(FARM_1).get(FARMING_INCOME).value == D("12000.00")
    assert return_bk(FARM_2).get(FARMING_INCOME).value == D("-2000.00")


def test_a_third_statement_is_added_too() -> None:
    worksheet = return_bk(FARM_1, FARM_2, FARM_1)

    assert worksheet.get(FARMING_INCOME).value == D("22000.00")


def test_a_return_with_no_statement_has_line_14100_of_zero() -> None:
    worksheet = return_bk()
    result = run_bk()

    assert worksheet.get(FARMING_INCOME).value == D("0")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("0")
    assert worksheet.get(TOTAL_INCOME).value == D("0")
    assert net_incomes(result) == []


def test_each_statement_has_its_own_worksheet_with_its_line_9946() -> None:
    result = run_bk(FARM_1, FARM_2)

    assert [worksheet.get(FARMING_INCOME).value for worksheet in result["ca/t2042"]] == [
        D("12000.00"),
        D("-2000.00"),
    ]
    assert len(result["ca/t2042"]) == 2


def test_a_return_with_no_statement_runs_the_form_on_no_instance() -> None:
    assert run_bk()["ca/t2042"] == ()


def test_the_trace_keeps_the_lines_of_each_statement_under_its_position() -> None:
    result = run_bk(FARM_1, FARM_2)

    groups = [
        line
        for line in service().compose(CA_ON, 2025).trace(result)
        if isinstance(line, FormInstanceLine)
    ]

    assert [(group.form, group.position) for group in groups] == [
        ("ca/has_investment_expenses", 1),
        ("ca/schedule_3", 1),
        ("ca/spouse_on_december_31", 1),
        ("ca/t1032", 1),
        ("ca/t1043", 1),
        ("ca/t1206_share_dispositions", 1),
        ("ca/t1212", 1),
        ("ca/t2017", 1),
        ("ca/t2042", 1),
        ("ca/t2042", 2),
        ("ca/farm_loss", 1),
        ("ca/t2043", 1),
        ("ca/t1139_return", 1),
        ("ca/schedule_8", 1),
        ("ca/t2205", 1),
        ("ca/t746", 1),
        ("ca/t777", 1),
        ("ca/t90", 1),
        ("ca/t936", 1),
        ("ca-on/return", 1),
    ]
    assert all(group.lines for group in groups)
