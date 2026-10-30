"""CA-ON 2025 end to end: return he, Form T2043 box 67062 with two statements in two provinces.

Return HE (returns/2025_return_he.yaml) is two farming businesses on two Form T2042 statements: a
farm in Ontario (designated province 1, amount 8 of 18,400.00) and a farm in Manitoba (designated
province 2, amount 8 of 9,200.00), each for a fiscal period of 365 days, 184 of them in 2024, and
with no Chart B. Part 2 (Chart A) gives 42.14 for Ontario and 21.07 for Manitoba, amount 5A and line
47556 are 63.21, and box 67062 is 1: the two statements are present in two places, Ontario and
Manitoba, so the box is ticked. The figures are the hand-worked ones of the return's description.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FARM_AMOUNT_8_MB,
    FARM_AMOUNT_8_ON,
    FARM_CHART_A_AMOUNT_8,
    FARM_PRESENT_AMOUNT_MB,
    FARM_PRESENT_AMOUNT_ON,
    FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_CREDIT_FARMERS_TOTAL,
    FUEL_CHARGE_CREDIT_MB,
    FUEL_CHARGE_CREDIT_ON,
    FUEL_CHARGE_EXPENSES_MB,
    FUEL_CHARGE_EXPENSES_ON,
    FUEL_CHARGE_FARM_STATEMENT_COUNT,
    FUEL_CHARGE_FARMS_IN_PROVINCE_MB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_ON,
    FUEL_CHARGE_FARMS_OUTSIDE_EIGHT,
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
    FUEL_CHARGE_MULTIPLE_PROVINCES_BOX,
    FUEL_CHARGE_PART_2_TOTAL,
    FUEL_CHARGE_PART_4_TOTAL,
    FUEL_CHARGE_PART_5A_CREDIT,
    FUEL_CHARGE_PART_5B_CREDIT,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    service,
    starting,
)

ONTARIO = 1
MANITOBA = 2


def statement(*, wheat: str, seeds_and_plants: str, province: int) -> dict[str, Any]:
    """One Form T2042 statement of Return HE: no salaries, no Chart B, a 365-day fiscal period with
    184 days in 2024, and the designated province `province`."""
    return {
        "farm": {"wheat": wheat, "seeds_and_plants": seeds_and_plants},
        "farm_chart_b_provinces_rows": (),
        "farm_fiscal_period_days_entered": 365,
        "farm_designated_province": province,
        "farm_days_in_2024": 184,
    }


STATEMENT_ONTARIO = statement(wheat="50000", seeds_and_plants="36500", province=ONTARIO)
STATEMENT_MANITOBA = statement(wheat="40000", seeds_and_plants="18250", province=MANITOBA)


def run_he(*statements: Mapping[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Return HE's starting artifacts with the statements given; the partnership credits are 0."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=statements,
        fuel_charge_partnership_credit_on="0",
        fuel_charge_partnership_credit_mb="0",
        fuel_charge_partnership_credit_sk="0",
        fuel_charge_partnership_credit_ab="0",
        fuel_charge_partnership_credit_ns="0",
        fuel_charge_partnership_credit_pe="0",
        fuel_charge_partnership_credit_nl="0",
        fuel_charge_partnership_credit_nb="0",
    )
    return service().compute(CA_ON, 2025, *artifacts)


def only(worksheets: tuple[Worksheet, ...]) -> Worksheet:
    (worksheet,) = worksheets
    return worksheet


def test_the_two_statements_are_present_in_ontario_and_in_manitoba_one_each() -> None:
    # Statement 1 is in Ontario and statement 2 in Manitoba; each is present in its one place only.
    result = run_he(STATEMENT_ONTARIO, STATEMENT_MANITOBA)
    ontario, manitoba = result["ca/t2042"]

    assert ontario.get(FARM_PRESENT_AMOUNT_ON).value == D("1")
    assert ontario.get(FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT).value == D("0")
    assert manitoba.get(FARM_PRESENT_AMOUNT_MB).value == D("1")
    assert manitoba.get(FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT).value == D("0")


def test_amount_8_is_18400_for_ontario_and_9200_for_manitoba() -> None:
    # Amount 6 of 36,500 times 184/365 is 18,400, and amount 6 of 18,250 times 184/365 is 9,200.
    result = run_he(STATEMENT_ONTARIO, STATEMENT_MANITOBA)
    ontario, manitoba = result["ca/t2042"]

    assert ontario.get(FARM_CHART_A_AMOUNT_8).value == D("18400")
    assert ontario.get(FARM_AMOUNT_8_ON).value == D("18400")
    assert ontario.get(FARM_AMOUNT_8_MB).value == D("0")
    assert manitoba.get(FARM_CHART_A_AMOUNT_8).value == D("9200")
    assert manitoba.get(FARM_AMOUNT_8_MB).value == D("9200")


def test_part_2_gives_42_14_for_ontario_and_21_07_for_manitoba_and_amount_5a_of_63_21() -> None:
    # 18,400 at 0.229% is 42.136, rounded half-up to 42.14; 9,200 at 0.229% is 21.068, to 21.07.
    result = run_he(STATEMENT_ONTARIO, STATEMENT_MANITOBA)
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_EXPENSES_ON).value == D("18400")
    assert form.get(FUEL_CHARGE_CREDIT_ON).value == D("42.14")
    assert form.get(FUEL_CHARGE_EXPENSES_MB).value == D("9200")
    assert form.get(FUEL_CHARGE_CREDIT_MB).value == D("21.07")
    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("63.21")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("63.21")


def test_the_total_gross_farming_expenses_of_54750_pass_the_25000_threshold() -> None:
    result = run_he(STATEMENT_ONTARIO, STATEMENT_MANITOBA)
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("54750")


def test_line_47556_is_63_21_with_no_chart_c_and_no_partnership_credit() -> None:
    # No Chart B means no Chart C, so Part 4 and amount 5B are 0, and no partnership credit either.
    result = run_he(STATEMENT_ONTARIO, STATEMENT_MANITOBA)
    form = only(result["ca/t2043"])
    return_form = only(result["ca-on/return"])

    assert form.get(FUEL_CHARGE_PART_4_TOTAL).value == D("0")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("0")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL).value == D("0")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("63.21")
    assert return_form.get(FUEL_CHARGE_CREDIT_FARMERS_TOTAL).value == D("63.21")


def test_box_67062_is_1_for_two_statements_in_ontario_and_manitoba() -> None:
    result = run_he(STATEMENT_ONTARIO, STATEMENT_MANITOBA)
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_FARM_STATEMENT_COUNT).value == 2
    assert form.get(FUEL_CHARGE_FARMS_IN_PROVINCE_ON).value == D("1")
    assert form.get(FUEL_CHARGE_FARMS_IN_PROVINCE_MB).value == D("1")
    assert form.get(FUEL_CHARGE_FARMS_OUTSIDE_EIGHT).value == D("0")
    assert form.get(FUEL_CHARGE_MULTIPLE_PROVINCES_BOX).value == 1
