"""CA-ON 2025 end to end: return FE, the deductions that no other return sets.

Return FE is `returns/2025_return_fe.yaml`: the RRSP unused contributions and their carry-forward,
the elected split-pension deduction, the line 22100 other expenses, the line 23500 social benefits
chart (completed through the EI condition, not repaid), the line 25000 other payments deduction on
its branch at or below $93,454, the net capital losses of 1985 to 1987, and the northern residents
deductions with a special work site benefit. The figures are chosen and worked out by hand from the
form text, as no CRA example exists for these lines. The tests check the hand figure of each line;
the tax figures are the engine's and are checked in the YAML only.
"""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ADJUSTED_LOSSES_APPLIED_1985_TO_1987,
    ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    DEDUCTIONS_FROM_NET_INCOME,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS,
    NET_CAPITAL_LOSS_BALANCE_1985_TO_1987,
    NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION,
    NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NORTHERN_RESIDENTS_DEDUCTIONS,
    OTHER_PAYMENTS_DEDUCTION,
    OTHER_PAYMENTS_LIMIT_INCOME,
    REMAINING_ADJUSTED_LOSSES_1985_TO_1987,
    RESIDENCY_DEDUCTION,
    RESIDENCY_NET_INCOME_LIMIT,
    RRSP_CONTRIBUTIONS_AVAILABLE,
    RRSP_DEDUCTION,
    RRSP_DEDUCTION_MAXIMUM,
    SOCIAL_BENEFITS_LINE_5,
    SOCIAL_BENEFITS_LINE_17,
    SOCIAL_BENEFITS_LINE_18,
    SOCIAL_BENEFITS_LINE_19,
    SOCIAL_BENEFITS_LINE_21,
    SOCIAL_BENEFITS_REPAYMENT,
    SOCIAL_BENEFITS_REPAYMENT_APPLIES,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES,
    TOTAL_INCOME,
    UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES,
    UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD,
    ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT,
    ZONE_A_BASIC_RESIDENCY_AMOUNT,
    ZONE_A_RESIDENCY_AFTER_WORK_SITE,
    ZONE_A_RESIDENCY_AMOUNT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_fe() -> Worksheet:
    """The worksheet of return FE: the inputs of `returns/2025_return_fe.yaml`."""
    return compute(
        "50000",
        (("12000", "6000", "0"),),
        "5000",
        "2000",
        "6000",
        "3000",
        "0",
        other_pensions_and_superannuation="32000",
        ei_and_other_benefits="6000",
        net_federal_supplements="2000",
        cpp_months=12,
        qpp_months=12,
        t4_cpp_pensionable_earnings_outside_quebec="50000",
        t2204_insurable_earnings="50000",
        t2204_premiums_deducted="820.00",
        cpp_t4_base_and_first_additional_contributions="2766.75",
        cpp_t4_second_additional_contributions="0",
        t1032_line_22="4000",
        t1032_eligible_pension_income="32000",
        t1032_filer_is_transferring_spouse=1,
        total_other_expenses="800",
        canadian_armed_forces_and_police_deduction="4000",
        limited_partnership_losses_of_other_years="1500",
        limited_partnership_at_risk_amount="1500",
        unapplied_net_capital_losses_1985_to_1987="5000",
        net_capital_losses_claimed="3000",
        zone_a_days_lived=200,
        zone_a_additional_residency_days=100,
        zone_a_special_work_site_benefits="600",
        additional_deductions="3000",
        exempt_income_deductions="3000",
        income_tax_deducted="12000",
    )


def test_total_income_is_93000_with_a_taxable_capital_gain_of_3000() -> None:
    # Line 10100 50,000 + line 11500 32,000 + line 11900 6,000 + line 12700 3,000 + line 14700
    # 2,000 = 93,000. The gain is 12,000 - 6,000 = 6,000, of which 50% (Schedule 3) is 3,000.
    worksheet = return_fe()

    assert worksheet.get(TOTAL_INCOME).value == D("93000.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("3000.00")


def test_rrsp_and_the_enhanced_cpp_contributions_on_the_return() -> None:
    # Schedule 7: unused contributions 5,000 + contributions 2,000 = 7,000 available. The most
    # that may be deducted is the lesser of the 6,000 limit and 7,000, so 6,000; the amount
    # deducted is a chosen 3,000 (at most 6,000), so the RRSP deduction is 3,000 and the carry-
    # forward is 7,000 - 3,000 = 4,000. CPP enhanced (line 22215): 1% x (50,000 - 3,500) = 465.00.
    worksheet = return_fe()

    assert worksheet.get(RRSP_CONTRIBUTIONS_AVAILABLE).value == D("7000")
    assert worksheet.get(RRSP_DEDUCTION_MAXIMUM).value == D("6000")
    assert worksheet.get(RRSP_DEDUCTION).value == D("3000")
    assert worksheet.get(UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD).value == D("4000")
    assert worksheet.get(CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES).value == D("800")
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("465.00")


def test_deductions_from_total_income_and_net_income_are_84735() -> None:
    # Line 23300: 3,000 (RRSP, line 20800) + 4,000 (elected split pension, line 21000) + 800
    # (line 22100) + 465 (line 22215) = 8,265. Line 23400: 93,000 - 8,265 = 84,735. There is no
    # social benefits repayment, so line 23600 is also 84,735.
    worksheet = return_fe()

    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("8265.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("84735.00")
    assert worksheet.get(NET_INCOME).value == D("84735.00")


def test_the_social_benefits_chart_applies_but_repays_nothing_as_line_17_is_floored() -> None:
    # Applies: EI benefits 6,000 (line 11900) and line 23400 84,735 is more than $82,125.
    # Line 5: line 3 2,000 (net federal supplements) - line 4 0 = 2,000. Line 15 84,735 minus
    # line 16 93,343 is -8,608, negative, so line 17 is the floored 0.00. Line 18: 0.00 x 15% =
    # 0.00. Line 19: the lesser of 2,000 and 0.00 is 0.00. Line 21: 0.00 + 0 = 0.00.
    worksheet = return_fe()

    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1
    assert worksheet.get(SOCIAL_BENEFITS_LINE_5).value == D("2000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("0.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_18).value == D("0.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == D("0.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("0.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("0.00")


def test_other_payments_at_or_below_93454_takes_line_14700_of_2000() -> None:
    # Line 25000 worksheet, line 9: line 1 84,735 plus lines 2 to 8 (all 0) = 84,735, not more
    # than $93,454, so the deduction is the amount from line 14700: 2,000.
    worksheet = return_fe()

    assert worksheet.get(OTHER_PAYMENTS_LIMIT_INCOME).value == D("84735.00")
    assert worksheet.get(OTHER_PAYMENTS_DEDUCTION).value == D("2000")


def test_net_capital_losses_of_1985_to_1987_claim_3000_and_leave_2000_unapplied() -> None:
    # Chart A column C is 5,000 (factor 1). Line 4 is 5,000 and line 5 is the taxable capital
    # gains of 3,000, so line 6 is 3,000 and the claim (line 7) is a chosen 3,000. Line 8 is
    # 5,000 - 3,000 = 2,000. With no pre-1986 balance, line 9 is the lesser of 0, 2,000 and
    # 2,000, so 0.00. Line 10, the line 25300 deduction, is 3,000 + 0 = 3,000. Chart A, row "After
    # May 22, 1985, and before 1988": column D is the 3,000 applied, column E is 5,000 - 3,000
    # = 2,000 and column G (x 1) is 2,000.
    worksheet = return_fe()

    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("5000.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("3000.00")
    assert worksheet.get(ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("3000")
    assert worksheet.get(UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES).value == D("2000.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("0.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("3000.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_1985_TO_1987).value == D("3000.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_1985_TO_1987).value == D("2000.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1985_TO_1987).value == D("2000.00")


def test_northern_residents_residency_deduction_is_2700_after_the_work_site_benefit() -> None:
    # Zone A basic: 200 days x $11.00 = 2,200.00; additional: 100 days x $11.00 = 1,100.00; the
    # total is 3,300.00. Less the 600 special work site benefit (box 31): 2,700.00. The limit is
    # 20% x 84,735 = 16,947.00. The residency deduction is the lesser, 2,700.00, and there are no
    # trips, so the northern residents deductions are 2,700.00.
    worksheet = return_fe()

    assert worksheet.get(ZONE_A_BASIC_RESIDENCY_AMOUNT).value == D("2200.00")
    assert worksheet.get(ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT).value == D("1100.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AMOUNT).value == D("3300.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("2700.00")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("16947.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("2700.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("2700.00")


def test_deductions_from_net_income_are_16200_and_taxable_income_is_68535() -> None:
    # Line 25700: 4,000 (line 24400) + 2,000 (line 25000) + 1,500 (line 25100) + 3,000 (line 25300)
    # + 2,700 (line 25500) + 3,000 (line 25600) = 16,200. Taxable income: 84,735 - 16,200 = 68,535.
    # The Form T2209 net income deductions are 4,000 + 2,000 + 3,000 (line 25300) + 3,000 (the
    # exempt income deduction on line 25600) = 12,000.
    worksheet = return_fe()

    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("16200.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("68535.00")
    assert worksheet.get(FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS).value == D("12000.00")
