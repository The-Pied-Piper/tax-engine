"""CA-ON 2025 end to end: return FM, the split income dividends and the minimum tax carryover.

Return FM is `returns/2025_return_fm.yaml`: a filer who was not resident in Canada at the start of
2025, bankrupt in 2025 and not claiming the Ontario tax reduction, with a spouse, dividends without
a slip that are all split income (Form T1206), a minimum tax carryover applied on ON428 line 59 and
the Ontario amounts transferred from the spouse (Schedule ON(S2)), so that the lines no other
worked return sets are non-zero: T1206 lines 18, 19, 20 and 21, ON428 lines 42, 45 and 46, line 59,
and the four conditions that make ON428 line 80 zero. The figures are chosen (no CRA example
exists) and worked out by hand from the form text, as the description of the return shows. The
tests check the hand figure of each line; the engine-only lines are checked in the YAML only.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMOUNTS_TRANSFERRED_FROM_SPOUSE,
    AMT_CARRYOVER_AVAILABLE_FOR_2026,
    AMT_CARRYOVER_BALANCE,
    AMT_MAXIMUM_CARRYOVER_APPLIED,
    AMT_MAXIMUM_CARRYOVER_CLAIM,
    AMT_MINIMUM_AMOUNT,
    AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM,
    AMT_SPLIT_INCOME_AND_CREDITS_TOTAL,
    AMT_TAX_PAYABLE_AFTER_CREDITS,
    AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_ON_SPLIT_INCOME,
    NET_INCOME,
    SPLIT_INCOME_LINE_18,
    SPLIT_INCOME_LINE_19,
    SPLIT_INCOME_LINE_20,
    SPLIT_INCOME_LINE_21,
    TAXABLE_DIVIDENDS,
    TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    TAXABLE_INCOME,
    TOSI_ADJUSTED_NET_INCOME,
    TOTAL_INCOME,
    TOTAL_SPLIT_INCOME,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, spouse_inputs, starting


def return_fm(carryover_claim: str = "800") -> Worksheet:
    """The worksheet of return FM: the inputs of `returns/2025_return_fm.yaml`, with the claim.

    Every input of the YAML is a keyword of `starting(...)`. The claim on the minimum tax carryover
    (Part 8 line 12) is the filer's election, 800.00 unless a test sets another claim.
    """
    base = starting(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t4_cpp_pensionable_earnings_outside_quebec="60000",
        t2204_insurable_earnings="60000",
        t2204_premiums_deducted="984.00",
        cpp_months=12,
        qpp_months=12,
        cpp_t4_base_and_first_additional_contributions="3361.75",
        cpp_t4_second_additional_contributions="0",
        income_tax_deducted="8000",
        resident_in_canada_throughout_2025=0,
        aged_18_or_older_at_end_of_2025=1,
        eligible_dividends_received_without_a_slip="5000",
        other_dividends_received_without_a_slip="4000",
        split_income_dividends="11500",
        split_income_dividends_other_than_eligible="4600",
        amt_minimum_tax_carryover_from_previous_years="1000",
        amt_minimum_tax_carryover_applied=carryover_claim,
        spouse_or_common_law_partner_on_december_31=1,
        spouse_not_separated_90_days=1,
        spouse_net_income="20000",
        spouse_net_income_before_adjustments="20000",
        spouse_return_taxable_income="20000",
        spouse_return_disability_amount="10138",
        spouse_return_line_96="1500",
        spouse_return_federal_tuition_amount="1000",
        spouse_return_basic_personal_amount="16129",
        spouse_return_ontario_disability_amount="10298",
        spouse_return_ontario_basic_personal_amount="12747",
        spouse_return_ontario_line_24="1500",
        spouse_return_ontario_unused_tuition_amount="1000",
        not_resident_of_canada_at_start_of_year=1,
        bankrupt_in_year=1,
        return_filed_by_trustee_in_bankruptcy=1,
        not_claiming_ontario_tax_reduction=1,
        unapplied_net_capital_losses_2000="0",
        schedule_8_copies=1,
        **spouse_inputs("20000"),
    )
    return service().compute(CA_ON, 2025, *base)["ca-on/return"][0]


def test_dividends_without_a_slip_are_11500_on_line_12000_and_4600_on_line_12010() -> None:
    # Eligible dividends of 5,000 x 138% = 6,900; other dividends of 4,000 x 115% = 4,600. Line
    # 12000 is 6,900 + 4,600 = 11,500 and line 12010 is the part other than eligible: 4,600.
    worksheet = return_fm()

    assert worksheet.get(TAXABLE_DIVIDENDS).value == D("11500.00")
    assert worksheet.get(TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE).value == D("4600.00")


def test_total_income_of_71500_less_the_split_income_gives_net_income_of_59435() -> None:
    # Total income: 60,000 (employment) + 11,500 (dividends, line 12000) = 71,500. Deductions: the
    # enhanced CPP of 565.00 and the split income of 11,500 (T1206 Part 1 line 4, line 23200):
    # 565 + 11,500 = 12,065. Net income and taxable income: 71,500 - 12,065 = 59,435. The TOSI
    # adjusted net income adds the split income back: 59,435 + 11,500 = 70,935.
    worksheet = return_fm()

    assert worksheet.get(TOTAL_INCOME).value == D("71500.00")
    assert worksheet.get(TOTAL_SPLIT_INCOME).value == D("11500.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("12065.00")
    assert worksheet.get(NET_INCOME).value == D("59435.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("59435.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME).value == D("70935.00")


def test_t1206_split_income_lines_18_to_21_give_a_dividend_credit_of_1451_75() -> None:
    # Line 18 (the eligible part): 11,500 - 4,600 = 6,900. Line 19: 4,600 x 9.0301% = 415.38
    # (415.3846). Line 20: 6,900 x 15.0198% = 1,036.37 (1,036.3662). Line 21: 415.38 + 1,036.37 =
    # 1,451.75. The federal tax on split income (T1206 line 8) is 11,500 x 33% = 3,795.00.
    worksheet = return_fm()

    assert worksheet.get(SPLIT_INCOME_LINE_18).value == D("6900.00")
    assert worksheet.get(SPLIT_INCOME_LINE_19).value == D("415.38")
    assert worksheet.get(SPLIT_INCOME_LINE_20).value == D("1036.37")
    assert worksheet.get(SPLIT_INCOME_LINE_21).value == D("1451.75")
    assert worksheet.get(FEDERAL_TAX_ON_SPLIT_INCOME).value == D("3795.00")


def test_ontario_split_income_lines_42_45_and_46_give_the_dividend_credit_of_827_37() -> None:
    # Ontario (Chart C columns 5 and 6): line 42 = 6,900 x 10% = 690.00; line 45 = 4,600 x 2.9863%
    # = 137.37 (137.3698); line 46 = 690.00 + 137.37 = 827.37, which is the Ontario dividend tax
    # credit of ON428 line 57 (the dividends are the same as on Worksheet ON428).
    worksheet = return_fm()

    assert worksheet.get(ontario.SPLIT_INCOME_LINE_42).value == D("690.00")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_45).value == D("137.37")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_46).value == D("827.37")
    assert worksheet.get(ontario.DIVIDEND_TAX_CREDIT).value == D("827.37")


def test_the_ontario_tax_on_split_income_is_2360_95() -> None:
    # The Ontario tax on split income is 11,500 x 20.53% = 2,360.95.
    worksheet = return_fm()

    assert worksheet.get(ontario.ONTARIO_TAX_ON_SPLIT_INCOME).value == D("2360.95")


def test_t691_part_8_claims_800_of_the_carryover_and_leaves_200_for_2026() -> None:
    # Part 2: the federal tax with the tax on split income, 8,741.68 + 3,795.00 = 12,536.68, less
    # the credits 4,371.42 and the dividend tax credit 1,451.75 (5,823.17) is 6,713.51. Part 8
    # line 9: 6,713.51 - 3,795.00 = 2,918.51, the maximum that may be applied (line 11). The
    # minimum amount of Part 1 (line 10) is 0. The carryover of 1,000.00 is line 1; the claim of
    # 800.00 (line 12) is at most line 1 and line 11, so it is within the maximum, and the balance
    # for later years (line 13) is 1,000.00 - 800.00 = 200.00, which is the amount for 2026.
    worksheet = return_fm()

    assert worksheet.get(AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER).value == D("6713.51")
    assert worksheet.get(AMT_SPLIT_INCOME_AND_CREDITS_TOTAL).value == D("3795.00")
    assert worksheet.get(AMT_TAX_PAYABLE_AFTER_CREDITS).value == D("2918.51")
    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("0")
    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_APPLIED).value == D("2918.51")
    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_CLAIM).value == D("1000")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM).value == D("800.00")
    assert worksheet.get(AMT_CARRYOVER_BALANCE).value == D("200.00")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("200.00")


def test_on428_line_59_is_197_04_and_line_61_is_4319_21_after_the_carryover() -> None:
    # Line 59: 800 x 24.63% = 197.04. Line 60, the lesser of line 58 and line 59, is 197.04. Line
    # 55 is the Ontario tax after credits 2,155.30 plus the Ontario tax on split income 2,360.95 =
    # 4,516.25, and line 61 is 4,516.25 - 197.04 = 4,319.21.
    worksheet = return_fm()

    assert worksheet.get(ontario.MINIMUM_TAX_CARRYOVER_CREDIT).value == D("197.04")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("197.04")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SPLIT_INCOME).value == D("4516.25")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER).value == D("4319.21")


def test_schedule_on_s2_transfers_5545_from_the_spouse_on_lines_3_to_11() -> None:
    # Line 3, the spouse's disability amount, 10,298 (at most 16,305); line 4 is 10,298. Line 5,
    # their taxable income: 20,000. Line 9: 12,747 + 1,500 + 1,000 = 15,247. Line 10: 20,000 -
    # 15,247 = 4,753. Line 11: 10,298 - 4,753 = 5,545, claimed once (the spouse was not separated
    # for 90 days).
    worksheet = return_fm()

    assert worksheet.get(ontario.SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT_CHECKED).value == D(
        "10298.00"
    )
    assert worksheet.get(ontario.SPOUSE_TRANSFERABLE_AMOUNTS).value == D("10298.00")
    assert worksheet.get(ontario.SPOUSE_INCOME_FOR_TRANSFER).value == D("20000.00")
    assert worksheet.get(ontario.SPOUSE_CREDITS_USED).value == D("15247.00")
    assert worksheet.get(ontario.SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("4753.00")
    assert worksheet.get(ontario.SPOUSE_UNUSED_AMOUNTS).value == D("5545.00")
    assert worksheet.get(ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("5545.00")


def test_the_federal_amount_transferred_from_the_spouse_is_8767() -> None:
    # Schedule 2: line 4 is the disability amount 10,138; line 7 their taxable income 20,000; lines
    # 8 to 10 are 16,129, 1,500 and 1,000, so line 11 is 18,629; line 12 is 20,000 - 18,629 =
    # 1,371; line 13 is 10,138 - 1,371 = 8,767.
    worksheet = return_fm()

    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("8767.00")


def test_the_federal_and_ontario_tax_before_the_carryover_follow_from_the_credits() -> None:
    # Federal basic tax on 59,435: 14.5% x 57,375 = 8,319.375 plus 20.5% x 2,060 = 422.30, 8,741.68.
    # Ontario basic tax: 5.05% x 52,886 = 2,670.74 plus 9.15% x 6,549 = 599.23, 3,269.97. The
    # credit amounts 12,747 + 2,796.75 + 984 + 5,545 = 22,072.75 at 5.05% = 1,114.67, so the tax
    # after credits is 3,269.97 - 1,114.67 = 2,155.30.
    worksheet = return_fm()

    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("8741.68")
    assert worksheet.get(ontario.ONTARIO_BASIC_TAX).value == D("3269.97")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("22072.75")
    assert worksheet.get(ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("1114.67")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_CREDITS).value == D("2155.30")


def test_the_four_conditions_are_checked_and_the_ontario_tax_reduction_is_zero() -> None:
    # Each of the four conditions, not resident of Canada at the start of the year, bankrupt in
    # 2025, return filed by a trustee in bankruptcy, and not claiming the tax reduction, is checked
    # (1), and each makes ON428 line 80 zero by itself. The reduction before the conditions is
    # 2 x 294.00 = 588.00 less the tax (line 79), below zero, so 0.00; the tax reduction is 0.
    worksheet = return_fm()

    assert worksheet.get(ontario.NOT_RESIDENT_OF_CANADA_AT_START_OF_YEAR_CHECKED).value == 1
    assert worksheet.get(ontario.BANKRUPT_IN_YEAR_CHECKED).value == 1
    assert worksheet.get(ontario.RETURN_FILED_BY_TRUSTEE_IN_BANKRUPTCY_CHECKED).value == 1
    assert worksheet.get(ontario.NOT_CLAIMING_ONTARIO_TAX_REDUCTION_CHECKED).value == 1
    assert worksheet.get(ontario.TAX_REDUCTION_CLAIMABLE).value == 0
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION_BEFORE_CONDITIONS).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION).value == 0


def test_a_carryover_claim_above_the_1000_cap_is_refused_not_capped() -> None:
    # Part 8 line 12 "not more than line 1 or 11, whichever is less": the cap is the carryover of
    # 1,000.00 (line 1, below line 11 of 2,918.51), and 1,000.01 is above it, an input error.
    with pytest.raises(InputAboveBoundError) as raised:
        return_fm(carryover_claim="1000.01")

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/amt_minimum_tax_carryover_applied 1000.01 is above ca/amt_maximum_carryover_claim 1000"
    )
