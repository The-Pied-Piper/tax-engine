"""CA-ON 2025 end to end: an RDSP income repayment is at most the line 23200 amount it is in."""

from __future__ import annotations

import re

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    RDSP_INCOME_REPAYMENT_CHECKED,
    SOCIAL_BENEFITS_LINE_14,
    SOCIAL_BENEFITS_REPAYMENT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# The input error of `core/at_most` on the repayment against the line 23200 amount:
# "ca/rdsp_income_repayment <amount> is above ca/other_deductions <bound>".
ABOVE_LINE_23200 = "ca/rdsp_income_repayment {amount} is above ca/other_deductions {bound}"


def rdsp_return(rdsp_income_repayment: str, other_deductions: str) -> Worksheet:
    """The return of employment income 100,000 and old age security 8,000 with the RDSP income
    repayment and the caller's line 23200 amount given."""
    return compute(
        "100000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        old_age_security="8000",
        rdsp_income_repayment=rdsp_income_repayment,
        other_deductions=other_deductions,
    )


def test_a_repayment_of_5000_with_no_line_23200_amount_is_refused_not_taken() -> None:
    # Federal Worksheet "Line 23500 - Social benefits repayment" line 13 "RDSP income repayment
    # (included in the amount on line 23200 of your return)": a repayment of 5,000 with nothing on
    # line 23200 is an input error. It is not added to line 14 as if it were a deduction that was
    # never taken, so no social benefits repayment is worked out on it.
    with pytest.raises(
        InputAboveBoundError,
        match=re.escape(ABOVE_LINE_23200.format(amount="5000", bound="0")),
    ):
        rdsp_return("5000", "0")


def test_a_repayment_within_a_line_23200_amount_is_taken_as_the_deduction_it_is_in() -> None:
    # The 5,000 is one of the caller's line 23200 amounts: line 23400 is 5,000 less and line 14 adds
    # the 5,000 back, so line 15 and the social benefits repayment are those of the return with no
    # repayment. The absolute figures are not pinned here; the return with no repayment is the
    # baseline.
    worksheet = rdsp_return("5000", "5000")
    baseline = rdsp_return("0", "0")

    assert worksheet.get(RDSP_INCOME_REPAYMENT_CHECKED).value == D("5000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_14).value == D("5000")
    assert (
        worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value
        == baseline.get(SOCIAL_BENEFITS_REPAYMENT).value
    )


def test_a_repayment_equal_to_the_line_23200_amount_is_accepted() -> None:
    # The bound is inclusive: a repayment of 2,000 within a line 23200 amount of 2,000 is the whole
    # of that amount, and the social benefits repayment is again that of the return with no
    # repayment.
    worksheet = rdsp_return("2000", "2000")
    baseline = rdsp_return("0", "0")

    assert worksheet.get(RDSP_INCOME_REPAYMENT_CHECKED).value == D("2000")
    assert (
        worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value
        == baseline.get(SOCIAL_BENEFITS_REPAYMENT).value
    )


def test_a_repayment_one_cent_above_the_line_23200_amount_is_refused_not_capped() -> None:
    # The bound is refused, not capped: 5,000.01 against 5,000.00 is an input error, and nothing is
    # taken at 5,000.00.
    with pytest.raises(
        InputAboveBoundError,
        match=re.escape(ABOVE_LINE_23200.format(amount="5000.01", bound="5000")),
    ):
        rdsp_return("5000.01", "5000")


def test_a_zero_repayment_is_accepted_and_adds_nothing_to_line_14() -> None:
    # No RDSP income repayment: the checked amount and line 14 are both 0.
    worksheet = rdsp_return("0", "0")

    assert worksheet.get(RDSP_INCOME_REPAYMENT_CHECKED).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_14).value == D("0")
