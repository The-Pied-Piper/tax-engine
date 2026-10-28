"""CA-ON 2025 end to end: return eu (Form T657 Step 1, Step 2, Charts 2016 to 2025 with QSBCS, QFFP
and ordinary share dispositions)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ABIL_AFTER_QBT_REDUCTION,
    ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025,
    ALLOWABLE_BUSINESS_INVESTMENT_LOSS,
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
    CHART_2_LINE_19,
    CHART_2_NUMERATOR_ONE,
    CHART_2016_AMOUNT_B,
    CHART_2016_PART_1_AMOUNT_A,
    CHART_2016_PART_1_AMOUNT_C,
    CHART_2016_PART_2_AMOUNT_A,
    CHART_2016_PART_2_AMOUNT_C,
    CHART_2016_PART_2_AMOUNT_E,
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
    CHART_2017_PART_2_AMOUNT_F,
    CHART_2017_PART_2_AMOUNT_G,
    CHART_2017_PART_2_AMOUNT_I,
    CHART_2017_PART_2_AMOUNT_J,
    CHART_2017_PART_2_AMOUNT_K,
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
    CHART_2019_PART_1_AMOUNT_K,
    CHART_2019_PART_1_AMOUNT_L,
    CHART_2019_PART_2_AMOUNT_A,
    CHART_2019_PART_2_AMOUNT_C,
    CHART_2019_PART_2_AMOUNT_E,
    CHART_2019_PART_2_AMOUNT_I,
    CHART_2019_PART_2_APPLIES,
    CHART_2019_TOTAL_CARRIED,
    CHART_2020_AMOUNT_D,
    CHART_2020_PART_1_AMOUNT_A,
    CHART_2020_PART_1_AMOUNT_C,
    CHART_2020_PART_1_AMOUNT_E,
    CHART_2020_PART_1_AMOUNT_H,
    CHART_2020_PART_1_AMOUNT_I,
    CHART_2020_PART_1_AMOUNT_K,
    CHART_2020_PART_1_AMOUNT_L,
    CHART_2020_PART_1_AMOUNTS_F_AND_G,
    CHART_2020_PART_2_AMOUNT_A,
    CHART_2020_PART_2_AMOUNT_C,
    CHART_2020_PART_2_AMOUNT_E,
    CHART_2020_PART_2_AMOUNT_F,
    CHART_2020_PART_2_AMOUNT_G,
    CHART_2020_PART_2_AMOUNT_I,
    CHART_2020_PART_2_AMOUNT_J,
    CHART_2020_PART_2_AMOUNT_K,
    CHART_2020_PART_2_APPLIES,
    CHART_2020_TOTAL_CARRIED,
    CHART_2021_AMOUNT_D,
    CHART_2021_PART_1_AMOUNT_A,
    CHART_2021_PART_1_AMOUNT_C,
    CHART_2021_PART_1_AMOUNT_E,
    CHART_2021_PART_1_AMOUNT_H,
    CHART_2021_PART_1_AMOUNT_I,
    CHART_2021_PART_1_AMOUNT_J,
    CHART_2021_PART_1_AMOUNT_K,
    CHART_2021_PART_1_AMOUNT_M,
    CHART_2021_PART_1_AMOUNT_N,
    CHART_2021_PART_1_AMOUNTS_F_AND_G,
    CHART_2021_PART_2_AMOUNT_A,
    CHART_2021_PART_2_AMOUNT_C,
    CHART_2021_PART_2_AMOUNT_E,
    CHART_2021_PART_2_AMOUNT_F,
    CHART_2021_PART_2_AMOUNT_G,
    CHART_2021_PART_2_AMOUNT_H,
    CHART_2021_PART_2_AMOUNT_I,
    CHART_2021_PART_2_AMOUNT_K,
    CHART_2021_PART_2_AMOUNT_L,
    CHART_2021_PART_2_AMOUNT_M,
    CHART_2021_PART_2_APPLIES,
    CHART_2021_TOTAL_CARRIED,
    CHART_2022_AMOUNT_D,
    CHART_2022_PART_1_AMOUNT_A,
    CHART_2022_PART_1_AMOUNT_C,
    CHART_2022_PART_1_AMOUNT_E,
    CHART_2022_PART_1_AMOUNT_H,
    CHART_2022_PART_1_AMOUNT_I,
    CHART_2022_PART_1_AMOUNT_J,
    CHART_2022_PART_1_AMOUNT_K,
    CHART_2022_PART_1_AMOUNT_M,
    CHART_2022_PART_1_AMOUNT_N,
    CHART_2022_PART_1_AMOUNTS_F_AND_G,
    CHART_2022_PART_2_AMOUNT_A,
    CHART_2022_PART_2_AMOUNT_C,
    CHART_2022_PART_2_AMOUNT_E,
    CHART_2022_PART_2_AMOUNT_F,
    CHART_2022_PART_2_AMOUNT_G,
    CHART_2022_PART_2_AMOUNT_H,
    CHART_2022_PART_2_AMOUNT_I,
    CHART_2022_PART_2_AMOUNT_K,
    CHART_2022_PART_2_AMOUNT_L,
    CHART_2022_PART_2_AMOUNT_M,
    CHART_2022_PART_2_APPLIES,
    CHART_2022_TOTAL_CARRIED,
    CHART_2023_AMOUNT_D,
    CHART_2023_PART_1_AMOUNT_A,
    CHART_2023_PART_1_AMOUNT_C,
    CHART_2023_PART_1_AMOUNT_E,
    CHART_2023_PART_1_AMOUNT_H,
    CHART_2023_PART_1_AMOUNT_I,
    CHART_2023_PART_1_AMOUNT_J,
    CHART_2023_PART_1_AMOUNT_K,
    CHART_2023_PART_1_AMOUNT_M,
    CHART_2023_PART_1_AMOUNT_N,
    CHART_2023_PART_1_AMOUNTS_F_AND_G,
    CHART_2023_PART_2_AMOUNT_A,
    CHART_2023_PART_2_AMOUNT_C,
    CHART_2023_PART_2_AMOUNT_E,
    CHART_2023_PART_2_AMOUNT_F,
    CHART_2023_PART_2_AMOUNT_G,
    CHART_2023_PART_2_AMOUNT_H,
    CHART_2023_PART_2_AMOUNT_I,
    CHART_2023_PART_2_AMOUNT_K,
    CHART_2023_PART_2_AMOUNT_L,
    CHART_2023_PART_2_AMOUNT_M,
    CHART_2023_PART_2_APPLIES,
    CHART_2023_TOTAL_CARRIED,
    CHART_2024_PERIOD_1_AMOUNT_A,
    CHART_2024_PERIOD_1_AMOUNT_C,
    CHART_2024_PERIOD_1_AMOUNT_E,
    CHART_2024_PERIOD_1_AMOUNT_I,
    CHART_2024_PERIOD_1_AMOUNT_K,
    CHART_2024_PERIOD_1_AMOUNT_L,
    CHART_2024_PERIOD_1_AMOUNT_N,
    CHART_2024_PERIOD_1_AMOUNT_O,
    CHART_2024_PERIOD_1_AMOUNTS_F_TO_H,
    CHART_2024_PERIOD_2_AMOUNT_A,
    CHART_2024_PERIOD_2_AMOUNT_C,
    CHART_2024_PERIOD_2_AMOUNT_E,
    CHART_2024_PERIOD_2_AMOUNT_I,
    CHART_2024_PERIOD_2_AMOUNT_K,
    CHART_2024_PERIOD_2_AMOUNT_L,
    CHART_2024_PERIOD_2_AMOUNT_N,
    CHART_2024_PERIOD_2_AMOUNT_O,
    CHART_2024_PERIOD_2_AMOUNTS_F_TO_H,
    CHART_2025_PART_1_AMOUNT_A,
    CHART_2025_PART_1_AMOUNT_C,
    CHART_2025_PART_1_AMOUNT_E,
    CHART_2025_PART_1_AMOUNT_K,
    CHART_2025_PART_1_AMOUNT_M,
    CHART_2025_PART_1_AMOUNT_N,
    CHART_2025_PART_1_AMOUNT_P,
    CHART_2025_PART_1_AMOUNT_Q,
    CHART_2025_PART_1_AMOUNTS_F_TO_J,
    CHART_2025_PART_2_AMOUNT_A,
    CHART_2025_PART_2_AMOUNT_C,
    CHART_2025_PART_2_AMOUNT_E,
    CHART_2025_PART_2_AMOUNT_F,
    CHART_2025_PART_2_AMOUNT_G,
    CHART_2025_PART_2_AMOUNT_H,
    CHART_2025_PART_2_AMOUNT_K,
    CHART_2025_PART_2_AMOUNT_M,
    CHART_2025_PART_2_AMOUNT_N,
    CHART_2025_PART_2_AMOUNT_P,
    CHART_2025_PART_2_AMOUNT_Q,
    CHART_2025_PART_2_AMOUNTS_F_TO_J,
    CHART_2025_PART_2_MAXIMUM_CLAIM,
    CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
    CUMULATIVE_GAINS_LIMIT_2025,
    CUMULATIVE_LOSSES_AND_DEDUCTIONS,
    DEDUCTIONS_FROM_NET_INCOME,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025,
    NET_INCOME,
    QBT_ABIL_REDUCTION,
    SCHEDULE_3_LINE_19200,
    SCHEDULE_3_LINE_19900,
    TAXABLE_INCOME,
    TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, t657_reserve_inputs

RESERVES = {
    "t657_chart_2017_amount_f": "300000",
    "t657_chart_2018_amount_f": "300000",
    "t657_chart_2020_amount_f": "200000",
    "t657_chart_2021_amount_f": "500000",
    "t657_chart_2021_amount_g": "40000",
    "t657_chart_2022_amount_f": "300000",
    "t657_chart_2022_amount_g": "20000",
    "t657_chart_2023_amount_f": "300000",
    "t657_chart_2023_amount_g": "30000",
    "t657_chart_2024_period_1_amount_f": "30000.01",
    "t657_chart_2024_period_1_amount_g": "0",
    "t657_chart_2024_period_2_amount_g": "50000",
    "t657_part_1_amount_i": "8000",
    "t657_part_1_amount_j": "6000",
    "t657_part_2_amount_i": "0",
    "t657_part_2_amount_j": "-2000",
}


def return_eu(**overrides: Any) -> Worksheet:
    """Return EU's inputs, as in `returns/2025_return_eu.yaml`: QSBCS, QFFP and QFFP foreclosure
    dispositions and ordinary shares in 2025, Form T657 Charts 2017, 2018 and 2020 to 2023 with
    the additional deduction, and 400000 claimed on line 25400."""
    inputs: dict[str, Any] = {
        # Required arguments of `compute` that the YAML leaves at zero.
        "employment_income": "0",
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "other_income": "10000",
        "qsbcs_dispositions": (
            (
                "400000",
                "100000",
                "0",
            ),
        ),
        "qffp_dispositions": (
            (
                "250000",
                "50000",
                "0",
            ),
        ),
        "qffp_foreclosure_dispositions": (
            (
                "120000",
                "20000",
                "0",
            ),
        ),
        "share_dispositions": (
            (
                "800000",
                "200000",
                "0",
            ),
        ),
        "t657_chart_2_line_18": "60000",
        # Form T2017 line 1 is 600,000; one line 27 row reserves 600,000 in the year of disposition.
        "t2017_amounts": {1: "600000"},
        "t2017_rows": {
            27: (
                {
                    "capital_gain": "1000000",
                    "payable": "1000000",
                    "proceeds": "1000000",
                    "years": 0,
                    "claimed": "600000",
                    "previous": "0",
                },
            ),
        },
        "t657_gains_2002_to_2024": "150000",
        "t657_deductions_claimed_1985_to_2024": "60000",
        "t657_chart_2017_uses_d_instead": 1,
        "t657_chart_2017_amount_d_instead": "412858",
        "t657_chart_2017_claims_additional_deduction": 1,
        "t657_chart_2018_uses_d_instead": 1,
        "t657_chart_2018_amount_d_instead": "326984",
        "t657_chart_2018_claims_additional_deduction": 1,
        "t657_chart_2020_uses_d_instead": 1,
        "t657_chart_2020_amount_d_instead": "281692",
        "t657_chart_2020_claims_additional_deduction": 1,
        "t657_chart_2021_uses_d_instead": 1,
        "t657_chart_2021_amount_d_instead": "336109",
        "t657_chart_2021_amount_i": "100000",
        "t657_chart_2021_part_2_amount_g": "100000",
        "t657_chart_2021_claims_additional_deduction": 1,
        "t657_chart_2022_uses_d_instead": 1,
        "t657_chart_2022_amount_d_instead": "282924",
        "t657_chart_2022_amount_i": "8000",
        "t657_chart_2022_part_2_amount_g": "140000",
        "t657_chart_2022_claims_additional_deduction": 1,
        "t657_chart_2023_uses_d_instead": 1,
        "t657_chart_2023_amount_d_instead": "258519",
        "t657_chart_2023_amount_i": "20000",
        "t657_chart_2023_part_2_amount_g": "100000",
        "t657_chart_2023_claims_additional_deduction": 1,
        "t657_chart_2024_period_1_amount_h": "20000",
        "t657_chart_2024_period_1_amount_j": "5000",
        "t657_chart_2024_period_2_amount_h": "10000",
        "t657_chart_2024_period_2_amount_j": "4000",
        "t657_part_1_amount_f": "50000",
        "t657_part_1_amount_g": "20000",
        "t657_part_1_amount_h": "15000",
        "t657_part_1_amount_l": "4000",
        "t657_part_2_excluded_f": "50000",
        "t657_part_2_excluded_g": "20000",
        "t657_part_2_excluded_h": "10000",
        "t657_part_2_amount_l": "7000",
        "capital_gains_deduction_claimed": "400000",
    }
    return compute(**t657_reserve_inputs(RESERVES, {**inputs, **overrides}))


def test_step_1_step_2_and_chart_2_line_19_derive_the_annual_gains_limit_599000() -> None:
    # Step 1: line 1 is 300,000.00 + 200,000.00 + 100,000.00 = 600,000.00 (lines 10700, 11000 and
    # 12400, not the ordinary shares); line 2 (Form T2017 line 13) is 598,000 (line 6, 600,000, plus
    # line 12, -2,000, the 2025 reserve of 2,000 on a QSBCS disposition), so line 3 is 1,198,000.00;
    # line 5 is 599,000.00; line 6 (Form T2048 line 17216) is 0; line 7 is 599,000.00. Line 8
    # (Schedule 3 line 19900, 600,000.00 less the -2,000 of line 19200) is 599,000.00; lines 9 and
    # 11 are 0; lines 10 and 12 are 599,000.00; line 13 is 599,000.00. Lines 14 to 20 are 0; line
    # 21, the annual gains limit, is 599,000.00. Chart 2: only line 18 (2001 to 2024 deductions) is
    # filed, 60,000; lines 1 to 14 are 0 and IR is blank (line 14 is 0), so line 15 to line 17 are 0
    # and line 19 is 60,000.00. Step 2: line 8 is 150,000 (2002 to 2024) + 599,000.00 = 749,000.00,
    # so line 9 is 749,000.00; line 17 is 60,000 and the other lines are 0, so line 18 is 60,000.00
    # and line 19, the cumulative gains limit, is 689,000.00.
    worksheet = return_eu()

    assert worksheet.get(ANNUAL_GAINS_LINE_2).value == D("598000")
    assert worksheet.get(SCHEDULE_3_LINE_19200).value == D("-2000")
    assert worksheet.get(ANNUAL_GAINS_SCHEDULE_3_TOTAL).value == D("600000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_3).value == D("1198000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE).value == D("599000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_5).value == D("599000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_7).value == D("599000.00")
    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("599000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_10).value == D("599000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_12).value == D("599000.00")
    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025).value == D("599000.00")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("599000.00")
    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025).value == D("749000.00")
    assert worksheet.get(CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS).value == D("749000.00")
    assert worksheet.get(CUMULATIVE_LOSSES_AND_DEDUCTIONS).value == D("60000.00")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("689000.00")
    assert worksheet.get(CHART_2_LINE_19).value == D("60000.00")
    assert worksheet.get(CHART_2_NUMERATOR_ONE).value == D("1.00")


def test_charts_2016_to_2019_part_2_applies_for_2017_and_2018() -> None:
    # Chart 2016 reports nothing: B is Chart 2 line 19, 60,000.00, so C is 412,088.00 - 60,000.00 =
    # 352,088.00; D, E, F, G and H are 0, the additional deduction is not claimed and the total
    # carried is G, 0. Chart 2017 uses the (2017-1) calculation: D is the entered 412,858. A is
    # 417,858.00, B is 0, so C is 417,858.00 and E is 5,000.00. F (line 6, QFFP) is 300,000 and G
    # (line 12) is 0: H is 150,000.00 and I, the lesser of E and H, is 5,000.00; K is 5,000.00 and L
    # is 5,000.00. The additional deduction is claimed and E (5,000.00) is equal to or less than
    # 599,000.00, 689,000.00 and K (5,000.00), so Part 2 is completed: A is 500,000.00; B (Part 1's
    # K) is 5,000.00, so C is 495,000.00; D is 412,858, so E is 82,142.00, the additional $82,142
    # the form prints; F (line 6 x 1/2) is 150,000.00; G is the lesser of E and F: 82,142.00; H is
    # 5,000.00 and I is 87,142.00; J is the lesser of F and I: 87,142.00; K is 87,142.00. The total
    # carried is Part 2's J, 87,142.00. Chart 2018 uses the (2018-1) calculation: D is the entered
    # 326,984. A is 424,126.00; B is 87,142.00, so C is 336,984.00 and E is 10,000.00. F (line 6) is
    # 300,000 and G is 0: H is 150,000.00 and I is 10,000.00; K is 97,142.00 and L is 97,142.00. The
    # additional deduction is claimed and E is equal to or less than 599,000.00, 689,000.00 and K,
    # so Part 2 is completed: A is 500,000.00; B (Part 1's K) is 97,142.00 and C is 402,858.00; D is
    # 326,984, so E is 75,874.00, the additional $75,874 the form prints; F is 150,000.00 (line 6 x
    # 1/2); G is 75,874.00; H is 97,142.00 and I is 173,016.00; J is the lesser of F and I:
    # 150,000.00; K is 150,000.00. The total carried is Part 2's J, 150,000.00. Chart 2019 reports
    # nothing and takes Chart 2 line 19 (60,000.00) as D: A is 433,456.00, B is 150,000.00, C is
    # 283,456.00 and E is 223,456.00; K is B, 150,000.00, and so is the total carried.
    worksheet = return_eu()

    assert worksheet.get(CHART_2016_PART_1_AMOUNT_A).value == D("412088.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_C).value == D("352088.00")
    assert worksheet.get(CHART_2016_AMOUNT_B).value == D("60000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_C).value == D("500000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_E).value == D("440000.00")
    assert worksheet.get(CHART_2016_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2016_TOTAL_CARRIED).value == D("0.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_A).value == D("417858.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_C).value == D("417858.00")
    assert worksheet.get(CHART_2017_AMOUNT_D).value == D("412858.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_E).value == D("5000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNTS_F_AND_G).value == D("300000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_H).value == D("150000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_I).value == D("5000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_K).value == D("5000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_L).value == D("5000.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_C).value == D("495000.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_E).value == D("82142.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_F).value == D("150000.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_G).value == D("82142.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_I).value == D("87142.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_J).value == D("87142.00")
    assert worksheet.get(CHART_2017_PART_2_AMOUNT_K).value == D("87142.00")
    assert worksheet.get(CHART_2017_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2017_TOTAL_CARRIED).value == D("87142.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_A).value == D("424126.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_C).value == D("336984.00")
    assert worksheet.get(CHART_2018_AMOUNT_D).value == D("326984.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_E).value == D("10000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNTS_F_AND_G).value == D("300000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_H).value == D("150000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_I).value == D("10000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_K).value == D("97142.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_L).value == D("97142.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_C).value == D("402858.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_E).value == D("75874.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_F).value == D("150000.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_G).value == D("75874.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_I).value == D("173016.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_J).value == D("150000.00")
    assert worksheet.get(CHART_2018_PART_2_AMOUNT_K).value == D("150000.00")
    assert worksheet.get(CHART_2018_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2018_TOTAL_CARRIED).value == D("150000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_A).value == D("433456.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_C).value == D("283456.00")
    assert worksheet.get(CHART_2019_AMOUNT_D).value == D("60000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_E).value == D("223456.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_K).value == D("150000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_L).value == D("150000.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_C).value == D("350000.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_E).value == D("290000.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_I).value == D("150000.00")
    assert worksheet.get(CHART_2019_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2019_TOTAL_CARRIED).value == D("150000.00")


def test_chart_2020_part_2_applies_and_carries_100000() -> None:
    # Chart 2020 uses the (2020-1) calculation: D is the entered 281,692. A is 441,692.00; B is
    # 150,000.00, so C is 291,692.00 and E is 10,000.00. F (line 6) is 200,000 and G is 0: H is
    # 100,000.00 and I is 10,000.00; K is 160,000.00 and L is 160,000.00. The additional deduction
    # is claimed and E is equal to or less than all three amounts, so Part 2 is completed: A is
    # 500,000.00; B (Part 1's K) is 160,000.00 and C is 340,000.00; D is 281,692, so E is 58,308.00,
    # the additional $58,308 the form prints; F is 100,000.00 (line 6 x 1/2); G is 58,308.00; H is
    # 160,000.00 and I is 218,308.00; J is the lesser of F and I: 100,000.00; K is 100,000.00. The
    # total carried is Part 2's J, 100,000.00.
    worksheet = return_eu()

    assert worksheet.get(CHART_2020_PART_1_AMOUNT_A).value == D("441692.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_C).value == D("291692.00")
    assert worksheet.get(CHART_2020_AMOUNT_D).value == D("281692.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_E).value == D("10000.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNTS_F_AND_G).value == D("200000.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_H).value == D("100000.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_I).value == D("10000.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_K).value == D("160000.00")
    assert worksheet.get(CHART_2020_PART_1_AMOUNT_L).value == D("160000.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_C).value == D("340000.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_E).value == D("58308.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_F).value == D("100000.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_G).value == D("58308.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_I).value == D("218308.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_J).value == D("100000.00")
    assert worksheet.get(CHART_2020_PART_2_AMOUNT_K).value == D("100000.00")
    assert worksheet.get(CHART_2020_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2020_TOTAL_CARRIED).value == D("100000.00")


def test_chart_2021_part_2_applies_and_carries_163891() -> None:
    # Chart 2021 uses the (2021-1) calculation: D is the entered 336,109. A is 446,109.00; B is
    # 100,000.00, so C is 346,109.00 and E is 10,000.00. F (line 6, QFFP) is 500,000 and G (line 12,
    # QSBCS) is 40,000: 540,000.00 x 1/2 is H, 270,000.00; the box 30 amount of a 2025 T3 slip for a
    # 2021 disposition is 100,000, so I is 50,000.00 and J (H plus I) is 320,000.00. K is the lesser
    # of E and J: 10,000.00; L (amount B) is 100,000.00 and M is 110,000.00; N is 110,000.00. The
    # additional deduction is claimed and E is equal to or less than 599,000.00, 689,000.00 and M,
    # so Part 2 is completed: A is 500,000.00; B (Part 1's M) is 110,000.00, so C is 390,000.00; D
    # is 336,109, so E is 53,891.00, the additional $53,891 the form prints; F (line 6 x 1/2) is
    # 250,000.00; G (the box 30 amount for the QFFP disposed of in 2021, 100,000, x 1/2) is
    # 50,000.00; H is 300,000.00; I is the lesser of E and H: 53,891.00; J (amount B) is 110,000.00
    # and K is 163,891.00; L is the lesser of H and K: 163,891.00; M is 163,891.00. The total
    # carried is Part 2's L, 163,891.00.
    worksheet = return_eu()

    assert worksheet.get(CHART_2021_PART_1_AMOUNT_A).value == D("446109.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_C).value == D("346109.00")
    assert worksheet.get(CHART_2021_AMOUNT_D).value == D("336109.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_E).value == D("10000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNTS_F_AND_G).value == D("540000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_H).value == D("270000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_I).value == D("50000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_J).value == D("320000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_K).value == D("10000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_M).value == D("110000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_N).value == D("110000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_C).value == D("390000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_E).value == D("53891.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_F).value == D("250000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_G).value == D("50000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_H).value == D("300000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_I).value == D("53891.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_K).value == D("163891.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_L).value == D("163891.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_M).value == D("163891.00")
    assert worksheet.get(CHART_2021_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2021_TOTAL_CARRIED).value == D("163891.00")


def test_chart_2022_part_2_applies_and_carries_217076() -> None:
    # Chart 2022 uses the (2022-1) calculation: D is the entered 282,924. A is 456,815.00; B is
    # 163,891.00, so C is 292,924.00 and E is 10,000.00. F (line 6) is 300,000 and G (line 12) is
    # 20,000: H is 160,000.00; the T3 box 30 amount is 8,000, so I is 4,000.00 and J is 164,000.00.
    # K is the lesser of E and J: 10,000.00; M is 173,891.00. The additional deduction is claimed
    # and Part 2 is completed: A is 500,000.00; B is 173,891.00 and C is 326,109.00; D is 282,924,
    # so E is 43,185.00, the additional $43,185 the form prints; F is 150,000.00 (300,000 x 1/2); G
    # (the box 30 amount for the QFFP, 140,000, x 1/2) is 70,000.00; H is 220,000.00; I is the
    # lesser of E and H: 43,185.00; K (I plus B) is 217,076.00; L is the lesser of H and K:
    # 217,076.00; M is 217,076.00. The total carried is Part 2's L, 217,076.00.
    worksheet = return_eu()

    assert worksheet.get(CHART_2022_PART_1_AMOUNT_A).value == D("456815.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_C).value == D("292924.00")
    assert worksheet.get(CHART_2022_AMOUNT_D).value == D("282924.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_E).value == D("10000.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNTS_F_AND_G).value == D("320000.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_H).value == D("160000.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_I).value == D("4000.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_J).value == D("164000.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_K).value == D("10000.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_M).value == D("173891.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_N).value == D("173891.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_C).value == D("326109.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_E).value == D("43185.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_F).value == D("150000.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_G).value == D("70000.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_H).value == D("220000.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_I).value == D("43185.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_K).value == D("217076.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_L).value == D("217076.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_M).value == D("217076.00")
    assert worksheet.get(CHART_2022_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2022_TOTAL_CARRIED).value == D("217076.00")


def test_chart_2023_part_2_applies_and_carries_200000() -> None:
    # Chart 2023 uses the (2023-1) calculation: D is the entered 258,519. A is 485,595.00; B is
    # 217,076.00, so C is 268,519.00 and E is 10,000.00. F (line 6) is 300,000 and G (line 12) is
    # 30,000: H is 165,000.00; the T3 box 30 amount is 20,000, so I is 10,000.00 and J is
    # 175,000.00. K is the lesser of E and J: 10,000.00; M is 227,076.00 and N is 227,076.00. The
    # additional deduction is claimed and Part 2 is completed: A is 500,000.00; B is 227,076.00 and
    # C is 272,924.00; D is 258,519, so E is 14,405.00, the additional $14,405 the form prints; F is
    # 150,000.00 (300,000 x 1/2); G (the box 30 amount for the QFFP, 100,000, x 1/2) is 50,000.00; H
    # is 200,000.00; I is the lesser of E and H: 14,405.00; K (I plus B) is 241,481.00; L is the
    # lesser of H and K: 200,000.00; M is 200,000.00. The total carried is Part 2's L, 200,000.00.
    worksheet = return_eu()

    assert worksheet.get(CHART_2023_PART_1_AMOUNT_A).value == D("485595.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_C).value == D("268519.00")
    assert worksheet.get(CHART_2023_AMOUNT_D).value == D("258519.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_E).value == D("10000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNTS_F_AND_G).value == D("330000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_H).value == D("165000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_I).value == D("10000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_J).value == D("175000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_K).value == D("10000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_M).value == D("227076.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_N).value == D("227076.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_A).value == D("500000.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_C).value == D("272924.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_E).value == D("14405.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_F).value == D("150000.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_G).value == D("50000.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_H).value == D("200000.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_I).value == D("14405.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_K).value == D("241481.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_L).value == D("200000.00")
    assert worksheet.get(CHART_2023_PART_2_AMOUNT_M).value == D("200000.00")
    assert worksheet.get(CHART_2023_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2023_TOTAL_CARRIED).value == D("200000.00")


def test_periods_1_and_2_of_2024_carry_246000_01() -> None:
    # Chart 2024 Period 1 (A 508,418.00): B is 200,000.00, so C is 308,418.00 and E is 248,418.00 (D
    # is Chart 2 line 19). Form T2017 gives F (line 6) 30,000.01 and G (line 12) 0: the reserves of
    # dispositions in Period 1 of 2024 reported on a T5013 slip by a partnership whose year began
    # before June 25, 2024 are Chart 2025 Part 1's, not this chart's (Guide T4037); H (T3 box 30) is
    # 20,000: F to H add to 50,000.01 and I is 50,000.01 x 1/2 = 25,000.005, rounded half up to the
    # cent: 25,000.01. J (the T2048 line 17216 portion) is 5,000, so K is 20,000.01; L is the lesser
    # of E and K: 20,000.01; M (amount B) is 200,000.00 and N is 220,000.01; O is 220,000.01. Period
    # 2 (A 625,000.00): B is Period 1's N, 220,000.01, so C is 404,999.99 and E is 344,999.99. F is
    # 0, G is 50,000 and H is 10,000: 60,000.00, I is 30,000.00; J is 4,000, so K is 26,000.00; L is
    # 26,000.00, N is 246,000.01 and O is 246,000.01.
    worksheet = return_eu()

    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_A).value == D("508418.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_C).value == D("308418.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_E).value == D("248418.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNTS_F_TO_H).value == D("50000.01")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_I).value == D("25000.01")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_K).value == D("20000.01")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_L).value == D("20000.01")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_N).value == D("220000.01")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_O).value == D("220000.01")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_A).value == D("625000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_C).value == D("404999.99")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_E).value == D("344999.99")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNTS_F_TO_H).value == D("60000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_I).value == D("30000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_K).value == D("26000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_L).value == D("26000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_N).value == D("246000.01")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_O).value == D("246000.01")


def test_chart_2024_amount_k_below_zero_stays_negative_and_lowers_the_total_carried() -> None:
    # Chart 2024 Period 1 "Amount I minus amount J" prints no "(if negative, enter "0")". I is
    # 25,000.01 as above and J (the T2048 line 17216 portion) is 30,000.01 (a chosen figure), so K
    # is 25,000.01 - 30,000.01 = -5,000.00 and L, the lesser of E (248,418.00) and K, is -5,000.00;
    # M (amount B) is 200,000.00 and N is 195,000.00. Period 2: B is 195,000.00, so C is
    # 430,000.00 and E is 370,000.00 (D is 60,000). I is 30,000.00 and J is 35,000 (a chosen
    # figure), so K is -5,000.00, L is -5,000.00 and N is 190,000.00.
    worksheet = return_eu(
        t657_chart_2024_period_1_amount_j="30000.01",
        t657_chart_2024_period_2_amount_j="35000",
    )

    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_K).value == D("-5000.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_L).value == D("-5000.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_N).value == D("195000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_C).value == D("430000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_E).value == D("370000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_K).value == D("-5000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_L).value == D("-5000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_N).value == D("190000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_O).value == D("190000.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_C).value == D("332145.00")


def test_chart_2025_part_1_carries_291500_01_into_part_2() -> None:
    # Chart 2025 Part 1 (A 522,145.00): B is Period 2's N, 246,000.01, so C is 276,144.99 and E is
    # 216,144.99. The T3 or T5013 amounts are F 50,000 (box 57 or 153), G 20,000 (box 55 or 154), H
    # 15,000 (box 155) and the Form T2017 amounts I 8,000 (line 6) and J 6,000 (line 12), the
    # reserves of Period 1 dispositions reported on a slip by a partnership whose year began before
    # June 25, 2024: F to J add to 99,000.00 and K is 49,500.00. L (the T2048 line 17216 portion) is
    # 4,000, so M is 45,500.00 and N, the lesser of E and M, is 45,500.00; O (amount B) is
    # 246,000.01 and P is 291,500.01; Q is 291,500.01.
    worksheet = return_eu()

    assert worksheet.get(CHART_2025_PART_1_AMOUNT_A).value == D("522145.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_C).value == D("276144.99")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_E).value == D("216144.99")
    assert worksheet.get(CHART_2025_PART_1_AMOUNTS_F_TO_J).value == D("99000.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_K).value == D("49500.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_M).value == D("45500.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_N).value == D("45500.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_P).value == D("291500.01")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_Q).value == D("291500.01")


def test_chart_2025_part_2_caps_q_at_543500_01() -> None:
    # Chart 2025 Part 2 (A 625,000.00): B is Part 1's P, 291,500.01, so C is 333,499.99 and E is
    # 273,499.99. F is line 10700 less the 50,000 not to include, 250,000; G is line 11000 less
    # 20,000, 180,000; H is line 12400 less 10,000, 90,000. I (Form T2017 line 6, 2025 reserves) is
    # 0 and J (line 12) is -2,000, a loss: F to J add to 518,000.00 and K is 259,000.00. L is
    # 7,000, so M is 252,000.00 and N is the lesser of E (273,499.99) and M: 252,000.00. O (amount
    # B) is 291,500.01, so P is 543,500.01 and Q is the lesser of 599,000.00, 689,000.00 and P:
    # 543,500.01, the maximum for line 25400.
    worksheet = return_eu()

    assert worksheet.get(CHART_2025_PART_2_AMOUNT_A).value == D("625000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_C).value == D("333499.99")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_E).value == D("273499.99")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_F).value == D("250000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_G).value == D("180000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_H).value == D("90000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNTS_F_TO_J).value == D("518000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_K).value == D("259000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_M).value == D("252000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_N).value == D("252000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("543500.01")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("543500.01")


def test_line_25400_25700_net_income_and_taxable_income() -> None:
    # The filer claims 400,000 (a chosen figure, less than the maximum), so line 25400 is 400,000.00
    # and line 25700 is 400,000.00. Line 26000, the taxable income, is 609,000.00 - 400,000.00 =
    # 209,000.00.
    worksheet = return_eu()

    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("400000.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("400000.00")
    assert worksheet.get(NET_INCOME).value == D("609000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("209000.00")


def test_without_the_chart_2017_additional_deduction_carries_5000() -> None:
    # Chart 2017 Part 2 is not completed, so Part 1 K (5000.00) is the total carried. Chart 2018
    # takes it as B: C is 424126.00 less 5000.00 = 419126.00 and E is 419126.00 less D (326984) =
    # 92142.00. I is the lesser of E and H (150000.00), 92142.00, so K is I plus B = 97142.00.
    worksheet = return_eu(t657_chart_2017_claims_additional_deduction=0)

    assert worksheet.get(CHART_2017_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2017_TOTAL_CARRIED).value == D("5000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_C).value == D("419126.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_E).value == D("92142.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_K).value == D("97142.00")
    assert worksheet.get(CHART_2018_TOTAL_CARRIED).value == D("150000.00")


def test_without_the_chart_2022_additional_deduction_carries_173891() -> None:
    # Chart 2022 Part 2 is not completed, so Part 1 M (173891.00) is the total carried. Chart 2023
    # takes it as B: C is 485595.00 less 173891.00 = 311704.00, and E is 311704.00 less D (258519) =
    # 53185.00.
    worksheet = return_eu(t657_chart_2022_claims_additional_deduction=0)

    assert worksheet.get(CHART_2022_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2022_TOTAL_CARRIED).value == D("173891.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_C).value == D("311704.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_E).value == D("53185.00")
    assert worksheet.get(CHART_2023_TOTAL_CARRIED).value == D("200000.00")


def test_chart_2025_part_2_amounts_f_to_j_below_zero_is_entered_as_0() -> None:
    # Chart 2025 Part 2 "Add amounts F to J (if negative, enter "0")": I (Form T2017 line 6) is
    # -600,000 (a chosen figure, a 2025 reserve claimed above F, G and H), so F to J add to
    # 250,000.00 + 180,000.00 + 90,000.00 - 600,000.00 - 2,000.00 = -82,000.00, entered as 0.00.
    # K is 0.00. L is 0 (a chosen figure), so M is 0.00, N, the lesser of E (273,499.99) and M, is
    # 0.00 and P is 0.00 + O (291,500.01) = 291,500.01. The filer claims 200,000 (a chosen
    # figure), below that maximum.
    worksheet = return_eu(
        t657_part_2_amount_i="-600000",
        t657_part_2_amount_l="0",
        capital_gains_deduction_claimed="200000",
    )

    assert worksheet.get(CHART_2025_PART_2_AMOUNTS_F_TO_J).value == D("0.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_K).value == D("0.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_M).value == D("0.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_N).value == D("0.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("291500.01")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("200000.00")


def test_chart_2025_part_2_amount_m_below_zero_stays_negative() -> None:
    # Chart 2025 Part 2 "Amount K minus amount L" prints no "(if negative, enter "0")". I (Form
    # T2017 line 6) is -600,000 (a chosen figure) so F to J are entered as 0.00 and K is 0.00; L is
    # 7,000 (a chosen figure), so M is 0.00 - 7,000.00 = -7,000.00 and N, the lesser of E
    # (273,499.99) and M, is -7,000.00. P is -7,000.00 + O (291,500.01) = 284,500.01. The filer
    # claims 200,000 (a chosen figure), below that maximum.
    worksheet = return_eu(
        t657_part_2_amount_i="-600000",
        t657_part_2_amount_l="7000",
        capital_gains_deduction_claimed="200000",
    )

    assert worksheet.get(CHART_2025_PART_2_AMOUNT_K).value == D("0.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_M).value == D("-7000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_N).value == D("-7000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("284500.01")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("200000.00")


def test_chart_2025_part_2_amount_q_below_zero_allows_a_claim_of_0() -> None:
    # I (Form T2017 line 6) is -600,000 (a chosen figure) so F to J are entered as 0.00 and K is
    # 0.00; L is 300,000 (a chosen figure), so M and N are -300,000.00 and P is -300,000.00 + O
    # (291,500.01) = -8,499.99. Q, the lesser of the annual gains limit, the cumulative gains limit
    # and P, is -8,499.99, so nothing can be claimed: the Guide's "any amount ... up to the
    # maximum" leaves a claim of 0.
    worksheet = return_eu(
        t657_part_2_amount_i="-600000",
        t657_part_2_amount_l="300000",
        capital_gains_deduction_claimed="0",
    )

    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("-8499.99")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("-8499.99")
    assert worksheet.get(CHART_2025_PART_2_MAXIMUM_CLAIM).value == D("0.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("0.00")


def test_step_2_line_13_stays_negative_when_the_2024_t2048_amount_is_larger() -> None:
    # Step 2 line 11 is 2,000 (the ABIL claimed for 1985 to 2024, a chosen figure) and line 12 is
    # 3,000 (line 17217 of Form T2048 for 2024, a chosen figure), so line 13 is 2,000 - 3,000 =
    # -1,000.00. The form prints no floor, so the result stays negative. Line 18 is the sum of
    # line 10 (0), line 13 (-1,000.00), the Chart 1 column G total (0), line 15 (the Step 1 line 20
    # total of 0), line 16 (Form T936, 0) and line 17 (the 60,000 of deductions): 59,000.00. Line 19
    # is 749,000.00 - 59,000.00 = 690,000.00.
    worksheet = return_eu(
        t657_abil_claimed_1985_to_2024="2000",
        t657_t2048_line_17217_for_2024="3000",
    )

    assert worksheet.get(ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025).value == D("-1000.00")
    assert worksheet.get(CUMULATIVE_LOSSES_AND_DEDUCTIONS).value == D("59000.00")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("690000.00")


def test_step_1_line_19_is_0_when_the_t2048_abil_reduction_is_the_whole_abil() -> None:
    # A business investment loss of 6,000 with nothing reduced in earlier years: the ABIL (line
    # 21700) is 6,000 x 50% = 3,000.00. Form T2048 line 41 (Part 5 F, line 17217) is the ABIL times
    # line 36 over line 38, and line 36 is the lesser of line 30 and line 38, so the ratio is at
    # most 1 and the reduction is at most 3,000.00. With no amount claimed it is the whole
    # 3,000.00, so Step 1 line 19 is 3,000.00 - 3,000.00 = 0.00. Line 20 is 0 + 0.00 = 0.00, so the
    # annual gains limit (line 21) is the eligible gains of line 13. Step 2 line 18 is unchanged at
    # 60,000.00 (the deductions alone). The form cannot print a negative here: this pins the cap,
    # and the signed branch of line 19 is not reachable through the filer inputs.
    worksheet = return_eu(
        business_investment_loss="6000",
        t2048_dispositions_rows=(
            {
                "qbt_election_eligible_amount": "600000",
                "qbt_percentage_allocated": "50",
                "qbt_capital_gains": "160000",
                "qbt_election_is_qbt": 1,
            },
        ),
    )

    assert worksheet.get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D("3000.00")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("3000.00")
    assert worksheet.get(ABIL_AFTER_QBT_REDUCTION).value == D("0.00")
    assert worksheet.get(TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT).value == D("0.00")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == (
        worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025).value
    )
    assert worksheet.get(CUMULATIVE_LOSSES_AND_DEDUCTIONS).value == D("60000.00")


def test_step_2_line_18_below_zero_stays_negative_and_raises_line_19() -> None:
    # Step 2 line 13 is 2,000 - 3,000 = -1,000.00 (chosen figures) and the 1985 to 2024 deductions
    # (line 17) are 0, so line 18 "Add lines 10 and 13 to 17." is -1,000.00: the form prints no
    # floor. Line 19 "Line 9 minus line 18" is 749,000.00 + 1,000.00 = 750,000.00.
    worksheet = return_eu(
        t657_abil_claimed_1985_to_2024="2000",
        t657_t2048_line_17217_for_2024="3000",
        t657_deductions_claimed_1985_to_2024="0",
    )

    assert worksheet.get(CUMULATIVE_LOSSES_AND_DEDUCTIONS).value == D("-1000.00")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("750000.00")
