"""CA-ON 2025 end to end: return gc (the Schedule 3 line 13 deferral checked at most line 4)."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.trace import AtMostLine, SubtractedLine, SumNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CAPITAL_GAINS_AFTER_DEFERRAL,
    CAPITAL_GAINS_BEFORE_RESERVES,
    CAPITAL_GAINS_DEFERRAL,
    CAPITAL_GAINS_DEFERRAL_CHECKED,
    CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES,
    NET_INCOME,
    REAL_ESTATE_GAIN_OR_LOSS,
    REFUND_OR_BALANCE_OWING,
    SHARE_GAIN_NOT_BELOW_ZERO,
    SHARE_GAIN_OR_LOSS,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    Disposition,
    RealEstateDisposition,
    compute,
)


def return_gc(
    share_dispositions: tuple[Disposition, ...] = (("5000", "0", "0"),),
    real_estate_dispositions: tuple[RealEstateDisposition, ...] = (("7000", "5000", "0", 0),),
    **overrides: Any,
) -> Worksheet:
    """Return GC's inputs, as in `returns/2025_return_gc.yaml`: Return AF's filer with no net
    capital losses of other years, a share row of proceeds 5000 (a gain of 5000), a real estate
    row of proceeds 7000 and cost 5000 (a gain of 2000), and a capital gains deferral of 5000
    (line 13), equal to line 4 unless `overrides` say otherwise.

    Employment income of 48000, line 4 of 5000, line 5 of 2000 and line 12 of 7000; line 14 is
    7000 less the deferral, and line 24 is half of line 21 (2000), so the taxable capital gains
    are 1000.00.
    """
    inputs: dict[str, Any] = {
        "income_tax_deducted": "4800",
        "capital_gains_deferral": "5000",
    }
    return compute(
        "48000",
        share_dispositions,
        "0",
        "0",
        "8640",
        "0",
        "0",
        real_estate_dispositions=real_estate_dispositions,
        **{**inputs, **overrides},
    )


def test_a_deferral_equal_to_line_4_is_accepted_and_line_14_is_line_12_less_it() -> None:
    # Schedule 3 line 4 "Total gain or loss" is 5000 (the one share row); line 13, the deferral
    # "included on line 4", is 5000, equal to it, so it is accepted (not refused, and not capped).
    # Line 12 is 5000 + 2000 = 7000, and line 14 is 7000 - 5000 = 2000, the capital gain of line
    # 21 (no reserves), half of which, 1000.00, is the taxable capital gains (line 12700).
    worksheet = return_gc()

    assert worksheet.get(SHARE_GAIN_OR_LOSS).value == D("5000")
    assert worksheet.get(SHARE_GAIN_NOT_BELOW_ZERO).value == D("5000")
    assert worksheet.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("2000")
    assert worksheet.get(CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES).value == D("7000")
    assert worksheet.get(CAPITAL_GAINS_DEFERRAL_CHECKED).value == D("5000")
    assert worksheet.get(CAPITAL_GAINS_AFTER_DEFERRAL).value == D("2000")
    assert worksheet.get(CAPITAL_GAINS_BEFORE_RESERVES).value == D("2000")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("1000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("49000.00")
    assert worksheet.get(NET_INCOME).value == D("48555.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("48555.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("6228.75")
    assert worksheet.get(TOTAL_CREDITS).value == D("4800.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("1428.75")


def test_the_trace_records_the_deferral_checked_at_most_line_4_and_line_4_floored() -> None:
    trace = return_gc().trace

    assert (
        AtMostLine(
            output=CAPITAL_GAINS_DEFERRAL_CHECKED,
            amount_kind=CAPITAL_GAINS_DEFERRAL,
            amount_value=D("5000"),
            bound=SHARE_GAIN_NOT_BELOW_ZERO,
            bound_value=D("5000"),
        )
        in trace
    )
    assert (
        SumNotBelowZeroLine(
            output=SHARE_GAIN_NOT_BELOW_ZERO,
            parts=((SHARE_GAIN_OR_LOSS, D("5000")),),
            total=D("5000"),
        )
        in trace
    )
    assert (
        SubtractedLine(
            output=CAPITAL_GAINS_AFTER_DEFERRAL,
            minuend=CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES,
            minuend_amount=D("7000"),
            subtrahend=CAPITAL_GAINS_DEFERRAL_CHECKED,
            subtrahend_amount=D("5000"),
            result=D("2000"),
        )
        in trace
    )


def test_a_share_loss_floors_line_4_at_0_so_a_deferral_of_0_is_accepted() -> None:
    # Schedule 3 line 4 is a loss of 1000 (proceeds 0, cost 1000): it is not a gain, so the bound
    # of line 13 is 0, and a deferral of 0 is at most it. Line 14 is then the loss itself.
    worksheet = return_gc(
        share_dispositions=(("0", "1000", "0"),),
        real_estate_dispositions=(),
        capital_gains_deferral="0",
    )

    assert worksheet.get(SHARE_GAIN_OR_LOSS).value == D("-1000")
    assert worksheet.get(SHARE_GAIN_NOT_BELOW_ZERO).value == D("0")
    assert worksheet.get(CAPITAL_GAINS_DEFERRAL_CHECKED).value == D("0")
    assert worksheet.get(CAPITAL_GAINS_AFTER_DEFERRAL).value == D("-1000")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("0")
    assert (
        SumNotBelowZeroLine(
            output=SHARE_GAIN_NOT_BELOW_ZERO,
            parts=((SHARE_GAIN_OR_LOSS, D("-1000")),),
            total=D("0"),
        )
        in worksheet.trace
    )


def test_a_deferral_above_line_4_is_refused_not_capped_though_line_12_is_larger() -> None:
    # The deferral of 5001 is one dollar above line 4 of 5000, although line 12 (7000) is larger
    # than it: the deferral is "included on line 4", so it is an input error, not capped.
    message = "ca/capital_gains_deferral 5001 is above ca/share_gain_not_below_zero 5000"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_gc(capital_gains_deferral="5001")


def test_a_deferral_with_no_share_row_is_refused_as_above_a_line_4_of_0() -> None:
    # With no share row, line 4 is 0, so any deferral is above it.
    message = "ca/capital_gains_deferral 1 is above ca/share_gain_not_below_zero 0"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_gc(
            share_dispositions=(),
            real_estate_dispositions=(),
            capital_gains_deferral="1",
        )


def test_the_dollar_example_a_real_estate_gain_of_9000_cannot_defer_3000() -> None:
    # A real estate gain of 9000 with no share row, and a deferral of 3000. Line 4 is 0, so the
    # deferral is refused; without the refusal it would take 3000 off line 12 and understate the
    # taxable capital gains by 1500.
    message = "ca/capital_gains_deferral 3000 is above ca/share_gain_not_below_zero 0"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_gc(
            share_dispositions=(),
            real_estate_dispositions=(("9000", "0", "0", 0),),
            capital_gains_deferral="3000",
        )
