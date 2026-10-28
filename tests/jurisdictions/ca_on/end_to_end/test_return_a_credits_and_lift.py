"""CA-ON 2025 end to end: return a credits and lift."""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    CANADA_EMPLOYMENT_AMOUNT,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
    CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT,
    CPP_BASE_CONTRIBUTIONS,
    CPP_ENHANCED_CONTRIBUTIONS,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CWB_BEFORE_REDUCTION_WITH_DEPENDANT,
    CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT,
    CWB_REDUCTION_WITH_DEPENDANT,
    CWB_REDUCTION_WITHOUT_DEPENDANT,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    EI_PREMIUMS,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    NET_FEDERAL_TAX,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    REFUND_OR_BALANCE_OWING,
    RRSP_CONTRIBUTIONS_AVAILABLE,
    RRSP_DEDUCTION,
    RRSP_DEDUCTION_MAXIMUM,
    SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS,
    TAXABLE_INCOME,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
    UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD,
    WORKING_INCOME,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    DEPENDANTS,
    DEPENDENT_CHILDREN,
    LIFT_CREDIT,
    LIFT_CREDIT_BEFORE_MAXIMUM,
    LIFT_MAXIMUM_CREDIT,
    LIFT_REDUCTION,
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_SURTAX,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
    ONTARIO_TAX_AFTER_LIFT_CREDIT,
    ONTARIO_TAX_AFTER_REDUCTION,
    ONTARIO_TAX_REDUCTION,
    ONTARIO_TAX_WITH_SURTAX,
    TAX_REDUCTION_AMOUNTS,
    TAX_REDUCTION_FOR_CHILDREN,
    TAX_REDUCTION_FOR_DEPENDANTS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, compute_with_schedule_8


def test_a_credit_larger_than_the_tax_leaves_zero_not_a_refund() -> None:
    # Employment income of 10000, with the CPP contributions computed by Schedule 8's tiers:
    # base 4.95% x (10000 - 3500) = 321.75, first additional 1% x 6500 = 65.00, no second
    # additional, so enhanced 65.00; the EI premiums computed from employment income, 1.64% x
    # 10000 = 164.00; no unused or new RRSP contributions, so the most that may be deducted is
    # the lesser of 0 and the deduction limit of 1800, and the amount deducted is 0; the Canada
    # employment amount is the lesser of 10000 and 1471.
    worksheet = compute_with_schedule_8("10000", (), "0", "0", "1800", "0", "0")

    assert worksheet.get(TOTAL_INCOME).value == D("10000")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS).value == D("321.75")
    assert worksheet.get(CPP_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("65.00")
    assert worksheet.get(CPP_SECOND_ADDITIONAL_CONTRIBUTIONS).value == D("0")
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS).value == D("65.00")
    assert worksheet.get(EI_PREMIUMS).value == D("164.00")
    assert worksheet.get(RRSP_CONTRIBUTIONS_AVAILABLE).value == D("0")
    assert worksheet.get(RRSP_DEDUCTION_MAXIMUM).value == D("0")
    assert worksheet.get(RRSP_DEDUCTION).value == D("0")
    assert worksheet.get(UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD).value == D("0")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("65.00")
    assert worksheet.get(NET_INCOME).value == D("9935.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("9935.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("1440.58")
    assert worksheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D("1471")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("18085.75")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("13232.75")
    # 14.5% of 18085.75 = 2622.43375 and 5.05% of 13232.75 = 668.253875, each rounded half-up to
    # the cent: each larger than its basic tax (14.5% of 9935.00 = 1440.575, rounded half-up to
    # the cent: 1440.58).
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("2622.43")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("668.25")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("0")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("0")
    # A zero Ontario tax is below the first surtax threshold: no surtax.
    assert worksheet.get(ONTARIO_SURTAX).value == D("0")
    assert worksheet.get(ONTARIO_TAX_WITH_SURTAX).value == D("0")
    # ON428 line 80: twice the basic reduction of 294.00, less a tax of zero, is 588.00, all of
    # it unused; line 81 leaves zero, not a refund.
    assert worksheet.get(TAX_REDUCTION_AMOUNTS).value == D("294.00")
    assert worksheet.get(ONTARIO_TAX_REDUCTION).value == D("588.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("0")
    # Schedule ON428-A: line 5 is 5.05% x 10000 = 505.00, below the $875 maximum, and net
    # income of 9935.00 is below the 32,500.00 threshold, so no reduction: the credit (ON428 line
    # 85) is 505.00, more than the Ontario tax after the reduction of zero, so line 86 is zero.
    assert worksheet.get(LIFT_CREDIT_BEFORE_MAXIMUM).value == D("505.00")
    assert worksheet.get(LIFT_MAXIMUM_CREDIT).value == D("505.00")
    assert worksheet.get(LIFT_REDUCTION).value == D("0")
    assert worksheet.get(LIFT_CREDIT).value == D("505.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("0")
    # A taxable income of 9935.00 is "$20,000 or less" on the health premium chart: no premium.
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("0")
    assert worksheet.get(ONTARIO_TAX).value == D("0")
    # Schedule 6: the working income is the employment income of 10000, and line 20 is (10000 -
    # 3000) x 27% = 1890.00, more than the $1,633 of line 21, so line 22 is 1633; the adjusted
    # family net income of 9935.00 is below the $26,855 of line 24, so no reduction: the benefit
    # (line 28) is 1633. With an eligible dependant line 22 would be 1890.00, below the $2,813,
    # and line 24's $30,639 is above the income too, so its line 28 is 1890.00; with 0 eligible
    # dependants the amounts without one are the ones claimed (T1 line 45300): 1633.
    assert worksheet.get(WORKING_INCOME).value == D("10000")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("9935.00")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT).value == D("1633")
    assert worksheet.get(CWB_REDUCTION_WITHOUT_DEPENDANT).value == D("0")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT).value == D("1633")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITH_DEPENDANT).value == D("1890.00")
    assert worksheet.get(CWB_REDUCTION_WITH_DEPENDANT).value == D("0")
    assert worksheet.get(CANADA_WORKERS_BENEFIT_WITH_DEPENDANT).value == D("1890.00")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1633")
    # With no tax deducted, nothing is payable and the benefit is the only credit: line 167 is
    # 0 - 1633 = -1633, a refund.
    assert worksheet.get(NET_FEDERAL_TAX).value == D("0")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(TOTAL_CREDITS).value == D("1633")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1633")


def test_the_tax_reduction_lowers_a_tax_below_twice_the_reduction_amounts() -> None:
    # Employment income of 24000, with no capital gain, no RRSP contributions and no union dues:
    # base CPP contributions 4.95% x (24000 - 3500) = 1014.75, first additional 1% x 20500 =
    # 205.00, EI premiums 1.64% x 24000 = 393.60; net and taxable income 23795.00; Ontario basic
    # tax 5.05% x 23795.00 = 1201.6475, rounded half-up to the cent: 1201.65, less the Ontario
    # credits 5.05% x (12747 + 1014.75 + 393.60 = 14155.35) = 714.845175, rounded half-up to the
    # cent: 714.85, is 486.80, below the first surtax threshold, so the Ontario tax with surtax
    # (ON428 line 73) is 486.80. With no dependent children and no dependants, line 78 is 2 x
    # 294.00 = 588.00, and line 80 is 588.00 - 486.80 = 101.20; line 81 is 486.80 - 101.20 =
    # 385.60.
    worksheet = compute("24000", (), "0", "0", "4320", "0", "0")

    assert worksheet.get(ONTARIO_TAX_WITH_SURTAX).value == D("486.80")
    assert worksheet.get(TAX_REDUCTION_AMOUNTS).value == D("294.00")
    assert worksheet.get(ONTARIO_TAX_REDUCTION).value == D("101.20")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("385.60")


def test_dependent_children_and_dependants_raise_the_tax_reduction() -> None:
    # Return A's amounts with five dependent children (ON428 line 75, line 60969) and three
    # dependants (line 76, line 60970): line 75 is 5 x 544 = 2720, line 76 is 3 x 544 = 1632,
    # line 77 is 294.00 + 2720 + 1632 = 4646.00 and line 78 is 9292.00; line 80 is 9292.00 -
    # 8195.77 = 1096.23, and line 81 is 8195.77 - 1096.23 = 7099.54.
    worksheet = compute(
        "110000",
        (("20000", "0", "0"),),
        "0",
        "1926",
        "19800",
        "1926",
        "2000",
        dependent_children=5,
        dependants=3,
    )

    assert worksheet.get(DEPENDENT_CHILDREN).value == 5
    assert worksheet.get(DEPENDANTS).value == 3
    assert worksheet.get(TAX_REDUCTION_FOR_CHILDREN).value == D("2720")
    assert worksheet.get(TAX_REDUCTION_FOR_DEPENDANTS).value == D("1632")
    assert worksheet.get(TAX_REDUCTION_AMOUNTS).value == D("4646.00")
    assert worksheet.get(ONTARIO_TAX_WITH_SURTAX).value == D("8195.77")
    assert worksheet.get(ONTARIO_TAX_REDUCTION).value == D("1096.23")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("7099.54")


def test_the_health_premium_in_a_sloped_row_adds_the_rate_to_the_plateau() -> None:
    # A capital gain of 74000 alone, with no employment income, no RRSP contributions and no
    # union dues: taxable income is half the gain, 37000, and the Ontario credits are 5.05% x
    # 12747 = 643.7235, rounded half-up to the cent: 643.72. ON428 line 89's chart, "more than
    # $36,000 but not more than $38,500": (37000 - 36000) x 6% + 300 = 360.00; the Ontario basic
    # tax 5.05% x 37000 = 1868.50 less the credits is 1224.78, above 588.00, so no reduction,
    # and line 90 is 1224.78 + 360.00 = 1584.78.
    worksheet = compute("0", (("74000", "0", "0"),), "0", "0", "0", "0", "0")

    assert worksheet.get(TAXABLE_INCOME).value == D("37000")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("1224.78")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("360.00")
    assert worksheet.get(ONTARIO_TAX).value == D("1584.78")


def test_the_health_premium_at_the_top_of_a_sloped_row_is_the_plateau() -> None:
    # A capital gain of 50000 alone: taxable income 25000, "more than $20,000 but not more than
    # $25,000": (25000 - 20000) x 6% = 300.00, the plateau itself; the Ontario basic tax 5.05%
    # x 25000 = 1262.50 less the credits of 643.72 is 618.78, above 588.00, so no reduction,
    # and line 90 is 618.78 + 300.00 = 918.78.
    worksheet = compute("0", (("50000", "0", "0"),), "0", "0", "0", "0", "0")

    assert worksheet.get(TAXABLE_INCOME).value == D("25000")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("618.78")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("300.00")
    assert worksheet.get(ONTARIO_TAX).value == D("918.78")


def test_no_health_premium_at_the_first_threshold() -> None:
    # A capital gain of 40000 alone: taxable income 20000, "$20,000 or less", so no premium;
    # the Ontario basic tax 5.05% x 20000 = 1010.00 less the credits of 643.72 is 366.28, below
    # 588.00, so the reduction is 221.72 and line 81 is 144.56, which is line 90.
    worksheet = compute("0", (("40000", "0", "0"),), "0", "0", "0", "0", "0")

    assert worksheet.get(TAXABLE_INCOME).value == D("20000")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("144.56")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("0")
    assert worksheet.get(ONTARIO_TAX).value == D("144.56")


def test_the_lift_credit_between_the_thresholds_is_reduced_and_comes_off_the_tax() -> None:
    # Employment income of 40000, with no capital gain, no RRSP contributions and no union dues:
    # base CPP contributions 4.95% x (40000 - 3500) = 1806.75, first additional 1% x 36500 =
    # 365.00, EI premiums 1.64% x 40000 = 656.00; net and taxable income 39635.00. Ontario basic
    # tax 5.05% x 39635.00 = 2001.5675, rounded half-up to the cent: 2001.57, less the Ontario
    # credits 5.05% x (12747 + 1806.75 + 656.00 = 15209.75) = 768.092375, rounded half-up to the
    # cent: 768.09, is 1233.48, below the first surtax threshold and above 588.00, so line 81 is
    # 1233.48.
    # Schedule ON428-A: line 5 is 5.05% x 40000 = 2020.00, at most 875 (line 14); line 17 is
    # 39635.00 - 32500 = 7135.00 and line 19 7135.00 x 5% = 356.75; line 20 is 875 - 356.75 =
    # 518.25 (ON428 line 85). Line 86 is 1233.48 - 518.25 = 715.23; the health premium on
    # 39635.00, "more than $38,500 but not more than $48,000", is 450, so line 90 is 715.23 + 450
    # = 1165.23.
    worksheet = compute("40000", (), "0", "0", "7200", "0", "0")

    assert worksheet.get(NET_INCOME).value == D("39635.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("1233.48")
    assert worksheet.get(LIFT_CREDIT_BEFORE_MAXIMUM).value == D("2020.00")
    assert worksheet.get(LIFT_MAXIMUM_CREDIT).value == D("875")
    assert worksheet.get(LIFT_REDUCTION).value == D("356.75")
    assert worksheet.get(LIFT_CREDIT).value == D("518.25")
    assert worksheet.get(ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("715.23")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("450")
    assert worksheet.get(ONTARIO_TAX).value == D("1165.23")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "lift_credit_single: lift_maximum_credit 875 less lift_reduction 356.75, "
        "not below 0 = 518.25"
    ) in rendered
    assert (
        "lift_credit: lift_credit_single 518.25, chosen as "
        "spouse_or_common_law_partner_on_december_31_total is 0"
    ) in rendered
    assert (
        "ontario_tax_after_lift_credit: ontario_tax_after_foreign_tax_credit 1233.48 "
        "less lift_credit 518.25, not below 0 = 715.23"
    ) in rendered


def test_the_lift_credit_with_a_spouse_is_reduced_by_the_family_income_over_65000() -> None:
    # The ticket's example. Employment income of 25217.17, with no capital gain, no RRSP
    # contributions and no union dues: first additional CPP contribution 1% x (25217.17 - 3500) =
    # 217.1717, rounded half-up to the cent: 217.17, so net income is 25217.17 - 217.17 = 25000.00.
    # Schedule ON428-A: line 5 is 5.05% x 25217.17 = 1273.4670, rounded half-up to 1273.47, at
    # most 875 (lines 14 and 29). Line 13 (and lines 15, 30 and 33) is 25000.00; the spouse's
    # line 21 is 50000, so line 28 (and line 34) is 50000 and line 35 is 75000.00. Line 32 is
    # 25000.00 - 32500.00 below zero, so 0; line 37 is 75000.00 - 65000.00 = 10000.00; line 38,
    # whichever is more, is 10000.00; line 40 is 10000.00 x 5% = 500.00; line 41 is 875 - 500.00
    # = 375.00 (ON428 line 85), where Part A (line 20) would have been the whole 875.
    worksheet = compute(
        "25217.17",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        spouse_or_common_law_partner_on_december_31=1,
        spouse_net_income_before_adjustments="50000",
    )

    assert worksheet.get(NET_INCOME).value == D("25000.00")
    assert worksheet.get(LIFT_CREDIT_BEFORE_MAXIMUM).value == D("1273.47")
    assert worksheet.get(LIFT_MAXIMUM_CREDIT).value == D("875")
    assert worksheet.get(ontario.LIFT_ADJUSTED_NET_INCOME).value == D("25000.00")
    assert worksheet.get(ontario.LIFT_SPOUSE_ADJUSTED_NET_INCOME).value == D("50000")
    assert worksheet.get(ontario.LIFT_FAMILY_NET_INCOME).value == D("75000.00")
    assert worksheet.get(ontario.LIFT_EXCESS_OVER_INDIVIDUAL_THRESHOLD).value == D("0")
    assert worksheet.get(ontario.LIFT_EXCESS_OVER_FAMILY_THRESHOLD).value == D("10000.00")
    assert worksheet.get(ontario.LIFT_GREATER_EXCESS).value == D("10000.00")
    assert worksheet.get(ontario.LIFT_FAMILY_REDUCTION).value == D("500.00")
    assert worksheet.get(ontario.LIFT_CREDIT_WITH_SPOUSE).value == D("375.00")
    assert worksheet.get(ontario.LIFT_CREDIT_SINGLE).value == D("875.00")
    assert worksheet.get(LIFT_CREDIT).value == D("375.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "lift_greater_excess: greater of lift_excess_over_individual_threshold 0 "
        "and lift_excess_over_family_threshold 10000 = 10000"
    ) in rendered
    assert (
        "lift_credit: lift_credit_with_spouse 375, chosen as "
        "spouse_or_common_law_partner_on_december_31_total is 1"
    ) in rendered


def test_a_count_of_0_spouses_at_year_end_applies_part_a_even_with_the_spouse_figures_given() -> (
    None
):
    # The same figures as the ticket's example, but the spouse or common-law partner died during
    # the year ("complete Part A as if you were single"), so the caller enters 0 for the count:
    # Part B is still computed from the figures given, 375.00, and line 20 is 875 - 0 = 875.00,
    # the credit.
    worksheet = compute(
        "25217.17",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        spouse_or_common_law_partner_on_december_31=0,
        spouse_net_income_before_adjustments="50000",
    )

    assert worksheet.get(NET_INCOME).value == D("25000.00")
    assert worksheet.get(ontario.LIFT_CREDIT_WITH_SPOUSE).value == D("375.00")
    assert worksheet.get(ontario.LIFT_CREDIT_SINGLE).value == D("875.00")
    assert worksheet.get(LIFT_CREDIT).value == D("875.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "lift_credit: lift_credit_single 875, chosen as "
        "spouse_or_common_law_partner_on_december_31_total is 0"
    ) in rendered


def test_with_a_spouse_the_greater_of_the_two_excesses_is_line_32_below_the_family_threshold() -> (
    None
):
    # Employment income of 40000 as in the LIFT test above: net income 39635.00 and line 32 =
    # 39635.00 - 32500.00 = 7135.00. The spouse's 20000 makes line 35 59635.00, below the
    # 65000.00 family threshold, so line 37 is 0 and line 38 is line 32: 7135.00 x 5% = 356.75
    # and line 41 is 875 - 356.75 = 518.25, as for a single filer.
    worksheet = compute(
        "40000",
        (),
        "0",
        "0",
        "7200",
        "0",
        "0",
        spouse_or_common_law_partner_on_december_31=1,
        spouse_net_income_before_adjustments="20000",
    )

    assert worksheet.get(ontario.LIFT_EXCESS_OVER_INDIVIDUAL_THRESHOLD).value == D("7135.00")
    assert worksheet.get(ontario.LIFT_FAMILY_NET_INCOME).value == D("59635.00")
    assert worksheet.get(ontario.LIFT_EXCESS_OVER_FAMILY_THRESHOLD).value == D("0")
    assert worksheet.get(ontario.LIFT_GREATER_EXCESS).value == D("7135.00")
    assert worksheet.get(ontario.LIFT_FAMILY_REDUCTION).value == D("356.75")
    assert worksheet.get(LIFT_CREDIT).value == D("518.25")


def test_the_spouses_own_adjustments_make_line_28_as_the_filers_make_line_13() -> None:
    # Employment income of 25217.17 (net income 25000.00). The spouse's net income is 50000
    # (line 21), their UCCB repayment (line 22) 1000 and RDSP income repayment (line 23) 500, so
    # line 24 is 51500; their UCCB (line 25) is 2000 and RDSP income (line 26) 300, so line 27 is
    # 2300 and line 28 is 51500 - 2300 = 49200. Line 35 is 25000.00 + 49200 = 74200.00, line 37
    # 9200.00, line 40 9200.00 x 5% = 460.00 and line 41 875 - 460.00 = 415.00.
    worksheet = compute(
        "25217.17",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        spouse_or_common_law_partner_on_december_31=1,
        spouse_net_income_before_adjustments="50000",
        spouse_uccb_repayment="1000",
        spouse_rdsp_income_repayment="500",
        spouse_universal_child_care_benefit="2000",
        spouse_rdsp_income="300",
    )

    assert worksheet.get(ontario.LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS).value == D("51500")
    assert worksheet.get(ontario.LIFT_SPOUSE_UCCB_AND_RDSP_INCOME).value == D("2300")
    assert worksheet.get(ontario.LIFT_SPOUSE_ADJUSTED_NET_INCOME).value == D("49200")
    assert worksheet.get(ontario.LIFT_FAMILY_NET_INCOME).value == D("74200.00")
    assert worksheet.get(ontario.LIFT_EXCESS_OVER_FAMILY_THRESHOLD).value == D("9200.00")
    assert worksheet.get(ontario.LIFT_FAMILY_REDUCTION).value == D("460.00")
    assert worksheet.get(LIFT_CREDIT).value == D("415.00")


def test_a_negative_spouse_net_income_is_kept_on_line_21_and_floored_on_line_28() -> None:
    # Line 21 takes the net income "or the amount they would have entered if the instructions on
    # line 23600 said "if negative, show in brackets"": -5000 here, added to the repayments on
    # line 24 and floored at zero on line 28, so the family income is the filer's alone.
    worksheet = compute(
        "25217.17",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        spouse_or_common_law_partner_on_december_31=1,
        spouse_net_income_before_adjustments="-5000",
        spouse_uccb_repayment="1000",
    )

    assert worksheet.get(SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-5000")
    assert worksheet.get(ontario.LIFT_SPOUSE_NET_INCOME_AND_REPAYMENTS).value == D("-4000")
    assert worksheet.get(ontario.LIFT_SPOUSE_ADJUSTED_NET_INCOME).value == D("0")
    assert worksheet.get(ontario.LIFT_FAMILY_NET_INCOME).value == D("25000.00")
    assert worksheet.get(ontario.LIFT_GREATER_EXCESS).value == D("0")
    assert worksheet.get(LIFT_CREDIT).value == D("875.00")


def test_the_filers_repayments_and_income_adjust_net_income_into_line_13() -> None:
    # Employment income of 25217.17, a UCCB repayment of 1000 and an RDSP income repayment of 500
    # (both in the deductions, the latter as other deductions), a UCCB of 2000 and RDSP income of
    # 300. Line 6 is net income before adjustments: 25217.17 + 2000 + 300 = 27517.17, less the
    # first additional CPP contribution 217.17, the 1000 and the 500 = 25800.00 (line 23400,
    # which is not floored). Line 9 is 25800.00 + 1000 + 500 = 27300.00 (lines 7 and 8 add the
    # repayments back); line 12 is 2000 + 300 = 2300; line 13 is 27300.00 - 2300 = 25000.00.
    worksheet = compute(
        "25217.17",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        universal_child_care_benefit="2000",
        rdsp_income="300",
        uccb_repayment="1000",
        rdsp_income_repayment="500",
        other_deductions="500",
    )

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("25800.00")
    assert worksheet.get(ontario.LIFT_NET_INCOME_AND_REPAYMENTS).value == D("27300.00")
    assert worksheet.get(ontario.LIFT_UCCB_AND_RDSP_INCOME).value == D("2300")
    assert worksheet.get(ontario.LIFT_ADJUSTED_NET_INCOME).value == D("25000.00")
    # Part A's reduction reads line 13, not net income: 25000.00 is below 32500.
    assert worksheet.get(LIFT_REDUCTION).value == D("0")
    assert worksheet.get(LIFT_CREDIT).value == D("875.00")


def test_a_negative_net_income_before_adjustments_is_floored_into_line_13() -> None:
    # Line 6 may be negative ("if negative, show in brackets"), and line 13 floors line 9 minus
    # line 12 at zero: an other deduction of 30000 against employment income of 10000 gives net
    # income before adjustments of 10000 - 65 - 30000 = -20065.00 (the first additional CPP
    # contribution is 1% x 6500 = 65.00), line 9 is -20065.00 and line 13 is 0.
    worksheet = compute("10000", (), "0", "0", "0", "0", "0", other_deductions="30000")

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-20065.00")
    assert worksheet.get(NET_INCOME).value == D("0")
    assert worksheet.get(ontario.LIFT_NET_INCOME_AND_REPAYMENTS).value == D("-20065.00")
    assert worksheet.get(ontario.LIFT_ADJUSTED_NET_INCOME).value == D("0")
