"""CA-ON 2025 end to end: return fj, the child care, infirm child, search and rescue, home
accessibility, spouse transfer and top-up lines.

Return FJ is `returns/2025_return_fj.yaml`: two children under 7 and one child with a disability
are claimed on Form T778 (the child care limits and the deduction), an infirm child is claimed
(Schedule 5, line 30500), the search and rescue volunteers' amount is claimed (line 31240), home
accessibility expenses are claimed with an amount claimed by others (Federal Worksheet D1), the
spouse's infirm children and disability amounts are transferred on Schedule 2, and the top-up tax
credit (Federal Worksheet D1, line 34990) is reached. The figures are chosen and worked out by hand
from the form text, as no CRA example exists for these lines. The tests check the hand figure of
each line; the engine-only lines (the Ontario CARE credit and the rest) are checked in the YAML
only.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMOUNTS_TRANSFERRED_FROM_SPOUSE,
    BASIC_PERSONAL_AMOUNT,
    CANADA_EMPLOYMENT_AMOUNT,
    CHILD_CARE_BASIC_LIMIT,
    CHILD_CARE_EARNED_INCOME,
    CHILD_CARE_EARNED_INCOME_LIMIT,
    CHILD_CARE_EXPENSES,
    CHILD_CARE_LIMIT_FOR_CHILDREN_UNDER_SEVEN,
    CHILD_CARE_LIMIT_FOR_CHILDREN_WITH_DISABILITY,
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CREDIT_AMOUNTS_AT_CREDIT_RATE,
    CREDIT_AMOUNTS_SUBTOTAL,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    EI_PREMIUMS,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS,
    HOME_ACCESSIBILITY_CREDIT,
    HOME_ACCESSIBILITY_EXPENSES,
    HOME_ACCESSIBILITY_LINE_2,
    INFIRM_CHILDREN_AMOUNT,
    NET_INCOME,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    SEARCH_AND_RESCUE_CONDITIONS_MET,
    SEARCH_AND_RESCUE_CREDIT,
    SPOUSE_CREDITS_USED,
    SPOUSE_INCOME_FOR_TRANSFER,
    SPOUSE_TRANSFERABLE_AMOUNTS,
    SPOUSE_UNUSED_AMOUNTS,
    TAXABLE_INCOME,
    TOP_UP_CREDITS_BASE,
    TOP_UP_EXCESS,
    TOP_UP_TAX_CREDIT,
    TOP_UP_THRESHOLD,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
    VOLUNTEER_CREDITS_CHECKED,
    VOLUNTEER_CREDITS_CLAIMED,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting


def return_fj() -> Worksheet:
    """The worksheet of return FJ: the inputs of `returns/2025_return_fj.yaml`.

    The search and rescue condition and the home accessibility amounts are not keywords of
    `starting(...)`, so they are given as artifacts that replace the zero ones `starting(...)`
    gives.
    """
    overrides: list[Artifact[Any]] = [
        Artifact(SEARCH_AND_RESCUE_CONDITIONS_MET, 1),
        Artifact(HOME_ACCESSIBILITY_EXPENSES, D("25000")),
        Artifact(HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS, D("5000")),
    ]
    base = starting(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="40000",
        income_tax_deducted="8000",
        t4_cpp_pensionable_earnings_outside_quebec="60000",
        t2204_insurable_earnings="60000",
        t2204_premiums_deducted="984.00",
        cpp_months=12,
        qpp_months=12,
        cpp_t4_base_and_first_additional_contributions="3361.75",
        cpp_t4_second_additional_contributions="0",
        resident_in_canada_throughout_2025=1,
        aged_18_or_older_at_end_of_2025=1,
        children_under_seven=2,
        children_with_disability=1,
        child_care_expenses_paid="30000",
        infirm_children=1,
        spouse_return_taxable_income="15000",
        spouse_return_basic_personal_amount="16129",
        spouse_return_infirm_children_amount="2687",
        spouse_return_disability_amount="10138",
        spouse_not_separated_90_days=1,
    )
    given = {artifact.kind for artifact in overrides}
    rest = [artifact for artifact in base if artifact.kind not in given]
    return service().compute(CA_ON, 2025, *rest, *overrides)["ca-on/return"][0]


def test_t778_limits_give_16000_11000_and_a_deduction_of_27000() -> None:
    # Part B line 1 is 2 x 8,000 = 16,000.00 (the limit for children under 7); line 2 is 1 x 11,000
    # = 11,000.00 (children with a disability); line 3 is 0 x 5,000 = 0; line 4 is 16,000 + 11,000 +
    # 0 = 27,000.00. Line 5 is the 30,000.00 paid and line 6 is the earned income of 60,000 x two-
    # thirds = 40,000.00. Line 7, the least of lines 4, 5 and 6, is 27,000.00, the allowable
    # deduction (line 21400).
    worksheet = return_fj()

    assert worksheet.get(CHILD_CARE_LIMIT_FOR_CHILDREN_UNDER_SEVEN).value == D("16000.00")
    assert worksheet.get(CHILD_CARE_LIMIT_FOR_CHILDREN_WITH_DISABILITY).value == D("11000.00")
    assert worksheet.get(CHILD_CARE_BASIC_LIMIT).value == D("27000.00")
    assert worksheet.get(CHILD_CARE_EARNED_INCOME).value == D("60000.00")
    assert worksheet.get(CHILD_CARE_EARNED_INCOME_LIMIT).value == D("40000.00")
    assert worksheet.get(CHILD_CARE_EXPENSES).value == D("27000.00")


def test_total_deductions_27565_give_net_income_and_taxable_income_of_72435() -> None:
    # Total deductions from total income are 27,000.00 (the child care deduction) + 565.00 (the
    # enhanced CPP contributions, the first additional) = 27,565.00. Total income is 60,000 + 40,000
    # = 100,000.00, so net income and taxable income are 100,000 - 27,565 = 72,435.00. The CPP base
    # contributions are 4.95% x (60,000 - 3,500) = 2,796.75 and the EI premiums 1.64% x 60,000 =
    # 984.00.
    worksheet = return_fj()

    assert worksheet.get(TOTAL_INCOME).value == D("100000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("27565.00")
    assert worksheet.get(NET_INCOME).value == D("72435.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("72435.00")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2796.75")
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("565.00")
    assert worksheet.get(EI_PREMIUMS).value == D("984.00")


def test_one_infirm_child_gives_the_caregiver_amount_of_2687() -> None:
    # Line 30500 is the number of infirm children, 1, multiplied by $2,687 = 2,687.00.
    worksheet = return_fj()

    assert worksheet.get(INFIRM_CHILDREN_AMOUNT).value == D("2687.00")


def test_search_and_rescue_volunteers_amount_is_6000_with_no_firefighters_amount() -> None:
    # Line 31240: the 200 hours condition is met, so 1 x 6,000 = 6,000.00. No volunteer
    # firefighters' amount is claimed ("but not both"), so the volunteers' total is 6,000.00.
    worksheet = return_fj()

    assert worksheet.get(SEARCH_AND_RESCUE_CREDIT).value == D("6000.00")
    assert worksheet.get(VOLUNTEER_CREDITS_CLAIMED).value == D("6000.00")
    assert worksheet.get(VOLUNTEER_CREDITS_CHECKED).value == D("6000.00")


def test_home_accessibility_line_2_is_20000_and_the_credit_is_15000() -> None:
    # Federal Worksheet D1, line 31285. Line 1, the eligible expenses, is 25,000 (chosen). Line 2
    # is the lesser of 25,000 and 20,000: 20,000.00. Line 3, the amount claimed by other qualifying
    # individuals in the same dwelling, is 5,000 (chosen), so line 4 is 20,000 - 5,000 = 15,000.00,
    # the home accessibility credit.
    worksheet = return_fj()

    assert worksheet.get(HOME_ACCESSIBILITY_LINE_2).value == D("20000.00")
    assert worksheet.get(HOME_ACCESSIBILITY_CREDIT).value == D("15000.00")


def test_schedule_2_transfers_12825_from_the_spouse_return() -> None:
    # Line 6 is the spouse's line 30500 (2,687, an infirm child) + line 31600 (10,138, the
    # disability amount) = 12,825.00 (the other lines are 0). Their taxable income of 15,000 is at
    # or below 57,375, so line 7 is 15,000.00. Line 8 is their basic personal amount, 16,129, so
    # line 11 is 16,129.00 and line 12 is 15,000 - 16,129, not below zero: 0.00. Line 13 is 12,825 -
    # 0 = 12,825.00, and as the filer was not separated for 90 days or more including December 31,
    # 2025, line 32600 is 12,825.00.
    worksheet = return_fj()

    assert worksheet.get(SPOUSE_INCOME_FOR_TRANSFER).value == D("15000.00")
    assert worksheet.get(SPOUSE_CREDITS_USED).value == D("16129")
    assert worksheet.get(SPOUSE_UNUSED_AMOUNTS).value == D("12825.00")
    assert worksheet.get(SPOUSE_TRANSFERABLE_AMOUNTS).value == D("12825.00")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("12825.00")


def test_the_federal_credit_amounts_give_45067_75_and_57892_75_with_the_transfer() -> None:
    # The credit amounts up to line 100 are 16,129.00 (basic personal amount) + 2,796.75 (CPP base)
    # + 984.00 (EI) + 1,471.00 (Canada employment amount) + 2,687.00 + 6,000.00 + 15,000.00 =
    # 45,067.75. With line 32600 (12,825.00) the total of the credit amounts (line 33500) is
    # 45,067.75 + 12,825.00 = 57,892.75, and line 33800 is 14.5% of it = 8,394.44875, rounded
    # half-up to the cent: 8,394.45.
    worksheet = return_fj()

    assert worksheet.get(BASIC_PERSONAL_AMOUNT).value == D("16129.00")
    assert worksheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D("1471.00")
    assert worksheet.get(CREDIT_AMOUNTS_SUBTOTAL).value == D("45067.75")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("57892.75")
    assert worksheet.get(CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("8394.45")


def test_top_up_tax_credit_is_259_on_an_excess_of_75_07() -> None:
    # Federal Worksheet D1, line 34990. Line 1 is 8,394.45; line 2 (Schedule 9 line 22) is 0; line 3
    # is 8,394.45; line 4 is 8,319.38; line 5 is 8,394.45 - 8,319.38 = 75.07; line 6 is 3.45% and
    # line 7 is 75.07 x 3.45% = 2.589915, rounded half-up to the cent: 2.59.
    worksheet = return_fj()

    assert worksheet.get(TOP_UP_CREDITS_BASE).value == D("8394.45")
    assert worksheet.get(TOP_UP_THRESHOLD).value == D("8319.38")
    assert worksheet.get(TOP_UP_EXCESS).value == D("75.07")
    assert worksheet.get(TOP_UP_TAX_CREDIT).value == D("2.59")


def test_federal_tax_after_credits_is_3009_64() -> None:
    # The federal non-refundable tax credits (line 35000) are 8,394.45 + 0 + 2.59 = 8,397.04. On
    # the federal tax of 11,406.68 (line 76: 3,087.30 + 8,319.38), the federal tax after credits is
    # 11,406.68 - 8,397.04 = 3,009.64.
    worksheet = return_fj()

    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("11406.68")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("8397.04")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3009.64")


def test_ontario_tax_after_credits_is_3624_82_and_ontario_tax_is_4333_57() -> None:
    # The tax on 72,435.00 is the printed 2,670.74 on the first 52,886 plus 9.15% x (72,435 -
    # 52,886) = 1,788.7335, 4,459.4735, rounded half-up to the cent: 4,459.47. The Ontario credit
    # amounts are 12,747 + 2,796.75 + 984.00 = 16,527.75, times 5.05% = 834.651375, rounded half-up
    # to the cent: 834.65, which leaves 4,459.47 - 834.65 = 3,624.82. The health premium on
    # 72,435.00 is (72,435 - 72,000) x 25% + 600 = 708.75, and the LIFT credit is 0, so the Ontario
    # tax is 3,624.82 + 708.75 = 4,333.57.
    worksheet = return_fj()

    assert worksheet.get(ontario.ONTARIO_BASIC_TAX).value == D("4459.47")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("16527.75")
    assert worksheet.get(ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("834.65")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_CREDITS).value == D("3624.82")
    assert worksheet.get(ontario.ONTARIO_HEALTH_PREMIUM).value == D("708.75")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("4333.57")


def test_total_payable_is_7343_21_and_the_refund_is_8486_79() -> None:
    # The total payable is the federal tax after credits 3,009.64 + the Ontario tax 4,333.57 =
    # 7,343.21. The total credits are the 8,000.00 of tax deducted plus the Ontario CARE credit of
    # 7,830.00 (an engine figure), 15,830.00, so the refund is 15,830.00 - 7,343.21 = 8,486.79.
    worksheet = return_fj()

    assert worksheet.get(TOTAL_PAYABLE).value == D("7343.21")
    assert worksheet.get(REFUND).value == D("8486.79")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-8486.79")
    assert worksheet.get(ontario.NET_REFUND).value == D("8486.79")
