"""CA-ON 2025 end to end: return aj."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    NET_INCOME,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    APPLIES_FOR_ENERGY_AND_PROPERTY_TAX_CREDIT,
    APPLIES_FOR_NORTHERN_ENERGY_CREDIT,
    APPLIES_FOR_SENIOR_HOMEOWNERS_GRANT,
    CHOOSES_SINGLE_BENEFIT_PAYMENT,
    LIVED_IN_STUDENT_RESIDENCE,
    PROPERTY_TAX_PAID,
    PUBLIC_LONG_TERM_CARE_PAID,
    RENT_PAID,
    RESERVE_HOME_ENERGY_COSTS,
    SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, return_a


def return_aj(**overrides: Any) -> Worksheet:
    """Return AJ's inputs, as in `returns/2025_return_aj.yaml`: Return B's filer on Form ON-BEN.

    Employment income of 30000 and no other income, a deduction limit of 5400 and 3000 deducted,
    as Return B; the filer applies for the Ontario energy and property tax credit (line 61020 is
    ticked) and has paid rent of 14400.00 (line 61100), a chosen figure.
    """
    inputs: dict[str, Any] = {
        "income_tax_deducted": "3000",
        "applies_for_energy_and_property_tax_credit": 1,
        "rent_paid": "14400.00",
    }
    return compute("30000", (), "0", "0", "5400", "0", "0", **{**inputs, **overrides})


def test_return_ajs_on_ben_lines_are_carried_on_the_return_as_entered() -> None:
    # Form ON-BEN "Line 61020: If you met any of these conditions and are applying for the 2026
    # OEPTC, tick this box" and "Line: 61100: Enter the total amount of rent paid for your
    # principal residence (including a private long-term care home) in Ontario for 2025.": the
    # form computes nothing, so the tick is 1 and the rent 14400.00, as entered, and the other
    # eight lines are the 0 and $0 entered.
    worksheet = return_aj()

    assert worksheet.get(APPLIES_FOR_ENERGY_AND_PROPERTY_TAX_CREDIT).value == 1
    assert worksheet.get(APPLIES_FOR_NORTHERN_ENERGY_CREDIT).value == 0
    assert worksheet.get(CHOOSES_SINGLE_BENEFIT_PAYMENT).value == 0
    assert worksheet.get(APPLIES_FOR_SENIOR_HOMEOWNERS_GRANT).value == 0
    assert worksheet.get(SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS).value == 0
    assert worksheet.get(LIVED_IN_STUDENT_RESIDENCE).value == 0
    assert worksheet.get(RENT_PAID).value == D("14400.00")
    assert worksheet.get(PROPERTY_TAX_PAID).value == D("0")
    assert worksheet.get(RESERVE_HOME_ENERGY_COSTS).value == D("0")
    assert worksheet.get(PUBLIC_LONG_TERM_CARE_PAID).value == D("0")


def test_each_on_ben_line_is_carried_as_entered_whatever_the_others_are() -> None:
    # Part A's lines 61100, 61120, 61210 and 61230 and the six tick boxes each stand alone: a
    # different figure on each, so that a line carried from another would show.
    # Line 61080 is ticked with a spouse or common-law partner on December 31, 2025 (the spouse fact
    # is 1), since a tick of 1 with no spouse is refused (as in `test_return_ge.py`).
    worksheet = return_aj(
        applies_for_energy_and_property_tax_credit=0,
        applies_for_northern_energy_credit=1,
        chooses_single_benefit_payment=1,
        applies_for_senior_homeowners_grant=1,
        separate_residences_for_medical_reasons=1,
        spouse_or_common_law_partner_on_december_31=1,
        lived_in_student_residence=1,
        rent_paid="9600.50",
        property_tax_paid="3210.25",
        reserve_home_energy_costs="1875.75",
        public_long_term_care_paid="21000.00",
    )

    assert worksheet.get(APPLIES_FOR_ENERGY_AND_PROPERTY_TAX_CREDIT).value == 0
    assert worksheet.get(APPLIES_FOR_NORTHERN_ENERGY_CREDIT).value == 1
    assert worksheet.get(CHOOSES_SINGLE_BENEFIT_PAYMENT).value == 1
    assert worksheet.get(APPLIES_FOR_SENIOR_HOMEOWNERS_GRANT).value == 1
    assert worksheet.get(SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS).value == 1
    assert worksheet.get(LIVED_IN_STUDENT_RESIDENCE).value == 1
    assert worksheet.get(RENT_PAID).value == D("9600.50")
    assert worksheet.get(PROPERTY_TAX_PAID).value == D("3210.25")
    assert worksheet.get(RESERVE_HOME_ENERGY_COSTS).value == D("1875.75")
    assert worksheet.get(PUBLIC_LONG_TERM_CARE_PAID).value == D("21000.00")


def test_a_return_that_does_not_apply_on_form_on_ben_carries_its_lines_as_0() -> None:
    worksheet = return_a()

    for kind in (
        APPLIES_FOR_ENERGY_AND_PROPERTY_TAX_CREDIT,
        APPLIES_FOR_NORTHERN_ENERGY_CREDIT,
        CHOOSES_SINGLE_BENEFIT_PAYMENT,
        APPLIES_FOR_SENIOR_HOMEOWNERS_GRANT,
        SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS,
        LIVED_IN_STUDENT_RESIDENCE,
    ):
        assert worksheet.get(kind).value == 0, kind.identifier
    for amount_kind in (
        RENT_PAID,
        PROPERTY_TAX_PAID,
        RESERVE_HOME_ENERGY_COSTS,
        PUBLIC_LONG_TERM_CARE_PAID,
    ):
        assert worksheet.get(amount_kind).value == D("0"), amount_kind.identifier


def test_the_on_ben_lines_change_no_computed_line() -> None:
    # The benefit amounts are not on the return and nothing is computed from Form ON-BEN: Return
    # AJ has Return B's net income, 29735.00, and its refund, -2402.96, whatever it applies for.
    applying = return_aj()
    not_applying = return_aj(
        applies_for_energy_and_property_tax_credit=0, rent_paid="0", property_tax_paid="0"
    )

    for worksheet in (applying, not_applying):
        assert worksheet.get(NET_INCOME).value == D("29735.00")
        assert worksheet.get(TOTAL_CREDITS).value == D("4201.00")
        assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-2402.96")
        assert worksheet.get(ontario.NET_REFUND).value == D("2402.96")
