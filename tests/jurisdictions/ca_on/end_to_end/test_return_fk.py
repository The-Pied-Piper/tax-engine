"""CA-ON 2025 end to end: return fk, the clergy residence, Schedule 13 EI, Schedule 2 spouse
transfer and foreign tax credit lines.

Return FK is `returns/2025_return_fk.yaml`: a member of the clergy with an employer-provided
residence for part of the year and other accommodation claims (Form T1223 Part C), EI premiums on
self-employment and other eligible earnings with earnings from a controlled corporation and
tax-exempt self-employment income (Schedule 13), the federal refundable First Nations abatement in
the limit of the foreign tax credit (Form T2209), and the Schedule 2 amounts transferred from a
spouse whose taxable income is above 57,375 (line 7 from their line 76). The figures are chosen and
worked out by hand from the form text, as no CRA example exists for these lines. The tests check
the hand figure of each line; the engine-only lines (the Ontario CARE rate, the Canada workers
benefit and the rest) are checked in the YAML only.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMOUNTS_TRANSFERRED_FROM_SPOUSE,
    BASIC_PERSONAL_AMOUNT,
    CANADA_EMPLOYMENT_AMOUNT,
    CLERGY_EMPLOYER_RESIDENCE_BENEFIT_CHECKED,
    CLERGY_RESIDENCE_DEDUCTION,
    CLERGY_RESIDENCE_LINE_2,
    CLERGY_RESIDENCE_LINE_4,
    CLERGY_RESIDENCE_LINE_5,
    CLERGY_RESIDENCE_LINE_8,
    CLERGY_RESIDENCE_LINE_9,
    CLERGY_RESIDENCE_LINE_10,
    CLERGY_RESIDENCE_MONTHS_AMOUNT,
    CLERGY_RESIDENCE_TOTAL,
    CLERGY_RESIDENCE_TOTAL_LIMITED,
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CREDIT_AMOUNTS_AT_CREDIT_RATE,
    CREDIT_AMOUNTS_SUBTOTAL,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    EI_EARNINGS_SUBJECT_TO_PREMIUM,
    EI_INSURABLE_EARNINGS_REMAINING,
    EI_MAXIMUM_INSURABLE_EARNINGS,
    EI_NET_SELF_EMPLOYMENT_INCOME,
    EI_PAYABLE_ON_SELF_EMPLOYMENT,
    EI_PREMIUMS,
    EI_PREMIUMS_ON_SELF_EMPLOYMENT,
    EI_SELF_EMPLOYMENT_BEFORE_SLIPS,
    EI_SELF_EMPLOYMENT_EARNINGS,
    FEDERAL_BASIC_TAX,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
    FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT,
    FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX,
    NET_INCOME,
    NON_REFUNDABLE_TAX_CREDITS,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    SELF_EMPLOYED_EI_PREMIUMS,
    SPOUSE_ADJUSTED_TAXABLE_INCOME,
    SPOUSE_CREDITS_USED,
    SPOUSE_INCOME_FOR_TRANSFER,
    SPOUSE_TRANSFERABLE_AMOUNTS,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_fk() -> Worksheet:
    """The worksheet of return FK: the inputs of `returns/2025_return_fk.yaml`."""
    return compute(
        "49000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_employment_income="6000",
        net_partnership_income="10000",
        income_tax_deducted="6000",
        t4_cpp_pensionable_earnings_outside_quebec="49000",
        t2204_insurable_earnings="45000",
        t2204_premiums_deducted="738.00",
        cpp_months=12,
        qpp_months=12,
        cpp_t4_base_and_first_additional_contributions="2707.25",
        cpp_t4_second_additional_contributions="0",
        resident_in_canada_throughout_2025=1,
        aged_18_or_older_at_end_of_2025=1,
        clergy_qualifying_employment_income="51000",
        clergy_months_in_qualifying_employment=8,
        clergy_accommodation_cost="14000",
        clergy_other_accommodation_claims="2000",
        clergy_employer_residence_benefit="6000",
        ei_special_benefits_agreement=1,
        ei_insurable_earnings="45000",
        ei_controlled_corporation_earnings="4000",
        ei_exempt_self_employment_income="2000",
        first_nations_abatement="500",
        foreign_tax_countries_rows=(("600", "3000"),),
        spouse_return_taxable_income="90000",
        spouse_return_federal_basic_tax="12300",
        spouse_return_basic_personal_amount="16129",
        spouse_return_age_amount="2356.30",
        spouse_return_pension_income_amount="2000",
        spouse_not_separated_90_days=1,
    )


def test_clergy_residence_line_2_is_17000_and_the_benefit_is_checked_at_6000() -> None:
    # Form T1223 Part C, line 1 is the church earnings and benefit, 45,000 + 6,000 = 51,000
    # (chosen). Line 2 is 51,000 x 1/3 = 17,000.00. The benefit checked is the employer's 6,000.
    worksheet = return_fk()

    assert worksheet.get(CLERGY_RESIDENCE_LINE_2).value == D("17000.00")
    assert worksheet.get(CLERGY_EMPLOYER_RESIDENCE_BENEFIT_CHECKED).value == D("6000")


def test_clergy_lines_4_to_10_limit_the_rent_claim_to_12000() -> None:
    # Line 3 is 8 months and line 4 is 8 x 1,000 = 8,000.00 (at most 10,000). Line 5 is the more of
    # line 2 and line 4: 17,000.00. Line 6, the rent and utilities, is 14,000 and line 7, the
    # amounts claimed by any person, is 2,000 (chosen), so line 8 is 14,000 - 2,000 = 12,000.00.
    # Line 9 is the lesser of line 5 and line 8: 12,000.00, and line 10 the lesser of line 1
    # (51,000) and line 9: 12,000.00.
    worksheet = return_fk()

    assert worksheet.get(CLERGY_RESIDENCE_MONTHS_AMOUNT).value == D("8000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_4).value == D("8000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_5).value == D("17000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_8).value == D("12000")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_9).value == D("12000")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_10).value == D("12000")


def test_the_clergy_deduction_of_18000_gives_net_income_of_46545() -> None:
    # Part C: (C), (A) and (B) added: 6,000 + 12,000 = 18,000.00, which is not more than line 1, so
    # line 23100 is 18,000.00. Total deductions from total income are 18,000.00 + 455.00 (the
    # enhanced CPP contributions) = 18,455.00. Total income is 49,000 + 6,000 + 10,000 = 65,000.00,
    # so net income and taxable income are 65,000 - 18,455 = 46,545.00. The CPP base contributions
    # are 4.95% x (49,000 - 3,500) = 2,252.25.
    worksheet = return_fk()

    assert worksheet.get(CLERGY_RESIDENCE_TOTAL).value == D("18000")
    assert worksheet.get(CLERGY_RESIDENCE_TOTAL_LIMITED).value == D("18000")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("18000")
    assert worksheet.get(TOTAL_INCOME).value == D("65000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("18455.00")
    assert worksheet.get(NET_INCOME).value == D("46545.00")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2252.25")
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("455.00")


def test_schedule_13_gives_self_employed_ei_premiums_of_262_40() -> None:
    # Schedule 13 line 1 is the net income from partnership and self-employment, 10,000.00. Line 2
    # is the box 14 earnings from the corporation the filer controls, 4,000, and line 3 is the
    # tax-exempt self-employment income, 2,000 (both chosen), so line 4 is 10,000 + 4,000 + 2,000 =
    # 16,000.00. Line 5 is the maximum insurable earnings, 65,700.00, and line 6 the box 24 EI
    # insurable earnings, 45,000, so line 7 is 65,700 - 45,000 = 20,700.00 and line 8 is the lesser
    # of line 4 and line 7: 16,000.00. Line 9 is 16,000 x 1.64% = 262.40 (at most 1,077.48), the EI
    # premiums on self-employment. The EI premiums on the church earnings are 1.64% x 45,000 =
    # 738.00.
    worksheet = return_fk()

    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("10000.00")
    assert worksheet.get(EI_SELF_EMPLOYMENT_BEFORE_SLIPS).value == D("10000")
    assert worksheet.get(EI_NET_SELF_EMPLOYMENT_INCOME).value == D("16000")
    assert worksheet.get(EI_EARNINGS_SUBJECT_TO_PREMIUM).value == D("16000")
    assert worksheet.get(EI_MAXIMUM_INSURABLE_EARNINGS).value == D("65700.00")
    assert worksheet.get(EI_INSURABLE_EARNINGS_REMAINING).value == D("20700.00")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("262.40")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("262.40")
    assert worksheet.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value == D("262.40")
    assert worksheet.get(EI_PREMIUMS).value == D("738.00")


def test_schedule_2_transfers_4356_30_from_a_spouse_above_57375() -> None:
    # Line 6 is the spouse's line 30100 (the age amount, 2,356.30) + line 31400 (2,000), so
    # 4,356.30. Their taxable income of 90,000 is above 57,375, so line 7 is their line 76, 12,300,
    # divided by 14.5% = 84,827.586..., rounded half-up to the cent: 84,827.59. Line 8 is their line
    # 30000, 16,129, and lines 9 and 10 are 0, so line 11 is 16,129.00 and line 12 is 84,827.59 -
    # 16,129.00 = 68,698.59. Line 13 is 4,356.30 - 68,698.59, not below zero: 0.00, so line 32600 is
    # 0.
    worksheet = return_fk()

    assert worksheet.get(SPOUSE_TRANSFERABLE_AMOUNTS).value == D("4356.30")
    assert worksheet.get(SPOUSE_INCOME_FOR_TRANSFER).value == D("84827.59")
    assert worksheet.get(SPOUSE_CREDITS_USED).value == D("16129")
    assert worksheet.get(SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("68698.59")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("0")


def test_the_federal_credit_amounts_give_20852_65_and_federal_tax_after_credits_of_3725_40() -> (
    None
):
    # The federal credit amounts are 16,129.00 (basic personal amount) + 2,252.25 (CPP base) +
    # 738.00 (EI) + 262.40 (EI on self-employment, line 31217) + 1,471.00 (Canada employment amount)
    # = 20,852.65. Line 33800 is 14.5% of it = 3,023.63425, rounded half-up to the cent: 3,023.63.
    # The federal basic tax on 46,545.00 is 46,545 x 14.5% = 6,749.025, rounded half-up to the cent:
    # 6,749.03, and the federal tax after credits is 6,749.03 - 3,023.63 = 3,725.40.
    worksheet = return_fk()

    assert worksheet.get(BASIC_PERSONAL_AMOUNT).value == D("16129.00")
    assert worksheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D("1471.00")
    assert worksheet.get(CREDIT_AMOUNTS_SUBTOTAL).value == D("20852.65")
    assert worksheet.get(CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("3023.63")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("3023.63")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("6749.03")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3725.40")


def test_the_foreign_tax_credit_is_207_89_on_the_tax_after_the_abatement() -> None:
    # Form T2209: the basic federal tax (note 4) is line 42900, 3,725.40, less the First Nations
    # abatement of 500.00: 3,225.40. Line 2 is 3,000 x 3,225.40 / 46,545.00 = 207.8890..., rounded
    # half-up to the cent: 207.89, and line 3 is the lesser of the 600 of foreign tax paid and line
    # 2: 207.89. The federal tax less the foreign tax credit is 3,725.40 - 207.89 = 3,517.51.
    worksheet = return_fk()

    assert worksheet.get(FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX).value == D("3225.40")
    assert worksheet.get(FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT).value == D("207.89")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT).value == D("207.89")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("207.89")
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("3517.51")


def test_ontario_tax_after_the_foreign_tax_credit_and_lift_is_1720_37() -> None:
    # Ontario: 46,545 x 5.05% = 2,350.5225, rounded half-up to the cent: 2,350.52. The Ontario
    # credit amounts are 12,747 + 2,252.25 + 738.00 + 262.40 = 15,999.65, times 5.05% = 807.982325,
    # rounded to 807.98, leaving 1,542.54. The Ontario foreign tax credit is 1,542.54 x 3,000 /
    # 46,545.00 = 99.4233..., rounded to 99.42, which leaves 1,443.12. The LIFT credit is 875 less
    # 5% x (46,545 - 32,500) = 702.25, that is 172.75, which leaves 1,270.37; the health premium on
    # 46,545.00 is 450, so the Ontario tax is 1,270.37 + 450 = 1,720.37.
    worksheet = return_fk()

    assert worksheet.get(ontario.ONTARIO_BASIC_TAX).value == D("2350.52")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15999.65")
    assert worksheet.get(ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("807.98")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("807.98")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_CREDITS).value == D("1542.54")
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT).value == D("99.42")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_FOREIGN_TAX_CREDIT).value == D("1443.12")
    assert worksheet.get(ontario.LIFT_CREDIT).value == D("172.75")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("1270.37")
    assert worksheet.get(ontario.ONTARIO_HEALTH_PREMIUM).value == D("450.00")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("1720.37")


def test_total_payable_is_5500_28_and_the_refund_is_499_72() -> None:
    # The total payable is the federal tax less the foreign tax credit 3,517.51 + the Ontario tax
    # 1,720.37 + the EI premiums payable on self-employment 262.40 = 5,500.28. The total credits are
    # the 6,000.00 of tax deducted, so the refund is 6,000.00 - 5,500.28 = 499.72.
    worksheet = return_fk()

    assert worksheet.get(TOTAL_CREDITS).value == D("6000.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("5500.28")
    assert worksheet.get(REFUND).value == D("499.72")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-499.72")
    assert worksheet.get(ontario.NET_REFUND).value == D("499.72")
