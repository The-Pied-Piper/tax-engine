"""CA-ON 2025 end to end: return ky (Guide T4002's Rick)."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS,
    FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
    FARMING_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_ky(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return KY's inputs, as in `returns/2025_return_ky.yaml`; `overrides` replace any of them."""
    inputs: dict[str, Any] = dict(
        other_income="2000",
        farm_statements=(
            {
                "farm": {
                    "fertilizers_and_lime": "50000",
                    "optional_inventory_adjustment_current_year": "15000",
                }
            },
        ),
    )
    inputs.update(overrides)
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_kys_ricks_farm_loss_after_the_oia_is_35000() -> None:
    # Line 9899 is the loss before adjustments, -50000; line 9941 adds the OIA of 15000, so
    # amount 4C is -35000, the farming income on the return.
    result = run_ky()
    assert result["ca/t2042"][0].get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-50000")
    assert result["ca/t2042"][0].get(FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS).value == D(
        "-35000"
    )
    assert result["ca-on/return"][0].get(FARMING_INCOME).value == D("-35000")


def test_return_kys_ricks_farm_loss_for_2025_is_33000_after_the_other_income() -> None:
    # The other income of 2000 added to the farm loss of 35000 gives a total income of -33000,
    # the guide's farm loss for 2025.
    result = run_ky()
    assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D("-33000.00")
