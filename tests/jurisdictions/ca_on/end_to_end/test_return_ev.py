"""CA-ON 2025 end to end: return ev, Form T2043 Parts 1, 2 and 5 with Chart A, six provinces.

Return EV (returns/2025_return_ev.yaml) is six farming businesses, each on its own Form T2042
statement for a fiscal period of 365 days, one in each designated province other than Ontario and
Manitoba: Saskatchewan (code 3), Alberta (4), Nova Scotia (5), Prince Edward Island (6),
Newfoundland and Labrador (7) and New Brunswick (8). Form T2043 totals the statements: Part 1 line
67061, Part 2 lines 2A to 2I (one credit per province) and Part 5 lines 5A to 5D, the last being
line 47556 of the return. The gate of Part 1 Note 1 ("$25,000 or more") zeroes Part 5 line 5A
below it.

The statements are the keywords of `t2042_statement` (`farm_designated_province`, the province
code 1 to 8 in the form's order ON, MB, SK, AB, NS, PE, NL, NB, 0 for none;
`farm_non_arms_length_expenses`; `farm_days_in_2024`), and the wheat income of each statement is
its seeds and plants expense plus 10,000, so each net farming income is 10,000.

Amount 7 (days in 2024 over the period's days) is an exact fraction inside amount 8, so the
examples check amount 8 (through the provinces' amounts) and the lines that follow it.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FARM_AMOUNT_8_AB,
    FARM_AMOUNT_8_NB,
    FARM_AMOUNT_8_NL,
    FARM_AMOUNT_8_NS,
    FARM_AMOUNT_8_PE,
    FARM_AMOUNT_8_SK,
    FARM_CHART_A_GROSS_EXPENSES,
    FUEL_CHARGE_CREDIT_AB,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_CREDIT_NB,
    FUEL_CHARGE_CREDIT_NL,
    FUEL_CHARGE_CREDIT_NS,
    FUEL_CHARGE_CREDIT_PE,
    FUEL_CHARGE_CREDIT_SK,
    FUEL_CHARGE_EXPENSES_AB,
    FUEL_CHARGE_EXPENSES_NB,
    FUEL_CHARGE_EXPENSES_NL,
    FUEL_CHARGE_EXPENSES_NS,
    FUEL_CHARGE_EXPENSES_PE,
    FUEL_CHARGE_EXPENSES_SK,
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
    FUEL_CHARGE_PART_2_TOTAL,
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

SASKATCHEWAN = 3
ALBERTA = 4
NOVA_SCOTIA = 5
PRINCE_EDWARD_ISLAND = 6
NEWFOUNDLAND_AND_LABRADOR = 7
NEW_BRUNSWICK = 8

# The six provinces of return EV: (designated province code, amount 8 of the statement's province,
# the province's expenses and credit of Part 2), with the Part 2 line of the credit.
PROVINCES = (
    (SASKATCHEWAN, FARM_AMOUNT_8_SK, FUEL_CHARGE_EXPENSES_SK, FUEL_CHARGE_CREDIT_SK),
    (ALBERTA, FARM_AMOUNT_8_AB, FUEL_CHARGE_EXPENSES_AB, FUEL_CHARGE_CREDIT_AB),
    (NOVA_SCOTIA, FARM_AMOUNT_8_NS, FUEL_CHARGE_EXPENSES_NS, FUEL_CHARGE_CREDIT_NS),
    (PRINCE_EDWARD_ISLAND, FARM_AMOUNT_8_PE, FUEL_CHARGE_EXPENSES_PE, FUEL_CHARGE_CREDIT_PE),
    (NEWFOUNDLAND_AND_LABRADOR, FARM_AMOUNT_8_NL, FUEL_CHARGE_EXPENSES_NL, FUEL_CHARGE_CREDIT_NL),
    (NEW_BRUNSWICK, FARM_AMOUNT_8_NB, FUEL_CHARGE_EXPENSES_NB, FUEL_CHARGE_CREDIT_NB),
)


def statement(
    province: int,
    expenses: str,
    *,
    days_in_2024: int,
    period_days: int = 365,
    **changes: Any,
) -> dict[str, Any]:
    """One Form T2042 statement, as the keywords of `t2042_statement`: the wheat income is the seeds
    and plants expense plus 10,000, so the net farming income is 10,000; no inventory adjustment, no
    partner and no non-arm's length expense; the designated province and the days in 2024 as given.
    """
    return {
        "farm": {"wheat": str(D(expenses) + 10000), "seeds_and_plants": expenses},
        "farm_fiscal_period_days_entered": period_days,
        "farm_designated_province": province,
        "farm_days_in_2024": days_in_2024,
        **changes,
    }


def run_ev(*statements: Mapping[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Return EV's starting artifacts, with the statements given; the partnership credits are 0."""
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


# --- the six farms of return EV ---------------------------------------------


def test_six_farms_in_six_provinces_give_gross_expenses_of_192450_and_a_credit_of_230_31() -> None:
    # Amount 6 is 40,000 + 50,000 + 30,000 + 25,000 + 36,500 + 10,950 = 192,450 on line 67061. Each
    # province's amount 8 at 0.229%: SK 91.60, AB 22.90, NS 54.96, PE 22.90, NL 22.90 and NB 15.05
    # (6,570 x 0.00229 = 15.0453, half-up to 15.05): 2I is 230.31, and 5A and line 47556 are 230.31.
    result = run_ev(
        statement(SASKATCHEWAN, "40000", days_in_2024=365),
        statement(ALBERTA, "50000", days_in_2024=73),
        statement(NOVA_SCOTIA, "30000", days_in_2024=292),
        statement(PRINCE_EDWARD_ISLAND, "25000", days_in_2024=146),
        statement(NEWFOUNDLAND_AND_LABRADOR, "36500", days_in_2024=100),
        statement(NEW_BRUNSWICK, "10950", days_in_2024=219),
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("192450")
    assert form.get(FUEL_CHARGE_EXPENSES_SK).value == D("40000.00")
    assert form.get(FUEL_CHARGE_EXPENSES_AB).value == D("10000.00")
    assert form.get(FUEL_CHARGE_EXPENSES_NS).value == D("24000.00")
    assert form.get(FUEL_CHARGE_EXPENSES_PE).value == D("10000.00")
    assert form.get(FUEL_CHARGE_EXPENSES_NL).value == D("10000.00")
    assert form.get(FUEL_CHARGE_EXPENSES_NB).value == D("6570.00")
    assert form.get(FUEL_CHARGE_CREDIT_SK).value == D("91.60")
    assert form.get(FUEL_CHARGE_CREDIT_AB).value == D("22.90")
    assert form.get(FUEL_CHARGE_CREDIT_NS).value == D("54.96")
    assert form.get(FUEL_CHARGE_CREDIT_PE).value == D("22.90")
    assert form.get(FUEL_CHARGE_CREDIT_NL).value == D("22.90")
    assert form.get(FUEL_CHARGE_CREDIT_NB).value == D("15.05")
    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("230.31")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("230.31")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("0")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL).value == D("0")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("230.31")


def test_each_statement_gives_its_amount_8_of_the_table_on_its_own_chart_a() -> None:
    # Amount 8 of each Chart A is amount 6 times amount 7 (days in 2024 over 365), rounded once:
    # 40,000.00, 10,000.00, 24,000.00, 10,000.00, 10,000.00 and 6,570.00, one per statement, in the
    # order of the statements. Each statement's net farming income is 10,000.
    result = run_ev(
        statement(SASKATCHEWAN, "40000", days_in_2024=365),
        statement(ALBERTA, "50000", days_in_2024=73),
        statement(NOVA_SCOTIA, "30000", days_in_2024=292),
        statement(PRINCE_EDWARD_ISLAND, "25000", days_in_2024=146),
        statement(NEWFOUNDLAND_AND_LABRADOR, "36500", days_in_2024=100),
        statement(NEW_BRUNSWICK, "10950", days_in_2024=219),
    )
    farms = result["ca/t2042"]

    assert [farm.get(FARM_CHART_A_GROSS_EXPENSES).value for farm in farms] == [
        D("40000"),
        D("50000"),
        D("30000"),
        D("25000"),
        D("36500"),
        D("10950"),
    ]
    assert farms[0].get(FARM_AMOUNT_8_SK).value == D("40000.00")
    assert farms[1].get(FARM_AMOUNT_8_AB).value == D("10000.00")
    assert farms[2].get(FARM_AMOUNT_8_NS).value == D("24000.00")
    assert farms[3].get(FARM_AMOUNT_8_PE).value == D("10000.00")
    assert farms[4].get(FARM_AMOUNT_8_NL).value == D("10000.00")
    assert farms[5].get(FARM_AMOUNT_8_NB).value == D("6570.00")


@pytest.mark.parametrize(("province", "amount_8", "expenses", "credit"), PROVINCES)
def test_a_farm_in_each_province_credits_only_its_own_part_2_line(
    province: int, amount_8: Any, expenses: Any, credit: Any
) -> None:
    # A 40,000 farm for 365 days in 2024, so amount 8 is 40,000.00 in every province and its credit
    # is 91.60 on that province's line, 0 on the other seven; 5A is 91.60 (the gate is passed).
    result = run_ev(statement(province, "40000", days_in_2024=365))
    form = only(result["ca/t2043"])

    assert form.get(expenses).value == D("40000.00")
    assert form.get(credit).value == D("91.60")
    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("91.60")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("91.60")


def test_a_new_brunswick_farm_of_10950_is_below_the_gate_so_5a_and_line_47556_are_0() -> None:
    # Amount 8 is 6,570.00 (10,950 x 219/365) and its credit on line 2H is 15.05 (15.0453, half-up),
    # but line 67061 is 10,950.00, under 25,000, so 5A is 0 and line 47556 is 0.
    result = run_ev(statement(NEW_BRUNSWICK, "10950", days_in_2024=219))
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_AMOUNT_8_NB).value == D("6570.00")
    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("10950.00")
    assert form.get(FUEL_CHARGE_CREDIT_NB).value == D("15.05")
    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("15.05")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("0.00")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("0.00")


def test_a_saskatchewan_farm_with_0_days_in_2024_gives_amount_8_and_the_credit_0() -> None:
    # Days in 2024 of 0 (a period that starts and ends in 2025): amount 7 is 0, so amount 8 is 0.
    result = run_ev(statement(SASKATCHEWAN, "40000", days_in_2024=0))
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_AMOUNT_8_SK).value == D("0.00")
    assert form.get(FUEL_CHARGE_CREDIT_SK).value == D("0.00")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("0.00")


def test_days_in_2024_above_the_days_of_the_fiscal_period_are_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run_ev(statement(ALBERTA, "50000", days_in_2024=200, period_days=180))
