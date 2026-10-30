"""CA-ON 2025 end to end: return ic (Form T657 Step 1 line 9, a T3 gain on Schedule 3 17600)."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ANNUAL_GAINS_LIMIT_2025,
    ANNUAL_GAINS_LINE_5,
    ANNUAL_GAINS_LINE_7,
    ANNUAL_GAINS_LINE_9,
    ANNUAL_GAINS_LINE_10,
    ANNUAL_GAINS_LINE_12,
    CAPITAL_GAINS_DEDUCTION,
    CHART_2025_PART_2_AMOUNT_P,
    CHART_2025_PART_2_AMOUNT_Q,
    CUMULATIVE_GAINS_LIMIT_2025,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025,
    NET_INCOME,
    SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO,
    SCHEDULE_3_LINE_19900,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ic(**overrides: Any) -> Worksheet:
    """Return IC's inputs, as in `returns/2025_return_ic.yaml`.

    One QSBCS disposition for a gain of 350000, a loss of 100000 on other shares, a T3 gain of
    40000 (Schedule 3 line 17600), 20000 of net capital losses of other years claimed, 100000 of
    eligible taxable capital gains for 2002 to 2024 and 105000 claimed on line 25400.
    """
    inputs: dict[str, Any] = {
        "employment_income": "0",
        "share_dispositions": (("20000", "120000", "0"),),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "other_income": "10000",
        "qsbcs_dispositions": (("500000", "150000", "0"),),
        "t3_capital_gains_or_losses": "40000",
        "unapplied_net_capital_losses_2001_to_2024": "20000",
        "net_capital_losses_claimed": "20000",
        "t657_gains_2002_to_2024": "100000",
        "capital_gains_deduction_claimed": "105000",
    }
    return compute(**{**inputs, **overrides})


def test_step_1_line_9_takes_half_of_the_20000_t3_gain_off_line_10() -> None:
    # Line 17600 of Schedule 3 is the T3 gain, 40000.00; line 9 is 40000.00 x 1/2 = 20000.00. Line
    # 8 (line 19900) is (350000 - 100000 + 40000) x 1/2 = 145000.00, so line 10 is 145000.00 -
    # 20000.00 = 125000.00 and line 12 is 125000.00 (line 11, Form T2048 line 17215, is 0). Line 7
    # is 175000.00 (line 1 is the QSBCS gain, 350000.00, alone), so line 13 is the lesser:
    # 125000.00.
    worksheet = return_ic()

    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("145000.00")
    assert worksheet.get(SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO).value == D("40000")
    assert worksheet.get(ANNUAL_GAINS_LINE_9).value == D("20000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_5).value == D("175000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_7).value == D("175000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_10).value == D("125000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_12).value == D("125000.00")
    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025).value == D("125000.00")


def test_the_annual_gains_limit_is_105000_and_the_claim_is_limited_to_it() -> None:
    # Line 21 is line 13 less the 20000.00 of line 25300: 105000.00. Step 2 line 8 is 100000 +
    # 125000.00 = 225000.00, line 19 is 225000.00 - 20000.00 = 205000.00. Chart 2025 Part 2 P is
    # 175000.00 (K, 350000.00 x 1/2), so Q is the lesser of 105000.00, 205000.00 and 175000.00:
    # 105000.00, claimed in full on line 25400. Net income is 10000 + 145000.00 = 155000.00 and
    # taxable income is 155000.00 - 20000 - 105000 = 30000.00.
    worksheet = return_ic()

    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("105000.00")
    assert worksheet.get(ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025).value == D("225000.00")
    assert worksheet.get(CUMULATIVE_GAINS_LIMIT_2025).value == D("205000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_P).value == D("175000.00")
    assert worksheet.get(CHART_2025_PART_2_AMOUNT_Q).value == D("105000.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTION).value == D("105000")
    assert worksheet.get(NET_INCOME).value == D("155000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")


def test_a_t3_gain_of_80000_takes_40000_off_line_10_and_the_limit_stays_105000() -> None:
    # T3 gain 80000: line 8 is (350000 - 100000 + 80000) x 1/2 = 165000.00, line 9 is 40000.00, so
    # line 10 is 125000.00 again: the T3 gain does not change line 13, 125000.00, or line 21,
    # 105000.00.
    worksheet = return_ic(t3_capital_gains_or_losses="80000")

    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("165000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_9).value == D("40000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_10).value == D("125000.00")
    assert worksheet.get(ANNUAL_GAINS_LIMIT_2025).value == D("105000.00")
