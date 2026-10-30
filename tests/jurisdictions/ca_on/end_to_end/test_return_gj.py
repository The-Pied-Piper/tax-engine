"""CA-ON 2025 end to end: return gj (a box of Schedule 3 line 17906 ticked with line 17905 "Yes").

Return GJ is `returns/2025_return_gj.yaml`: Return GC's filer with no capital gains deferral, a
flipped property answer of line 17905 "Yes" and box 3 of line 17906 ticked. That pairing is valid:
the box is asked after a "Yes", so it is accepted, and a life event applies, so the flag is 0. The
same return with line 17905 "No" and box 3 ticked is refused, an input error, not a flag of 0.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_engine.domain.errors import InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CAPITAL_GAINS_AFTER_DEFERRAL,
    FLIPPED_PROPERTY,
    FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES_CHECKED,
    NET_INCOME,
    REAL_ESTATE_GAIN_OR_LOSS,
    REFUND_OR_BALANCE_OWING,
    SHARE_GAIN_NOT_BELOW_ZERO,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

REFUSED = (
    "ca/flipped_property_life_event_without_yes 1 is refused: a box of line 17906 is ticked "
    'without a "Yes" on line 17905'
)


def _run_gj(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return GJ's inputs, as in `returns/2025_return_gj.yaml`, with `overrides` for any of them:
    Return GC's filer and dispositions, with no capital gains deferral, the Schedule 3 answers
    line 17905 "Yes" (1) and box 3 of line 17906 ticked (1)."""
    inputs: dict[str, Any] = {
        "income_tax_deducted": "4800",
        "flipped_property_disposed": 1,
        "flipped_property_life_event_3": 1,
    }
    return run(
        "48000",
        (("5000", "0", "0"),),
        "0",
        "0",
        "8640",
        "0",
        "0",
        real_estate_dispositions=(("7000", "5000", "0", 0),),
        **{**inputs, **overrides},
    )


def return_gj(**overrides: Any) -> Worksheet:
    """The worksheet of the return `ca-on/return` for Return GJ."""
    (worksheet,) = _run_gj(**overrides)["ca-on/return"]
    return worksheet


def schedule_3_gj(**overrides: Any) -> Worksheet:
    """The worksheet of Schedule 3 Part 1 (`ca/schedule_3`) for Return GJ."""
    (worksheet,) = _run_gj(**overrides)["ca/schedule_3"]
    return worksheet


def test_a_box_ticked_with_line_17905_yes_computes_and_the_flag_is_0() -> None:
    # Line 17905 "Yes" and box 3 ticked: the box is accepted and no check refuses it, a life event
    # applies so the flag is 0, and the check's count of boxes ticked without a "Yes" is 0.
    schedule = schedule_3_gj()

    assert schedule.get(FLIPPED_PROPERTY).value == 0
    assert schedule.get(FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES_CHECKED).value == 0


def test_return_gj_computes_the_capital_gains_without_a_deferral_and_the_tax_on_them() -> None:
    # Line 12 is 5000 + 2000 = 7000 and, with no deferral, line 14 is 7000; line 24 is half of it,
    # 3500.00, the taxable capital gains. Total income is 48000 + 3500.00 = 51500.00 and the net
    # income is that less the enhanced CPP deduction of 445.00, as on Return GC.
    worksheet = return_gj()

    assert worksheet.get(SHARE_GAIN_NOT_BELOW_ZERO).value == D("5000")
    assert worksheet.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("2000")
    assert worksheet.get(CAPITAL_GAINS_AFTER_DEFERRAL).value == D("7000")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("3500.00")
    assert worksheet.get(TOTAL_INCOME).value == D("51500.00")
    assert worksheet.get(NET_INCOME).value == D("51055.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("51055.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("6801.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("4800.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2001.00")


def test_a_box_ticked_with_line_17905_no_is_refused_not_given_a_flag_of_0() -> None:
    # With line 17905 "No" a box of line 17906 is an input error, naming the box-without-Yes text.
    with pytest.raises(InputOutOfRangeError, match=re.escape(REFUSED)):
        return_gj(flipped_property_disposed=0)


def test_the_same_return_with_line_17905_no_and_no_box_ticked_computes_with_the_flag_0() -> None:
    schedule = schedule_3_gj(flipped_property_disposed=0, flipped_property_life_event_3=0)
    worksheet = return_gj(flipped_property_disposed=0, flipped_property_life_event_3=0)

    assert schedule.get(FLIPPED_PROPERTY).value == 0
    assert schedule.get(FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES_CHECKED).value == 0
    assert worksheet.get(TOTAL_PAYABLE).value == D("6801.00")
