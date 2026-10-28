"""CA-ON 2025 end to end: return je, the partnership credit on Form T2042 and Form T2043.

Return JE (returns/2025_return_je.yaml) is Return EW's two Alberta farming businesses with one
partnership credit of 500.00. Form T2043 note 2 says the credit allocated to each business is on
line 9951 of its Form T2042 and counts as farming income, and amount 5C of Form T2043 is the credit
of all the partnerships, so the total of line 9951 over the statements may not be above amount 5C
(it may be below: AgriStability and AgriInvest filers use other forms' line 9951).

The statements are the keywords of `t2042_statement` (line 9951 is `farm_fuel_charge_credit`, in the
farm amounts), and the eight partnership credits the keywords
`fuel_charge_partnership_credit_<province>` of `starting`. The wheat income of each statement is
its seeds and plants expense plus 10,000 less line 9951, so each net farming income is 10,000.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FARM_FUEL_CHARGE_CREDIT_TOTAL,
    FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED,
    FARM_NET_INCOME_AFTER_ADJUSTMENTS,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_PART_5A_CREDIT,
    FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

ALBERTA = 4
ABOVE_5C = r"farm_fuel_charge_credit_total 500.00 is above"


def statement(fuel_charge_credit: str = "0") -> dict[str, Any]:
    """One Alberta Form T2042 statement of 12,500.00 of expenses: the wheat income is the expenses
    plus 10,000 less line 9951, so the net farming income is 10,000, and line 9951 is the credit
    allocated to the business."""
    return {
        "farm": {
            "wheat": str(D("12500") + 10000 - D(fuel_charge_credit)),
            "seeds_and_plants": "12500",
            "fuel_charge_credit": fuel_charge_credit,
        },
        "farm_fiscal_period_days_entered": 365,
        "farm_designated_province": ALBERTA,
        "farm_days_in_2024": 365,
    }


def run_je(
    *statements: Mapping[str, Any], partnership: Mapping[str, str]
) -> dict[str, tuple[Worksheet, ...]]:
    """Return JE's starting artifacts, with the statements and the partnership credits given (the
    provinces not given are 0)."""
    credits = {
        **dict.fromkeys(("on", "mb", "sk", "ab", "ns", "pe", "nl", "nb"), "0"),
        **partnership,
    }
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


def test_a_credit_of_500_on_line_9951_and_on_line_67079_is_paid_as_line_47556() -> None:
    # Line 9951 of the first statement is 500.00, so the total over the statements is 500.00, which
    # is amount 5C (the Ontario line 67079 alone), and 5D is 5A 57.25 + 5C 500.00 = 557.25.
    result = run_je(statement("500.00"), statement(), partnership={"on": "500.00"})
    form = only(result["ca/t2043"])

    assert form.get(FARM_FUEL_CHARGE_CREDIT_TOTAL).value == D("500.00")
    assert form.get(FARM_FUEL_CHARGE_CREDIT_TOTAL_CHECKED).value == D("500.00")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL).value == D("500.00")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("57.25")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("557.25")


def test_the_credit_is_included_in_the_net_farming_income_of_the_statement_that_has_it() -> None:
    # Note 2: the portion of the credit allocated to the business is included in its net farming
    # income: 22,000.00 + 500.00 - 12,500.00 for the first statement and 22,500.00 - 12,500.00.
    result = run_je(statement("500.00"), statement(), partnership={"on": "500.00"})
    first, second = result["ca/t2042"]

    assert first.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value == D("10000.00")
    assert second.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value == D("10000")


def test_two_provinces_credit_matches_line_9951_over_two_statements() -> None:
    # Ontario 200.00 and Manitoba 300.00 on Form T2043, and 125.50 and 374.50 on the statements:
    # both total 500.00, whichever statement and province each part is on.
    result = run_je(
        statement("125.50"),
        statement("374.50"),
        partnership={"on": "200.00", "mb": "300.00"},
    )
    form = only(result["ca/t2043"])

    assert form.get(FARM_FUEL_CHARGE_CREDIT_TOTAL).value == D("500.00")
    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL).value == D("500.00")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("557.25")


def test_line_9951_above_amount_5c_is_refused_not_taxed_with_no_credit() -> None:
    # Line 9951 of 500.00 and amount 5C of 400.00: the credit would be taxed as farming income
    # while 100.00 of it is never paid.
    with pytest.raises(InputAboveBoundError, match=ABOVE_5C):
        run_je(statement("500.00"), statement(), partnership={"on": "400.00"})


def test_line_9951_with_no_credit_on_form_t2043_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=ABOVE_5C):
        run_je(statement("500.00"), statement(), partnership={})


def test_amount_5c_above_line_9951_is_accepted_for_the_agristability_forms() -> None:
    # Amount 5C of 600.00 and line 9951 of 500.00: the other 100.00 may be on line 9951 of Form
    # T1163, T1164, T1273 or T1274 (T2043 note 2), which the engine does not take, so it is paid.
    result = run_je(statement("500.00"), statement(), partnership={"on": "600.00"})
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_PARTNERSHIP_CREDIT_TOTAL).value == D("600.00")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("657.25")


def test_amount_5c_with_no_line_9951_on_any_statement_is_accepted() -> None:
    result = run_je(statement(), statement(), partnership={"on": "500.00"})
    form = only(result["ca/t2043"])

    assert form.get(FARM_FUEL_CHARGE_CREDIT_TOTAL).value == D("0")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("557.25")
