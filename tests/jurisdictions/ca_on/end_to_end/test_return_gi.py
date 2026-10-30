"""CA-ON 2025 end to end: return GI, Form ON-BEN with every tick box and Part A amount set.

Return GI is `returns/2025_return_gi.yaml`: a simple Ontario filer with other income of 40000 only,
who sets five ON-BEN tick boxes (lines 61020, 61040, 61060, 61070 and 61140; 61080 is left
unticked for a filer with no spouse) and four Part A amounts (lines 61100, 61120, 61210 and
61230). Form ON-BEN computes nothing, so the tests
check that each of its lines is carried as entered and that no return line is moved by them: the
Ontario credits stay at 0, and the income lines are the hand figures of other income alone. The
tax figures are the engine's and are checked in the YAML only.
"""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_NET_INCOME,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    APPLIES_FOR_ENERGY_AND_PROPERTY_TAX_CREDIT,
    APPLIES_FOR_NORTHERN_ENERGY_CREDIT,
    APPLIES_FOR_SENIOR_HOMEOWNERS_GRANT,
    CHOOSES_SINGLE_BENEFIT_PAYMENT,
    LIVED_IN_STUDENT_RESIDENCE,
    ONTARIO_CREDITS_SUBTOTAL,
    PROPERTY_TAX_PAID,
    PUBLIC_LONG_TERM_CARE_PAID,
    RENT_PAID,
    RESERVE_HOME_ENERGY_COSTS,
    SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_gi() -> Worksheet:
    """The worksheet of return GI, the inputs of `returns/2025_return_gi.yaml`.

    The filer has other income of 40000 and income tax deducted of 6000, with no employment income.
    Every ON-BEN tick box is 1 and the Part A amounts are 9600 (rent), 2400 (property tax), 1800
    (home energy costs on a reserve) and 4800 (public long-term care accommodation), all chosen.
    """
    return compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        resident_in_canada_throughout_2025=1,
        aged_18_or_older_at_end_of_2025=1,
        cpp_months=12,
        qpp_months=12,
        other_income="40000",
        income_tax_deducted="6000",
        applies_for_energy_and_property_tax_credit=1,
        applies_for_northern_energy_credit=1,
        chooses_single_benefit_payment=1,
        applies_for_senior_homeowners_grant=1,
        separate_residences_for_medical_reasons=0,
        lived_in_student_residence=1,
        rent_paid="9600",
        property_tax_paid="2400",
        reserve_home_energy_costs="1800",
        public_long_term_care_paid="4800",
    )


def test_total_income_is_40000_and_net_income_before_adjustments_is_40000() -> None:
    # Total income: other income of 40,000 (line 15000), since there is no employment income. There
    # are no deductions from total income (line 23300 is 0), so line 23400 is 40,000.
    worksheet = return_gi()

    assert worksheet.get(TOTAL_INCOME).value == D("40000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("0")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("40000.00")


def test_net_income_and_taxable_income_are_40000_with_no_deductions() -> None:
    # Net income (line 23600) is 40,000, with no deduction from net income, so taxable income (line
    # 26000) is 40,000 - 0 = 40,000.
    worksheet = return_gi()

    assert worksheet.get(NET_INCOME).value == D("40000.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("0")
    assert worksheet.get(TAXABLE_INCOME).value == D("40000.00")


def test_on_ben_tick_boxes_are_carried_as_entered() -> None:
    # Lines 61020, 61040, 61060, 61070 and 61140 are each ticked (a count of 1); line 61080 is not
    # (a count of 0), since the filer has no spouse. The form computes nothing
    # from them, so each is carried as entered.
    worksheet = return_gi()

    assert worksheet.get(APPLIES_FOR_ENERGY_AND_PROPERTY_TAX_CREDIT).value == 1
    assert worksheet.get(APPLIES_FOR_NORTHERN_ENERGY_CREDIT).value == 1
    assert worksheet.get(CHOOSES_SINGLE_BENEFIT_PAYMENT).value == 1
    assert worksheet.get(APPLIES_FOR_SENIOR_HOMEOWNERS_GRANT).value == 1
    assert worksheet.get(SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS).value == 0
    assert worksheet.get(LIVED_IN_STUDENT_RESIDENCE).value == 1


def test_on_ben_part_a_amounts_are_carried_as_entered() -> None:
    # Line 61100 (rent) 9,600, line 61120 (property tax) 2,400, line 61210 (home energy costs on a
    # reserve) 1,800 and line 61230 (public long-term care accommodation) 4,800: each as entered.
    worksheet = return_gi()

    assert worksheet.get(RENT_PAID).value == D("9600.00")
    assert worksheet.get(PROPERTY_TAX_PAID).value == D("2400.00")
    assert worksheet.get(RESERVE_HOME_ENERGY_COSTS).value == D("1800.00")
    assert worksheet.get(PUBLIC_LONG_TERM_CARE_PAID).value == D("4800.00")


def test_on_ben_does_not_move_the_ontario_credits() -> None:
    # The ON-BEN lines are not an Ontario credit on Schedule ON479, and no credit line is computed
    # from them: no ON479 credit is claimed, so the Ontario credits subtotal is 0.
    worksheet = return_gi()

    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("0")
