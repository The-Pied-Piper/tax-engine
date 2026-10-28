"""CA-ON 2025 end to end: return ke (Form T657 reads a later-year claim from Form T2017 rows)."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ANNUAL_GAINS_LIMIT_2025,
    ANNUAL_GAINS_LINE_2,
    ANNUAL_GAINS_LINE_3,
    ANNUAL_GAINS_LINE_5,
    CAPITAL_GAINS_DEDUCTION,
    CHART_2021_PART_1_AMOUNT_J,
    CHART_2021_PART_1_AMOUNT_M,
    CHART_2021_PART_1_AMOUNTS_F_AND_G,
    CHART_2021_TOTAL_CARRIED,
    CHART_2022_PART_1_AMOUNTS_F_AND_G,
    CHART_2024_PERIOD_1_AMOUNT_O,
    CHART_2024_PERIOD_2_AMOUNT_O,
    CHART_2025_PART_2_AMOUNT_Q,
    CUMULATIVE_GAINS_LIMIT_2025,
    NET_INCOME,
    SCHEDULE_3_LINE_19200,
    SCHEDULE_3_LINE_19900,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, t657_reserve_inputs

# The reserves Form T657 reads from Form T2017, with nothing claimed in 2025 (the rows are made by
# `t657_reserve_rows`): QSBCS 2016 (60000), QFFP 2019 (20000), QSBCS in Period 1 of 2024 (40000)
# and QFFP in Period 2 of 2024 (30000). The 2021 row claims in 2025, so it is given below.
RESERVES = {
    "t657_chart_2016_amount_e": "60000",
    "t657_chart_2019_amount_f": "20000",
    "t657_chart_2024_period_1_amount_g": "40000",
    "t657_chart_2024_period_2_amount_f": "30000",
}
# A QSBCS disposition in 2021 (4 years after): a capital gain, proceeds and amount payable after
# the end of the year of 1000000, a 2024 reserve of 70000 of which 30000 is claimed in 2025.
ROW_2021 = {
    "capital_gain": "1000000",
    "payable": "1000000",
    "proceeds": "1000000",
    "years": 4,
    "claimed": "30000",
    "previous": "70000",
    "nine_year": 1,
}


def return_ke(**overrides: Any) -> Worksheet:
    """Return KE's inputs, as in `returns/2025_return_ke.yaml`.

    Return BH's inputs (one QSBCS disposition in 2025 for a gain of 350000, 20000 of net capital
    losses of other years, 100000 of taxable capital gains for 2002 to 2024, 100000 of earlier
    years' deductions as Chart 2 line 18 and 155000 claimed on line 25400), but the Form T2017 row
    of the 2021 disposition claims 30000 of its 2024 reserve of 70000 in 2025, and Form T2017 lines
    1 (50000) and 7 (170000) are the 2024 reserves of the rows.
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
        "t2017_amounts": {1: "50000", 7: "170000"},
        "t2017_rows": {8: [ROW_2021]},
        "capital_gains_deduction_claimed": "155000",
    }
    return compute(**t657_reserve_inputs(RESERVES, {**inputs, **overrides}))


def test_the_2021_row_gives_chart_2021_the_change_in_its_reserve_not_the_2024_reserve() -> None:
    # The 2021 row has a 2024 reserve of 70000 (the previous year's claim, read as a later year) and
    # a 2025 reserve of 30000: Form T2017 line 12 of the row is 70000 - 30000 = 40000, which Chart
    # 2021 reads as amount G. F is 0, so F and G add to 40000.00 and H is 20000.00 (x 1/2); I is 0,
    # J (H plus I) is 20000.00 and M is J's K plus B (Chart 2020's total, 40000.00): 60000.00.
    worksheet = return_ke()

    assert worksheet.get(CHART_2021_PART_1_AMOUNTS_F_AND_G).value == D("40000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_J).value == D("20000.00")
    assert worksheet.get(CHART_2021_PART_1_AMOUNT_M).value == D("60000.00")
    assert worksheet.get(CHART_2021_TOTAL_CARRIED).value == D("60000.00")


def test_the_2021_row_is_not_taken_by_chart_2022() -> None:
    # Chart 2022 takes only the dispositions of 2022 (3 years after): the 2021 row (4 years after)
    # adds nothing to its amounts F and G.
    worksheet = return_ke()

    assert worksheet.get(CHART_2022_PART_1_AMOUNTS_F_AND_G).value == D("0.00")


def test_the_rows_2024_reserves_are_form_t2017_lines_1_and_7_so_line_13_is_190000() -> None:
    # Form T2017: line 1 (QFFP) is 20000 + 30000 = 50000 and no row of lines 2 to 4 claims in 2025,
    # so line 6 is 50000. Line 7 (QSBCS) is 60000 + 70000 + 40000 = 170000 and the 2021 row's 30000
    # is line 11, so line 12 is 140000. Line 13 is 50000 + 140000 = 190000, which T657 Step 1 takes
    # as line 2 and Schedule 3 as line 19200 (line 31).
    worksheet = return_ke()

    assert worksheet.get(ANNUAL_GAINS_LINE_2).value == D("190000")
    assert worksheet.get(SCHEDULE_3_LINE_19200).value == D("190000")


def test_step_1_and_step_2_derive_the_limits_of_250000_and_350000() -> None:
    # Step 1: line 1 is 350000.00, line 2 is 190000, so line 3 is 540000.00 and line 5 (x 1/2)
    # is 270000.00; line 8 (Schedule 3 line 19900) is 270000.00 and line 13 is 270000.00. Line 21
    # is 270000.00 less the 20000.00 of net capital losses: 250000.00, the annual gains limit.
    # Step 2: line 8 is 100000 + 270000.00 = 370000.00; line 19 is 370000.00 - 20000.00 =
    # 350000.00, the cumulative gains limit.
    worksheet = return_ke()

    assert worksheet.get(ANNUAL_GAINS_LINE_3).value == D("540000")
    assert worksheet.get(ANNUAL_GAINS_LINE_5).value == D("270000.00")
    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("270000.00")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("250000.00")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("350000.00")


def test_the_period_charts_total_to_80000_and_95000() -> None:
    # As in Return BH: Period 1 (G 40000, so I is 20000.00) has N 80000.00 and Period 2 (F 30000, so
    # I is 15000.00) has N 95000.00; each amount O is the lesser of the limits and N.
    worksheet = return_ke()

    assert worksheet.get(CHART_2024_PERIOD_1_AMOUNT_O).value == D("80000.00")
    assert worksheet.get(CHART_2024_PERIOD_2_AMOUNT_O).value == D("95000.00")


def test_chart_2025_part_2_allows_250000_and_the_claim_of_155000_is_below_it() -> None:
    # Part 2: F is 350000, K is 175000.00, N is 175000.00, O (amount B) is 95000.00 and P is
    # 270000.00; Q is the lesser of 250000.00, 350000.00 and 270000.00: 250000.00. The filer claims
    # 155000, so line 25400 is 155000.00 and line 25700 is 20000.00 + 155000.00 = 175000.00; net
    # income is 270000.00 + 10000 = 280000.00, so taxable income is 105000.00.
    worksheet = return_ke()

    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("250000.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("155000.00")
    assert worksheet.get(NET_INCOME).value == D("280000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("105000.00")


def test_a_claim_above_amount_q_of_250000_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        return_ke(capital_gains_deduction_claimed="250000.01")

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/capital_gains_deduction_claimed 250000.01 is above "
        "ca/chart_2025_part_2_maximum_claim 250000"
    )


def test_a_2025_claim_above_the_2024_reserve_of_the_row_is_refused() -> None:
    # Form T2017 page 3: "the amount you claim in a later year (Year B) cannot be more than the
    # amount you claimed for that property in the previous year (Year A)": 70000.01 against 70000.
    with pytest.raises(InputAboveBoundError):
        return_ke(t2017_rows={8: [{**ROW_2021, "claimed": "70000.01"}]})
