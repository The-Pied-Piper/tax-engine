"""CA-ON 2025 end to end: return et (Form T657 Step 1, Step 2, Chart 1, Chart 2 and Charts 2016 to
2025)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025,
    ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    ANNUAL_GAINS_LIMIT_2025,
    ANNUAL_GAINS_LINE_2,
    ANNUAL_GAINS_LINE_3,
    ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE,
    ANNUAL_GAINS_LINE_5,
    ANNUAL_GAINS_LINE_7,
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
    CHART_2_NUMERATOR_ONE,
    CHART_2_TWICE_IR,
    CHART_2016_AMOUNT_B,
    CHART_2016_PART_1_AMOUNT_A,
    CHART_2016_PART_1_AMOUNT_C,
    CHART_2016_PART_1_AMOUNT_F,
    CHART_2016_PART_1_AMOUNT_G,
    CHART_2016_PART_1_AMOUNT_H,
    CHART_2016_PART_1_AMOUNTS_D_AND_E,
    CHART_2016_PART_2_AMOUNT_A,
    CHART_2016_PART_2_AMOUNT_C,
    CHART_2016_PART_2_AMOUNT_E,
    CHART_2016_PART_2_AMOUNT_F,
    CHART_2016_PART_2_AMOUNT_G,
    CHART_2016_PART_2_AMOUNT_I,
    CHART_2016_PART_2_AMOUNT_J,
    CHART_2016_PART_2_AMOUNT_K,
    CHART_2016_PART_2_APPLIES,
    CHART_2016_TOTAL_CARRIED,
    CHART_2017_AMOUNT_D,
    CHART_2017_PART_1_AMOUNT_A,
    CHART_2017_PART_1_AMOUNT_C,
    CHART_2017_PART_1_AMOUNT_E,
    CHART_2017_PART_1_AMOUNT_H,
    CHART_2017_PART_1_AMOUNT_I,
    CHART_2017_PART_1_AMOUNT_K,
    CHART_2017_PART_1_AMOUNT_L,
    CHART_2017_PART_1_AMOUNTS_F_AND_G,
    CHART_2017_PART_2_AMOUNT_A,
    CHART_2017_PART_2_AMOUNT_C,
    CHART_2017_PART_2_AMOUNT_E,
    CHART_2017_PART_2_AMOUNT_I,
    CHART_2017_PART_2_APPLIES,
    CHART_2017_TOTAL_CARRIED,
    CHART_2018_AMOUNT_D,
    CHART_2018_PART_1_AMOUNT_A,
    CHART_2018_PART_1_AMOUNT_C,
    CHART_2018_PART_1_AMOUNT_E,
    CHART_2018_PART_1_AMOUNT_H,
    CHART_2018_PART_1_AMOUNT_I,
    CHART_2018_PART_1_AMOUNT_K,
    CHART_2018_PART_1_AMOUNT_L,
    CHART_2018_PART_1_AMOUNTS_F_AND_G,
    CHART_2018_PART_2_AMOUNT_A,
    CHART_2018_PART_2_AMOUNT_C,
    CHART_2018_PART_2_AMOUNT_E,
    CHART_2018_PART_2_AMOUNT_F,
    CHART_2018_PART_2_AMOUNT_G,
    CHART_2018_PART_2_AMOUNT_I,
    CHART_2018_PART_2_AMOUNT_J,
    CHART_2018_PART_2_AMOUNT_K,
    CHART_2018_PART_2_APPLIES,
    CHART_2018_TOTAL_CARRIED,
    CHART_2019_AMOUNT_D,
    CHART_2019_PART_1_AMOUNT_A,
    CHART_2019_PART_1_AMOUNT_C,
    CHART_2019_PART_1_AMOUNT_E,
    CHART_2019_PART_1_AMOUNT_H,
    CHART_2019_PART_1_AMOUNT_I,
    CHART_2019_PART_1_AMOUNT_K,
    CHART_2019_PART_1_AMOUNT_L,
    CHART_2019_PART_1_AMOUNTS_F_AND_G,
    CHART_2019_PART_2_AMOUNT_A,
    CHART_2019_PART_2_AMOUNT_C,
    CHART_2019_PART_2_AMOUNT_E,
    CHART_2019_PART_2_AMOUNT_F,
    CHART_2019_PART_2_AMOUNT_G,
    CHART_2019_PART_2_AMOUNT_I,
    CHART_2019_PART_2_AMOUNT_J,
    CHART_2019_PART_2_AMOUNT_K,
    CHART_2019_PART_2_APPLIES,
    CHART_2019_TOTAL_CARRIED,
    CHART_2020_AMOUNT_D,
    CHART_2020_PART_1_AMOUNT_A,
    CHART_2020_PART_1_AMOUNT_C,
    CHART_2020_PART_1_AMOUNT_E,
    CHART_2020_PART_1_AMOUNT_K,
    CHART_2020_PART_1_AMOUNT_L,
    CHART_2020_PART_2_AMOUNT_A,
    CHART_2020_PART_2_AMOUNT_C,
    CHART_2020_PART_2_AMOUNT_E,
    CHART_2020_PART_2_AMOUNT_I,
    CHART_2020_PART_2_APPLIES,
    CHART_2020_TOTAL_CARRIED,
    CHART_2021_AMOUNT_D,
    CHART_2021_PART_1_AMOUNT_A,
    CHART_2021_PART_1_AMOUNT_C,
    CHART_2021_PART_1_AMOUNT_E,
    CHART_2021_PART_1_AMOUNT_M,
    CHART_2021_PART_1_AMOUNT_N,
    CHART_2021_PART_2_AMOUNT_A,
    CHART_2021_PART_2_AMOUNT_C,
    CHART_2021_PART_2_AMOUNT_E,
    CHART_2021_PART_2_AMOUNT_K,
    CHART_2021_PART_2_APPLIES,
    CHART_2021_TOTAL_CARRIED,
    CHART_2022_AMOUNT_D,
    CHART_2022_PART_1_AMOUNT_A,
    CHART_2022_PART_1_AMOUNT_C,
    CHART_2022_PART_1_AMOUNT_E,
    CHART_2022_PART_1_AMOUNT_M,
    CHART_2022_PART_1_AMOUNT_N,
    CHART_2022_PART_2_AMOUNT_A,
    CHART_2022_PART_2_AMOUNT_C,
    CHART_2022_PART_2_AMOUNT_E,
    CHART_2022_PART_2_AMOUNT_K,
    CHART_2022_PART_2_APPLIES,
    CHART_2022_TOTAL_CARRIED,
    CHART_2023_AMOUNT_D,
    CHART_2023_PART_1_AMOUNT_A,
    CHART_2023_PART_1_AMOUNT_C,
    CHART_2023_PART_1_AMOUNT_E,
    CHART_2023_PART_1_AMOUNT_M,
    CHART_2023_PART_1_AMOUNT_N,
    CHART_2023_PART_2_AMOUNT_A,
    CHART_2023_PART_2_AMOUNT_C,
    CHART_2023_PART_2_AMOUNT_E,
    CHART_2023_PART_2_AMOUNT_K,
    CHART_2023_PART_2_APPLIES,
    CHART_2023_TOTAL_CARRIED,
    CHART_2024_PERIOD_1_AMOUNT_A,
    CHART_2024_PERIOD_1_AMOUNT_C,
    CHART_2024_PERIOD_1_AMOUNT_E,
    CHART_2024_PERIOD_1_AMOUNT_N,
    CHART_2024_PERIOD_1_AMOUNT_O,
    CHART_2024_PERIOD_2_AMOUNT_A,
    CHART_2024_PERIOD_2_AMOUNT_C,
    CHART_2024_PERIOD_2_AMOUNT_E,
    CHART_2024_PERIOD_2_AMOUNT_N,
    CHART_2024_PERIOD_2_AMOUNT_O,
    CHART_2025_PART_1_AMOUNT_A,
    CHART_2025_PART_1_AMOUNT_C,
    CHART_2025_PART_1_AMOUNT_E,
    CHART_2025_PART_1_AMOUNT_P,
    CHART_2025_PART_1_AMOUNT_Q,
    CHART_2025_PART_2_AMOUNT_A,
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
    NET_INCOME,
    SCHEDULE_3_LINE_19200,
    SCHEDULE_3_LINE_19900,
    T657_CUMULATIVE_NET_INVESTMENT_LOSS,
    T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    compute,
    t657_chart_1_row,
    t657_reserve_inputs,
)

# The reserves of earlier dispositions that Form T657 reads from Form T2017 (the rows are made by
# `t657_reserve_rows`): QFFP 2016 (300000), 2018 (30000) and 2019 (550000), and QSBCS 2017 (100000)
# and 2018 (20000).
RESERVES = {
    "t657_chart_2016_amount_d": "300000",
    "t657_chart_2017_amount_g": "100000",
    "t657_chart_2018_amount_f": "30000",
    "t657_chart_2018_amount_g": "20000",
    "t657_chart_2019_amount_f": "550000",
}


def return_et(**overrides: Any) -> Worksheet:
    """Return ET's inputs, as in `returns/2025_return_et.yaml`: one QSBCS disposition in 2025 for a
    gain of 700000, 40000 of net capital losses of other years of which 30000 is claimed, Form
    T657 with three Chart 1 rows, Chart 2 and the prior-year charts, and 280000 claimed on line
    25400."""
    inputs: dict[str, Any] = {
        # Required arguments of `compute` that the YAML leaves at zero.
        "employment_income": "0",
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "share_dispositions": (),
        "partnership_gains_at_full_inclusion": "10000",
        "qsbcs_dispositions": (
            (
                "900000",
                "200000",
                "0",
            ),
        ),
        "unapplied_net_capital_losses_2001_to_2024": "40000",
        "net_capital_losses_claimed": "30000",
        "t657_chart_2_line_1": "3000",
        "t657_chart_2_line_2": "8000.02",
        "t657_chart_2_line_6": "3000",
        "t657_chart_2_line_10": "6000",
        "t657_chart_2_line_14": "13000",
        "t657_chart_2_line_18": "20000",
        "t657_inclusion_rate_2000": "0.6",
        # Form T2017 line 2 has one reserve of 100,000 claimed (nine-year kind); line 16 is 100,000.
        "t2017_amounts": {16: "100000"},
        "t2017_rows": {
            2: (
                {
                    "capital_gain": "200000",
                    "payable": "200000",
                    "proceeds": "200000",
                    "years": 0,
                    "claimed": "100000",
                    "previous": "0",
                    "nine_year": 1,
                },
            ),
        },
        "t657_gains_1985_to_1991": "12000",
        "t657_gains_1992_and_1993": "6000",
        "t657_gains_1994": "3000",
        "t657_gains_1995": "4000",
        "t657_gains_1996_to_1999": "8000",
        "t657_gains_2000": "5000",
        "t657_gains_2001": "7000",
        "t657_gains_2002_to_2024": "100000",
        "t657_capital_losses_claimed_1985": "2000",
        "t657_abil_claimed_1985_to_2024": "30000",
        "t657_t2048_line_17217_for_2024": "5000",
        # Form T936 Part 3 lines 15 and 20; Step 1 line 15 and Step 2 line 16 come from the form.
        "t936_amounts": {
            "investment_expenses_previous_years": "20000",
            "investment_income_previous_years": "5000",
        },
        "t657_deductions_claimed_1985_to_2024": "53000.02",
        "t657_chart_1_rows": (
            t657_chart_1_row(a="10000", b="2000", c="8000", d="3000"),
            t657_chart_1_row(a="20000", b="0", c="4000", d="6000"),
            t657_chart_1_row(a="5000", b="6000", c="1000", d="0"),
        ),
        "t657_chart_2016_uses_d_instead": 1,
        "t657_chart_2016_amount_b_instead": "392088",
        "t657_chart_2016_claims_additional_deduction": 1,
        "t657_chart_2018_uses_d_instead": 1,
        "t657_chart_2018_amount_d_instead": "60000",
        "t657_chart_2018_claims_additional_deduction": 1,
        "t657_chart_2019_uses_d_instead": 1,
        "t657_chart_2019_amount_d_instead": "240544",
        "t657_chart_2019_claims_additional_deduction": 1,
        "capital_gains_deduction_claimed": "280000",
    }
    return compute(**t657_reserve_inputs(RESERVES, {**inputs, **overrides}))


def test_step_1_derives_the_annual_gains_limit_of_280000() -> None:
    # Step 1: line 1 is 700,000.00 (line 10700 only); line 2 (Form T2017 line 13) is -100,000 (a
    # loss, shown in brackets), so line 3 is 600,000.00; line 4 is 1/2, so line 5 is 300,000.00;
    # line 6 (Form T2048 line 17216) is 0; line 7 is 300,000.00. Line 8 (Schedule 3 line 19900) is
    # 360,000.00 (350,000.00 + 10,000.00 of partnership gains at full inclusion); line 9 is 0;
    # line 10 is 360,000.00; line 11 is 0; line 12 is 360,000.00. Line 13
    # is the lesser of line 7 and line 12: 300,000.00. Line 14 (line 25300) is 30,000.00 and line 15
    # (line 14 of Chart A of Form T936) is 10,000.00, so line 16 is 20,000.00; lines 17, 18 and 19
    # are 0; line 20 is 20,000.00; line 21, the annual gains limit, is 300,000.00 - 20,000.00 =
    # 280,000.00.
    worksheet = return_et()

    assert worksheet.get(ANNUAL_GAINS_SCHEDULE_3_TOTAL).value == D("700000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_2).value == D("-100000")
    assert worksheet.get(SCHEDULE_3_LINE_19200).value == D("0")
    assert worksheet.get(ANNUAL_GAINS_LINE_3).value == D("600000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE).value == D("300000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_5).value == D("300000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_7).value == D("300000.00")
    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("360000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_10).value == D("360000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_12).value == D("360000.00")
    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025).value == D("300000.00")
    assert worksheet.get(T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS).value == D("10000.00")
    assert worksheet.get(ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("20000.00")
    assert worksheet.get(TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT).value == D("20000.00")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("280000.00")


def test_form_t936_gives_step_1_line_15_and_step_2_line_16() -> None:
    # Form T936 Chart A: line 1 is 360,000.00, line 3 is 360,000.00, line 7 is 700,000.00, line 8
    # is 0 (no amount on line 19200), line 11 is 350,000.00, line 13 is 350,000.00 and line 14 is
    # 10,000.00 (Step 1 line 15); no T3 slip, so line 20 is 10,000.00. Part 1 line 7 is the lesser
    # of 10,000.00 and 30,000.00 (line 25300), so A is 10,000.00; B is 10,000.00 (line 13). Part 3:
    # line 16 is 10,000.00 + 20,000 = 30,000.00, line 21 is 10,000.00 + 5,000 = 15,000.00 and line
    # C is 15,000.00 (Step 2 line 16).
    worksheet = return_et()

    assert worksheet.get(T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS).value == D("10000.00")
    assert worksheet.get(T657_CUMULATIVE_NET_INVESTMENT_LOSS).value == D("15000.00")


def test_chart_1_column_g_total_is_23000() -> None:
    # Chart 1 (three rows, columns A to D chosen): row 1 has A 10,000, B 2,000, C 8,000 and D 3,000,
    # so E is 5,000 (C - D), F is 7,000 (B + E) and G is 3,000 (A - F). Row 2 has A 20,000, B 0, C
    # 4,000 and D 6,000, so C - D is -2,000 and E is entered as "0", F is 0 and G is 20,000. Row 3
    # has A 5,000, B 6,000, C 1,000 and D 0, so E is 1,000, F is 7,000 and A - F is -2,000, so G is
    # entered as "0". The column G total, Step 2 line 14, is 3,000 + 20,000 + 0 = 23,000.
    worksheet = return_et()

    assert worksheet.get(CHART_1_COLUMN_G_TOTAL).value == D("23000.00")


def test_chart_2_lines_3_to_19_round_half_up_at_lines_4_and_16() -> None:
    # Chart 2: line 1 is 3,000; line 2 is 8,000.02, so line 3 is 11,000.02; line 4 is line 2 x 1/4 =
    # 2,000.005, rounded half up to the cent: 2,000.01; line 5 is 9,000.01. Line 6 is 3,000, so line
    # 7 is 12,000.01; line 8 is 3,000 x 1/3 = 1,000.00; line 9 is 11,000.01. Line 10 is 6,000, so
    # line 11 is 17,000.01; line 12 is 6,000 x 1/3 = 2,000.00; line 13 is 15,000.01. Line 14 is
    # 13,000, so line 15 is 28,000.01; with IR 0.6 (the 2000 inclusion rate, a chosen figure) line
    # 16 is 13,000 x [1 - 1/(2 x 0.6)] = 13,000 - 13,000/1.2 = 13,000 - 10,833.33 = 2,166.67 (the
    # quotient rounded half up to the cent once); line 17 is 28,000.01 - 2,166.67 = 25,833.34; line
    # 18 is 20,000; line 19 is 45,833.34.
    worksheet = return_et()

    assert worksheet.get(CHART_2_LINE_3).value == D("11000.02")
    assert worksheet.get(CHART_2_LINE_4).value == D("2000.01")
    assert worksheet.get(CHART_2_LINE_5).value == D("9000.01")
    assert worksheet.get(CHART_2_LINE_7).value == D("12000.01")
    assert worksheet.get(CHART_2_LINE_8).value == D("1000.00")
    assert worksheet.get(CHART_2_LINE_9).value == D("11000.01")
    assert worksheet.get(CHART_2_LINE_11).value == D("17000.01")
    assert worksheet.get(CHART_2_LINE_12).value == D("2000.00")
    assert worksheet.get(CHART_2_LINE_13).value == D("15000.01")
    assert worksheet.get(CHART_2_LINE_15).value == D("28000.01")
    assert worksheet.get(CHART_2_TWICE_IR).value == D("1.20")
    assert worksheet.get(CHART_2_NUMERATOR_ONE).value == D("1.00")
    assert worksheet.get(CHART_2_LINE_14_OVER_TWICE_IR).value == D("10833.33")
    assert worksheet.get(CHART_2_LINE_16).value == D("2166.67")
    assert worksheet.get(CHART_2_LINE_17).value == D("25833.34")
    assert worksheet.get(CHART_2_LINE_19).value == D("45833.34")


def test_step_2_cumulative_gains_limit_is_306999_98() -> None:
    # Step 2: lines 1 to 7 are 12,000, 6,000, 3,000, 4,000, 8,000, 5,000 and 7,000; line 8 is
    # 100,000 (2002 to 2024) + 300,000.00 (Step 1 line 13) = 400,000.00; line 9 is 445,000.00. Line
    # 10 is 2,000; line 11 is 30,000 and line 12 is 5,000, so line 13 is 25,000; line 14 is 23,000
    # (Chart 1); line 15 is 20,000.00 (Step 1 line 20); line 16 is 15,000; line 17 is 53,000.02 (the
    # Chart 2 lines 1, 2, 6, 10, 14 and 18 as filed); line 18 is 2,000 + 25,000 + 23,000 + 20,000 +
    # 15,000 + 53,000.02 = 138,000.02; line 19, the cumulative gains limit, is 445,000.00 -
    # 138,000.02 = 306,999.98.
    worksheet = return_et()

    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025).value == D("400000.00")
    assert worksheet.get(CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS).value == D("445000.00")
    assert worksheet.get(ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025).value == D("25000.00")
    assert worksheet.get(CUMULATIVE_LOSSES_AND_DEDUCTIONS).value == D("138000.02")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("306999.98")


def test_chart_2016_part_2_applies_and_carries_107912() -> None:
    # Chart 2016 uses the (2016-1) calculation, so amount B is the entered 392,088 (a chosen figure,
    # not Chart 2 line 19). Part 1: A is 412,088.00, C is 20,000; D (Form T2017 line 6, QFFP) is
    # 300,000 and E (line 12) is 0, so D + E is 300,000 and F is 150,000.00; G is the lesser of C
    # and F: 20,000.00; H is the lesser of 280,000.00, 306,999.98 and G: 20,000.00. The additional
    # deduction is claimed and C (20,000) is equal to or less than 280,000.00, 306,999.98 and G
    # (20,000), so Part 2 is completed: A is 500,000.00; B (Part 1's G) is 20,000, so C is 480,000;
    # D (Part 1's amount B) is 392,088, so E is 87,912, the additional $87,912 the form prints; F
    # (line 6 x 1/2) is 150,000.00; G is the lesser of E and F: 87,912; H (Part 1's G) is 20,000, so
    # I is 107,912; J is the lesser of F and I: 107,912; K is the lesser of 280,000.00, 306,999.98
    # and J: 107,912. The total carried is Part 2's J, 107,912.
    worksheet = return_et()

    assert worksheet.get(CHART_2016_PART_1_AMOUNT_A).value == D("412088.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_C).value == D("20000.00")
    assert worksheet.get(CHART_2016_AMOUNT_B).value == D("392088.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNTS_D_AND_E).value == D("300000.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_F).value == D("150000.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_G).value == D("20000.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_H).value == D("20000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_C).value == D("480000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_E).value == D("87912.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_F).value == D("150000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_G).value == D("87912.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_I).value == D("107912.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_J).value == D("107912.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_K).value == D("107912.00")
    assert worksheet.get(CHART_2016_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2016_TOTAL_CARRIED).value == D("107912.00")


def test_chart_2017_carries_157912_without_part_2() -> None:
    # Chart 2017 takes Chart 2 line 19 as amount D. A is 417,858.00; B is 107,912, so C is 309,946;
    # D is 45,833.34, so E is 264,112.66. F (line 6) is 0 and G (line 12) is 100,000, so H is
    # 50,000.00 and I, the lesser of E and H, is 50,000.00; J is 107,912 and K is 157,912.00; L is
    # the lesser of 280,000.00, 306,999.98 and K: 157,912.00. The additional deduction is not
    # claimed, so Part 2 (its lines are worked from B 157,912.00 and J 0.00) does not apply and the
    # total carried is K, 157,912.00.
    worksheet = return_et()

    assert worksheet.get(CHART_2017_PART_1_AMOUNT_A).value == D("417858.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_C).value == D("309946.00")
    assert worksheet.get(CHART_2017_AMOUNT_D).value == D("45833.34")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_E).value == D("264112.66")
    assert worksheet.get(CHART_2017_PART_1_AMOUNTS_F_AND_G).value == D("100000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_H).value == D("50000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_I).value == D("50000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_K).value == D("157912.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_L).value == D("157912.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_C).value == D("342088.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_E).value == D("296254.66")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_I).value == D("157912.00")
    assert worksheet.get(CHART_2017_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2017_TOTAL_CARRIED).value == D("157912.00")


def test_chart_2018_refuses_part_2_because_e_exceeds_k() -> None:
    # Chart 2018 uses the (2018-1) calculation: D is the entered 60,000. A is 424,126.00; B is
    # 157,912.00, so C is 266,214.00 and E is 206,214.00. F (line 6) is 30,000 and G (line 12) is
    # 20,000: 50,000.00, H is 25,000.00, I is 25,000.00 and K is 182,912.00; L is 182,912.00. The
    # additional deduction is claimed, but E (206,214.00) is more than K (182,912.00), so Part 2 is
    # not completed (its J would be 15,000.00) and the total carried is K, 182,912.00.
    worksheet = return_et()

    assert worksheet.get(CHART_2018_PART_1_AMOUNT_A).value == D("424126.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_C).value == D("266214.00")
    assert worksheet.get(CHART_2018_AMOUNT_D).value == D("60000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_E).value == D("206214.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNTS_F_AND_G).value == D("50000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_H).value == D("25000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_I).value == D("25000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_K).value == D("182912.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_L).value == D("182912.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_C).value == D("317088.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_E).value == D("257088.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_F).value == D("15000.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_G).value == D("15000.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_I).value == D("197912.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_J).value == D("15000.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_K).value == D("15000.00")
    assert worksheet.get(CHART_2018_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2018_TOTAL_CARRIED).value == D("182912.00")


def test_chart_2019_part_2_applies_and_carries_259456() -> None:
    # Chart 2019 uses the (2019-1) calculation: D is the entered 240,544. A is 433,456.00; B is
    # 182,912.00, so C is 250,544.00 and E is 10,000.00. F (line 6) is 600,000 and G (line 12) is
    # -50,000 (a loss): F + G is 550,000.00, H is 275,000.00 and I, the lesser of E and H, is
    # 10,000.00; K is 192,912.00 and L is 192,912.00. The additional deduction is claimed and E
    # (10,000.00) is equal to or less than 280,000.00, 306,999.98 and K (192,912.00), so Part 2 is
    # completed: A is 500,000.00; B (Part 1's K) is 192,912.00, so C is 307,088.00; D is 240,544, so
    # E is 66,544.00, the additional $66,544 the form prints; F (line 6 x 1/2) is 275,000.00; G is
    # the lesser of E and F: 66,544.00; H is 192,912.00 and I is 259,456.00; J is the lesser of F
    # and I: 259,456.00; K is the lesser of 280,000.00, 306,999.98 and J: 259,456.00. The total
    # carried is Part 2's J, 259,456.00.
    worksheet = return_et()

    assert worksheet.get(CHART_2019_PART_1_AMOUNT_A).value == D("433456.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_C).value == D("250544.00")
    assert worksheet.get(CHART_2019_AMOUNT_D).value == D("240544.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_E).value == D("10000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNTS_F_AND_G).value == D("550000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_H).value == D("275000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_I).value == D("10000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_K).value == D("192912.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_L).value == D("192912.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_C).value == D("307088.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_E).value == D("66544.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_F).value == D("275000.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_G).value == D("66544.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_I).value == D("259456.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_J).value == D("259456.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_K).value == D("259456.00")
    assert worksheet.get(CHART_2019_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2019_TOTAL_CARRIED).value == D("259456.00")


def test_chart_2020_carries_259456_without_part_2() -> None:
    # Chart 2020 takes Chart 2 line 19 as amount D: A is 441,692.00; B is 259,456.00, so C is
    # 182,236.00; D is 45,833.34 and E is 136,402.66. F (line 6) is 0 and G (line 12) is -60,000, a
    # loss, so F plus G is negative and is entered as "0": H is 0 and I is 0; K is 259,456.00 and L
    # is 259,456.00. The additional deduction is not claimed; the total carried is 259,456.00.
    worksheet = return_et()

    assert worksheet.get(CHART_2020_PART_1_AMOUNT_A).value == D("441692.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_C).value == D("182236.00")
    assert worksheet.get(CHART_2020_AMOUNT_D).value == D("45833.34")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_E).value == D("136402.66")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_K).value == D("259456.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_L).value == D("259456.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_C).value == D("240544.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_E).value == D("194710.66")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_I).value == D("259456.00")
    assert worksheet.get(CHART_2020_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2020_TOTAL_CARRIED).value == D("259456.00")


def test_charts_2021_to_2024_carry_259456() -> None:
    # Charts 2021, 2022 and 2023 report nothing and carry 259,456.00 as amount B (D is Chart 2 line
    # 19, 45,833.34): Chart 2021 has A 446,109.00, C 186,653.00 and E 140,819.66; Chart 2022 has A
    # 456,815.00, C 197,359.00 and E 151,525.66; Chart 2023 has A 485,595.00, C 226,139.00 and E
    # 180,305.66; in each K is 0, M (K + B) is 259,456.00 and N is the lesser of 280,000.00,
    # 306,999.98 and M: 259,456.00; the total carried is M, 259,456.00. Chart 2024 Period 1 (A
    # 508,418.00) has C 248,962.00 and E 203,128.66, nothing reported, so L is 0, N is 259,456.00
    # and O is 259,456.00; Period 2 (A 625,000.00) has B 259,456.00, C 365,544.00 and E 319,710.66,
    # N 259,456.00 and O 259,456.00.
    worksheet = return_et()

    assert worksheet.get(CHART_2021_PART_1_AMOUNT_A).value == D("446109.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_C).value == D("186653.00")
    assert worksheet.get(CHART_2021_AMOUNT_D).value == D("45833.34")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_E).value == D("140819.66")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_M).value == D("259456.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_N).value == D("259456.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_C).value == D("240544.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_E).value == D("194710.66")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_K).value == D("259456.00")
    assert worksheet.get(CHART_2021_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2021_TOTAL_CARRIED).value == D("259456.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_A).value == D("456815.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_C).value == D("197359.00")
    assert worksheet.get(CHART_2022_AMOUNT_D).value == D("45833.34")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_E).value == D("151525.66")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_M).value == D("259456.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_N).value == D("259456.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_C).value == D("240544.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_E).value == D("194710.66")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_K).value == D("259456.00")
    assert worksheet.get(CHART_2022_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2022_TOTAL_CARRIED).value == D("259456.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_A).value == D("485595.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_C).value == D("226139.00")
    assert worksheet.get(CHART_2023_AMOUNT_D).value == D("45833.34")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_E).value == D("180305.66")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_M).value == D("259456.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_N).value == D("259456.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_C).value == D("240544.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_E).value == D("194710.66")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_K).value == D("259456.00")
    assert worksheet.get(CHART_2023_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2023_TOTAL_CARRIED).value == D("259456.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_A).value == D("508418.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_C).value == D("248962.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_E).value == D("203128.66")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_N).value == D("259456.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_O).value == D("259456.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_A).value == D("625000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_C).value == D("365544.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_E).value == D("319710.66")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_N).value == D("259456.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_O).value == D("259456.00")


def test_chart_2025_part_1_carries_259456_into_part_2() -> None:
    # Chart 2025 Part 1 (A 522,145.00) has C 262,689.00 and E 216,855.66; amounts F to J are 0, so
    # K, M and N are 0 and P is 259,456.00; Q is 259,456.00.
    worksheet = return_et()

    assert worksheet.get(CHART_2025_PART_1_AMOUNT_A).value == D("522145.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_C).value == D("262689.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_E).value == D("216855.66")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_P).value == D("259456.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_Q).value == D("259456.00")


def test_chart_2025_part_2_caps_q_at_280000() -> None:
    # Chart 2025 Part 2 (A 625,000.00): B (Part 1's P) is 259,456.00, C is 365,544.00 and E is
    # 319,710.66; F (line 10700 less the amounts not to include, none) is 700,000; G and H are 0; I
    # is read from Form T2017: the 2025 line 2 row claims 100,000 and has no earlier claim, so its
    # change is -100,000. F to J add to 600,000.00 and K is 300,000.00; L is 0, so M is 300,000.00;
    # N is the lesser of E (319,710.66) and M: 300,000.00; O (amount B) is 259,456.00 and P is
    # 559,456.00; Q is the lesser of 280,000.00, 306,999.98 and P (559,456.00): 280,000.00, the
    # annual gains limit, the maximum for line 25400.
    worksheet = return_et()

    assert worksheet.get(CHART_2025_PART_2_AMOUNT_A).value == D("625000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_C).value == D("365544.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_E).value == D("319710.66")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_F).value == D("700000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNTS_F_TO_J).value == D("600000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_K).value == D("300000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_M).value == D("300000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_N).value == D("300000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("559456.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("280000.00")


def test_line_25400_25700_net_income_and_taxable_income() -> None:
    # The filer claims all of it (a chosen figure), 280,000, so line 25400 is 280,000.00 and line
    # 25700 is 30,000.00 (line 25300) + 280,000.00 = 310,000.00. Line 26000, the taxable income, is
    # 360,000.00 - 310,000.00 = 50,000.00.
    worksheet = return_et()

    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("280000.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("310000.00")
    assert worksheet.get(NET_INCOME).value == D("360000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("50000.00")


def test_without_the_chart_2016_additional_deduction_carries_20000() -> None:
    # Chart 2016 Part 2 is not completed, so Part 1 G (20000.00) is the total carried. Chart 2017
    # takes that as B: C is 417858.00 less 20000.00 = 397858.00, E is 397858.00 less D (45833.34) =
    # 352024.66, and K is I (50000.00) plus B (20000.00) = 70000.00, the total carried.
    worksheet = return_et(t657_chart_2016_claims_additional_deduction=0)

    assert worksheet.get(CHART_2016_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2016_TOTAL_CARRIED).value == D("20000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_C).value == D("397858.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_E).value == D("352024.66")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_K).value == D("70000.00")
    assert worksheet.get(CHART_2017_TOTAL_CARRIED).value == D("70000.00")


def test_without_the_chart_2019_additional_deduction_carries_192912() -> None:
    # Chart 2019 Part 2 is not completed, so Part 1 K (192912.00) is the total carried. Chart 2020
    # takes it as B: C is 441692.00 less 192912.00 = 248780.00, and K is I (0.00) plus B =
    # 192912.00. Chart 2025 Part 2 P is 492912.00, so Q, and line 25400, stay at the 280000.00
    # maximum.
    worksheet = return_et(t657_chart_2019_claims_additional_deduction=0)

    assert worksheet.get(CHART_2019_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2019_TOTAL_CARRIED).value == D("192912.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_C).value == D("248780.00")
    assert worksheet.get(CHART_2020_TOTAL_CARRIED).value == D("192912.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("492912.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("280000.00")
