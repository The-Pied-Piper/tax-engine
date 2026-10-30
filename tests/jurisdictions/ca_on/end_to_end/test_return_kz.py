"""CA-ON 2025 end to end: return kz (Guide T4002's Patrick)."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
    REFUND,
    TOTAL_CREDITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_kz(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return KZ's inputs, as in `returns/2025_return_kz.yaml`; `overrides` replace any of them."""
    inputs: dict[str, Any] = dict(
        employee_and_partner_gst_hst_rebate="392.90",
    )
    inputs.update(overrides)
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_kzs_patricks_gst_hst_rebate_for_partners_is_a_credit_of_392_90() -> None:
    # T1 line 45700 is the 392.90 Patrick enters from his Form GST370 ($8,250.84 x 5 / 105), a
    # refundable credit: the total credits and the refund are 392.90.
    result = run_kz()
    assert result["ca-on/return"][0].get(EMPLOYEE_AND_PARTNER_GST_HST_REBATE).value == D("392.90")
    assert result["ca-on/return"][0].get(TOTAL_CREDITS).value == D("392.90")
    assert result["ca-on/return"][0].get(REFUND).value == D("392.90")
