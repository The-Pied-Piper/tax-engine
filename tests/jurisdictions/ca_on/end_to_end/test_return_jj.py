"""CA-ON 2025 end to end: return JJ, Form T2204 line 4 with the box 55 premiums of a Quebec T4.

Return JJ is `returns/2025_return_jj.yaml`: $50,000 of insurable earnings from a Quebec employer,
box 18 of 655.00 (the Quebec EI rate of 1.31%) and box 55 of 247.00, so line 4 is 902.00, above
1.64% of the earnings (820.00). Line 4 is taken as typed: the form prints no limit on it.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    EI_OVERPAYMENT,
    EI_PREMIUMS,
    T2204_LINE_9,
    T2204_LINE_13,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def jj(premiums: str, ppip: str, insurable: str = "50000", **changes: Any) -> Worksheet:
    """Return JJ's worksheet of `ca-on/return`: T4 box 24 `insurable`, line 4 `premiums` (box 18
    and box 55 together) and the box 55 total `ppip`."""
    inputs = {
        "ei_insurable_earnings": insurable,
        "t2204_insurable_earnings": insurable,
        "t2204_premiums_deducted": premiums,
        "t2204_ppip_premiums": ppip,
        **changes,
    }
    return compute(insurable, (), "0", "0", "0", "0", "0", **inputs)


def test_return_jj_line_4_with_box_55_is_accepted_and_refunds_the_82_above_1_64_percent() -> None:
    # Line 4 = 655.00 + 247.00 = 902.00, read as typed. Line 10 is 820.00, so line 13 is 82.00
    # and line 45000 is 82.00; line 16 (line 31200) is 820.00.
    worksheet = jj("902.00", "247.00")

    assert worksheet.get(T2204_LINE_9).value == D("902.00")
    assert worksheet.get(T2204_LINE_13).value == D("82.00")
    assert worksheet.get(EI_OVERPAYMENT).value == D("82.00")
    assert worksheet.get(EI_PREMIUMS).value == D("820.00")


def test_line_4_above_the_rate_with_box_55_is_read_as_typed() -> None:
    # 1077.01 is a cent above 820.00 + 247.00, and it is taken as the filer enters it: line 13 is
    # 1077.01 - 820.00 = 257.01, and line 45000 is 257.01.
    worksheet = jj("1077.01", "247.00")

    assert worksheet.get(T2204_LINE_9).value == D("1077.01")
    assert worksheet.get(T2204_LINE_13).value == D("257.01")
    assert worksheet.get(EI_OVERPAYMENT).value == D("257.01")


def test_the_same_line_4_without_box_55_is_read_as_typed() -> None:
    # Without box 55 the rate alone is 820.00, and line 4 of 902.00 is taken as typed: line 13 is
    # 82.00.
    worksheet = jj("902.00", "0")

    assert worksheet.get(T2204_LINE_9).value == D("902.00")
    assert worksheet.get(T2204_LINE_13).value == D("82.00")


def test_a_controlling_shareholder_with_no_insurable_earnings_may_claim_box_55() -> None:
    # Note (2): box 24 of 0 with box 55 of 400.00 claimed on line 4. Line 10 is 0.00, so line 13
    # is 400.00 and line 15 is 400.00 (line 45000).
    worksheet = jj("400.00", "400.00", insurable="0")

    assert worksheet.get(T2204_LINE_13).value == D("400.00")
    assert worksheet.get(EI_OVERPAYMENT).value == D("400.00")


def test_box_55_above_line_4_is_refused_naming_box_55() -> None:
    # Box 55 is a part of line 4 ("box 18 and box 55"), so box 55 of 903.00 cannot exceed line 4
    # of 902.00.
    with pytest.raises(InputAboveBoundError, match="ca/t2204_ppip_premiums"):
        jj("902.00", "903.00")
