"""CA-ON 2025 end to end: return lb (Guide T4002's Wade and Vicky)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    FARM_RECAPTURED_CCA,
    FARM_TERMINAL_LOSS,
    REAL_ESTATE_GAIN_OR_LOSS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_lb(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return LB's inputs, as in `returns/2025_return_lb.yaml`; `overrides` replace any of them."""
    inputs: dict[str, Any] = dict(
        cpp_part_4_completed=1,
        real_estate_dispositions=(("85000", "85000", "0", 0),),
        farm_statements=(
            {
                "farm": {"wheat": "10000"},
                "farm_cca_classes_rows": (
                    ("8", "7840", "0", "7840", "0", "0", "0", 1, "0", "0", "0"),
                ),
            },
        ),
    )
    inputs.update(overrides)
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_lbs_wades_combine_at_its_ucc_has_no_recapture_or_terminal_loss() -> None:
    # Class 8: opening UCC 7840 less proceeds 7840 is 0, so there is nothing to recapture and
    # no terminal loss.
    result = run_lb()
    assert result["ca/t2042"][0].get(FARM_RECAPTURED_CCA).value == D("0")
    assert result["ca/t2042"][0].get(FARM_TERMINAL_LOSS).value == D("0")


def test_return_lbs_wades_land_at_its_acb_has_no_gain() -> None:
    # Land transferred at its ACB: proceeds 85000 less cost 85000 is a real estate gain of 0
    # and a capital gain of 0.
    result = run_lb()
    assert result["ca-on/return"][0].get(REAL_ESTATE_GAIN_OR_LOSS).value == D("0")
    assert result["ca-on/return"][0].get(CAPITAL_GAIN).value == D("0")
