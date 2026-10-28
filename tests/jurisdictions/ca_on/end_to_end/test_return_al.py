"""CA-ON 2025 end to end: return al."""

from __future__ import annotations

from typing import Any

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.trace import (
    DividedByRateLine,
    GreaterOfLine,
    RateAppliedLine,
    SubtractedLine,
    SubtractedNotBelowZeroLine,
    SumLine,
    SumNotBelowZeroLine,
)
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    ADVANCED_CANADA_WORKERS_BENEFIT,
    AGE_AMOUNT,
    AGE_AMOUNT_BEFORE_COUNT,
    AGE_INCOME_OVER_THRESHOLD,
    BASIC_PERSONAL_AMOUNT,
    CREDIT_AMOUNTS_SUBTOTAL,
    CREDITS_AGAINST_BASIC_FEDERAL_TAX,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_ON_SPLIT_INCOME,
    FEDERAL_TAX_WITH_SPLIT_INCOME,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5,
    MEDICAL_SUPPLEMENT_LINE_6,
    NET_FEDERAL_TAX,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_INCOME_SIGNED,
    REFUND_OR_BALANCE_OWING,
    SPECIAL_TAXES,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    SPLIT_INCOME_LINE_10,
    SPLIT_INCOME_LINE_13,
    SPLIT_INCOME_LINE_14,
    SPLIT_INCOME_LINE_15,
    SPLIT_INCOME_LINE_18,
    SPLIT_INCOME_LINE_19,
    SPLIT_INCOME_LINE_20,
    SPLIT_INCOME_LINE_21,
    SPLIT_INCOME_LINE_22,
    SPLIT_INCOME_LINE_23,
    SPLIT_INCOME_LINE_24,
    SPLIT_INCOME_LINE_29,
    SPLIT_INCOME_LINE_30,
    TAXABLE_INCOME,
    TOSI_ADJUSTED_NET_INCOME,
    TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO,
    TOSI_ADJUSTED_TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
    TOTAL_SPLIT_INCOME,
    TUITION_INCOME_BASE,
    TUITION_INCOME_LESS_CREDITS,
    TUITION_INCOME_REMAINING,
    TUITION_INCOME_WITH_TOSI,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    LIFT_CREDIT,
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_SURTAX,
    ONTARIO_TAX_AFTER_CREDITS,
    ONTARIO_TAX_AFTER_FOOD_CREDIT,
    ONTARIO_TAX_REDUCTION,
    ONTARIO_TAX_WITH_SURTAX,
    SENIORS_CARE_FAMILY_NET_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, compute, return_a


def return_al(**overrides: Any) -> Worksheet:
    """Return AL's inputs, as in `returns/2025_return_al.yaml`, over the keyword overrides given.

    A single filer, aged 20, whose only income is 10000 of dividends other than eligible dividends
    from a private corporation controlled by a relative, received with no slip: 11500.00 grossed
    up, all of it split income, so Form T1206's lines 1, 2 and 4 are 11500 and line 3 is 0. The
    tax on split income (line 8, T1 line 40424) is 3795.00.
    """
    inputs: dict[str, Any] = {
        "other_dividends_received_without_a_slip": "10000",
        "split_income_dividends": "11500",
        "split_income_dividends_other_than_eligible": "11500",
    }
    inputs.update(overrides)
    return compute("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_al_pays_the_tax_on_split_income_of_3795_on_line_40424() -> None:
    worksheet = return_al()

    # Form T1206 Part 1: line 4 is line 1 plus line 3, all of it a deduction of line 23300 (so the
    # net income is 0.00), and line 6 adds line 5 back: 11500 + 0.00, line 5 being line 23600
    # before its floor (line 23400 less line 23500, which is 0).
    assert worksheet.get(TOTAL_INCOME).value == D("11500.00")
    assert worksheet.get(TOTAL_SPLIT_INCOME).value == D("11500")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("11500.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("0.00")
    assert worksheet.get(NET_INCOME_SIGNED).value == D("0.00")
    assert worksheet.get(NET_INCOME).value == D("0.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME).value == D("11500.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO).value == D("11500.00")
    # Line 8, 11500 x 33% = 3795.00, enters T1 line 121 with the basic tax of 0.00.
    assert worksheet.get(FEDERAL_TAX_ON_SPLIT_INCOME).value == D("3795.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("0.00")
    assert worksheet.get(FEDERAL_TAX_WITH_SPLIT_INCOME).value == D("3795.00")
    # Part 2 lines 9 to 15: no advanced Canada workers benefit and no disability amounts.
    assert worksheet.get(SPLIT_INCOME_LINE_10).value == D("3795.00")
    assert worksheet.get(SPLIT_INCOME_LINE_13).value == D("0")
    assert worksheet.get(SPLIT_INCOME_LINE_14).value == D("0.00")
    assert worksheet.get(SPLIT_INCOME_LINE_15).value == D("3795.00")
    # Lines 16 to 22: line 18 is 11500 less 11500, 0; line 19 is 11500 x 9.0301% = 1038.4615,
    # rounded half-up to the cent, 1038.46; line 22 is 3795.00 - 1038.46 = 2756.54.
    assert worksheet.get(SPLIT_INCOME_LINE_18).value == D("0")
    assert worksheet.get(SPLIT_INCOME_LINE_19).value == D("1038.46")
    assert worksheet.get(SPLIT_INCOME_LINE_20).value == D("0.00")
    assert worksheet.get(SPLIT_INCOME_LINE_21).value == D("1038.46")
    assert worksheet.get(SPLIT_INCOME_LINE_22).value == D("2756.54")
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("2756.54")
    # Line 29 is the T1's federal tax less credits, 3795.00 - (2338.71 + 1038.46) = 417.83, and
    # line 30 is the more of lines 24 and 29, which is line 24 here.
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("417.83")
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == D("417.83")
    assert worksheet.get(SPLIT_INCOME_LINE_30).value == D("2756.54")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("2756.54")
    # The Ontario tax (ON428 line 90) is T1206 line 52, 2017.53, as the health premium is 0: the
    # total payable is 2756.54 + 2017.53 = 4774.07.
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("2017.53")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4774.07")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("4774.07")


def test_return_al_adds_t1206_line_8a_of_26172_41_to_schedule_11_line_11() -> None:
    worksheet = return_al()

    # T1206 Part 2 line 8A "Amount from line 8 ÷ 14.5%": 3795.00 / 0.145 = 26172.4137..., rounded
    # half-up to the cent, 26172.41. "Calculate line 8A and add it to the amount on line 11 of
    # Schedule 11": line 11 is the taxable income, 0.00 (at or below 57375), so the sum is 26172.41.
    assert worksheet.get(TAXABLE_INCOME).value == D("0.00")
    assert worksheet.get(TOSI_ADJUSTED_TAXABLE_INCOME).value == D("26172.41")
    assert worksheet.get(TUITION_INCOME_BASE).value == D("0.00")
    assert worksheet.get(TUITION_INCOME_WITH_TOSI).value == D("26172.41")
    # Line 13 reads that sum: 26172.41 less line 12 (the basic personal amount, 16129.00) is
    # 10043.41, and line 15 is the same as line 14 (the unused tuition from 2024) is 0.
    assert worksheet.get(CREDIT_AMOUNTS_SUBTOTAL).value == D("16129.00")
    assert worksheet.get(TUITION_INCOME_LESS_CREDITS).value == D("10043.41")
    assert worksheet.get(TUITION_INCOME_REMAINING).value == D("10043.41")


def test_return_als_trace_follows_line_8a_into_schedule_11_line_13() -> None:
    worksheet = return_al()
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    for line in (
        "tosi_adjusted_taxable_income: federal_tax_on_split_income 3795 divided by 14.5% "
        "(half-up to 0.01) = 26172.41",
        "tuition_income_with_tosi: tuition_income_base 0 + tosi_adjusted_taxable_income 26172.41 "
        "= 26172.41",
        "tuition_income_less_credits: tuition_income_with_tosi 26172.41 "
        "less credit_amounts_subtotal 16129, not below 0 = 10043.41",
    ):
        assert line in rendered, line


def test_return_al_records_line_8a_and_its_sum_as_structured_lines() -> None:
    trace = return_al().trace

    assert (
        DividedByRateLine(
            TOSI_ADJUSTED_TAXABLE_INCOME,
            FEDERAL_TAX_ON_SPLIT_INCOME,
            D("3795.00"),
            Rate(D("0.145")),
            CENT,
            D("26172.41"),
        )
        in trace
    )
    assert (
        SumLine(
            output=TUITION_INCOME_WITH_TOSI,
            parts=((TUITION_INCOME_BASE, D("0.00")), (TOSI_ADJUSTED_TAXABLE_INCOME, D("26172.41"))),
            total=D("26172.41"),
        )
        in trace
    )
    assert (
        SubtractedNotBelowZeroLine(
            output=TUITION_INCOME_LESS_CREDITS,
            minuend=TUITION_INCOME_WITH_TOSI,
            minuend_amount=D("26172.41"),
            subtrahend=CREDIT_AMOUNTS_SUBTOTAL,
            subtrahend_amount=D("16129.00"),
            result=D("10043.41"),
        )
        in trace
    )


def test_return_als_trace_follows_form_t1206_line_by_line() -> None:
    worksheet = return_al()
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    for line in (
        "total_split_income: split_income_dividends_checked 11500 "
        "+ other_split_income_checked 0 = 11500",
        "net_income_signed: net_income_before_adjustments 0 less social_benefits_repayment 0 = 0",
        "tosi_adjusted_net_income: total_split_income 11500 + net_income_signed 0 = 11500",
        "tosi_adjusted_net_income_not_below_zero: total_split_income 11500 "
        "+ net_income_signed 0, not below 0 = 11500",
        "federal_tax_on_split_income: 33% of total_split_income 11500 (half-up to 0.01)",
        "federal_tax_with_split_income: federal_basic_tax 0 + federal_tax_on_split_income 3795 "
        "= 3795",
        "split_income_line_10: federal_tax_on_split_income 3795 "
        "+ advanced_canada_workers_benefit 0 = 3795",
        "split_income_line_13: disability_amount_for_self 0 + disability_transferred_amount 0 = 0",
        "split_income_line_14: 14.5% of split_income_line_13 0 (half-up to 0.01)",
        "split_income_line_15: split_income_line_10 3795 less split_income_line_14 0 = 3795",
        "split_income_line_18: split_income_dividends_checked 11500 "
        "less split_income_dividends_other_than_eligible_checked 11500, not below 0 = 0",
        "split_income_line_19: 9.0301% of split_income_dividends_other_than_eligible_checked 11500 "
        "(half-up to 0.01)",
        "split_income_line_20: 15.0198% of split_income_line_18 0 (half-up to 0.01)",
        "split_income_line_21: split_income_line_19 1038.46 + split_income_line_20 0 = 1038.46",
        "split_income_line_22: split_income_line_15 3795 less split_income_line_21 1038.46 "
        "= 2756.54",
        "split_income_line_23: federal_foreign_tax_credit 0 "
        "× split_income_from_foreign_sources_checked 0 "
        "/ total_income_from_foreign_sources 0 (half-up to 0.01)",
        "split_income_line_24: split_income_line_22 2756.54 less split_income_line_23 0, "
        "not below 0 = 2756.54",
        "split_income_line_29: federal_tax_line_41700 417.83 "
        "+ advanced_canada_workers_benefit 0 = 417.83",
        "split_income_line_30: greater of split_income_line_24 2756.54 "
        "and split_income_line_29 417.83 = 2756.54",
        "net_federal_tax: split_income_line_30 2756.54 + special_taxes 0 = 2756.54",
        "federal_tax_after_credits: federal_tax_with_split_income 3795 "
        "less credits_against_basic_federal_tax 3377.17, not below 0 = 417.83",
        "basic_personal_amount: 14538 plus 1591 less 0 for "
        "tosi_adjusted_net_income_not_below_zero 11500 over 177882 (range 75532), "
        "not below 14538 (half-up to 0.01)",
        "cwb_family_net_income_line_10: tosi_adjusted_net_income 11500 + "
        "uccb_and_rdsp_income_repayments 0 + cwb_tax_exempt_net_income 0 = 11500",
        "cwb_family_net_income_line_12: cwb_family_net_income_line_10 11500 "
        "less uccb_and_rdsp_income 0, not below 0 = 11500",
        "cwb_family_net_income_line_13: cwb_family_net_income_line_12 11500 + "
        "cwb_spouse_family_net_income_line_12 0 = 11500",
        "adjusted_family_net_income: cwb_family_net_income_line_13 11500 less "
        "cwb_secondary_earner_exemption 0 = 11500",
    ):
        assert line in rendered, line


def test_return_als_trace_records_the_split_income_lines_as_structured_lines() -> None:
    trace = return_al().trace

    assert (
        RateAppliedLine(
            FEDERAL_TAX_ON_SPLIT_INCOME,
            TOTAL_SPLIT_INCOME,
            D("11500"),
            Rate(D("0.33")),
            CENT,
            D("3795.00"),
        )
        in trace
    )
    assert (
        RateAppliedLine(
            SPLIT_INCOME_LINE_19,
            SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
            D("11500"),
            Rate(D("0.090301")),
            CENT,
            D("1038.46"),
        )
        in trace
    )
    assert (
        SubtractedLine(
            output=SPLIT_INCOME_LINE_22,
            minuend=SPLIT_INCOME_LINE_15,
            minuend_amount=D("3795.00"),
            subtrahend=SPLIT_INCOME_LINE_21,
            subtrahend_amount=D("1038.46"),
            result=D("2756.54"),
        )
        in trace
    )
    assert (
        SubtractedNotBelowZeroLine(
            output=SPLIT_INCOME_LINE_24,
            minuend=SPLIT_INCOME_LINE_22,
            minuend_amount=D("2756.54"),
            subtrahend=SPLIT_INCOME_LINE_23,
            subtrahend_amount=D("0.00"),
            result=D("2756.54"),
        )
        in trace
    )
    assert (
        GreaterOfLine(
            output=SPLIT_INCOME_LINE_30,
            parts=((SPLIT_INCOME_LINE_24, D("2756.54")), (SPLIT_INCOME_LINE_29, D("417.83"))),
            result=D("2756.54"),
        )
        in trace
    )
    assert (
        SumNotBelowZeroLine(
            output=TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO,
            parts=((TOTAL_SPLIT_INCOME, D("11500")), (NET_INCOME_SIGNED, D("0.00"))),
            total=D("11500.00"),
        )
        in trace
    )
    assert (
        SubtractedNotBelowZeroLine(
            output=FEDERAL_TAX_AFTER_CREDITS,
            minuend=FEDERAL_TAX_WITH_SPLIT_INCOME,
            minuend_amount=D("3795.00"),
            subtrahend=CREDITS_AGAINST_BASIC_FEDERAL_TAX,
            subtrahend_amount=D("3377.17"),
            result=D("417.83"),
        )
        in trace
    )


def return_b_with_split_income_dividends(**overrides: Any) -> Worksheet:
    """Return B's filer (employment income of 30000, tax deducted 3000) with split income.

    Dividends of 1000 with no slip, all split income: grossed up by 115% to 1150, the Form T1206
    lines 1, 2 and 4 being 1150. The disability amount of line 31600, a chosen 10138 (the figure
    asked for line 31600 for 2025), is larger than the tax on split income of 379.50.
    """
    inputs: dict[str, Any] = {
        "income_tax_deducted": "3000",
        "other_dividends_received_without_a_slip": "1000",
        "split_income_dividends": "1150",
        "split_income_dividends_other_than_eligible": "1150",
        "eligible_for_disability_amount": 1,
        "under_18_on_december_31": 0,
    }
    inputs.update(overrides)
    return compute("30000", (), "0", "0", "5400", "0", "0", **inputs)


def test_a_disability_amount_larger_than_the_tax_leaves_line_22_negative_and_line_24_at_zero() -> (
    None
):
    worksheet = return_b_with_split_income_dividends()

    # Line 8 is 1150 x 33% = 379.50 and line 10 the same (no advanced Canada workers benefit).
    assert worksheet.get(TOTAL_SPLIT_INCOME).value == D("1150")
    assert worksheet.get(FEDERAL_TAX_ON_SPLIT_INCOME).value == D("379.50")
    assert worksheet.get(SPLIT_INCOME_LINE_10).value == D("379.50")
    # Line 13 is 10138 + 0 and line 14 is 14.5% of it, 1470.01 (exactly); line 15, which prints no
    # floor, is 379.50 - 1470.01 = -1090.51.
    assert worksheet.get(SPLIT_INCOME_LINE_13).value == D("10138")
    assert worksheet.get(SPLIT_INCOME_LINE_14).value == D("1470.01")
    assert worksheet.get(SPLIT_INCOME_LINE_15).value == D("-1090.51")
    # Line 19 is 1150 x 9.0301% = 103.84615, rounded half-up to the cent, 103.85; line 18 is 0.
    assert worksheet.get(SPLIT_INCOME_LINE_19).value == D("103.85")
    assert worksheet.get(SPLIT_INCOME_LINE_21).value == D("103.85")
    # Line 22 is -1090.51 - 103.85 = -1194.36, and line 24 takes 0 for a negative line 22.
    assert worksheet.get(SPLIT_INCOME_LINE_22).value == D("-1194.36")
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("0")
    # Line 29: the T1 tax of line 121, 4311.58 + 379.50 = 4691.08, less the credits of
    # 2813.54 + 1470.01 + 103.85 = 4387.40 (the federal dividend tax credit, line 40425, counts the
    # same 1150), is 303.68; the more of 0 and 303.68 is line 29, which is not floored at line 24.
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4311.58")
    assert worksheet.get(FEDERAL_TAX_WITH_SPLIT_INCOME).value == D("4691.08")
    assert worksheet.get(CREDITS_AGAINST_BASIC_FEDERAL_TAX).value == D("4387.40")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("303.68")
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == D("303.68")
    assert worksheet.get(SPLIT_INCOME_LINE_30).value == D("303.68")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("303.68")


def test_a_negative_line_22_is_recorded_signed_and_floored_by_line_24() -> None:
    trace = return_b_with_split_income_dividends().trace

    assert (
        SubtractedLine(
            output=SPLIT_INCOME_LINE_22,
            minuend=SPLIT_INCOME_LINE_15,
            minuend_amount=D("-1090.51"),
            subtrahend=SPLIT_INCOME_LINE_21,
            subtrahend_amount=D("103.85"),
            result=D("-1194.36"),
        )
        in trace
    )
    assert (
        SubtractedNotBelowZeroLine(
            output=SPLIT_INCOME_LINE_24,
            minuend=SPLIT_INCOME_LINE_22,
            minuend_amount=D("-1194.36"),
            subtrahend=SPLIT_INCOME_LINE_23,
            subtrahend_amount=D("0.00"),
            result=D("0"),
        )
        in trace
    )
    assert (
        GreaterOfLine(
            output=SPLIT_INCOME_LINE_30,
            parts=((SPLIT_INCOME_LINE_24, D("0")), (SPLIT_INCOME_LINE_29, D("303.68"))),
            result=D("303.68"),
        )
        in trace
    )
    rendered = EnglishTraceRenderer().render_all(trace)
    assert (
        "split_income_line_22: split_income_line_15 -1090.51 less split_income_line_21 103.85 "
        "= -1194.36"
    ) in rendered
    assert (
        "split_income_line_24: split_income_line_22 -1194.36 less split_income_line_23 0, "
        "not below 0 = 0"
    ) in rendered


def test_a_negative_tosi_adjusted_net_income_is_zero_in_the_twin_and_negative_on_line_45200() -> (
    None
):
    # 1150 of split income (1000 of dividends grossed up) is the only income; the other deductions
    # of 5000 (line 23200) are larger than it: line 23300 is 5000 + 1150 = 6150, line 23400 is
    # 1150 - 6150 = -5000.00 and the net income (line 23600) is 0. Form T1206 line 5 "Net income
    # from line 23600 of your tax return (or the amount you would have entered if the instructions
    # on line 23600 read "if negative, show in brackets")" is the signed -5000.00 (line 23400 less
    # line 23500, which is 0), so line 6 is 1150 + (-5000.00) = -3850.00.
    worksheet = compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_dividends_received_without_a_slip="1000",
        split_income_dividends="1150",
        split_income_dividends_other_than_eligible="1150",
        other_deductions="5000",
    )

    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("6150")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-5000.00")
    assert worksheet.get(NET_INCOME_SIGNED).value == D("-5000.00")
    assert worksheet.get(NET_INCOME).value == D("0")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME).value == D("-3850.00")
    # "(If the TOSI-adjusted net income at line 6 is negative, use the negative value when it is
    # part of an adjusted net income calculation, otherwise use zero.)"
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO).value == D("0")
    assert worksheet.get(BASIC_PERSONAL_AMOUNT).value == D("16129.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("0")
    # Line 45200 column 1: line 3 reads the signed line 6, line 5 takes 0 for a negative line 3.
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3).value == D("-3850.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_6).value == D("0")
    trace = worksheet.trace
    assert (
        SumLine(
            output=TOSI_ADJUSTED_NET_INCOME,
            parts=((TOTAL_SPLIT_INCOME, D("1150")), (NET_INCOME_SIGNED, D("-5000.00"))),
            total=D("-3850.00"),
        )
        in trace
    )
    assert (
        SumNotBelowZeroLine(
            output=TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO,
            parts=((TOTAL_SPLIT_INCOME, D("1150")), (NET_INCOME_SIGNED, D("-5000.00"))),
            total=D("0"),
        )
        in trace
    )


def test_line_23200_other_deductions_and_the_total_split_income_are_both_in_line_23300() -> None:
    # Other deductions of 300 and the split income of 11500: line 23300 is 11800 (line 23200 and
    # Form T1206 line 4), line 23400 is 11500.00 - 11800 = -300.00, and line 6 is
    # 11500 + (-300.00) = 11200.00.
    worksheet = return_al(other_deductions="300")

    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("11800")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-300.00")
    assert worksheet.get(NET_INCOME_SIGNED).value == D("-300.00")
    assert worksheet.get(NET_INCOME).value == D("0")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME).value == D("11200.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO).value == D("11200.00")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("11200.00")


def test_split_income_over_the_threshold_tapers_the_basic_amount_and_ends_the_age_amount() -> None:
    # Other income of 200000, all of it split income (a chosen figure): line 23300 is 200000, the
    # net income is 0.00, and the TOSI-adjusted net income is 200000.00. The basic personal amount
    # is 14538 + 1591 less 1591 x (200000 - 177882) / 75532 = 465.89..., 15663.11 rounded half-up
    # to the cent, where the net income of 0.00 would give the full 16129.00. A filer born in 1960
    # or earlier: line 4 of the Federal Worksheet is 200000.00 - 45522.00 = 154478.00, the age
    # reduction 15% of it, 23171.70, is more than the 9028.00, so the age amount is 0.
    worksheet = return_al(
        other_dividends_received_without_a_slip="0",
        other_income="200000",
        split_income_dividends="0",
        split_income_dividends_other_than_eligible="0",
        other_split_income="200000",
        born_in_1960_or_earlier=1,
    )

    assert worksheet.get(NET_INCOME).value == D("0.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO).value == D("200000.00")
    assert worksheet.get(BASIC_PERSONAL_AMOUNT).value == D("15663.11")
    assert worksheet.get(AGE_INCOME_OVER_THRESHOLD).value == D("154478.00")
    assert worksheet.get(AGE_AMOUNT_BEFORE_COUNT).value == D("0")
    assert worksheet.get(AGE_AMOUNT).value == D("0")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("200000.00")
    # Line 4 is all the split income: line 8 is 200000 x 33% = 66000.00 and line 24 the same, as
    # nothing is claimed against it (lines 13 and 19 are 0).
    assert worksheet.get(TOTAL_SPLIT_INCOME).value == D("200000")
    assert worksheet.get(FEDERAL_TAX_ON_SPLIT_INCOME).value == D("66000.00")
    assert worksheet.get(SPLIT_INCOME_LINE_22).value == D("66000.00")
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("66000.00")


def test_advance_payments_are_not_charged_back_when_the_benefit_is_zero() -> None:
    # Return AL has no working income, so the benefit (line 28) is 0 and Schedule 6 line 49, the
    # lesser of line 43 (0) and line 48 (200), is 0: lines 10 and 29 of Form T1206 are unchanged.
    worksheet = return_al(acwb_paid_to_you="200")

    assert worksheet.get(ADVANCED_CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(SPLIT_INCOME_LINE_10).value == D("3795.00")
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == D("417.83")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("2756.54")


def test_the_special_taxes_of_line_41800_are_added_to_line_30_of_form_t1206() -> None:
    # Return AL with 7 from the RL-10 slip on line 41800: 2756.54 + 7 = 2763.54, and with the
    # Ontario tax of 2017.53 the total payable is 4781.07.
    worksheet = return_al(rl_10_labour_sponsored_fund_amount="7")

    assert worksheet.get(SPECIAL_TAXES).value == D("7")
    assert worksheet.get(SPLIT_INCOME_LINE_30).value == D("2756.54")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("2763.54")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4781.07")


def test_without_split_income_the_net_federal_tax_is_line_29_and_line_24_is_zero() -> None:
    worksheet = return_a()

    assert worksheet.get(TOTAL_SPLIT_INCOME).value == D("0")
    assert worksheet.get(FEDERAL_TAX_ON_SPLIT_INCOME).value == D("0.00")
    assert worksheet.get(TOSI_ADJUSTED_NET_INCOME).value == worksheet.get(NET_INCOME).value
    assert (
        worksheet.get(FEDERAL_TAX_WITH_SPLIT_INCOME).value == worksheet.get(FEDERAL_BASIC_TAX).value
    )
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("0")
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == D("16951.38")
    assert worksheet.get(SPLIT_INCOME_LINE_30).value == D("16951.38")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("16951.38")


def test_return_al_pays_the_ontario_tax_on_split_income_on_form_t1206_part_3() -> None:
    worksheet = return_al()

    # Line 33 (ON428 line 54, line 61510) is 20.53% of the total split income: 11500 x 20.53% =
    # 2360.95. Lines 34 and 35 are 0, so lines 36 and 38 are 0 and line 39 is 2360.95.
    assert worksheet.get(ontario.ONTARIO_TAX_ON_SPLIT_INCOME).value == D("2360.95")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_36).value == D("0")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_38).value == D("0.00")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_39).value == D("2360.95")
    # Line 42 is 10% of line 18 (0.00); line 45 is 2.9863% of the 11500 of line 2 = 343.4245,
    # rounded half-up to the cent: 343.42. Line 47 is 2360.95 - 343.42 = 2017.53, which line 50
    # carries (line 49 is not wired).
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_42).value == D("0.00")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_45).value == D("343.42")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_46).value == D("343.42")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_47).value == D("2017.53")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_50).value == D("2017.53")
    # ON428 line 55 is line 53 (0) plus line 54; line 64 is line 54, so the surtax base (line 65)
    # is 0 and the surtax is 0; line 69 is 2360.95, less the dividend tax credit of 343.42 (line
    # 70): 2017.53, which is more than twice the basic reduction (588), so the reduction is 0.
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SPLIT_INCOME).value == D("2360.95")
    # No minimum tax carryover is applied (line 59 is 24.63% of 0.00), so line 60 is 0 and line 61
    # is line 55, 2360.95, which lines 62 and 63 carry.
    assert worksheet.get(ontario.MINIMUM_TAX_CARRYOVER_CREDIT).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER).value == D("2360.95")
    assert worksheet.get(ontario.ONTARIO_TAX_ON_SPLIT_INCOME_FOR_SURTAX).value == D("2360.95")
    assert worksheet.get(ontario.ONTARIO_SURTAX_BASE).value == D("0")
    assert worksheet.get(ONTARIO_SURTAX).value == D("0")
    assert worksheet.get(ONTARIO_TAX_WITH_SURTAX).value == D("2360.95")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("2017.53")
    assert worksheet.get(ONTARIO_TAX_REDUCTION).value == D("0")
    assert worksheet.get(ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("2017.53")
    # Line 52 is the more of line 50 and line 51 (ON428 line 88), equal here; the health premium
    # chart's line 1 is the taxable income 0.00 plus the total split income (T1206 line 4).
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_52).value == D("2017.53")
    assert worksheet.get(ontario.HEALTH_PREMIUM_INCOME).value == D("11500.00")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("0")
    # The seniors care family net income (ON479 line 8) and the LIFT (ON428-A line 6) start from
    # the TOSI-adjusted net income, 11500.00, not the net income of 0.00.
    assert worksheet.get(SENIORS_CARE_FAMILY_NET_INCOME).value == D("11500.00")
    assert worksheet.get(ontario.LIFT_NET_INCOME_AND_REPAYMENTS).value == D("11500.00")


def test_return_al_divides_t1206_line_33a_by_the_5_05_percent_of_line_33b_into_line_33c() -> None:
    worksheet = return_al()

    # Line 33C "Amount from line 33A divided by the tax rate you entered on line 33B": line 33A is
    # line 33, 2360.95, and line 33B is Chart C column 3 for Ontario, 5.05%: 2360.95 / 0.0505 =
    # 46751.4851..., rounded half-up to the cent: 46751.49. Nothing reads it; it is an output.
    assert worksheet.get(ontario.TOSI_ADJUSTED_TAXABLE_INCOME).value == D("46751.49")
    assert (
        "tosi_adjusted_taxable_income: ontario_tax_on_split_income 2360.95 divided by 5.05% "
        "(half-up to 0.01) = 46751.49"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        DividedByRateLine(
            ontario.TOSI_ADJUSTED_TAXABLE_INCOME,
            ontario.ONTARIO_TAX_ON_SPLIT_INCOME,
            D("2360.95"),
            Rate(D("0.0505")),
            CENT,
            D("46751.49"),
        )
        in worksheet.trace
    )


def test_return_als_trace_follows_form_t1206_part_3_line_by_line() -> None:
    rendered = EnglishTraceRenderer().render_all(return_al().trace)

    for line in (
        "ontario_tax_on_split_income: 20.53% of total_split_income 11500 (half-up to 0.01)",
        "split_income_line_36: disability_amount_for_self 0 + disability_transferred_amount 0 = 0",
        "split_income_line_38: 5.05% of split_income_line_36 0 (half-up to 0.01)",
        "split_income_line_39: ontario_tax_on_split_income 2360.95 less split_income_line_38 0 "
        "= 2360.95",
        "split_income_line_42: 10% of split_income_line_18 0 (half-up to 0.01)",
        "split_income_line_45: 2.9863% of split_income_dividends_other_than_eligible_checked 11500 "
        "(half-up to 0.01)",
        "split_income_line_46: split_income_line_42 0 + split_income_line_45 343.42 = 343.42",
        "split_income_line_47: split_income_line_39 2360.95 less split_income_line_46 343.42 "
        "= 2017.53",
        "split_income_line_49: provincial_foreign_tax_credit 0 "
        "× split_income_non_business_from_foreign_sources_checked 0 "
        "/ total_non_business_income_from_foreign_sources_checked 0 (half-up to 0.01)",
        "split_income_line_50: split_income_line_47 2017.53 less split_income_line_49 0 = 2017.53",
        "ontario_tax_with_split_income: ontario_tax_after_credits 0 "
        "+ ontario_tax_on_split_income 2360.95 = 2360.95",
        "ontario_tax_on_split_income_for_surtax: ontario_tax_on_split_income 2360.95 = 2360.95",
        "ontario_minimum_tax_carryover_applied: lesser of ontario_tax_less_dividend_credit 0 "
        "and minimum_tax_carryover_credit 0 = 0",
        "ontario_tax_after_minimum_tax_carryover: ontario_tax_with_split_income 2360.95 "
        "less ontario_minimum_tax_carryover_applied 0, not below 0 = 2360.95",
        "ontario_surtax_base: ontario_tax_after_minimum_tax_carryover 2360.95 "
        "less ontario_tax_on_split_income_for_surtax 2360.95, not below 0 = 0",
        "ontario_tax_with_surtax: ontario_tax_after_minimum_tax_carryover 2360.95 "
        "+ ontario_surtax 0 "
        "= 2360.95",
        "split_income_line_52: greater of split_income_line_50 2017.53 "
        "and ontario_tax_after_food_credit 2017.53 = 2017.53",
        "health_premium_income: taxable_income 0 + total_split_income 11500 = 11500",
        "ontario_tax: split_income_line_52 2017.53 + ontario_health_premium 0 = 2017.53",
    ):
        assert line in rendered, line


def test_return_al_records_the_ontario_split_income_lines_as_structured_lines() -> None:
    trace = return_al().trace

    assert (
        RateAppliedLine(
            ontario.ONTARIO_TAX_ON_SPLIT_INCOME,
            TOTAL_SPLIT_INCOME,
            D("11500"),
            Rate(D("0.2053")),
            CENT,
            D("2360.95"),
        )
        in trace
    )
    assert (
        RateAppliedLine(
            ontario.SPLIT_INCOME_LINE_45,
            SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
            D("11500"),
            Rate(D("0.029863")),
            CENT,
            D("343.42"),
        )
        in trace
    )
    assert (
        SubtractedLine(
            output=ontario.SPLIT_INCOME_LINE_47,
            minuend=ontario.SPLIT_INCOME_LINE_39,
            minuend_amount=D("2360.95"),
            subtrahend=ontario.SPLIT_INCOME_LINE_46,
            subtrahend_amount=D("343.42"),
            result=D("2017.53"),
        )
        in trace
    )
    assert (
        SubtractedNotBelowZeroLine(
            output=ontario.ONTARIO_SURTAX_BASE,
            minuend=ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER,
            minuend_amount=D("2360.95"),
            subtrahend=ontario.ONTARIO_TAX_ON_SPLIT_INCOME_FOR_SURTAX,
            subtrahend_amount=D("2360.95"),
            result=D("0"),
        )
        in trace
    )
    assert (
        GreaterOfLine(
            output=ontario.SPLIT_INCOME_LINE_52,
            parts=(
                (ontario.SPLIT_INCOME_LINE_50, D("2017.53")),
                (ONTARIO_TAX_AFTER_FOOD_CREDIT, D("2017.53")),
            ),
            result=D("2017.53"),
        )
        in trace
    )


def test_an_ontario_disability_credit_above_the_tax_leaves_line_88_as_line_52() -> None:
    # Return B's filer (employment income 30000) with 1000 of split dividends (1150 grossed up) and
    # the Ontario disability amount of ON428 line 58440, a chosen 10298. Line 33 is 1150 x 20.53%
    # = 236.095, rounded half-up to the cent: 236.10. Line 36 is 10298 + 0 and line 38 is 5.05% of
    # it, 520.049, 520.05, so line 39 is 236.10 - 520.05 = -283.95, negative and not floored. Line
    # 45 is 2.9863% x 1150 = 34.34245, 34.34 (line 42 is 0), so line 47 is -283.95 - 34.34 =
    # -318.29, which line 50 carries.
    worksheet = return_b_with_split_income_dividends()

    assert worksheet.get(ontario.ONTARIO_TAX_ON_SPLIT_INCOME).value == D("236.10")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_36).value == D("10298")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_38).value == D("520.05")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_39).value == D("-283.95")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_42).value == D("0.00")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_45).value == D("34.34")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_46).value == D("34.34")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_47).value == D("-318.29")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_50).value == D("-318.29")
    # Line 53 is 246.76 (766.81 less the 520.05 of line 38 comes off through the credit amounts) and
    # line 55 is 246.76 + 236.10 = 482.86, no surtax (the base, line 65, is 246.76); less the
    # dividend tax credit of 34.34: 448.52, no reduction; the LIFT credit of 875 (the TOSI-adjusted
    # net income, 29735.00 + 1150 = 30885.00, is under 32500) leaves 0 on line 88. Line 52 is the
    # more of -318.29 and 0: line 88.
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SPLIT_INCOME).value == D("482.86")
    assert worksheet.get(ontario.ONTARIO_SURTAX_BASE).value == D("246.76")
    assert worksheet.get(ONTARIO_SURTAX).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("448.52")
    assert worksheet.get(LIFT_CREDIT).value == D("875")
    assert worksheet.get(ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("0")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_52).value == D("0")
    # The health premium chart's line 1 is the taxable income 29735.00 plus line 4 (1150): 30885.
    assert worksheet.get(ontario.HEALTH_PREMIUM_INCOME).value == D("30885.00")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("300")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("300")

    trace = worksheet.trace
    assert (
        SubtractedLine(
            output=ontario.SPLIT_INCOME_LINE_47,
            minuend=ontario.SPLIT_INCOME_LINE_39,
            minuend_amount=D("-283.95"),
            subtrahend=ontario.SPLIT_INCOME_LINE_46,
            subtrahend_amount=D("34.34"),
            result=D("-318.29"),
        )
        in trace
    )
    assert (
        GreaterOfLine(
            output=ontario.SPLIT_INCOME_LINE_52,
            parts=(
                (ontario.SPLIT_INCOME_LINE_50, D("-318.29")),
                (ONTARIO_TAX_AFTER_FOOD_CREDIT, D("0")),
            ),
            result=D("0"),
        )
        in trace
    )
    rendered = EnglishTraceRenderer().render_all(trace)
    assert (
        "split_income_line_39: ontario_tax_on_split_income 236.1 less split_income_line_38 520.05 "
        "= -283.95"
    ) in rendered
    assert (
        "split_income_line_52: greater of split_income_line_50 -318.29 "
        "and ontario_tax_after_food_credit 0 = 0"
    ) in rendered


def test_the_ontario_surtax_applies_to_the_non_split_part_of_the_tax_only() -> None:
    # Return A with 20000 more of income, all of it split income (a chosen figure): the net income
    # and the taxable income stay 115000.00, so the Ontario tax after credits (line 53) is
    # 7671.98. Line 54 is 20000 x 20.53% = 4106.00 and line 55 is 11777.98, but line 64 takes line
    # 54 off again, so the surtax base (line 65) is 7671.98 and the surtax is the 523.79 of Return
    # A alone (20% of 1961.98 and 36% of 364.98), not that on 11777.98.
    worksheet = compute(
        "110000",
        (("20000", "0", "0"),),
        "0",
        "1926",
        "19800",
        "1926",
        "2000",
        income_tax_deducted="25000",
        other_income="20000",
        other_split_income="20000",
    )

    assert worksheet.get(TAXABLE_INCOME).value == D("115000.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("7671.98")
    assert worksheet.get(ontario.ONTARIO_TAX_ON_SPLIT_INCOME).value == D("4106.00")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SPLIT_INCOME).value == D("11777.98")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER).value == D("11777.98")
    assert worksheet.get(ontario.ONTARIO_TAX_ON_SPLIT_INCOME_FOR_SURTAX).value == D("4106.00")
    assert worksheet.get(ontario.ONTARIO_SURTAX_BASE).value == D("7671.98")
    assert worksheet.get(ONTARIO_SURTAX).value == D("523.79")
    # Line 69 is line 62 (11777.98) plus the surtax: 12301.77; no credit, reduction or LIFT credit
    # (the TOSI-adjusted net income, 135000, is far over the LIFT thresholds) comes off, so line
    # 88 is 12301.77, which is more than line 50 (4106.00), so line 52 is line 88; the health
    # premium chart's line 1 is 115000.00 + 20000 = 135000.00: 750.
    assert worksheet.get(ONTARIO_TAX_WITH_SURTAX).value == D("12301.77")
    assert worksheet.get(ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("12301.77")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_50).value == D("4106.00")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_52).value == D("12301.77")
    assert worksheet.get(ontario.HEALTH_PREMIUM_INCOME).value == D("135000.00")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("750")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("13051.77")


def test_the_health_premium_chart_starts_from_the_taxable_income_plus_t1206_line_4() -> None:
    # Return AL with 30000 of other income, all of it split income: the taxable income is 0.00 but
    # line 4 of Form T1206 is 30000, so the chart's line 1 is 30000, in the row of more than 25000
    # but not more than 36000: 300, where the taxable income alone (0.00) would give 0.
    worksheet = return_al(
        other_dividends_received_without_a_slip="0",
        other_income="30000",
        split_income_dividends="0",
        split_income_dividends_other_than_eligible="0",
        other_split_income="30000",
    )

    assert worksheet.get(TAXABLE_INCOME).value == D("0")
    assert worksheet.get(TOTAL_SPLIT_INCOME).value == D("30000")
    assert worksheet.get(ontario.HEALTH_PREMIUM_INCOME).value == D("30000")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("300")
    # Line 33 is 30000 x 20.53% = 6159.00, line 47 and line 50 the same (no credits, no dividends),
    # and line 88 the same (the surtax base is 0, no dividend credit, no reduction as 588.00 is
    # less than 6159.00, no LIFT credit with no employment income), so line 52 is 6159.00 and the
    # Ontario tax is 6159.00 + 300 = 6459.00.
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_50).value == D("6159.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("6159.00")
    assert worksheet.get(ontario.SPLIT_INCOME_LINE_52).value == D("6159.00")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("6459.00")
