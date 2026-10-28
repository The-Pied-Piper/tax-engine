"""CA-ON 2025 end to end: return bh (Form T657 Charts 2016 to 2024 into Chart 2025)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ANNUAL_GAINS_LIMIT_2025,
    CAPITAL_GAINS_DEDUCTION,
    CHART_2016_AMOUNT_B,
    CHART_2016_PART_1_AMOUNT_A,
    CHART_2016_PART_1_AMOUNT_C,
    CHART_2016_PART_1_AMOUNT_F,
    CHART_2016_PART_1_AMOUNT_G,
    CHART_2016_PART_1_AMOUNTS_D_AND_E,
    CHART_2016_PART_2_AMOUNT_C,
    CHART_2016_PART_2_AMOUNT_E,
    CHART_2016_PART_2_AMOUNT_I,
    CHART_2016_PART_2_AMOUNT_J,
    CHART_2016_PART_2_APPLIES,
    CHART_2016_TOTAL_CARRIED,
    CHART_2017_PART_1_AMOUNT_C,
    CHART_2017_PART_1_AMOUNT_E,
    CHART_2017_PART_1_AMOUNT_K,
    CHART_2017_PART_1_AMOUNT_L,
    CHART_2017_TOTAL_CARRIED,
    CHART_2018_PART_1_AMOUNT_K,
    CHART_2018_TOTAL_CARRIED,
    CHART_2019_PART_1_AMOUNT_C,
    CHART_2019_PART_1_AMOUNT_E,
    CHART_2019_PART_1_AMOUNT_H,
    CHART_2019_PART_1_AMOUNT_I,
    CHART_2019_PART_1_AMOUNT_K,
    CHART_2019_PART_1_AMOUNTS_F_AND_G,
    CHART_2019_PART_2_AMOUNT_J,
    CHART_2019_PART_2_APPLIES,
    CHART_2019_TOTAL_CARRIED,
    CHART_2020_TOTAL_CARRIED,
    CHART_2021_AMOUNT_D,
    CHART_2021_PART_1_AMOUNT_C,
    CHART_2021_PART_1_AMOUNT_E,
    CHART_2021_PART_1_AMOUNT_J,
    CHART_2021_PART_1_AMOUNT_K,
    CHART_2021_PART_1_AMOUNT_M,
    CHART_2021_PART_1_AMOUNT_N,
    CHART_2021_PART_1_AMOUNTS_F_AND_G,
    CHART_2021_PART_2_AMOUNT_C,
    CHART_2021_PART_2_AMOUNT_E,
    CHART_2021_PART_2_AMOUNT_K,
    CHART_2021_PART_2_AMOUNT_L,
    CHART_2021_PART_2_APPLIES,
    CHART_2021_TOTAL_CARRIED,
    CHART_2022_PART_1_AMOUNT_C,
    CHART_2022_PART_1_AMOUNT_E,
    CHART_2022_PART_1_AMOUNT_K,
    CHART_2022_PART_1_AMOUNT_M,
    CHART_2022_PART_2_AMOUNT_C,
    CHART_2022_PART_2_AMOUNT_E,
    CHART_2022_PART_2_AMOUNT_L,
    CHART_2022_PART_2_APPLIES,
    CHART_2022_TOTAL_CARRIED,
    CHART_2023_PART_1_AMOUNT_C,
    CHART_2023_PART_1_AMOUNT_E,
    CHART_2023_PART_1_AMOUNT_M,
    CHART_2023_PART_1_AMOUNT_N,
    CHART_2023_TOTAL_CARRIED,
    CHART_2024_PERIOD_1_AMOUNT_A,
    CHART_2024_PERIOD_1_AMOUNT_C,
    CHART_2024_PERIOD_1_AMOUNT_E,
    CHART_2024_PERIOD_1_AMOUNT_I,
    CHART_2024_PERIOD_1_AMOUNT_L,
    CHART_2024_PERIOD_1_AMOUNT_N,
    CHART_2024_PERIOD_1_AMOUNT_O,
    CHART_2024_PERIOD_1_AMOUNTS_F_TO_H,
    CHART_2024_PERIOD_2_AMOUNT_C,
    CHART_2024_PERIOD_2_AMOUNT_E,
    CHART_2024_PERIOD_2_AMOUNT_I,
    CHART_2024_PERIOD_2_AMOUNT_L,
    CHART_2024_PERIOD_2_AMOUNT_N,
    CHART_2024_PERIOD_2_AMOUNT_O,
    CHART_2025_PART_1_AMOUNT_C,
    CHART_2025_PART_1_AMOUNT_E,
    CHART_2025_PART_1_AMOUNT_N,
    CHART_2025_PART_1_AMOUNT_P,
    CHART_2025_PART_1_AMOUNT_Q,
    CHART_2025_PART_2_AMOUNT_C,
    CHART_2025_PART_2_AMOUNT_E,
    CHART_2025_PART_2_AMOUNT_N,
    CHART_2025_PART_2_AMOUNT_P,
    CHART_2025_PART_2_AMOUNT_Q,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, t657_reserve_inputs

# The reserves Form T657 reads from Form T2017 (the rows are made by `t657_reserve_rows`).
RESERVES = {
    "t657_chart_2016_amount_e": "60000",
    "t657_chart_2019_amount_f": "20000",
    "t657_chart_2021_amount_g": "40000",
    "t657_chart_2024_period_1_amount_g": "40000",
    "t657_chart_2024_period_2_amount_f": "30000",
}


def return_bh(**overrides: Any) -> Worksheet:
    """Return BH's inputs, as in `returns/2025_return_bh.yaml`.

    Return BF's inputs (one QSBCS disposition in 2025 for a gain of 350000, 20000 of net capital
    losses of other years, 100000 of taxable capital gains for 2002 to 2024 and 155000 claimed on
    line 25400), and the reserves reported in 2025: 60000 on Form T2017 line 12 for Chart 2016
    (QSBCS, so Part 1 F is 30000), 20000 on Form T2017 line 6 for Chart 2019, 40000 on Form T2017
    line 12 for Chart 2021 (QSBCS), 40000 on Form T2017 line 12 for Chart 2024 Period 1, and 30000
    on Form T2017 line 6 for Chart 2024 Period 2; with 100000 of earlier years' deductions entered
    as Chart 2 line 18.
    """
    inputs: dict[str, Any] = {
        "employment_income": "0",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "other_income": "10000",
        "qsbcs_dispositions": (("500000", "150000", "0"),),
        "unapplied_net_capital_losses_2001_to_2024": "20000",
        "net_capital_losses_claimed": "20000",
        "t657_gains_2002_to_2024": "100000",
        "t657_chart_2_line_18": "100000",
        "capital_gains_deduction_claimed": "155000",
    }
    return compute(**t657_reserve_inputs(RESERVES, {**inputs, **overrides}))


def test_chart_2016_takes_the_60000_reserve_to_amount_g_of_30000() -> None:
    # Chart 2016 Part 1: A 412088.00; B is Chart 2 line 19, 100000 (line 18 entered as 100000), so C
    # is 312088.00. D (line 6) is 0 and E (line 12) is 60000: D plus E is 60000, F is 30000 (x 1/2),
    # and G is the lesser of C and F: 30000.00. Part 2 (A 500000.00, B is Part 1's G): C is
    # 470000.00,
    # E is 470000.00 less D (100000) = 370000.00. F (the line 6 amount, halved) is 0, so G is 0 and
    # I is G plus Part 1's G = 30000.00; J is the lesser of F and I: 0. No additional deduction is
    # claimed, so Part 2 does not apply, and the total carried is Part 1's G, 30000.00.
    worksheet = return_bh()

    assert worksheet.get(CHART_2016_PART_1_AMOUNT_A).value == D("412088")
    assert worksheet.get(CHART_2016_AMOUNT_B).value == D("100000.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_C).value == D("312088.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNTS_D_AND_E).value == D("60000.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_F).value == D("30000.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_G).value == D("30000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_C).value == D("470000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_E).value == D("370000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_I).value == D("30000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_J).value == D("0.00")
    assert worksheet.get(CHART_2016_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2016_TOTAL_CARRIED).value == D("30000.00")


def test_charts_2017_and_2018_pass_the_30000_total_through() -> None:
    # Chart 2017: A 417858.00 less B (Chart 2016's total, 30000.00) is C, 387858.00; E is 287858.00
    # (D 100000.00). F and G are 0, so H and I are 0 and K is I plus B: 30000.00; L is 30000.00.
    # Chart 2018: A 424126.00 less 30000.00 is C, 394126.00, and K is 30000.00. Both carry 30000.00.
    worksheet = return_bh()

    assert worksheet.get(CHART_2017_PART_1_AMOUNT_C).value == D("387858.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_E).value == D("287858.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_K).value == D("30000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_L).value == D("30000.00")
    assert worksheet.get(CHART_2017_TOTAL_CARRIED).value == D("30000.00")
    assert worksheet.get(CHART_2018_PART_1_AMOUNT_K).value == D("30000.00")
    assert worksheet.get(CHART_2018_TOTAL_CARRIED).value == D("30000.00")


def test_chart_2019_takes_the_20000_line_6_reserve_to_amount_i_of_10000() -> None:
    # Chart 2019 Part 1: A 433456.00 less B (30000.00) is C, 403456.00; E is 303456.00 (D
    # 100000.00).
    # Line 6 (F) is 20000 and G is 0: F plus G is 20000.00, H is 10000.00 (x 1/2) and I is the
    # lesser
    # of E and H: 10000.00. K is I plus B: 40000.00, and L is 40000.00, the total carried.
    # Part 2: A 500000.00 less K (40000.00) is C, 460000.00; E is 360000.00; F is 10000.00 (line 6
    # x 1/2), G is 10000.00, I is G plus K (50000.00) and J is the lesser of F and I: 10000.00.
    worksheet = return_bh()

    assert worksheet.get(CHART_2019_PART_1_AMOUNT_C).value == D("403456.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_E).value == D("303456.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNTS_F_AND_G).value == D("20000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_H).value == D("10000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_I).value == D("10000.00")
    assert worksheet.get(CHART_2019_PART_1_AMOUNT_K).value == D("40000.00")
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_J).value == D("10000.00")
    assert worksheet.get(CHART_2019_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2019_TOTAL_CARRIED).value == D("40000.00")
    assert worksheet.get(CHART_2020_TOTAL_CARRIED).value == D("40000.00")


def test_chart_2021_takes_chart_2020s_total_of_40000_as_amount_b() -> None:
    # Chart 2021 Part 1: A 446109.00 less B (Chart 2020's total, 40000.00) is C, 406109.00; D is
    # Chart 2 line 19, 100000.00, so E is 306109.00. G is 40000 and F and G add to 40000.00; H is
    # 20000.00, I is 0 and J is 20000.00. K is the lesser of E and J: 20000.00. M is K plus B,
    # 60000.00,
    # and N is the lesser of 155000.00, 255000.00 and M: 60000.00.
    # Part 2: A 500000.00, B is Part 1's M, so C is 440000.00 and E is 340000.00. F, G and H are 0,
    # so
    # I is 0; K is I plus Part 1's M: 60000.00; L is the lesser of H and K: 0. Part 2 does not
    # apply,
    # so the total carried forward is Part 1's M, 60000.00.
    worksheet = return_bh()

    assert worksheet.get(CHART_2021_PART_1_AMOUNT_C).value == D("406109.00")
    assert worksheet.get(CHART_2021_AMOUNT_D).value == D("100000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_E).value == D("306109.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNTS_F_AND_G).value == D("40000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_J).value == D("20000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_K).value == D("20000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_M).value == D("60000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_N).value == D("60000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_C).value == D("440000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_E).value == D("340000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_K).value == D("60000.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_L).value == D("0.00")
    assert worksheet.get(CHART_2021_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2021_TOTAL_CARRIED).value == D("60000.00")


def test_charts_2022_and_2023_pass_the_60000_total_through() -> None:
    # Chart 2022: A 456815.00 less B (Chart 2021's 60000.00) is C, 396815.00, and E 296815.00 (D
    # 100000.00). Nothing is reported, so K is 0 and M is 60000.00 (K plus B), N 60000.00; the Part
    # 2
    # gate is 0 and the total carried is 60000.00. Chart 2023: A 485595.00 less B (60000.00) is C,
    # 425595.00, E 325595.00; M is 60000.00 and the total carried is 60000.00.
    worksheet = return_bh()

    assert worksheet.get(CHART_2022_PART_1_AMOUNT_C).value == D("396815.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_E).value == D("296815.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_K).value == D("0.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_M).value == D("60000.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_C).value == D("440000.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_E).value == D("340000.00")
    assert worksheet.get(CHART_2022_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2022_TOTAL_CARRIED).value == D("60000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_C).value == D("425595.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_E).value == D("325595.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_M).value == D("60000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_N).value == D("60000.00")
    assert worksheet.get(CHART_2023_TOTAL_CARRIED).value == D("60000.00")


def test_period_1_of_2024_takes_chart_2023s_total_of_60000_as_amount_b() -> None:
    # Period 1: A 508418.00 less B (Chart 2023's total, 60000.00) is C, 448418.00, and E is
    # 348418.00
    # (D 100000.00). G is 40000, so F to H add to 40000 and I is 20000.00; J is 0, so K is 20000.00.
    # L is the lesser of E and K: 20000.00. N is L plus B, 80000.00, and O is the lesser of
    # 155000.00, 255000.00 and N: 80000.00.
    worksheet = return_bh()

    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_A).value == D("508418")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_C).value == D("448418.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_E).value == D("348418.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNTS_F_TO_H).value == D("40000")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_I).value == D("20000.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_L).value == D("20000.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_N).value == D("80000.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_O).value == D("80000.00")


def test_period_2_of_2024_takes_period_1s_total_of_80000_as_amount_b() -> None:
    # Period 2: A 625000.00 less B (Period 1's N, 80000.00) is C, 545000.00, and E is 445000.00 (D
    # 100000.00). F is 30000, so I is 15000.00; L is the lesser of E and K, 15000.00. N is L plus B,
    # 15000.00 + 80000.00 = 95000.00, and O is the lesser of 155000.00, 255000.00 and N: 95000.00.
    worksheet = return_bh()

    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_C).value == D("545000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_E).value == D("445000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_I).value == D("15000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_L).value == D("15000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_N).value == D("95000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_O).value == D("95000.00")


def test_chart_2025_part_1_takes_period_2s_total_of_95000_as_amount_b() -> None:
    # Part 1: A 522145.00 less B (Period 2's N, 95000.00) is C, 427145.00, and E is 327145.00 (D
    # 100000.00). Nothing is reported in F to J, so K and M are 0 and N is 0. O is B, 95000.00, so
    # P is 95000.00, and Q is the lesser of 155000.00, 255000.00 and P: 95000.00.
    worksheet = return_bh()

    assert worksheet.get(CHART_2025_PART_1_AMOUNT_C).value == D("427145.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_E).value == D("327145.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_N).value == D("0.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_P).value == D("95000.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_Q).value == D("95000.00")


def test_chart_2025_part_2_takes_part_1s_total_as_amount_b_and_line_25400_stays_at_155000() -> None:
    # Part 2: A 625000.00 less B (Part 1's P, 95000.00) is C, 530000.00, and E is 430000.00 (D
    # 100000.00). F is 350000, the other amounts 0, so K is 175000.00 and M is 175000.00; N is the
    # lesser of E and M, 175000.00. O is B, 95000.00, so P is 270000.00. Q is the lesser of
    # 155000.00,
    # 255000.00 and P: 155000.00. The filer claims 155000, so line 25400 is 155000.00.
    worksheet = return_bh()

    assert worksheet.get(CHART_2025_PART_2_AMOUNT_C).value == D("530000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_E).value == D("430000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_N).value == D("175000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("270000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("155000.00")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("155000.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("155000")


def test_a_2023_qsbcs_reserve_of_20000_carries_into_period_1_of_2024_and_onward() -> None:
    # A 2023 QSBCS reserve of 20000 (Form T2017 line 12) on Chart 2023 Part 1: F plus G is 20000, H
    # is 10000.00, J is 10000.00, K is 10000.00, and M is K plus B, 70000.00, so Chart 2023 carries
    # 70000.00 into Period 1 of 2024 (C is 438418.00, and N is 90000.00). Period 2 takes 90000.00
    # (C 535000.00, N 105000.00), and Chart 2025 Part 1 and Part 2 take 105000.00 (Part 1 P
    # 105000.00,
    # Part 2 P 280000.00). Line 25400 stays at 155000.00.
    worksheet = return_bh(t657_chart_2023_amount_g="20000")

    assert worksheet.get(CHART_2023_PART_1_AMOUNT_M).value == D("70000.00")
    assert worksheet.get(CHART_2023_TOTAL_CARRIED).value == D("70000.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_N).value == D("90000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_N).value == D("105000.00")
    assert worksheet.get(CHART_2025_PART_1_AMOUNT_P).value == D("105000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("280000.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("155000")


def test_part_2_of_2016_applies_with_a_qffp_reserve_and_replaces_part_1s_g_as_the_total() -> None:
    # Chart 2 line 18 of 400000 (so line 19, and amount B of Chart 2016, is 400000): Part 1 C is
    # 12088.00 and D plus E is 120000 (line 6 of 60000 and line 12 of 60000), F 60000 and G the
    # lesser
    # of C and F: 12088.00. Part 2: C is 487912.00 (500000 less G), E is 87912.00 (C less D); F is
    # 30000
    # (line 6 of 60000, halved), G is 30000, I is G plus G of Part 1 (42088.00) and J is the lesser
    # of F
    # and I: 30000.00. The gate: C of Part 1 (12088.00) is not more than the limits or G (12088.00),
    # and
    # the additional deduction is claimed (count 1), so Part 2 applies and its J of 30000.00
    # replaces
    # Part 1's G as the total carried into Chart 2017 (not 12088.00). Chart 2017 then takes
    # 30000.00.
    worksheet = return_bh(
        t657_chart_2_line_18="400000",
        t657_chart_2016_amount_d="60000",
        t657_chart_2016_claims_additional_deduction=1,
    )

    assert worksheet.get(CHART_2016_PART_1_AMOUNT_G).value == D("12088.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_J).value == D("30000.00")
    assert worksheet.get(CHART_2016_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2016_TOTAL_CARRIED).value == D("30000.00")
    assert worksheet.get(CHART_2017_PART_1_AMOUNT_E).value == D("0.00")
    assert worksheet.get(CHART_2017_TOTAL_CARRIED).value == D("30000.00")


def test_chart_2016_amount_b_alternative_is_the_callers_30000_for_both_parts() -> None:
    # The (2016-1) calculation, the caller's 30000 (uses_d_instead 1) instead of Chart 2 line 19: B
    # is 30000.00, so C is 382088.00; G is the lesser of C and F (30000): 30000.00. Part 2 uses the
    # same 30000 as its D: C is 470000.00 and E is 440000.00. The total carried is unchanged.
    worksheet = return_bh(
        t657_chart_2016_uses_d_instead=1,
        t657_chart_2016_amount_b_instead="30000",
    )

    assert worksheet.get(CHART_2016_AMOUNT_B).value == D("30000.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_C).value == D("382088.00")
    assert worksheet.get(CHART_2016_PART_1_AMOUNT_G).value == D("30000.00")
    assert worksheet.get(CHART_2016_PART_2_AMOUNT_E).value == D("440000.00")
    assert worksheet.get(CHART_2016_TOTAL_CARRIED).value == D("30000.00")


def test_part_2_of_2019_is_refused_when_part_1_e_exceeds_the_annual_limit() -> None:
    # The additional deduction claimed for the 2019 QFFP reserve, but Part 1 amount E (303456.00) is
    # more than the annual gains limit of 155000.00, so Part 2 is not completed: the total carried
    # is
    # Part 1's K, 40000.00, although Part 2's J is computed (10000.00).
    worksheet = return_bh(t657_chart_2019_claims_additional_deduction=1)

    assert worksheet.get(CHART_2019_PART_1_AMOUNT_E).value == D("303456.00")
    assert worksheet.get(CHART_2019_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2019_PART_2_AMOUNT_J).value == D("10000.00")
    assert worksheet.get(CHART_2019_TOTAL_CARRIED).value == D("40000.00")
    assert worksheet.get(CHART_2020_TOTAL_CARRIED).value == D("40000.00")


def test_part_2_of_2022_applies_with_a_qffp_reserve_and_replaces_part_1s_m_as_the_total() -> None:
    # A 2022 QFFP reserve of 40000 (Form T2017 line 6) on Chart 2022 Part 1 and Part 2, with the
    # additional deduction claimed (count 1), and Chart 2 line 18 of 400000 so that amount E is
    # within
    # the limits. The chain carries 42088.00 into Chart 2022 (Chart 2021's M under this line 18).
    # Part 1: C is 414727.00 (456815 less 42088), E is 14727.00 (D 400000); F is 40000 so H is 20000
    # and J is 20000; K is the lesser of E and J, 14727.00; M is K plus B, 56815.00. Part 2: C is
    # 443185.00 (500000 less M), E is 43185.00; F is 20000.00 (40000 times 1/2), H is 20000.00, I is
    # the lesser of E and H, 20000.00; K is I plus M, 76815.00; L is the lesser of H and K:
    # 20000.00.
    # Part 1 E (14727.00) is within the annual limit, the cumulative limit and amount M (56815.00),
    # so
    # Part 2 applies, and its L replaces Part 1's M as the total carried into Chart 2023.
    worksheet = return_bh(
        t657_chart_2_line_18="400000",
        t657_chart_2022_amount_f="40000",
        t657_chart_2022_claims_additional_deduction=1,
    )

    assert worksheet.get(CHART_2022_PART_1_AMOUNT_E).value == D("14727.00")
    assert worksheet.get(CHART_2022_PART_1_AMOUNT_M).value == D("56815.00")
    assert worksheet.get(CHART_2022_PART_2_AMOUNT_L).value == D("20000.00")
    assert worksheet.get(CHART_2022_PART_2_APPLIES).value == 1
    assert worksheet.get(CHART_2022_TOTAL_CARRIED).value == D("20000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_M).value == D("20000.00")


def test_part_2_of_2022_with_no_additional_deduction_carries_part_1s_m() -> None:
    # The same 2022 reserve and Chart 2 line 18 of 400000, with the additional deduction not claimed
    # (count 0): the gate is 0, so Part 2 is not completed and the total carried is Part 1's M,
    # 56815.00, although Part 2's L is computed (20000.00).
    worksheet = return_bh(t657_chart_2_line_18="400000", t657_chart_2022_amount_f="40000")

    assert worksheet.get(CHART_2022_PART_2_AMOUNT_L).value == D("20000.00")
    assert worksheet.get(CHART_2022_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2022_TOTAL_CARRIED).value == D("56815.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_M).value == D("56815.00")


def test_part_2_of_2022_is_refused_when_part_1_e_exceeds_the_annual_limit() -> None:
    # The same 2022 QFFP reserve and the additional deduction claimed, but Chart 2 line 18 is
    # 100000:
    # amount E of Part 1 is 296815.00, more than the annual gains limit of 155000.00, so Part 2 is
    # not
    # completed and the total carried is Part 1's M, 80000.00.
    worksheet = return_bh(
        t657_chart_2022_amount_f="40000", t657_chart_2022_claims_additional_deduction=1
    )

    assert worksheet.get(CHART_2022_PART_1_AMOUNT_E).value == D("296815.00")
    assert worksheet.get(CHART_2022_PART_2_APPLIES).value == 0
    assert worksheet.get(CHART_2022_TOTAL_CARRIED).value == D("80000.00")
    assert worksheet.get(CHART_2023_PART_1_AMOUNT_M).value == D("80000.00")


def test_uses_d_instead_takes_the_callers_amount_at_amount_d_of_chart_2021() -> None:
    # Chart 2021 D is the caller's 30000.00 (uses_d_instead 1) rather than Chart 2 line 19 (100000),
    # so E is 376109.00 (406109.00 less 30000.00); Part 2's E is 410000.00 (440000.00 less
    # 30000.00).
    # The total carried is unchanged, 60000.00, because the other charts read the same figures.
    worksheet = return_bh(
        t657_chart_2021_uses_d_instead=1,
        t657_chart_2021_amount_d_instead="30000",
    )

    assert worksheet.get(CHART_2021_AMOUNT_D).value == D("30000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_E).value == D("376109.00")
    assert worksheet.get(CHART_2021_PART_2_AMOUNT_E).value == D("410000.00")
    assert worksheet.get(CHART_2021_TOTAL_CARRIED).value == D("60000.00")
    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_N).value == D("80000.00")
