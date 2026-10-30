"""CA-ON 2025 end to end: return dp, Form T2043 Parts 1, 2 and 5 with Chart A.

Return DP (returns/2025_return_dp.yaml) is an Ontario farm and a Manitoba farm, each on its own
Form T2042 statement for a fiscal period of 365 days, 184 of them in 2024. Each statement's
Chart A (Form T2043) is computed for the statement, and Form T2043 totals the statements: Part 1
line 67061, Part 2 lines 2A to 2I, and Part 5 lines 5A to 5D, the last being line 47556 of the
return. The gate of Part 1 Note 1 ("$25,000 or more") zeroes Part 5 line 5A below it; the
partnership credits of Part 5 are not gated.

The statements are the keywords of `t2042_statement` (`farm_designated_province`, the province
code 1 to 8 in the form's order ON, MB, SK, AB, NS, PE, NL, NB, 0 for none;
`farm_non_arms_length_expenses`; `farm_days_in_2024`), and the eight partnership credits are the
keywords of `starting`, which the examples give as they need them.

Form T2043's line 5B (the amount 4I of Part 4, which is not yet wired) is 0 in every case here.
Amount 7 (days in 2024 over the period's days) is an exact fraction inside amount 8, so the
examples check amount 8 (through the provinces' amounts) and the lines that follow it.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FARM_AMOUNT_8_ON,
    FARM_CHART_A_GROSS_EXPENSES,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_CREDIT_MB,
    FUEL_CHARGE_CREDIT_ON,
    FUEL_CHARGE_EXPENSES_MB,
    FUEL_CHARGE_EXPENSES_ON,
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
    FUEL_CHARGE_PART_2_TOTAL,
    FUEL_CHARGE_PART_5A_CREDIT,
    FUEL_CHARGE_PART_5B_CREDIT,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_ON,
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


def statement(
    province: int,
    expenses: str,
    *,
    days_in_2024: int = 184,
    period_days: int = 365,
    fuel_charge_credit: str = "0",
    **changes: Any,
) -> dict[str, Any]:
    """One Form T2042 statement, as the keywords of `t2042_statement`: the wheat income equals the
    seeds and plants expense, so the net income is 0 before line 9951; no inventory adjustment, no
    partner; the designated province, the days in 2024 and line 9951 (the credit allocated to the
    business) as given."""
    return {
        "farm": {
            "wheat": expenses,
            "seeds_and_plants": expenses,
            "fuel_charge_credit": fuel_charge_credit,
        },
        "farm_fiscal_period_days_entered": period_days,
        "farm_designated_province": province,
        "farm_days_in_2024": days_in_2024,
        **changes,
    }


def run_dp(
    *statements: Mapping[str, Any],
    partnership: Mapping[str, str] | None = None,
) -> dict[str, tuple[Worksheet, ...]]:
    """Return DP's starting artifacts, with the statements and the partnership credits given.

    The statements replace the blank list of `starting`; the partnership credits are the eight
    inputs of Form T2043 Part 5 (the ones not given are 0)."""
    credits = partnership or {}
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=statements,
        fuel_charge_partnership_credit_on=credits.get("on", "0"),
        fuel_charge_partnership_credit_mb=credits.get("mb", "0"),
        fuel_charge_partnership_credit_sk=credits.get("sk", "0"),
        fuel_charge_partnership_credit_ab=credits.get("ab", "0"),
        fuel_charge_partnership_credit_ns=credits.get("ns", "0"),
        fuel_charge_partnership_credit_pe=credits.get("pe", "0"),
        fuel_charge_partnership_credit_nl=credits.get("nl", "0"),
        fuel_charge_partnership_credit_nb=credits.get("nb", "0"),
    )
    return service().compute(CA_ON, 2025, *artifacts)


def only(worksheets: tuple[Worksheet, ...]) -> Worksheet:
    (worksheet,) = worksheets
    return worksheet


# --- the acceptance examples of Form T2043 -------------------------------------------------------


def test_an_ontario_farm_of_36500_with_184_of_365_days_gives_a_credit_of_42_14() -> None:
    # Amount 6 is 36,500.00 and amount 8 is 36,500 times 184/365, which is 18,400.00; line 2A is
    # 18,400 at 0.229%, 42.136, rounded half-up to 42.14; 2I and line 47556 are 42.14.
    result = run_dp(statement(ONTARIO, "36500"))
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_CHART_A_GROSS_EXPENSES).value == D("36500.00")
    assert farm.get(FARM_AMOUNT_8_ON).value == D("18400.00")
    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("36500.00")
    assert form.get(FUEL_CHARGE_EXPENSES_ON).value == D("18400.00")
    assert form.get(FUEL_CHARGE_CREDIT_ON).value == D("42.14")
    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("42.14")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("42.14")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("0")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("42.14")


def test_the_same_farm_of_20000_is_below_the_25000_gate_so_5a_and_line_47556_are_0() -> None:
    result = run_dp(statement(ONTARIO, "20000"))
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("20000.00")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("0.00")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("0.00")


def test_a_period_starting_and_ending_in_2025_gives_amount_8_and_the_credit_0() -> None:
    # Days in 2024 of 0 (a period that starts and ends in 2025): amount 7 is 0, so amount 8 is 0.
    result = run_dp(statement(ONTARIO, "36500", days_in_2024=0, period_days=365))
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_AMOUNT_8_ON).value == D("0.00")
    assert form.get(FUEL_CHARGE_CREDIT_ON).value == D("0.00")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("0.00")


def test_an_ontario_and_a_manitoba_farm_give_54750_and_a_credit_of_63_21() -> None:
    # Ontario 36,500 (amount 8 18,400.00, 2A 42.14) and Manitoba 18,250 (amount 8 9,200.00, 2B
    # 21.07, 9,200 at 0.229% being 21.068): 2I is 42.14 + 21.07, and 5A and line 47556 are 63.21.
    result = run_dp(
        statement(ONTARIO, "36500"),
        statement(MANITOBA, "18250"),
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("54750.00")
    assert form.get(FUEL_CHARGE_CREDIT_ON).value == D("42.14")
    assert form.get(FUEL_CHARGE_EXPENSES_MB).value == D("9200.00")
    assert form.get(FUEL_CHARGE_CREDIT_MB).value == D("21.07")
    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("63.21")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("63.21")


def test_a_partnership_credit_of_100_for_ontario_is_added_even_under_the_gate() -> None:
    # Line 67061 is 20,000.00, under 25,000, so 5A is 0; 5C is the partnership credit of 100.00,
    # which is not gated, so 5D and line 47556 are 100.00. Line 9951 of the statement is the same
    # 100.00 (Form T2043 note 2).
    result = run_dp(
        statement(ONTARIO, "20000", fuel_charge_credit="100.00"),
        partnership={"on": "100.00"},
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("20000.00")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("0.00")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_ON).value == D("100.00")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL).value == D("100.00")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("100.00")


def test_days_in_2024_above_the_days_of_the_fiscal_period_are_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run_dp(statement(ONTARIO, "36500", days_in_2024=200, period_days=180))


@pytest.mark.parametrize("province", [9, 10])
def test_a_province_code_above_8_is_refused_not_dropped(province: int) -> None:
    # A code above 8 names none of the provinces of Part 2, so its amount 8 would be added to none
    # of lines 2A to 2H and the credit would be understated with no error shown: it is refused.
    with pytest.raises(InputOutOfRangeError, match="ca/farm_designated_province"):
        run_dp(statement(province, "36500"))


def test_a_province_code_above_8_on_the_second_statement_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError, match=r"ca/farm_designated_province 9 is refused"):
        run_dp(statement(ONTARIO, "36500"), statement(9, "18250"))


def test_province_code_0_for_a_farm_in_none_of_the_provinces_adds_nothing_to_part_2() -> None:
    result = run_dp(statement(0, "36500"))
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("0")


@pytest.mark.parametrize("province", [1, 2, 3, 4, 5, 6, 7, 8])
def test_every_province_code_from_1_to_8_is_accepted(province: int) -> None:
    result = run_dp(statement(province, "36500"))
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("36500.00")
    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value > D("0")


def test_no_statements_gives_line_47556_of_0_and_no_chart_a() -> None:
    result = run_dp()
    form = only(result["ca/t2043"])

    assert result["ca/t2042"] == ()
    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("0")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("0")
