"""CA-ON 2025 end to end: return FV, the social benefits chart where line 19 takes line 5.

Return FV is `returns/2025_return_fv.yaml`: an Ontario filer with other income of 143000 and old age
security of 7000, so the chart's line 5 (7000) is below line 18 (8498.55) and line 19 takes line 5.
The northern residents deduction runs over two zones: Zone A (183 days lived and a special work site
benefit of 4000) has line 5 floored at 0, where the unfloored figure would be -1987, and Zone B (182
days lived and 120 additional days, no work site benefit) takes lines 6 to 11 to 1661. The figures
are chosen and worked out by hand from the form text, as no CRA example exists for these charts. The
tests check the hand figure of each line; the tax figures are the engine's and are checked in the
YAML only.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_NET_INCOME,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NORTHERN_RESIDENTS_DEDUCTIONS,
    OAS_AND_FEDERAL_SUPPLEMENTS,
    OAS_BENEFITS_BASE_AMOUNT,
    RESIDENCY_AMOUNT,
    RESIDENCY_DEDUCTION,
    RESIDENCY_NET_INCOME_LIMIT,
    SOCIAL_BENEFITS_LINE_5,
    SOCIAL_BENEFITS_LINE_6,
    SOCIAL_BENEFITS_LINE_10,
    SOCIAL_BENEFITS_LINE_11,
    SOCIAL_BENEFITS_LINE_14,
    SOCIAL_BENEFITS_LINE_15,
    SOCIAL_BENEFITS_LINE_17,
    SOCIAL_BENEFITS_LINE_18,
    SOCIAL_BENEFITS_LINE_19,
    SOCIAL_BENEFITS_LINE_21,
    SOCIAL_BENEFITS_REPAYMENT,
    SOCIAL_BENEFITS_REPAYMENT_APPLIES,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT,
    ZONE_A_BASIC_RESIDENCY_AMOUNT,
    ZONE_A_RESIDENCY_AFTER_WORK_SITE,
    ZONE_A_RESIDENCY_AMOUNT,
    ZONE_A_SPECIAL_WORK_SITE_BENEFITS,
    ZONE_B_ADDITIONAL_RESIDENCY_AMOUNT,
    ZONE_B_BASIC_RESIDENCY_AMOUNT,
    ZONE_B_RESIDENCY_AFTER_WORK_SITE,
    ZONE_B_RESIDENCY_AMOUNT,
    ZONE_B_SPECIAL_WORK_SITE_BENEFITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_fv() -> Worksheet:
    """The worksheet of return FV, the inputs of `returns/2025_return_fv.yaml`.

    The filer has other income of 143000 and old age security of 7000, with no employment income and
    income tax deducted of 30000. Zone A: 183 days lived, no days for the additional residency
    amount and a special work site benefit of 4000. Zone B: 182 days lived and 120 days for the
    additional residency amount, with no special work site benefit.
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
        other_income="143000",
        old_age_security="7000",
        income_tax_deducted="30000",
        zone_a_days_lived=183,
        zone_a_special_work_site_benefits="4000",
        zone_b_days_lived=182,
        zone_b_additional_residency_days=120,
    )


def test_total_income_is_150000_and_net_income_before_adjustments_is_150000() -> None:
    # Total income: 143,000 + 7,000 = 150,000 (line 15000). There are no deductions from total
    # income (line 23300 is 0), so line 23400 is 150,000.
    worksheet = return_fv()

    assert worksheet.get(TOTAL_INCOME).value == D("150000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("0")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("150000.00")


def test_chart_line_5_is_7000_and_line_19_takes_line_5_because_it_is_the_lesser() -> None:
    # Line 3: line 1 (OAS pension, 7,000) + line 2 (net federal supplements, 0) = 7,000. Line 5:
    # 7,000 - line 4 (0) = 7,000. Line 18: line 17 (150,000 - 93,343 = 56,657) x 15% = 8,498.55.
    # Line 19 is the lesser of line 5 (7,000) and line 18 (8,498.55): 7,000, which is line 5.
    worksheet = return_fv()

    line_5 = worksheet.get(SOCIAL_BENEFITS_LINE_5).value
    line_18 = worksheet.get(SOCIAL_BENEFITS_LINE_18).value
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1
    assert worksheet.get(OAS_AND_FEDERAL_SUPPLEMENTS).value == D("7000")
    assert line_5 == D("7000")
    assert line_18 == D("8498.55")
    assert line_5 < line_18
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == min(line_5, line_18) == D("7000")


def test_chart_lines_6_10_11_and_15_are_150000_0_150000_and_150000() -> None:
    # Line 6: the net income before adjustments, 150,000. Lines 7 to 10 are 0 (no EI repayment, no
    # UCCB, no RDSP income). Line 11: 150,000 - 0 = 150,000. Line 14 is 0, so line 15, the adjusted
    # net income, is 150,000 + 0 = 150,000.
    worksheet = return_fv()

    assert worksheet.get(SOCIAL_BENEFITS_LINE_6).value == D("150000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_10).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_11).value == D("150000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_14).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_15).value == D("150000.00")


def test_chart_line_17_is_56657_and_line_21_is_the_repayment_of_7000() -> None:
    # Line 16: the OAS benefits base amount, 93,343. Line 17: 150,000 - 93,343 = 56,657 (positive,
    # so not set to 0). Line 18: 56,657 x 15% = 8,498.55. Line 21: line 19 (7,000) + line 20 (0) =
    # 7,000, the social benefits repayment on line 23500. Net income (line 23600) is 150,000 - 7,000
    # = 143,000.
    worksheet = return_fv()

    assert worksheet.get(OAS_BENEFITS_BASE_AMOUNT).value == D("93343.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("56657.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("7000")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("7000")
    assert worksheet.get(NET_INCOME).value == D("143000.00")


def test_zone_a_lines_1_to_4_are_2013_0_2013_and_4000() -> None:
    # Line 1: 183 days x $11.00 = 2,013. Line 2: no days for the additional residency amount, so 0.
    # Line 3: 2,013 + 0 = 2,013. Line 4, the special work site benefit: 4,000 (a starting amount).
    worksheet = return_fv()

    assert worksheet.get(ZONE_A_BASIC_RESIDENCY_AMOUNT).value == D("2013.00")
    assert worksheet.get(ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT).value == D("0")
    assert worksheet.get(ZONE_A_RESIDENCY_AMOUNT).value == D("2013.00")
    assert worksheet.get(ZONE_A_SPECIAL_WORK_SITE_BENEFITS).value == D("4000")


def test_zone_a_line_5_is_0_not_the_unfloored_minus_1987() -> None:
    # Line 5: line 3 (2,013) minus line 4 (4,000) = -1,987, which the form sets to "0" (if negative,
    # enter "0"). The unfloored -1,987 is what this test rules out.
    worksheet = return_fv()

    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("0")


def test_zone_b_lines_6_to_11_are_1001_660_1661_0_1661_and_1661() -> None:
    # Line 6: 182 days x $5.50 = 1,001. Line 7: 120 days x $5.50 = 660. Line 8: 1,001 + 660 = 1,661.
    # Line 9, the special work site benefit: 0. Line 10: 1,661 - 0 = 1,661. Line 11: line 5 (0) +
    # line 10 (1,661) = 1,661. With the unfloored Zone A line 5 (-1,987) line 11 would be -326.
    worksheet = return_fv()

    assert worksheet.get(ZONE_B_BASIC_RESIDENCY_AMOUNT).value == D("1001.00")
    assert worksheet.get(ZONE_B_ADDITIONAL_RESIDENCY_AMOUNT).value == D("660.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AMOUNT).value == D("1661.00")
    assert worksheet.get(ZONE_B_SPECIAL_WORK_SITE_BENEFITS).value == D("0")
    assert worksheet.get(ZONE_B_RESIDENCY_AFTER_WORK_SITE).value == D("1661.00")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("1661.00")


def test_line_13_is_1661_the_lesser_of_line_11_and_line_12() -> None:
    # Line 12: net income from line 23600 (143,000) x 20% = 28,600. Line 13 is the lesser of line 11
    # (1,661) and line 12 (28,600): 1,661, the residency deduction, which is also the northern
    # residents deductions (no travel deduction).
    worksheet = return_fv()

    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("28600.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("1661.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("1661.00")


def test_deductions_from_net_income_are_1661_and_taxable_income_is_141339() -> None:
    # Net income (line 23600) is 143,000. The northern residents deduction (1,661) is the only
    # deduction from net income, so taxable income (line 26000) is 143,000 - 1,661 = 141,339.
    worksheet = return_fv()

    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("1661.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("141339.00")
