"""CA-ON 2025 end to end: return bl, two Form T2121 statements on one return."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.trace import FormInstanceLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FISHING_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, compute, run, service

# T2121 Part 3 "Fish products" (amount 3A): the first fishing business has 12,000 of it and no
# expenses, so its line 9946 "Your net income (loss)" is 12,000. The second has no income and
# fishing gear (line 9136) of 2,000, so its line 9946 is 0 - 2,000 = -2,000: a loss.
FISH_1: dict[str, Any] = {"fish": {"fish_products": "12000"}}
FISH_2: dict[str, Any] = {"fish": {"fishing_gear": "2000"}}


def bl_inputs(statements: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    """Return BL's inputs, as in `returns/2025_return_bl.yaml`: a sole proprietor with the T2121
    `statements` given (none: no fishing business), no business, no farm, no rental operation and
    no other income."""
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
        "fish_statements": statements,
        "farm_statements": (),
    }


def return_bl(*statements: dict[str, Any]) -> Worksheet:
    """The return form's worksheet of return BL with the T2121 `statements`."""
    return compute(**bl_inputs(statements))


def run_bl(*statements: dict[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return BL with the T2121 `statements`."""
    return run(**bl_inputs(statements))


def net_incomes(result: dict[str, tuple[Worksheet, ...]]) -> list[Any]:
    """Line 9946 of each statement, in statement order, as its own form's worksheet holds it (the
    return no longer carries the list of statements: it reads the profit of each business from
    Form T1139's summary form)."""
    return [worksheet.get(FISHING_INCOME).value for worksheet in result["ca/t2121"]]


def test_two_statements_with_lines_9946_of_12000_and_minus_2000_give_line_14300_of_10000() -> None:
    # T1 line 14300 "Net" adds the lines 9946 of the statements: 12,000.00 + (-2,000.00).
    worksheet = return_bl(FISH_1, FISH_2)

    assert worksheet.get(FISHING_INCOME).value == D("10000.00")


def test_line_14300_is_the_whole_of_net_self_employment_income_and_total_income() -> None:
    worksheet = return_bl(FISH_1, FISH_2)

    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("10000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("10000.00")


def test_the_return_receives_line_9946_of_each_statement_in_statement_order() -> None:
    result = run_bl(FISH_1, FISH_2)

    assert net_incomes(result) == [D("12000.00"), D("-2000.00")]


def test_the_order_of_the_statements_does_not_change_the_total() -> None:
    worksheet = return_bl(FISH_2, FISH_1)
    result = run_bl(FISH_2, FISH_1)

    assert net_incomes(result) == [D("-2000.00"), D("12000.00")]
    assert worksheet.get(FISHING_INCOME).value == D("10000.00")


def test_one_statement_gives_its_own_line_9946_a_loss_staying_a_loss() -> None:
    assert return_bl(FISH_1).get(FISHING_INCOME).value == D("12000.00")
    assert return_bl(FISH_2).get(FISHING_INCOME).value == D("-2000.00")


def test_a_third_statement_is_added_too() -> None:
    worksheet = return_bl(FISH_1, FISH_2, FISH_1)

    assert worksheet.get(FISHING_INCOME).value == D("22000.00")


def test_a_return_with_no_statement_has_line_14300_of_zero() -> None:
    worksheet = return_bl()
    result = run_bl()

    assert worksheet.get(FISHING_INCOME).value == D("0")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("0")
    assert worksheet.get(TOTAL_INCOME).value == D("0")
    assert net_incomes(result) == []


def test_each_statement_has_its_own_worksheet_with_its_line_9946() -> None:
    result = run_bl(FISH_1, FISH_2)

    assert [worksheet.get(FISHING_INCOME).value for worksheet in result["ca/t2121"]] == [
        D("12000.00"),
        D("-2000.00"),
    ]
    assert len(result["ca/t2121"]) == 2


def test_a_return_with_no_statement_runs_the_form_on_no_instance() -> None:
    assert run_bl()["ca/t2121"] == ()


def test_the_trace_keeps_the_lines_of_each_statement_under_its_position() -> None:
    result = run_bl(FISH_1, FISH_2)

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
        ("ca/farm_loss", 1),
        ("ca/t2043", 1),
        ("ca/t2121", 1),
        ("ca/t2121", 2),
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
