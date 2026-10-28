"""CA-ON 2025 end to end: return as."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.capabilities.times_count import TimesCount
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    BASIC_PERSONAL_AMOUNT,
    CHARITABLE_DONATIONS_LIMIT,
    DONATION_LIMIT_ON_NET_INCOME,
    EI_BENEFITS_REPAYMENT_CHECKED,
    FEDERAL_BASIC_TAX,
    MEDICAL_NET_INCOME_SHARE,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3,
    NET_FEDERAL_TAX,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO,
    NET_INCOME_SIGNED,
    OAS_AND_FEDERAL_SUPPLEMENTS,
    OAS_BENEFITS_BASE_AMOUNT,
    OTHER_PAYMENTS_LIMIT_INCOME,
    REFUND_OR_BALANCE_OWING,
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
    SOCIAL_BENEFITS_REPAYMENT_PAYABLE,
    TAXABLE_INCOME,
    TOSI_ADJUSTED_NET_INCOME,
    TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, routed_statement


def return_as(employment_income: str = "92074", **overrides: Any) -> Worksheet:
    """Return AS's inputs, as in `returns/2025_return_as.yaml`, over the keyword overrides given.

    A filer with employment income of 92074 and old age security of 9000 on line 11300. The CPP
    contributions and EI premiums are at their maximums for any employment income over 81200
    (the CPP second ceiling), and the enhanced CPP contributions of 1074 (678 + 396) are the
    only deduction, so the total income of 101074.00 gives a net income before adjustments (line
    23400) of exactly 100000.00.
    """
    inputs: dict[str, Any] = {"old_age_security": "9000"}
    inputs.update(overrides)
    return compute(employment_income, (), "0", "0", "0", "0", "0", **inputs)


def test_return_as_has_a_net_income_before_adjustments_of_100000_00_on_line_23400() -> None:
    # Employment income 92074.00 plus the OAS pension 9000.00 is total income (line 15000)
    # 101074.00; the enhanced CPP contributions (line 22215) are 1% x (71300 - 3500) = 678.00 plus
    # 4% x (81200 - 71300) = 396.00, 1074.00, so line 23400 is 101074.00 - 1074.00 = 100000.00.
    worksheet = return_as()

    assert worksheet.get(TOTAL_INCOME).value == D("101074.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("100000.00")


def test_return_as_chart_applies_as_line_11300_is_entered_and_line_23400_over_93454() -> None:
    # Federal Worksheet "Line 23500": the second condition holds (an amount on line 11300 and
    # 100000.00 more than $93,454); the first does not (nothing on line 11900).
    worksheet = return_as()

    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1


def test_return_as_chart_gives_998_55_on_line_21() -> None:
    # Line 3 is 9000 + 0 = 9000.00; line 4 is 0, so line 5 is 9000.00. Line 6 is the line 23400 of
    # 100000.00 plus the T1206 line 4 of 0; lines 7 to 9 are 0, so line 10 is 0.00 and line 11 is
    # 100000.00; lines 12 and 13 are 0, so line 14 is 0.00 and line 15 is 100000.00. Line 16 is
    # 93343.00, so line 17 is 6657.00 and line 18 is 15% of it, 998.55; line 19 is the lesser of
    # 9000.00 and 998.55, 998.55; line 20 is 0, so line 21 is 998.55.
    worksheet = return_as()

    assert worksheet.get(OAS_AND_FEDERAL_SUPPLEMENTS).value == D("9000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_5).value == D("9000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_6).value == D("100000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_10).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_11).value == D("100000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_14).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_15).value == D("100000.00")
    assert worksheet.get(OAS_BENEFITS_BASE_AMOUNT).value == D("93343.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("6657.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_18).value == D("998.55")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == D("998.55")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("998.55")


def test_return_as_has_998_55_on_lines_23500_and_42200_and_99001_45_on_line_23600() -> None:
    # T1 line 55 (23500) is the chart's line 21, 998.55, line 146 (42200) carries it, and line 56
    # (23600) is line 54 less line 55: 100000.00 - 998.55 = 99001.45.
    worksheet = return_as()

    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("998.55")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_PAYABLE).value == D("998.55")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("100000.00")
    assert worksheet.get(NET_INCOME_SIGNED).value == D("99001.45")
    assert worksheet.get(NET_INCOME).value == D("99001.45")


def test_return_as_line_25000_worksheet_still_reads_line_23400_not_line_23600() -> None:
    # Federal Worksheet "Line 25000" line 1 "Amount from line 23400 of your return (if negative,
    # enter "0")": 100000.00, floored at 0, though the net income of line 23600 is now 99001.45.
    # Line 9 is that, less the UCCB and RDSP income of 0, plus the repayments of 0.
    worksheet = return_as()

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO).value == D("100000.00")
    assert worksheet.get(OTHER_PAYMENTS_LIMIT_INCOME).value == D("100000.00")


def test_return_as_readers_of_line_23600_take_the_net_income_of_99001_45() -> None:
    # The lines whose forms say "from line 23600": line 26000 (the taxable income) is 99001.45
    # with no deductions from net income; T1 line 108 and ON428 line 37 take 3% of it,
    # 2970.0435, rounded half-up to the cent, 2970.04; Schedule 9 line 6 takes 75% of it,
    # 74251.0875, to 74251.09, which is below the net income itself, so line 9 is 74251.09; the
    # northern residents worksheet's line 12 takes 20% of it, 19800.29.
    worksheet = return_as()

    assert worksheet.get(TAXABLE_INCOME).value == D("99001.45")
    assert worksheet.get(MEDICAL_NET_INCOME_SHARE).value == D("2970.04")
    assert worksheet.get(ontario.MEDICAL_NET_INCOME_SHARE).value == D("2970.04")
    assert worksheet.get(DONATION_LIMIT_ON_NET_INCOME).value == D("74251.09")
    assert worksheet.get(CHARITABLE_DONATIONS_LIMIT).value == D("74251.09")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("19800.29")


def test_return_as_form_t1206_line_5_and_on479_a_line_1_read_line_23600_of_99001_45() -> None:
    # Form T1206 Part 1 line 5 "Net income from line 23600 of your tax return (or the amount you
    # would have entered if the instructions on line 23600 read "if negative, show in brackets")"
    # is 100000.00 - 998.55 = 99001.45, and line 6 "TOSI-adjusted net income: line 4 plus line 5"
    # is 0 + 99001.45, so each of the two kinds is 99001.45 and the figures that read them follow
    # by exactly the 998.55 of line 23500. Schedule ON479-A column 1: line 1 is 99001.45, line 2
    # (child care expenses) 0 and line 3 "Social benefits repayment from line 23500 of the
    # return" 998.55, so line 4 "Add lines 1 to 3" is 100000.00 again. The adjusted family net
    # income of the Canada workers benefit takes the TOSI-adjusted net income not below zero.
    worksheet = return_as()

    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME).value == D("99001.45")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO).value == D("99001.45")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("99001.45")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3).value == D("99001.45")
    assert worksheet.get(ontario.CARE_ADJUSTED_INCOME).value == D("100000.00")
    assert worksheet.get(ontario.CARE_FAMILY_ADJUSTED_INCOME).value == D("100000.00")


def test_a_line_23500_of_3000_lowers_the_basic_personal_amount_by_the_taper_on_line_23600() -> None:
    # Employment income 198074 plus the OAS pension 3000 is 201074.00, less 1074.00, 200000.00
    # (line 23400). The chart applies and line 23500 is 3000 (as in the case above), so line
    # 23600 and the TOSI-adjusted net income are 197000.00. The Federal Worksheet for line 30000
    # reads the TOSI-adjusted net income: line 5 is 197000.00 - 177882.00 = 19118.00, line 7 is
    # 19118.00 / 75532.00, line 9 that x 1591.00 = 402.700..., rounded half-up to the cent
    # 402.70, line 10 is 1591.00 - 402.70 = 1188.30 and line 11 is 14538.00 + 1188.30 =
    # 15726.30; reading line 23400 (200000.00) it would be 15663.11.
    worksheet = return_as("198074", old_age_security="3000")

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("200000.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("3000.00")
    assert worksheet.get(NET_INCOME_SIGNED).value == D("197000.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME).value == D("197000.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO).value == D("197000.00")
    assert worksheet.get(BASIC_PERSONAL_AMOUNT).value == D("15726.30")
    assert worksheet.get(ontario.CARE_ADJUSTED_INCOME).value == D("200000.00")


def test_return_as_taxes_the_reduced_income_and_adds_line_42200_to_the_total_payable() -> None:
    # Federal basic tax on 99001.45: 14.5% x 57375 = 8319.375, 8319.38 half-up, plus 20.5% x
    # (99001.45 - 57375) = 41626.45 x 20.5% = 8533.42225, 8533.42, so 16852.80. The credits are
    # 3194.87 (22033.58 x 14.5%), so the federal tax after credits and the net federal tax are
    # 13657.93. Ontario basic tax: 5.05% x 52886 = 2670.743, 2670.74, plus 9.15% x (99001.45 -
    # 52886) = 46115.45 x 9.15% = 4219.563675, 4219.56, so 6890.30; less the credits of 867.62 is
    # 6022.68; the surtax is 20% x (6022.68 - 5710) = 62.536, 62.54, so 6085.22, and the health
    # premium of 750 makes the Ontario tax 6835.22. The total payable (line 43500) is
    # 13657.93 + 0 + 0 + 998.55 (line 42200) + 6835.22 = 21491.70.
    worksheet = return_as()

    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("16852.80")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("13657.93")
    assert worksheet.get(ontario.ONTARIO_BASIC_TAX).value == D("6890.30")
    assert worksheet.get(ontario.ONTARIO_TAX_LESS_DIVIDEND_CREDIT).value == D("6022.68")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("6835.22")
    assert worksheet.get(TOTAL_PAYABLE).value == D("21491.70")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("21491.70")


def test_return_as_trace_names_each_line_of_the_chart() -> None:
    rendered = EnglishTraceRenderer().render_all(return_as().trace)

    for line in (
        "social_benefits_repayment_applies: condition 2 applies, so 1",
        "oas_and_federal_supplements: old_age_security 9000 + net_federal_supplements 0 = 9000",
        "social_benefits_line_5: oas_and_federal_supplements 9000 "
        "less oas_overpayment_recovered 0, not below 0 = 9000",
        "social_benefits_line_6: net_income_before_adjustments 100000 + total_split_income 0 "
        "= 100000",
        "social_benefits_line_10: ei_benefits_repayment_checked 0 + universal_child_care_benefit 0 "
        "+ rdsp_income 0 = 0",
        "social_benefits_line_11: social_benefits_line_6 100000 less social_benefits_line_10 0 "
        "= 100000",
        "social_benefits_line_14: uccb_repayment 0 + rdsp_income_repayment_checked 0 = 0",
        "social_benefits_line_15: social_benefits_line_11 100000 + social_benefits_line_14 0 "
        "= 100000",
        "oas_benefits_base_amount: credit amount 93343 (half-up to 0.01)",
        "social_benefits_line_17: social_benefits_line_15 100000 "
        "less oas_benefits_base_amount 93343, not below 0 = 6657",
        "social_benefits_line_18: 15% of social_benefits_line_17 6657 (half-up to 0.01)",
        "social_benefits_line_19: lesser of social_benefits_line_5 9000 "
        "and social_benefits_line_18 998.55 = 998.55",
        "social_benefits_line_21: social_benefits_line_19 998.55 + ei_benefits_repayment_checked 0 "
        "= 998.55",
        "social_benefits_repayment: social_benefits_line_21 998.55 "
        "for each of 1 social_benefits_repayment_applies = 998.55",
        "net_income_signed: net_income_before_adjustments 100000 "
        "less social_benefits_repayment 998.55 = 99001.45",
        "net_income: net_income_before_adjustments 100000 less social_benefits_repayment 998.55, "
        "not below 0 = 99001.45",
        "tosi_adjusted_net_income: total_split_income 0 + net_income_signed 99001.45 = 99001.45",
        "tosi_adjusted_net_income_not_below_zero: total_split_income 0 "
        "+ net_income_signed 99001.45, not below 0 = 99001.45",
        "care_adjusted_income: tosi_adjusted_net_income 99001.45 + child_care_expenses 0 "
        "+ social_benefits_repayment 998.55, not below 0 = 100000",
    ):
        assert line in rendered, line


# --- the acceptance cases ----------------------------------------------------------------------


def test_a_line_23400_of_93400_does_not_trigger_the_chart_so_line_23500_is_0() -> None:
    # Employment income 85474 plus the OAS pension 9000 is 94474.00, less the enhanced CPP
    # contributions of 1074.00, 93400.00. The chart does not apply (93400.00 is not more than
    # $93,454, and nothing is on line 11900), so line 23500 is 0 ("If not, enter "0" on line
    # 23500."), although line 17 would be 93400.00 - 93343.00 = 57.00, line 18 15% of it, 8.55,
    # and the chart's line 21 8.55.
    worksheet = return_as("85474")

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("93400.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 0
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("57.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_18).value == D("8.55")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == D("8.55")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("8.55")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_PAYABLE).value == D("0")
    assert worksheet.get(NET_INCOME).value == D("93400.00")


def test_oas_of_3000_with_line_23400_of_150000_gives_3000_limited_by_line_5() -> None:
    # Employment income 148074 plus the OAS pension 3000 is 151074.00, less 1074.00, 150000.00.
    # The chart applies (3000 on line 11300, 150000.00 more than $93,454). Line 17 is 150000.00 -
    # 93343.00 = 56657.00 and line 18 is 15% of it, 8498.55, but line 5 is 3000.00, so line 19
    # (the lesser) and line 21 are 3000.00, the lines 23500 and 42200, and line 23600 is 150000.00
    # - 3000.00 = 147000.00.
    worksheet = return_as("148074", old_age_security="3000")

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("150000.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1
    assert worksheet.get(SOCIAL_BENEFITS_LINE_5).value == D("3000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("56657.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_18).value == D("8498.55")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == D("3000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("3000")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("3000.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_PAYABLE).value == D("3000.00")
    assert worksheet.get(NET_INCOME).value == D("147000.00")


# --- the other lines of the chart --------------------------------------------------------------


def test_line_4_the_oas_overpayment_recovered_comes_off_line_3_not_below_zero() -> None:
    # Same income as above (line 23400 150000.00, OAS 3000), with 1000 recovered (box 20 of the
    # T4A(OAS) slip): line 5 is 3000 - 1000 = 2000.00, the lesser of it and 8498.55.
    worksheet = return_as("148074", old_age_security="3000", oas_overpayment_recovered="1000")

    assert worksheet.get(OAS_AND_FEDERAL_SUPPLEMENTS).value == D("3000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_5).value == D("2000")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("2000.00")


def test_an_overpayment_recovered_over_line_3_gives_a_line_5_of_0() -> None:
    # Line 5 "Line 3 minus line 4 (if negative, enter "0")": 3000 - 4000 is 0, so lines 19 and 23500
    # are 0 though the chart applies.
    worksheet = return_as("148074", old_age_security="3000", oas_overpayment_recovered="4000")

    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1
    assert worksheet.get(SOCIAL_BENEFITS_LINE_5).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("0")


def test_the_ei_benefits_repayment_of_line_7_comes_off_line_11_and_is_added_to_line_21() -> None:
    # Employment income 90000 plus EI benefits (line 11900) of 5000 is 95000.00, less the enhanced
    # CPP contributions of 1074.00, 93926.00. The first condition holds (an amount on line 11900
    # and 93926.00 more than $82,125). Line 7 is the T4E's 1000 (a chosen figure), so line 10 is
    # 1000.00, line 11 is 93926.00 - 1000.00 = 92926.00 and so is line 15, under the 93343.00 of
    # line 16, so lines 17, 18 and 19 are 0; line 21 is 0 + 1000 = 1000.00, the lines 23500 and
    # 42200, and line 23600 is 93926.00 - 1000.00 = 92926.00.
    worksheet = compute(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        ei_and_other_benefits="5000",
        ei_benefits_repayment="1000",
    )

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("93926.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1
    assert worksheet.get(SOCIAL_BENEFITS_LINE_10).value == D("1000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_11).value == D("92926.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_15).value == D("92926.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_18).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("1000")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("1000.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_PAYABLE).value == D("1000.00")
    assert worksheet.get(NET_INCOME).value == D("92926.00")


# The input error of `core/at_most` on the EI benefits repayment against the EI and other benefits
# received on line 11900: "ca/ei_benefits_repayment <amount> is above ca/ei_and_other_benefits
# <bound>".
ABOVE_LINE_11900 = "ca/ei_benefits_repayment {amount} is above ca/ei_and_other_benefits {bound}"


def test_an_ei_benefits_repayment_above_the_ei_benefits_received_is_refused_not_taken() -> None:
    # Federal Worksheet "Line 23500 - Social benefits repayment" line 7 "EI benefits repayment from
    # line 4 of the repayment chart on your T4E slip, if any", and Guide 5000-G line 23500 "You have
    # to repay part of the EI benefits (line 11900) that you received in 2025": a repayment of
    # 40,000 against EI benefits of 10,000 is an input error. It is not taken off line 11 or added
    # to line 21, and no social benefits repayment is worked out on it.
    with pytest.raises(
        InputAboveBoundError,
        match=re.escape(ABOVE_LINE_11900.format(amount="40000", bound="10000")),
    ):
        compute(
            "90000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            ei_and_other_benefits="10000",
            ei_benefits_repayment="40000",
        )


def test_an_ei_benefits_repayment_one_cent_above_the_ei_benefits_is_refused_not_capped() -> None:
    # The bound is refused, not capped: 5,000.01 against EI benefits of 5,000.00 is an input error,
    # and nothing is taken at 5,000.00.
    with pytest.raises(
        InputAboveBoundError,
        match=re.escape(ABOVE_LINE_11900.format(amount="5000.01", bound="5000")),
    ):
        compute(
            "90000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            ei_and_other_benefits="5000",
            ei_benefits_repayment="5000.01",
        )


def test_an_ei_benefits_repayment_with_no_ei_benefits_received_is_refused() -> None:
    # Nothing received on line 11900 is the bound 0: a repayment of 1,000 is above it.
    with pytest.raises(
        InputAboveBoundError,
        match=re.escape(ABOVE_LINE_11900.format(amount="1000", bound="0")),
    ):
        compute(
            "90000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            ei_benefits_repayment="1000",
        )


def test_an_ei_benefits_repayment_equal_to_the_ei_benefits_received_is_accepted() -> None:
    # The bound is inclusive. Employment income 90000 plus EI benefits of 5000 is 95000.00, less the
    # enhanced CPP contributions of 1074.00, 93926.00 (the first condition holds). The repayment of
    # 5000 is the whole of the benefits, so line 10 is 5000.00, line 11 is 88926.00 and line 15 is
    # under the 93343.00 of line 16, so lines 17 to 19 are 0; line 21 is 0 + 5000 = 5000.00, the
    # lines 23500 and 42200, and line 23600 is 93926.00 - 5000.00 = 88926.00.
    worksheet = compute(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        ei_and_other_benefits="5000",
        ei_benefits_repayment="5000",
    )

    assert worksheet.get(EI_BENEFITS_REPAYMENT_CHECKED).value == D("5000")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("93926.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_10).value == D("5000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_11).value == D("88926.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("5000")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("5000")
    assert worksheet.get(NET_INCOME).value == D("88926.00")


def test_no_ei_benefits_and_no_repayment_is_accepted_and_adds_nothing() -> None:
    # No EI benefits and no repayment: the checked repayment and line 10 are 0, and so are line 21
    # and the social benefits repayment.
    worksheet = compute("90000", (), "0", "0", "0", "0", "0")

    assert worksheet.get(EI_BENEFITS_REPAYMENT_CHECKED).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_10).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("0")


def test_lines_8_9_12_and_13_adjust_the_adjusted_net_income_of_line_15() -> None:
    # Employment income 86000, OAS 9000, UCCB (line 11700) 1000 and RDSP income (line 12500) 600
    # are 96600.00 of total income; the deductions are the enhanced CPP contributions 1074, the
    # UCCB repayment (line 21300) 400 and other deductions (line 23200) of 100, which the caller
    # makes the RDSP income repayment, 1574.00, so line 23400 is 95026.00 (over $93,454, with OAS
    # on line 11300, so the chart applies). Line 10 is 0 + 1000 + 600 = 1600.00, line 11 is
    # 95026.00 - 1600.00 = 93426.00, line 14 is 400 + 100 = 500.00 and line 15 is 93926.00; line
    # 17 is 93926.00 - 93343.00 = 583.00, line 18 is 15% of it, 87.45, under line 5 (9000.00), so
    # lines 19, 21 and 23500 are 87.45 and line 23600 is 95026.00 - 87.45 = 94938.55.
    worksheet = compute(
        "86000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        old_age_security="9000",
        universal_child_care_benefit="1000",
        rdsp_income="600",
        uccb_repayment="400",
        rdsp_income_repayment="100",
        other_deductions="100",
    )

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("95026.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1
    assert worksheet.get(SOCIAL_BENEFITS_LINE_6).value == D("95026.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_10).value == D("1600")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_11).value == D("93426.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_14).value == D("500")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_15).value == D("93926.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("583.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_18).value == D("87.45")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == D("87.45")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("87.45")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("87.45")
    assert worksheet.get(NET_INCOME).value == D("94938.55")


def test_line_6_adds_form_t1206_line_4_to_line_23400() -> None:
    # Form T1206 Part 1: "add the amount from line 4 of this form to line 6 of your Federal
    # Worksheet". Employment income 86500 plus OAS 9000 is 95500.00, less the enhanced CPP
    # contributions 1074 and the split income of 500 (T1206 line 4, a part of line 23200),
    # 1574.00, so line 23400 is 93926.00 (over $93,454, so the chart applies). Line 6 is
    # 93926.00 + 500 = 94426.00, and so are lines 11 and 15; line 17 is 94426.00 - 93343.00 =
    # 1083.00 and line 18 is 15% of it, 162.45, under line 5 (9000.00): lines 19, 21 and 23500.
    worksheet = return_as("86500", other_split_income="500")

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("93926.00")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1
    assert worksheet.get(SOCIAL_BENEFITS_LINE_6).value == D("94426.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_11).value == D("94426.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_15).value == D("94426.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("1083.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_18).value == D("162.45")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("162.45")


def test_a_negative_line_23400_is_floored_for_the_net_income_and_the_line_25000_worksheet() -> None:
    # A business loss of 1000 with no income (a T2125 net of -1000 routed to line 13500): line 23400
    # is -1000.00 (shown in brackets). The chart's
    # lines 6, 11 and 15 print no floor, so each is -1000.00, and line 17 is 0; the chart does not
    # apply (nothing on lines 11900, 11300 or 14600), so line 23500 is 0. Line 23600 is
    # -1000.00 less 0, not below zero: 0; the line 25000 worksheet's line 1 is 0, not -1000.00.
    worksheet = compute(
        "0", (), "0", "0", "0", "0", "0", business_statements=(routed_statement("-1000", 1),)
    )

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-1000.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 0
    assert worksheet.get(SOCIAL_BENEFITS_LINE_6).value == D("-1000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_11).value == D("-1000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_15).value == D("-1000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("0")
    assert worksheet.get(NET_INCOME).value == D("0")
    # Form T1206 line 5 takes the amount before the floor, which stays in brackets (negative).
    assert worksheet.get(NET_INCOME_SIGNED).value == D("-1000.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME).value == D("-1000.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO).value == D("0")
    assert worksheet.get(OTHER_PAYMENTS_LIMIT_INCOME).value == D("0")


def test_a_return_with_no_social_benefits_has_a_line_23500_of_0() -> None:
    # Employment income of 200000 alone has no OAS, EI benefits or net federal supplements, so the
    # chart does not apply whatever line 23400 is, and line 23600 is line 23400 itself.
    worksheet = compute("200000", (), "0", "0", "0", "0", "0")

    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 0
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_PAYABLE).value == D("0")
    assert worksheet.get(NET_INCOME).value == worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value


def test_each_line_of_the_chart_is_produced_by_its_capability() -> None:
    # One step for each calculated line: the gate counts the conditions; lines 3, 6, 10, 14, 15
    # and 21 add; line 5 and line 17 subtract not below zero; line 11 subtracts; line 16 is
    # claimed whole; line 18 applies the 15%; line 19 takes the lesser; line 23500 counts line 21
    # once; line 23600 subtracts line 23500 from line 23400, not below zero; line 23400 not below
    # zero is a floored sum of line 23400 alone; line 42200 carries line 23500 over one part.
    worksheet = return_as()

    assert isinstance(worksheet.producer_of(SOCIAL_BENEFITS_REPAYMENT_APPLIES), CountByConditions)
    for kind in (
        OAS_AND_FEDERAL_SUPPLEMENTS,
        SOCIAL_BENEFITS_LINE_6,
        SOCIAL_BENEFITS_LINE_10,
        SOCIAL_BENEFITS_LINE_14,
        SOCIAL_BENEFITS_LINE_15,
        SOCIAL_BENEFITS_LINE_21,
        SOCIAL_BENEFITS_REPAYMENT_PAYABLE,
    ):
        assert isinstance(worksheet.producer_of(kind), Sum), kind.identifier
    for kind in (SOCIAL_BENEFITS_LINE_5, SOCIAL_BENEFITS_LINE_17, NET_INCOME):
        assert isinstance(worksheet.producer_of(kind), SubtractNotBelowZero), kind.identifier
    assert isinstance(worksheet.producer_of(SOCIAL_BENEFITS_LINE_11), Subtract)
    assert isinstance(worksheet.producer_of(NET_INCOME_SIGNED), Subtract)
    assert isinstance(worksheet.producer_of(TOSI_ADJUSTED_NET_INCOME), Sum)
    assert isinstance(worksheet.producer_of(OAS_BENEFITS_BASE_AMOUNT), CreditAmount)
    assert isinstance(worksheet.producer_of(SOCIAL_BENEFITS_LINE_18), ApplyRate)
    assert isinstance(worksheet.producer_of(SOCIAL_BENEFITS_LINE_19), LesserOf)
    assert isinstance(worksheet.producer_of(SOCIAL_BENEFITS_REPAYMENT), TimesCount)
    assert isinstance(
        worksheet.producer_of(NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO), SumNotBelowZero
    )
    assert worksheet.producer_of(SOCIAL_BENEFITS_REPAYMENT_PAYABLE) is not worksheet.producer_of(
        SOCIAL_BENEFITS_REPAYMENT
    )
