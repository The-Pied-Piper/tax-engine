"""CA-ON 2025 end to end: return fc, the T1 benefit and income-support lines with a spouse.

Return FC is `returns/2025_return_fc.yaml`: the elected split-pension amount, UCCB, EI and other
benefits, RDSP income, support payments, scholarships, social assistance and net federal supplements
are all entered, so line 14700 and the Federal Worksheet's line 25000, social benefits and medical
expense supplement charts are reached, and Schedule ON428-A Part B is used for the spouse. The
figures are chosen and worked out by hand from the form text, as no CRA example exists for these
lines. The tests check the hand figure of each line; the tax figures are the engine's and are
checked in the YAML only.
"""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    INCOME_SUPPORT_BENEFITS,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS,
    MEDICAL_SUPPLEMENT_LINE_6,
    MEDICAL_SUPPLEMENT_LINE_8,
    MEDICAL_SUPPLEMENT_LINE_15,
    MEDICAL_SUPPLEMENT_LINE_16,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_INCOME_LESS_UCCB_AND_RDSP_INCOME,
    OTHER_PAYMENTS_DEDUCTION,
    OTHER_PAYMENTS_LIMIT_INCOME,
    SOCIAL_BENEFITS_LINE_10,
    SOCIAL_BENEFITS_REPAYMENT,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    UCCB_AND_RDSP_INCOME,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    LIFT_ADJUSTED_NET_INCOME,
    LIFT_CREDIT,
    LIFT_CREDIT_BEFORE_MAXIMUM,
    LIFT_CREDIT_SINGLE,
    LIFT_CREDIT_WITH_SPOUSE,
    LIFT_EMPLOYMENT_INCOME,
    LIFT_MAXIMUM_CREDIT,
    LIFT_NET_INCOME_AND_REPAYMENTS,
    LIFT_REDUCTION,
    LIFT_SPOUSE_ADJUSTED_NET_INCOME,
    LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS,
    LIFT_SPOUSE_UCCB_AND_RDSP_INCOME,
    LIFT_UCCB_AND_RDSP_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute_with_spouse


def return_fc() -> Worksheet:
    """The worksheet of return FC: the inputs of `returns/2025_return_fc.yaml`."""
    return compute_with_spouse(
        "15000",
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        aged_19_or_older_at_end_of_2025=0,
        resided_with_spouse_or_child_at_end_of_2025=1,
        other_employment_income="14000",
        wage_loss_replacement_plan_income="12000",
        t1032_line_22="6000",
        t1032_eligible_pension_income="20000",
        t1032_filer_is_transferring_spouse=0,
        universal_child_care_benefit="2400",
        ei_and_other_benefits="3000",
        rdsp_income="1500",
        taxable_support_payments="4800",
        taxable_scholarships="2000",
        social_assistance_payments="3000",
        net_federal_supplements="5000",
        other_payments_deduction_above_limit="0",
        resident_in_canada_throughout_2025=1,
        aged_18_or_older_at_end_of_2025=1,
        cpp_months=12,
        qpp_months=12,
        spouse_or_common_law_partner_on_december_31=1,
        spouse_net_income="15000",
        spouse_net_income_before_adjustments="15000",
        spouse_universal_child_care_benefit="1800",
        spouse_rdsp_income="1200",
        spouse_uccb_repayment="200",
        spouse_rdsp_income_repayment="100",
    )


def test_total_income_is_41700_and_line_14700_is_8000() -> None:
    # Line 14700 is line 14400 (0) + social assistance 3,000 + net federal supplements 5,000 =
    # 8,000. Total income (line 15000) is 14,000 + 6,000 + 2,400 + 3,000 + 1,500 + 4,800 + 2,000 +
    # 8,000 = 41,700. No deduction applies, so net income before adjustments (line 23400) and net
    # income (line 23600) are 41,700. The social benefits repayment (line 23500) is 0: the EI amount
    # is entered but 41,700 is not more than $82,125, and the supplements are entered but 41,700 is
    # not more than $93,454, so the chart is not completed and line 23500 is "0".
    worksheet = return_fc()

    assert worksheet.get(INCOME_SUPPORT_BENEFITS).value == D("8000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("41700.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("41700.00")
    assert worksheet.get(NET_INCOME).value == D("41700.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("0.00")


def test_line_25000_deducts_all_of_line_14700_as_the_limit_income_is_37800() -> None:
    # UCCB and RDSP income is 2,400 + 1,500 = 3,900. The Federal Worksheet's line 25000 chart:
    # line 1 is line 23400, 41,700; line 5 is 41,700 - 3,900 = 37,800; line 9 is 37,800 + 0 =
    # 37,800, not more than $93,454, so line 25000 is the amount of line 14700, 8,000. Taxable
    # income (line 26000) is 41,700 - 8,000 = 33,700. The social benefits chart's line 10 is
    # 0 + 2,400 + 1,500 = 3,900, and its line 11 is 41,700 - 3,900 = 37,800.
    worksheet = return_fc()

    assert worksheet.get(UCCB_AND_RDSP_INCOME).value == D("3900.00")
    assert worksheet.get(NET_INCOME_LESS_UCCB_AND_RDSP_INCOME).value == D("37800.00")
    assert worksheet.get(OTHER_PAYMENTS_LIMIT_INCOME).value == D("37800.00")
    assert worksheet.get(OTHER_PAYMENTS_DEDUCTION).value == D("8000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("33700.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_10).value == D("3900.00")


def test_the_medical_supplement_chart_takes_the_spouse_into_column_2_and_line_16_is_0() -> None:
    # Column 1 (the filer): line 1 is 41,700; line 2 is 0; line 3 is 41,700; line 4 is 2,400 + 1,500
    # = 3,900; line 5 is 37,800. Column 2 (the spouse): line 2 is 200 + 100 = 300; line 3 is
    # 15,000 + 300 = 15,300; line 4 is 1,800 + 1,200 = 3,000; line 5 is 15,300 - 3,000 = 12,300.
    # Line 6 is 37,800 + 12,300 = 50,100; line 8 is 50,100 - 33,294 = 16,806; line 15 is 16,806 x 5%
    # = 840.30. Line 14 is 0 (no medical expense on line 21500 or line 33200, so line 13 is 0), and
    # line 16 is 0 - 840.30, negative, so 0. The employment income test of $4,390 is also not met:
    # 14,000 - 12,000 = 2,000 from the amounts other than the wage-loss replacement plan.
    worksheet = return_fc()

    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME).value == D("14000.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS).value == D("2000.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3).value == D("41700.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5).value == D("37800.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2).value == D("300.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3).value == D("15300.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4).value == D("3000.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5).value == D("12300.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_6).value == D("50100.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_8).value == D("16806.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_15).value == D("840.30")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_16).value == D("0.00")


def test_lift_part_b_takes_the_filer_and_the_spouse_to_a_credit_of_442() -> None:
    # Filer (Schedule ON428-A lines 1 to 13): line 2 is line 10400, 14,000; line 3 is 14,000; line 5
    # is 14,000 x 5.05% = 707.00 (under $875). Line 9 is 41,700 + 0 + 0; line 12 is 2,400 + 1,500
    # = 3,900; line 13 is 41,700 - 3,900 = 37,800. Spouse (lines 21 to 28): line 24 is
    # 15,000 + 200 + 100 = 15,300; line 27 is 1,800 + 1,200 = 3,000; line 28 is 15,300 - 3,000 =
    # 12,300. Part B: line 32 is 37,800 - 32,500 = 5,300; line 35 is 37,800 + 12,300 = 50,100, so
    # line 37 is 0 below the family threshold; line 38 is 5,300; line 40 is 5,300 x 5% = 265.00;
    # line 41 is 707 - 265 = 442.00 (Form ON428 line 62140).
    worksheet = return_fc()

    assert worksheet.get(LIFT_EMPLOYMENT_INCOME).value == D("14000.00")
    assert worksheet.get(LIFT_CREDIT_BEFORE_MAXIMUM).value == D("707.00")
    assert worksheet.get(LIFT_MAXIMUM_CREDIT).value == D("707.00")
    assert worksheet.get(LIFT_NET_INCOME_AND_REPAYMENTS).value == D("41700.00")
    assert worksheet.get(LIFT_UCCB_AND_RDSP_INCOME).value == D("3900.00")
    assert worksheet.get(LIFT_ADJUSTED_NET_INCOME).value == D("37800.00")
    assert worksheet.get(LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS).value == D("15300.00")
    assert worksheet.get(LIFT_SPOUSE_UCCB_AND_RDSP_INCOME).value == D("3000.00")
    assert worksheet.get(LIFT_SPOUSE_ADJUSTED_NET_INCOME).value == D("12300.00")
    assert worksheet.get(LIFT_REDUCTION).value == D("265.00")
    assert worksheet.get(LIFT_CREDIT_WITH_SPOUSE).value == D("442.00")
    assert worksheet.get(LIFT_CREDIT).value == D("442.00")
    # Part A would give the same figure; the filer completes Part B.
    assert worksheet.get(LIFT_CREDIT_SINGLE).value == D("442.00")
