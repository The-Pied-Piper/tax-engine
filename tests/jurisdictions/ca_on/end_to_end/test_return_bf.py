"""CA-ON 2025 end to end: return bf (Form T657, line 25400)."""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.jurisdictions.ca.catalog import (
    ABIL_AFTER_QBT_REDUCTION,
    ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2000,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
    ADJUSTED_LOSSES_APPLIED_1990_TO_1999,
    ADJUSTED_LOSSES_APPLIED_2000,
    ADJUSTED_LOSSES_APPLIED_2001_TO_2024,
    ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999,
    ADJUSTED_LOSSES_LEFT_AFTER_2000,
    ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    ANNUAL_GAINS_LIMIT_2025,
    ANNUAL_GAINS_LINE_3,
    ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE,
    ANNUAL_GAINS_LINE_5,
    ANNUAL_GAINS_LINE_7,
    ANNUAL_GAINS_LINE_9,
    ANNUAL_GAINS_LINE_10,
    ANNUAL_GAINS_LINE_12,
    ANNUAL_GAINS_SCHEDULE_3_TOTAL,
    CAPITAL_GAINS_DEDUCTION,
    CHART_1_COLUMN_G_TOTAL,
    CHART_2_LINE_3,
    CHART_2_LINE_4,
    CHART_2_LINE_5,
    CHART_2_LINE_7,
    CHART_2_LINE_8,
    CHART_2_LINE_9,
    CHART_2_LINE_11,
    CHART_2_LINE_12,
    CHART_2_LINE_13,
    CHART_2_LINE_14_OVER_TWICE_IR,
    CHART_2_LINE_15,
    CHART_2_LINE_16,
    CHART_2_LINE_17,
    CHART_2_LINE_19,
    CHART_2_TWICE_IR,
    CHART_2025_PART_1_AMOUNT_C,
    CHART_2025_PART_1_AMOUNT_E,
    CHART_2025_PART_1_AMOUNT_K,
    CHART_2025_PART_1_AMOUNT_M,
    CHART_2025_PART_1_AMOUNT_N,
    CHART_2025_PART_1_AMOUNT_P,
    CHART_2025_PART_1_AMOUNT_Q,
    CHART_2025_PART_1_AMOUNTS_F_TO_J,
    CHART_2025_PART_2_AMOUNT_C,
    CHART_2025_PART_2_AMOUNT_E,
    CHART_2025_PART_2_AMOUNT_F,
    CHART_2025_PART_2_AMOUNT_K,
    CHART_2025_PART_2_AMOUNT_M,
    CHART_2025_PART_2_AMOUNT_N,
    CHART_2025_PART_2_AMOUNT_P,
    CHART_2025_PART_2_AMOUNT_Q,
    CHART_2025_PART_2_AMOUNTS_F_TO_J,
    CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
    CUMULATIVE_GAINS_LIMIT_2025,
    CUMULATIVE_LOSSES_AND_DEDUCTIONS,
    DEDUCTIONS_FROM_NET_INCOME,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025,
    INCLUDED_CAPITAL_GAIN,
    NET_CAPITAL_LOSS_BALANCE_2000,
    NET_CAPITAL_LOSS_BALANCE_2001_TO_2024,
    NET_CAPITAL_LOSS_TWICE_IR_2000,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NET_INCOME,
    QBT_ABIL_REDUCTION,
    QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    REMAINING_ADJUSTED_LOSSES_2000,
    REMAINING_ADJUSTED_LOSSES_2001_TO_2024,
    SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO,
    SCHEDULE_3_LINE_19900,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES,
    TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    compute,
    return_be,
    return_bf,
    t657_chart_1_row,
)


def test_step_1_gives_an_annual_gains_limit_of_155000() -> None:
    # Line 1 is line 10700 (350000.00) + 0 + 0 = 350000.00; line 2 (T2017) is 0, so line 3 is
    # 350000.00. Line 4 is 1/2, so line 5 is 175000.00; line 6 (T2048 line 17216) is 0, so line 7
    # is 175000.00. Line 8 (line 19900) is the included gain, 175000.00, and line 9 (line 17600 x
    # 1/2) is 0, so line 10 is 175000.00; line 11 (T2048 line 17215) is 0, so line 12 is
    # 175000.00. Line 13 is the lesser of line 7 and line 12: 175000.00. Line 14 is 20000 (line
    # 25300); line 15 (T936) is 0, so line 16 is 20000; line 17 (line 21700) and line 18 (T2048
    # line 17217) are 0, so line 19 is 0. Line 20 is 20000 + 0 = 20000 and line 21 is 175000.00 -
    # 20000 = 155000.00.
    worksheet = return_bf()

    assert worksheet.get(ANNUAL_GAINS_SCHEDULE_3_TOTAL).value == D("350000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_3).value == D("350000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE).value == D("175000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_5).value == D("175000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_7).value == D("175000.00")
    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("175000.00")
    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("175000.00")
    assert worksheet.get(SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO).value == D("0")
    assert worksheet.get(ANNUAL_GAINS_LINE_9).value == D("0")
    assert worksheet.get(ANNUAL_GAINS_LINE_10).value == D("175000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_12).value == D("175000.00")
    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025).value == D("175000.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("20000")
    assert worksheet.get(ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("20000")
    assert worksheet.get(ABIL_AFTER_QBT_REDUCTION).value == D("0")
    assert worksheet.get(TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT).value == D("20000")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("155000.00")


def test_step_2_gives_a_cumulative_gains_limit_of_255000() -> None:
    # Line 8 is 100000 (2002 to 2024) + 175000.00 (Step 1 line 13) = 275000.00 and line 9 adds
    # lines 1 to 7, all 0: 275000.00. Line 13 is 0 - 0 (no ABIL claimed) and line 14 is 0 (Chart
    # 1 has no rows); line 15 is 20000 (Step 1 line 20) and lines 10, 16 and 17 are 0, so line 18
    # is 20000. Line 19 is 275000.00 - 20000 = 255000.00.
    worksheet = return_bf()

    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025).value == D("275000.00")
    assert worksheet.get(CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS).value == D("275000.00")
    assert worksheet.get(ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025).value == D("0")
    assert worksheet.get(CHART_1_COLUMN_G_TOTAL).value == D("0")
    assert worksheet.get(CUMULATIVE_LOSSES_AND_DEDUCTIONS).value == D("20000")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("255000.00")


def test_step_1_line_21_limits_amount_q_and_the_claim_is_155000() -> None:
    # Part 2: A is 625000; B is Part 1's P, 0, so C is 625000; D (Chart 2 line 19) is 0, so E is
    # 625000. F is line 10700 less the excluded slip amounts (none): 350000; G, H, I and J are 0,
    # so F to J add to 350000 and K is 1/2 of it, 175000.00. L is 0, so M is 175000.00; N is the
    # lesser of E and M, 175000.00; O is B, 0, so P is 175000.00. Q is the lesser of line 21 of
    # Step 1 (155000.00), line 19 of Step 2 (255000.00) and P (175000.00): 155000.00, line 21.
    # The filer claims all of it. Line 25700 adds line 25300 (20000) and line 25400 (155000):
    # 175000; net income is 185000.00 (other income 10000 + taxable capital gains 175000.00), so
    # taxable income is 185000.00 - 175000 = 10000.00.
    worksheet = return_bf()

    assert worksheet.get(CHART_2_LINE_19).value == D("0")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_C).value == D("625000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_E).value == D("625000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_F).value == D("350000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNTS_F_TO_J).value == D("350000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_K).value == D("175000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_M).value == D("175000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_N).value == D("175000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("175000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("155000.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("155000")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("175000")
    assert worksheet.get(NET_INCOME).value == D("185000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("10000.00")


def test_step_2_line_19_limits_amount_q_to_105000() -> None:
    # Capital gains deductions claimed in earlier years of 150000 (Step 2 line 17 and Chart 2
    # line 18): Step 2 line 18 is 20000 + 150000 = 170000, so line 19 is 275000.00 - 170000 =
    # 105000.00. Chart 2 line 19 is 0 + 150000 = 150000 (D), so Part 2's E is 625000 - 150000 =
    # 475000; M is 175000.00, N is the lesser, 175000.00, and P is 175000.00. Q is the lesser of
    # 155000.00, 105000.00 and 175000.00: 105000.00, line 19 of Step 2.
    worksheet = return_bf(
        t657_deductions_claimed_1985_to_2024="150000",
        t657_chart_2_line_18="150000",
        capital_gains_deduction_claimed="105000",
    )

    assert worksheet.get(CUMULATIVE_LOSSES_AND_DEDUCTIONS).value == D("170000")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("105000.00")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("155000.00")
    assert worksheet.get(CHART_2_LINE_19).value == D("150000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_E).value == D("475000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("175000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("105000.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("105000")
    # Line 25700 is 20000 + 105000 = 125000, so taxable income is 185000.00 - 125000 = 60000.00.
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("125000")
    assert worksheet.get(TAXABLE_INCOME).value == D("60000.00")


def test_amount_p_limits_amount_q_when_amount_l_takes_60000_off_amount_k() -> None:
    # Part 2's L (the portion of T2048 line 17216 for the disposition) is 60000: M is K less L,
    # 175000.00 - 60000 = 115000.00, below E (625000), so N and P are 115000.00. Q is the lesser
    # of 155000.00, 255000.00 and 115000.00: 115000.00, amount P. The filer claims all of it.
    worksheet = return_bf(t657_part_2_amount_l="60000", capital_gains_deduction_claimed="115000")

    assert worksheet.get(CHART_2025_PART_2_AMOUNT_M).value == D("115000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_N).value == D("115000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("115000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("115000.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("115000")
    # Line 25700 is 20000 + 115000 = 135000, so taxable income is 185000.00 - 135000 = 50000.00.
    assert worksheet.get(TAXABLE_INCOME).value == D("50000.00")


def test_amount_e_limits_amount_n_when_chart_2_takes_500000_off_the_maximum() -> None:
    # Chart 2 line 18 of 500000 makes Chart 2 line 19 500000: Part 2's E is 625000 - 500000 =
    # 125000, below M (175000.00), so N is 125000, P is 125000 and Q is the lesser of 155000.00,
    # 255000.00 (Step 2 line 17 is left blank) and 125000: 125000.
    worksheet = return_bf(t657_chart_2_line_18="500000", capital_gains_deduction_claimed="125000")

    assert worksheet.get(CHART_2_LINE_19).value == D("500000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_E).value == D("125000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_M).value == D("175000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_N).value == D("125000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("125000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("125000")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("125000")


def test_a_claim_above_amount_q_is_refused_naming_both_kinds() -> None:
    # Part 2 amount Q "This is the maximum amount you can claim on line 25400 of your 2025 return.
    # However, you can choose to claim less.": 155000.01 against 155000.00 is an input error, not
    # capped.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bf(capital_gains_deduction_claimed="155000.01")

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/capital_gains_deduction_claimed 155000.01 is above "
        "ca/chart_2025_part_2_maximum_claim 155000"
    )


def test_a_claim_above_amount_q_that_step_2_line_19_lowers_is_refused() -> None:
    # Step 2 line 19 of 105000.00 is amount Q: the annual gains limit (155000.00) no longer is the
    # most that can be claimed.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bf(
            t657_deductions_claimed_1985_to_2024="150000",
            t657_chart_2_line_18="150000",
            capital_gains_deduction_claimed="105000.01",
        )

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/capital_gains_deduction_claimed 105000.01 is above "
        "ca/chart_2025_part_2_maximum_claim 105000"
    )


@pytest.mark.parametrize(
    ("claimed", "deductions", "taxable_income"),
    [
        # "You can choose to claim less": line 25700 is 20000 + the claim; taxable income is
        # 185000.00 less it.
        ("0", "20000", "165000.00"),
        ("100000", "120000", "65000.00"),
        ("155000", "175000", "10000.00"),
    ],
)
def test_the_filer_may_claim_less_than_amount_q(
    claimed: str, deductions: str, taxable_income: str
) -> None:
    worksheet = return_bf(capital_gains_deduction_claimed=claimed)

    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D(claimed)
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D(deductions)
    assert worksheet.get(TAXABLE_INCOME).value == D(taxable_income)


def test_chart_1_rows_total_6500_into_step_2_line_14() -> None:
    # Chart 1: 1985 to 1987, A 3000 and B 1000 (C and D are N/A): E 0, F 1000, G 2000. 1992, A
    # 5000, C 4000 and D 1500 (B is N/A): E 2500, F 2500, G 2500. 2001 to 2024, A 20000 and C
    # 18000: E 18000, F 18000, G 2000. Total of column G: 6500, Step 2 line 14. Line 18 is 20000
    # (line 15) + 6500 = 26500 and line 19 is 275000.00 - 26500 = 248500.00; Step 1 line 21
    # (155000.00) is still the least.
    worksheet = return_bf(
        t657_chart_1_rows=(
            t657_chart_1_row(a="3000", b="1000"),
            t657_chart_1_row(a="5000", c="4000", d="1500"),
            t657_chart_1_row(a="20000", c="18000"),
        )
    )

    assert worksheet.get(CHART_1_COLUMN_G_TOTAL).value == D("6500")
    assert worksheet.get(CUMULATIVE_LOSSES_AND_DEDUCTIONS).value == D("26500")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("248500.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("155000.00")


def test_chart_2_adjusts_each_period_and_gives_65000_for_amount_d() -> None:
    # Line 1 10000 and line 2 40000: line 3 is 50000; line 4 is 40000 x 1/4 = 10000.00 and line 5
    # is 50000 - 10000.00 = 40000.00. Line 6 is 6000: line 7 is 46000.00; line 8 is 6000 x 1/3 =
    # 2000.00 and line 9 is 44000.00. Line 10 is 9000: line 11 is 53000.00; line 12 is 9000 x 1/3
    # = 3000.00 and line 13 is 50000.00. Line 14 is 12000: line 15 is 62000.00; with IR 0.6, line
    # 16 is 12000 x [1 - 1 / (2 x 0.6)] = 12000 - 12000 / 1.2 = 12000 - 10000.00 = 2000.00 (2 x
    # IR is exactly 1.2), so
    # line 17 is 60000.00. Line 18 is 5000: line 19 is 65000.00, amount D. Part 2's E is 625000 -
    # 65000.00 = 560000.00.
    worksheet = return_bf(
        t657_chart_2_line_1="10000",
        t657_chart_2_line_2="40000",
        t657_chart_2_line_6="6000",
        t657_chart_2_line_10="9000",
        t657_chart_2_line_14="12000",
        t657_inclusion_rate_2000="0.6",
        t657_chart_2_line_18="5000",
    )

    assert worksheet.get(CHART_2_LINE_3).value == D("50000")
    assert worksheet.get(CHART_2_LINE_4).value == D("10000.00")
    assert worksheet.get(CHART_2_LINE_5).value == D("40000.00")
    assert worksheet.get(CHART_2_LINE_7).value == D("46000.00")
    assert worksheet.get(CHART_2_LINE_8).value == D("2000.00")
    assert worksheet.get(CHART_2_LINE_9).value == D("44000.00")
    assert worksheet.get(CHART_2_LINE_11).value == D("53000.00")
    assert worksheet.get(CHART_2_LINE_12).value == D("3000.00")
    assert worksheet.get(CHART_2_LINE_13).value == D("50000.00")
    assert worksheet.get(CHART_2_LINE_15).value == D("62000.00")
    assert worksheet.get(CHART_2_TWICE_IR).value == D("1.2")
    assert worksheet.get(CHART_2_LINE_14_OVER_TWICE_IR).value == D("10000.00")
    assert worksheet.get(CHART_2_LINE_16).value == D("2000.00")
    assert worksheet.get(CHART_2_LINE_17).value == D("60000.00")
    assert worksheet.get(CHART_2_LINE_19).value == D("65000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_E).value == D("560000.00")


def test_chart_1_takes_one_record_for_each_year() -> None:
    # Year 1: A 100, C 300: E 300, F 300, G 0 (A - F is negative, so 0). Year 2: A 500, C 100: E
    # 100, F 100, G 400. Total of column G: 400.
    worksheet = return_bf(
        t657_chart_1_rows=(
            t657_chart_1_row(a="100", c="300"),
            t657_chart_1_row(a="500", c="100"),
        )
    )

    assert worksheet.get(CHART_1_COLUMN_G_TOTAL).value == D("400")


def test_chart_2_line_16_rounds_once_so_a_line_14_of_1000_01_at_ir_half_gives_zero() -> None:
    # 2 x IR is 1, so line 14 x 1/1 is 1000.01 and line 16 is 1000.01 - 1000.01 = 0.00. Halving
    # line 14 first would round 500.005 up to 500.01 and make line 16 -0.01.
    worksheet = return_bf(t657_chart_2_line_14="1000.01", t657_inclusion_rate_2000="0.5")

    assert worksheet.get(CHART_2_TWICE_IR).value == D("1.0")
    assert worksheet.get(CHART_2_LINE_14_OVER_TWICE_IR).value == D("1000.01")
    assert worksheet.get(CHART_2_LINE_16).value == D("0.00")


def test_chart_2_line_16_at_an_odd_ir_is_rounded_once() -> None:
    # IR 0.6667: 2 x IR is 1.3334 and 1000.01 / 1.3334 = 749.97000..., rounded half-up once to
    # 749.97, so line 16 is 1000.01 - 749.97 = 250.04.
    worksheet = return_bf(t657_chart_2_line_14="1000.01", t657_inclusion_rate_2000="0.6667")

    assert worksheet.get(CHART_2_TWICE_IR).value == D("1.3334")
    assert worksheet.get(CHART_2_LINE_14_OVER_TWICE_IR).value == D("749.97")
    assert worksheet.get(CHART_2_LINE_16).value == D("250.04")


def test_chart_2_line_16_with_ir_not_entered_is_line_14() -> None:
    # IR is required when line 14 is not 0; an IR of 0 means not entered, so the adjustment is 0
    # and line 16 is line 14 (documented behaviour).
    worksheet = return_bf(t657_chart_2_line_14="1000.01", t657_inclusion_rate_2000="0")

    assert worksheet.get(CHART_2_LINE_14_OVER_TWICE_IR).value == D("0.00")
    assert worksheet.get(CHART_2_LINE_16).value == D("1000.01")


def test_an_ir_above_1_is_accepted_and_flows_into_chart_2_line_16() -> None:
    # IR 2 is above 1, and the form prints no maximum, so it is not refused or capped. 2 x IR is 4,
    # and line 14 x 1/(IR x 2) is 1000.01 / 4 = 250.0025, rounded half-up once to 250.00, so line 16
    # is 1000.01 - 250.00 = 750.01.
    worksheet = return_bf(t657_chart_2_line_14="1000.01", t657_inclusion_rate_2000="2")

    assert worksheet.get(CHART_2_TWICE_IR).value == D("4")
    assert worksheet.get(CHART_2_LINE_14_OVER_TWICE_IR).value == D("250.00")
    assert worksheet.get(CHART_2_LINE_16).value == D("750.01")


def test_an_ir_of_exactly_1_is_taken_and_the_unit_rate_halves_nothing() -> None:
    # 2 x IR is 2, so line 14 x 1/2 is 500.01 (500.005 rounded half-up once) and line 16 is
    # 1000.01 - 500.01 = 500.00.
    worksheet = return_bf(t657_chart_2_line_14="1000.01", t657_inclusion_rate_2000="1")

    assert worksheet.get(CHART_2_TWICE_IR).value == D("2")
    assert worksheet.get(CHART_2_LINE_14_OVER_TWICE_IR).value == D("500.01")
    assert worksheet.get(CHART_2_LINE_16).value == D("500.00")


def test_a_period_1_of_2024_amount_feeds_part_2s_amounts_b_and_o() -> None:
    # Part 1: A 522145; B 0, so C is 522145 and (D 0) E is 522145. F, a T3 box 57 amount for a
    # disposition in Period 1 of 2024, is 200000: F to J add to 200000 and K is 100000.00; L is 0,
    # so M is 100000.00, N is the lesser of E and M, 100000.00, O is B (0) and P is 100000.00. Q
    # is the lesser of 155000.00, 255000.00 and 100000.00: 100000.00, which nothing reads.
    # Part 2's B is Part 1's P, 100000.00: C is 625000 - 100000.00 = 525000.00 and E the same; M
    # and N are 175000.00; O is B, 100000.00, so P is 275000.00. Q is the lesser of 155000.00,
    # 255000.00 and 275000.00: 155000.00, so the claim is not limited to Part 1's Q.
    worksheet = return_bf(t657_part_1_amount_f="200000")

    assert worksheet.get(CHART_2025_PART_1_AMOUNT_C).value == D("522145")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_E).value == D("522145")
    assert worksheet.get(CHART_2025_PART_1_AMOUNTS_F_TO_J).value == D("200000")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_K).value == D("100000.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_M).value == D("100000.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_N).value == D("100000.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_P).value == D("100000.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_Q).value == D("100000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_C).value == D("525000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_E).value == D("525000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_N).value == D("175000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("275000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("155000.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("155000")


def test_slip_amounts_excluded_from_line_10700_come_off_part_2_amount_f() -> None:
    # Part 2's F is line 10700 less the amount the form says not to include (a T3 box 30 amount
    # for QSBCS), 120000: 350000 - 120000 = 230000; with G and H at 0, an I of -10000 (T2017 line 6
    # with a 2025 reserve of 10000 claimed) and J at 0, F to J add to 220000 and K is 110000.00,
    # M is 110000.00, N is 110000.00 and P is 110000.00. Q is the lesser of 150000.00 (the annual
    # gains limit, 5000 less than without the reserve), 250000.00 and 110000.00: 110000.00.
    worksheet = return_bf(
        t657_part_2_excluded_f="120000",
        t657_part_2_amount_i="-10000",
        capital_gains_deduction_claimed="110000",
    )

    assert worksheet.get(CHART_2025_PART_2_AMOUNT_F).value == D("230000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNTS_F_TO_J).value == D("220000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_K).value == D("110000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("110000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("110000.00")


def test_a_t3_gain_on_line_17600_is_taken_off_the_annual_gains_by_line_9() -> None:
    # A T3 slip gain of 40000 (line 17600) adds 20000.00 to line 19900: 195000.00. Line 9 is 40000
    # x 1/2 = 20000.00, so line 10 is 195000.00 - 20000.00 = 175000.00 and line 12 is the same;
    # line 7 is still 175000.00, so line 13 is 175000.00. Step 1 line 15 is now Form T936 Chart A
    # line 14, which the T3 gain moves: line 1 is 195000.00, line 2 is 0, line 3 is 195000.00;
    # lines 4 to 6 are 350000 (QSBCS) + 0 + 0, line 7 is 350000.00, line 8 is 0 (no line 19200), so
    # line 9 is 350000.00, line 11 is 350000.00 x 50% = 175000.00, line 12 is 0 and line 13 is
    # 175000.00: line 14 is 195000.00 - 175000.00 = 20000.00 (the T3 gain taken at 50% is the part
    # of line 1 that no qualified property explains). Step 1 line 14 is 20000 (line 25300), so
    # line 16 is 20000 - 20000.00 = 0, line 20 is 0 and line 21 is 175000.00 - 0 = 175000.00
    # (the 155000.00 of the return without the gain assumed a line 15 of 0).
    worksheet = return_bf(t3_capital_gains_or_losses="40000")

    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("195000.00")
    assert worksheet.get(SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO).value == D("40000")
    assert worksheet.get(ANNUAL_GAINS_LINE_9).value == D("20000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_10).value == D("175000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_12).value == D("175000.00")
    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025).value == D("175000.00")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("175000.00")


def test_a_loss_on_qsbcs_gives_no_annual_gains_limit() -> None:
    # Proceeds of 100000 against an adjusted cost base of 150000: line 1 and line 3 are -50000.00
    # and the product at 1/2 is -25000.00, which line 5 floors at 0. Line 7 is 0 - 0 = 0. Line 8
    # (line 19900) is the net capital loss, -25000.00, line 9 is 0, so lines 10 and 12 are
    # -25000.00 and line 13 is the lesser of 0 and -25000.00: -25000.00. Line 21 is -25000.00 - 0,
    # floored at 0. Part 2's F is -50000.00 and F to J, floored at 0, add to 0; Q is 0.
    worksheet = return_bf(
        qsbcs_dispositions=(("100000", "150000", "0"),),
        unapplied_net_capital_losses_2001_to_2024="0",
        net_capital_losses_claimed="0",
        capital_gains_deduction_claimed="0",
    )

    assert worksheet.get(ANNUAL_GAINS_SCHEDULE_3_TOTAL).value == D("-50000")
    assert worksheet.get(ANNUAL_GAINS_LINE_3).value == D("-50000")
    assert worksheet.get(ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE).value == D("-25000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_5).value == D("0")
    assert worksheet.get(ANNUAL_GAINS_LINE_7).value == D("0")
    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("-25000.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("0")
    assert worksheet.get(ANNUAL_GAINS_LINE_10).value == D("-25000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_12).value == D("-25000.00")
    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025).value == D("-25000.00")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("0")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_F).value == D("-50000")
    assert worksheet.get(CHART_2025_PART_2_AMOUNTS_F_TO_J).value == D("0")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("0")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("0")


def test_a_claim_of_anything_is_refused_when_nothing_can_be_claimed() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        return_bf(
            qsbcs_dispositions=(("100000", "150000", "0"),),
            unapplied_net_capital_losses_2001_to_2024="0",
            net_capital_losses_claimed="0",
            capital_gains_deduction_claimed="0.01",
        )

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/capital_gains_deduction_claimed 0.01 is above ca/chart_2025_part_2_maximum_claim 0"
    )


def test_form_t2048_figures_are_read_on_lines_6_11_and_18_of_step_1() -> None:
    # Return BE's T2048 gives line 17216 of 70000.00, line 17215 of 70000.00 and line 17217 of
    # 4000.00. Step 1: line 1 is 0 (its gains are not on line 10700), so line 5 is 0 and line 7
    # is 0 - 70000.00 = -70000.00. Line 8 is the included gain, 100000.00, line 9 is 0 and line
    # 10 is 100000.00; line 12 is 100000.00 - 70000.00 = 30000.00. Line 13 is the lesser of
    # -70000.00 and 30000.00: -70000.00. Line 14 is 30000 and line 15 is Form T936 Chart A line 14:
    # line 1 is 100000.00 (line 19900), line 2 is 70000.00 (T2048 line 17215), line 3 is 30000.00;
    # lines 4 to 8 are 0 (no QSBCS gain on Schedule 3, no line 19200), so lines 9 and 11 are 0;
    # line 12 is 70000.00 (T2048 line 17216), line 13 is 0 - 70000.00 = -70000.00 (no floor), and
    # line 14 is 30000.00 - (-70000.00) = 100000.00. So line 16 is 30000 - 100000.00 floored at 0;
    # line 17 is 4000.00 and line 18 is 4000.00, so line 19 is 0. Line 20 is 0 + 0 = 0 and line 21
    # is -70000.00 - 0 floored at 0.
    worksheet = return_be()

    assert worksheet.get(QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("70000.00")
    assert worksheet.get(QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("70000.00")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("4000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_5).value == D("0")
    assert worksheet.get(ANNUAL_GAINS_LINE_7).value == D("-70000.00")
    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("100000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_10).value == D("100000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_12).value == D("30000.00")
    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025).value == D("-70000.00")
    assert worksheet.get(ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("0")
    assert worksheet.get(ABIL_AFTER_QBT_REDUCTION).value == D("0.00")
    assert worksheet.get(TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT).value == D("0")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("0")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("0")
    # Return BE's line 25395 claim is unchanged, so are its deductions (30000 + 60500).
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("90500.00")


def test_a_return_with_no_form_t657_has_every_line_at_zero() -> None:
    # Returns A to BE enter nothing on Form T657: every input is 0 (and Chart 1 has no rows), so
    # the annual and cumulative gains limits, both Parts' amount Q and line 25400 are 0.
    worksheet = compute("60000", (), "0", "0", "10800", "0", "0", income_tax_deducted="8000")

    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025).value == D("0")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("0")
    assert worksheet.get(CHART_1_COLUMN_G_TOTAL).value == D("0")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("0")
    assert worksheet.get(CHART_2_LINE_16).value == D("0")
    assert worksheet.get(CHART_2_LINE_19).value == D("0")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_Q).value == D("0")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("0")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("0")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("0")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("0")


def test_a_2000_loss_at_ir_06_is_adjusted_on_chart_a_and_line_4_and_the_claim_stays_20000() -> None:
    # Chart A row "In 2000": 1000 at IR 0.6. Column F is 2 × 0.6 = 1.20; column C is 1000 ÷ 1.20 =
    # 833.33; column D is 833.33 (the lesser of C and the 20000 left on line 13); column E and G are
    # 0.00. The row "After 2000 and before 2025" then has 19166.67 left: column C 20000.00, D
    # 19166.67, E 833.33 and G 833.33. Line 4 is 833.33 + 20000.00 = 20833.33, line 6 is 20833.33,
    # and the 20000 claimed is line 7 and line 25300, so the claim does not change.
    worksheet = return_bf(unapplied_net_capital_losses_2000="1000", t657_inclusion_rate_2000="0.6")

    assert worksheet.get(NET_CAPITAL_LOSS_TWICE_IR_2000).value == D("1.20")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_2000).value == D("833.33")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_2000).value == D("833.33")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_2000).value == D("19166.67")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_2000).value == D("0.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2000).value == D("0.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024).value == D("20000.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_2001_TO_2024).value == D("19166.67")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_2001_TO_2024).value == D("833.33")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("833.33")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("20833.33")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("20000")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("155000.00")


def test_the_2000_row_takes_what_the_1990_to_1999_row_leaves_of_the_claim() -> None:
    # The 1990 to 1999 row of 9000 at 2/3 is 6000.00 in column C and is applied first, so 14000.00
    # is left on line 13 for the 2000 row. The 2000 row's C is 833.33 (1000 at IR 0.6), applied in
    # full; 13166.67 is left for the 2001 to 2024 row, which takes 13166.67 of its 20000 and leaves
    # 6833.33 in column E. The column D total is 6000.00 + 833.33 + 13166.67 = 20000.00, line 13.
    worksheet = return_bf(
        unapplied_net_capital_losses_1990_to_1999="9000",
        unapplied_net_capital_losses_2000="1000",
        t657_inclusion_rate_2000="0.6",
    )

    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999).value == D("6000.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_1990_TO_1999).value == D("6000.00")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999).value == D("14000.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_2000).value == D("833.33")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_2000).value == D("833.33")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_2000).value == D("13166.67")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_2001_TO_2024).value == D("13166.67")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_2001_TO_2024).value == D("6833.33")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("6833.33")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("26833.33")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("20000")
