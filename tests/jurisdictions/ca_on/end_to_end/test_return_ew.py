"""CA-ON 2025 end to end: return ew, Form T2043 Parts 1, 2 and 5 and the partnership credits.

Return EW (returns/2025_return_ew.yaml) is two Alberta farming businesses, each on its own Form
T2042 statement for a fiscal period of 365 days, 365 of them in 2024. Their gross farming expenses
total 25,000.00 on Part 1 line 67061, which is exactly the "$25,000 or more" of Note 1, so the gate
passes and Part 5 line 5A is the Part 2 credit. Part 5 line 5C adds the eight partnership credits,
which are not gated, and line 5D is line 47556 of the return.

The statements are the keywords of `t2042_statement` (`farm_designated_province` 4 for Alberta,
`farm_non_arms_length_expenses`, `farm_days_in_2024`), and the eight partnership credits are the
keywords `fuel_charge_partnership_credit_<province>` of `starting`. The wheat income of each
statement is its seeds and plants expense plus 10,000, so each net farming income is 10,000.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FARM_AMOUNT_8_AB,
    FARM_CHART_A_GROSS_EXPENSES,
    FUEL_CHARGE_CREDIT_AB,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_EXPENSES_AB,
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
    FUEL_CHARGE_PART_2_TOTAL,
    FUEL_CHARGE_PART_5A_CREDIT,
    FUEL_CHARGE_PART_5B_CREDIT,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_AB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_MB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NB,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NL,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_NS,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_ON,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_PE,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_SK,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    service,
    starting,
)

ALBERTA = 4

PARTNERSHIP_CREDITS = {
    "on": "11.11",
    "mb": "22.22",
    "sk": "33.33",
    "ab": "44.44",
    "ns": "55.55",
    "pe": "66.66",
    "nl": "77.77",
    "nb": "88.88",
}


def statement(
    province: int,
    expenses: str,
    *,
    days_in_2024: int = 365,
    period_days: int = 365,
    fuel_charge_credit: str = "0",
    **changes: Any,
) -> dict[str, Any]:
    """One Form T2042 statement, as the keywords of `t2042_statement`: the wheat income is the seeds
    and plants expense plus 10,000 less line 9951, so the net farming income is 10,000; no
    inventory adjustment, no partner and no non-arm's length expense; the designated province, the
    days in 2024 and line 9951 (the credit allocated to the business) as given.
    """
    return {
        "farm": {
            "wheat": str(D(expenses) + 10000 - D(fuel_charge_credit)),
            "seeds_and_plants": expenses,
            "fuel_charge_credit": fuel_charge_credit,
        },
        "farm_fiscal_period_days_entered": period_days,
        "farm_designated_province": province,
        "farm_days_in_2024": days_in_2024,
        **changes,
    }


def run_ew(
    *statements: Mapping[str, Any],
    partnership: Mapping[str, str] | None = None,
) -> dict[str, tuple[Worksheet, ...]]:
    """Return EW's starting artifacts, with the statements and the partnership credits given (the
    ones not given are 0)."""
    credits = {**dict.fromkeys(PARTNERSHIP_CREDITS, "0"), **(partnership or {})}
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=statements,
        fuel_charge_partnership_credit_on=credits["on"],
        fuel_charge_partnership_credit_mb=credits["mb"],
        fuel_charge_partnership_credit_sk=credits["sk"],
        fuel_charge_partnership_credit_ab=credits["ab"],
        fuel_charge_partnership_credit_ns=credits["ns"],
        fuel_charge_partnership_credit_pe=credits["pe"],
        fuel_charge_partnership_credit_nl=credits["nl"],
        fuel_charge_partnership_credit_nb=credits["nb"],
    )
    return service().compute(CA_ON, 2025, *artifacts)


def only(worksheets: tuple[Worksheet, ...]) -> Worksheet:
    (worksheet,) = worksheets
    return worksheet


# --- the two Alberta farms and the eight partnership credits ----------------------------


def test_two_alberta_farms_of_12500_reach_the_25000_gate_so_5a_is_their_credit_of_57_25() -> None:
    # Amount 8 is 12,500.00 for each farm, 25,000.00 in all on line 2D (25,000 x 0.00229 = 57.25).
    # Line 67061 is exactly 25,000.00, which is accepted: 5A is 57.25.
    result = run_ew(
        statement(ALBERTA, "12500"),
        statement(ALBERTA, "12500"),
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("25000")
    assert form.get(FUEL_CHARGE_EXPENSES_AB).value == D("25000.00")
    assert form.get(FUEL_CHARGE_CREDIT_AB).value == D("57.25")
    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("57.25")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("57.25")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("0")


def test_each_alberta_statement_gives_amount_8_of_12500() -> None:
    result = run_ew(
        statement(ALBERTA, "12500"),
        statement(ALBERTA, "12500"),
    )
    farms = result["ca/t2042"]

    assert [farm.get(FARM_CHART_A_GROSS_EXPENSES).value for farm in farms] == [
        D("12500"),
        D("12500"),
    ]
    assert [farm.get(FARM_AMOUNT_8_AB).value for farm in farms] == [
        D("12500.00"),
        D("12500.00"),
    ]


def test_the_eight_partnership_credits_total_399_96_and_are_added_to_line_47556() -> None:
    # 11.11 + 22.22 + 33.33 + 44.44 + 55.55 + 66.66 + 77.77 + 88.88 = 399.96 on line 5C, and line
    # 5D (line 47556) is 5A 57.25 plus 5C 399.96, which is 457.21.
    result = run_ew(
        statement(ALBERTA, "12500", fuel_charge_credit="200.00"),
        statement(ALBERTA, "12500", fuel_charge_credit="199.96"),
        partnership=PARTNERSHIP_CREDITS,
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_ON).value == D("11.11")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_MB).value == D("22.22")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_SK).value == D("33.33")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_AB).value == D("44.44")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_NS).value == D("55.55")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_PE).value == D("66.66")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_NL).value == D("77.77")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_NB).value == D("88.88")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL).value == D("399.96")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("457.21")


def test_below_the_gate_5a_is_0_but_the_partnership_credits_are_not_gated() -> None:
    # Two Alberta farms of 12,400 each: line 67061 is 24,800.00, under 25,000, so 5A and the credit
    # of the farms are 0, while the partnership credits of 399.96 are added on line 5C, not gated.
    result = run_ew(
        statement(ALBERTA, "12400", fuel_charge_credit="200.00"),
        statement(ALBERTA, "12400", fuel_charge_credit="199.96"),
        partnership=PARTNERSHIP_CREDITS,
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("24800.00")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("0.00")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL).value == D("399.96")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("399.96")


def test_partnership_credits_alone_give_line_47556_with_no_statement() -> None:
    result = run_ew(partnership=PARTNERSHIP_CREDITS)
    form = only(result["ca/t2043"])

    assert result["ca/t2042"] == ()
    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("0")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("0")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("399.96")
