"""CA-ON 2025 end to end: return FD, the social benefits repayment chart (line 23500) with every
line non-zero, the line 25000 worksheet on its branch above $93,454, and the UCCB, RDSP income and
EI repayments.

Return FD is `returns/2025_return_fd.yaml`: the chart is completed, every line of it is non-zero,
and the other payments worksheet (line 25000) takes its "above $93,454" branch, so the deduction
is the chosen $1,200.00 and not the line 14700 amount. The spouse's figures feed the Schedule
ON428-A (LIFT) and column 2 of the Federal Worksheet for line 45200. The figures are chosen and
worked out by hand from the form text, as no CRA example exists for these charts. The tests check
the hand figure of each line; the tax figures are the engine's and are checked in the YAML only.
"""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_NET_INCOME,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    INCOME_SUPPORT_BENEFITS,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_INCOME_LESS_UCCB_AND_RDSP_INCOME,
    OAS_AND_FEDERAL_SUPPLEMENTS,
    OAS_BENEFITS_BASE_AMOUNT,
    OTHER_PAYMENTS_DEDUCTION,
    OTHER_PAYMENTS_DEDUCTION_AFTER_LIMIT,
    OTHER_PAYMENTS_LIMIT_INCOME,
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
    UCCB_AND_RDSP_INCOME_REPAYMENTS,
)
from tax_engine.jurisdictions.ca_on.catalog import LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_fd() -> Worksheet:
    """The worksheet of return FD: the inputs of `returns/2025_return_fd.yaml`."""
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
        other_income="100000",
        old_age_security="8000",
        ei_and_other_benefits="12000",
        universal_child_care_benefit="1500",
        rdsp_income="3000",
        net_federal_supplements="2000",
        uccb_repayment="500",
        rdsp_income_repayment="1000",
        other_deductions="4000",
        oas_overpayment_recovered="400",
        ei_benefits_repayment="600",
        other_payments_deduction_above_limit="1200",
        spouse_net_income_before_adjustments="40000",
        spouse_uccb_repayment="300",
        spouse_rdsp_income_repayment="200",
        income_tax_deducted="20000",
    )


def test_total_income_is_126500_and_net_income_before_adjustments_is_122000() -> None:
    # Total income: 100,000 + 8,000 + 12,000 + 1,500 + 3,000 + 2,000 = 126,500 (line 15000);
    # line 14700 is 2,000 because lines 14400 and 14500 are 0. Deductions: 500 (UCCB repayment,
    # line 21300) + 4,000 (other deductions, line 23200) = 4,500 (line 23300). Line 23400:
    # 126,500 - 4,500 = 122,000.
    worksheet = return_fd()

    assert worksheet.get(TOTAL_INCOME).value == D("126500.00")
    assert worksheet.get(INCOME_SUPPORT_BENEFITS).value == D("2000")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("4500.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("122000.00")


def test_chart_lines_3_5_and_6_are_10000_9600_and_122000() -> None:
    # Line 3: line 1 (OAS pension, 8,000) + line 2 (net federal supplements, 2,000) = 10,000.
    # Line 5: 10,000 - line 4 (OAS overpayment recovered, 400) = 9,600. Line 6: the net income
    # before adjustments, 122,000 (plus total split income, 0).
    worksheet = return_fd()

    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1
    assert worksheet.get(OAS_AND_FEDERAL_SUPPLEMENTS).value == D("10000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_5).value == D("9600")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_6).value == D("122000.00")


def test_chart_lines_10_11_14_and_15_are_5100_116900_1500_and_118400() -> None:
    # Line 10: line 7 (EI repayment, 600) + line 8 (UCCB, 1,500) + line 9 (RDSP income, 3,000)
    # = 5,100. Line 11: 122,000 - 5,100 = 116,900. Line 14: line 12 (UCCB repayment, 500) + line 13
    # (RDSP income repayment, 1,000) = 1,500. Line 15, the adjusted net income: 116,900 + 1,500 =
    # 118,400.
    worksheet = return_fd()

    assert worksheet.get(SOCIAL_BENEFITS_LINE_10).value == D("5100")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_11).value == D("116900.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_14).value == D("1500")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_15).value == D("118400.00")


def test_chart_lines_17_18_19_and_21_and_the_repayment_are_25057_3758_55_and_4358_55() -> None:
    # Line 17: 118,400 - the OAS benefits base amount 93,343 = 25,057 (positive, so not 0). Line
    # 18: 25,057 x 15% = 3,758.55. Line 19: the lesser of line 5 (9,600) and line 18 (3,758.55) is
    # 3,758.55. Line 21: 3,758.55 + line 20 (EI repayment, 600) = 4,358.55, the social benefits
    # repayment on line 23500. Net income (line 23600): 122,000 - 4,358.55 = 117,641.45.
    worksheet = return_fd()

    assert worksheet.get(OAS_BENEFITS_BASE_AMOUNT).value == D("93343.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("25057.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_18).value == D("3758.55")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == D("3758.55")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("4358.55")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("4358.55")
    assert worksheet.get(NET_INCOME).value == D("117641.45")


def test_line_19_takes_line_18_because_it_is_the_lesser_of_line_5_and_line_18() -> None:
    # Line 5 is 9,600 and line 18 is 3,758.55: line 19 ("Enter whichever is less: amount from
    # line 5 or line 18") is the lesser, 3,758.55.
    worksheet = return_fd()

    line_5 = worksheet.get(SOCIAL_BENEFITS_LINE_5).value
    line_18 = worksheet.get(SOCIAL_BENEFITS_LINE_18).value
    assert line_18 < line_5
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == min(line_5, line_18) == D("3758.55")


def test_line_25000_chart_lines_5_8_and_9_are_117500_1500_and_119000() -> None:
    # Line 2: the UCCB (1,500); line 3: the RDSP income (3,000); line 4: 1,500 + 3,000 = 4,500.
    # Line 5: line 1 (net income before adjustments, 122,000) - 4,500 = 117,500. Line 8: line 6
    # (UCCB repayment, 500) + line 7 (RDSP income repayment, 1,000) = 1,500. Line 9: 117,500 +
    # 1,500 = 119,000, which is more than $93,454, so the deduction is not the line 14700 amount
    # and comes from canada.ca/line-25000 (the chosen figure of the next test).
    worksheet = return_fd()

    assert worksheet.get(NET_INCOME_LESS_UCCB_AND_RDSP_INCOME).value == D("117500.00")
    assert worksheet.get(UCCB_AND_RDSP_INCOME_REPAYMENTS).value == D("1500")
    assert worksheet.get(OTHER_PAYMENTS_LIMIT_INCOME).value == D("119000.00")


def test_line_25000_deduction_is_the_chosen_1200_and_taxable_income_is_116441_45() -> None:
    # Above $93,454 the deduction is the chosen 1,200 (at most line 14700's 2,000), so it is the
    # only deduction from net income: taxable income = 117,641.45 - 1,200 = 116,441.45.
    worksheet = return_fd()

    assert worksheet.get(OTHER_PAYMENTS_DEDUCTION_AFTER_LIMIT).value == D("1200")
    assert worksheet.get(OTHER_PAYMENTS_DEDUCTION).value == D("1200")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("1200.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("116441.45")


def test_spouse_federal_worksheet_column_2_is_500_40500_and_40500() -> None:
    # Line 45200, column 2, line 2: the spouse's UCCB repayment (300) + RDSP income repayment (200)
    # = 500. Line 3: the spouse's net income (40,000) + 500 = 40,500. Line 4 is 0, so line 5 is
    # 40,500.
    worksheet = return_fd()

    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2).value == D("500")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3).value == D("40500")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5).value == D("40500")


def test_spouse_lift_net_income_and_repayments_is_40500() -> None:
    # Schedule ON428-A (LIFT) Part B, line 24: the spouse's net income (40,000) + UCCB repayment
    # (300) + RDSP income repayment (200) = 40,500.
    worksheet = return_fd()

    assert worksheet.get(LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS).value == D("40500")
