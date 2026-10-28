"""CA-ON 2025 end to end: return js, Form T1206 page 6 read by the T1.

The worked returns `returns/2025_return_jn.yaml` (a filer under 18) and
`returns/2025_return_js.yaml` (a filer 18 or older) are checked by `test_worked_returns.py`.
This module checks what the T1 does with the section's amounts, over the figures the filer enters
on the return itself: the amount deemed to be a dividend is added to the dividends of lines 12000
and 12010 and to Part 1 lines 1 and 2, and 50% of line G to Part 1 line 3, each added to the
filer's own figure, never replacing it. Line G itself is on no line of Schedule 3: T1206 names
none, so the filer reports the sales on the Schedule 3 lines for what was sold.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAINS_DEFERRAL_CHECKED,
    DIVIDENDS_AMOUNT_A,
    DIVIDENDS_AMOUNT_B,
    OTHER_DIVIDENDS_CREDIT,
    OTHER_SPLIT_INCOME_CHECKED,
    OTHER_SPLIT_INCOME_TOTAL,
    SHARE_GAIN_OR_LOSS,
    SPLIT_INCOME_DIVIDENDS_CHECKED,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_TOTAL,
    SPLIT_INCOME_DIVIDENDS_TOTAL,
    TAXABLE_DIVIDENDS,
    TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    TOTAL_INCOME,
    TOTAL_SPLIT_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# Return JN's section: line G is 20,700.00 (lines A, B and F of 20,000, 5,000 and 1,000 and two
# dispositions with a reserve of 5,300.00).
ROWS = (
    {
        "capital_gain": "10000",
        "payable": "6000",
        "proceeds": "12000",
        "years": 0,
        "claimed": "5000",
    },
    {"capital_gain": "4000", "payable": "1000", "proceeds": "8000", "years": 2, "claimed": "300"},
)
SECTION: dict[str, Any] = {
    "t1206_capital_gain_on_dispositions": "20000",
    "t1206_reserve_2024": "5000",
    "t1206_t3_box_21_capital_gains": "1000",
    "t1206_rows": ROWS,
}
# The filer's own figures: 1,000 of dividends other than eligible with no slip (1,150.00 grossed
# up) all of which are split income, 500 of other split income and a share disposition with a gain
# of 2,000 (proceeds 5,000 less an adjusted cost base of 3,000).
OWN: dict[str, Any] = {
    "other_dividends_received_without_a_slip": "1000",
    "split_income_dividends": "1150",
    "split_income_dividends_other_than_eligible": "1150",
    "other_split_income": "500",
}
SHARES = (("5000", "3000", "0"),)


def under_18(**overrides: Any) -> Worksheet:
    inputs = {**SECTION, **OWN, "aged_18_or_older_at_end_of_2025": 0, **overrides}
    return compute("0", SHARES, "0", "0", "0", "0", "0", **inputs)


def aged_18_or_older(**overrides: Any) -> Worksheet:
    inputs = {**SECTION, **OWN, "aged_18_or_older_at_end_of_2025": 1, **overrides}
    return compute("0", SHARES, "0", "0", "0", "0", "0", **inputs)


# --- under 18: the amount deemed to be a dividend ------------------------------------------------


def test_an_under_18_filer_adds_the_deemed_dividend_to_lines_12000_and_12010() -> None:
    worksheet = under_18()

    # 1,000 x 1.15 = 1,150.00 of the filer's own, plus 20,700.00 x 1.15 = 23,805.00.
    assert worksheet.get(TAXABLE_DIVIDENDS).value == D("24955.00")
    assert worksheet.get(TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE).value == D("24955.00")


def test_an_under_18_filer_adds_the_deemed_dividend_to_part_1_lines_1_and_2() -> None:
    worksheet = under_18()

    # The filer's own 1,150 plus 23,805.00; the checks see the sum, line 2 being part of line 1.
    assert worksheet.get(SPLIT_INCOME_DIVIDENDS_TOTAL).value == D("24955.00")
    assert worksheet.get(SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_TOTAL).value == D("24955.00")
    assert worksheet.get(SPLIT_INCOME_DIVIDENDS_CHECKED).value == D("24955.00")
    assert worksheet.get(SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED).value == D("24955.00")


def test_an_under_18_filer_has_nothing_on_schedule_3_or_part_1_line_3_from_the_section() -> None:
    worksheet = under_18()

    assert worksheet.get(SHARE_GAIN_OR_LOSS).value == D("2000.00")
    assert worksheet.get(OTHER_SPLIT_INCOME_TOTAL).value == D("500.00")


def test_an_under_18_filer_is_taxed_on_the_split_income_of_lines_1_and_3() -> None:
    worksheet = under_18()

    # Line 4: 24,955.00 on line 1 plus 500.00 on line 3.
    assert worksheet.get(TOTAL_SPLIT_INCOME).value == D("25455.00")


def test_an_under_18_filer_counts_the_deemed_dividend_in_the_no_slip_dividend_credit() -> None:
    # The Federal Worksheet "Line 40425" lines A and B take only dividends not on an information
    # slip; the deemed dividend (23,805.00) is on none, so it is added to the 1,150.00 of the
    # filer's own no-slip dividends on both lines: 24,955.00, and 24,955.00 x 9.0301% = 2,253.46.
    worksheet = under_18()

    assert worksheet.get(DIVIDENDS_AMOUNT_A).value == D("24955.00")
    assert worksheet.get(DIVIDENDS_AMOUNT_B).value == D("24955.00")
    assert worksheet.get(OTHER_DIVIDENDS_CREDIT).value == D("2253.46")


def test_a_filer_18_or_older_has_no_deemed_dividend_in_the_no_slip_dividend_credit() -> None:
    worksheet = aged_18_or_older()

    assert worksheet.get(DIVIDENDS_AMOUNT_A).value == D("1150.00")


def test_the_own_figure_and_the_deemed_dividend_above_the_dividends_are_refused() -> None:
    # The filer's own line 1 of 1,200 is more than their own dividends (1,150.00), so with the
    # deemed dividend (23,805.00) line 1 is 25,005.00, above the dividends of 24,955.00.
    message = "ca/split_income_dividends_total 25005.00 is above ca/taxable_dividends 24955.00"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        under_18(split_income_dividends="1200")


# --- 18 or older: Part 1 line 3 and no Schedule 3 ----------------------------------------------


def test_a_filer_18_or_older_has_no_line_g_on_schedule_3() -> None:
    worksheet = aged_18_or_older()

    # Schedule 3 line 4 is the filer's own 2,000.00 of gain: line G is on no line of Schedule 3.
    assert worksheet.get(SHARE_GAIN_OR_LOSS).value == D("2000.00")
    # The taxable half of the 2,000.00 plus the 1,150.00 of dividends.
    assert worksheet.get(TOTAL_INCOME).value == D("2150.00")


def test_a_filer_18_or_older_has_no_deemed_dividend() -> None:
    worksheet = aged_18_or_older()

    assert worksheet.get(TAXABLE_DIVIDENDS).value == D("1150.00")
    assert worksheet.get(SPLIT_INCOME_DIVIDENDS_TOTAL).value == D("1150.00")


def test_a_filer_18_or_older_adds_half_of_line_g_to_part_1_line_3() -> None:
    worksheet = aged_18_or_older()

    # The filer's own 500 plus 20,700.00 x 50% = 10,350.00.
    assert worksheet.get(OTHER_SPLIT_INCOME_TOTAL).value == D("10850.00")
    assert worksheet.get(OTHER_SPLIT_INCOME_CHECKED).value == D("10850.00")
    assert worksheet.get(TOTAL_SPLIT_INCOME).value == D("12000.00")


def test_the_own_line_3_above_the_income_before_losses_is_refused() -> None:
    # The income before losses is 2,150.00; the filer's own line 3 is bounded by it, and the
    # Part 1 line 3 amount of the section (10,350.00) is added after the check.
    message = "ca/other_split_income 2151 is above ca/income_before_losses 2150.00"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        aged_18_or_older(other_split_income="2151")


def test_a_share_loss_does_not_refuse_the_line_3_amount_of_the_section() -> None:
    # Shares sold for 1,000 against a cost of 40,000 lose 39,000, so the income before losses is
    # 0. Part 1 line 3 is still 50% of line G, 10,350.00, which is not bounded by that income.
    inputs = {**SECTION, "aged_18_or_older_at_end_of_2025": 1}
    worksheet = compute("0", (("1000", "40000", "0"),), "0", "0", "0", "0", "0", **inputs)

    assert worksheet.get(SHARE_GAIN_OR_LOSS).value == D("-39000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("0")
    assert worksheet.get(OTHER_SPLIT_INCOME_CHECKED).value == D("10350.00")
    assert worksheet.get(TOTAL_SPLIT_INCOME).value == D("10350.00")


def test_the_deferral_of_line_13_is_bounded_by_the_filers_own_line_4_not_line_g() -> None:
    # Line 4 is the filer's own 2,000: a deferral of 2,000 is accepted, and one above it is
    # refused, line G being on no line of Schedule 3.
    assert aged_18_or_older(capital_gains_deferral="2000").get(
        CAPITAL_GAINS_DEFERRAL_CHECKED
    ).value == D("2000")

    message = "ca/capital_gains_deferral 2000.01 is above ca/share_gain_not_below_zero 2000"
    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        aged_18_or_older(capital_gains_deferral="2000.01")
