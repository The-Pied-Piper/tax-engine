"""CA-ON 2025 end to end: return la (Guide T4002's Helena)."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    REAL_ESTATE_GAIN_OR_LOSS,
    TAXABLE_CAPITAL_GAINS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_la(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return LA's inputs, as in `returns/2025_return_la.yaml`; `overrides` replace any of them."""
    inputs: dict[str, Any] = dict(
        real_estate_dispositions=(
            ("175000", "105000", "0", 0),
            ("20000", "16000", "0", 1),
            ("5000", "4000", "0", 1),
        ),
        principal_residence_properties_rows=((12, 0, 12, 0, "100000", "0", "75000", 1),),
    )
    inputs.update(overrides)
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_las_helenas_farm_gain_is_75000_with_the_residence_exempt() -> None:
    # The three farm rows give (175000 - 105000) + (20000 - 16000) + (5000 - 4000) = 75000;
    # her principal residence, all years designated, adds no taxable gain, so the capital gain
    # is 75000.
    result = run_la()
    assert result["ca-on/return"][0].get(REAL_ESTATE_GAIN_OR_LOSS).value == D("75000")
    assert result["ca-on/return"][0].get(CAPITAL_GAIN).value == D("75000.00")


def test_return_las_helenas_taxable_capital_gain_is_37500_on_t1_line_12700() -> None:
    # Half of 75000 is 37500, the taxable capital gain, which is also the total income.
    result = run_la()
    assert result["ca-on/return"][0].get(TAXABLE_CAPITAL_GAINS).value == D("37500.00")
    assert result["ca-on/return"][0].get(TOTAL_INCOME).value == D("37500.00")
