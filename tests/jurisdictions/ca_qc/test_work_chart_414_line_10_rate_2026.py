"""The 2026 `ca-qc/work_chart_414_line_10_rate` dataset, provisional.

Pins the file as shipped: its figures, rounding, sources and tax year, and the two comment lines
(the provisional line and the derivation line) that close every 2026 file of this chart.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/work_chart_414_line_10_rate"
PATH = (
    Path(ca_qc_package.__file__).parent / "parameters" / "work_chart_414_line_10_rate" / "2026.yaml"
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when Revenu Quebec publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; "
    "the 2026 form is not yet published."
)

EXPECTED: dict[str, Any] = {
    "family": FAMILY,
    "tax_year": 2026,
    "kind": "rate",
    "sources": ["Revenu Quebec TP-1.D.GR-V (2025-12), Work Chart 414"],
    "rounding": {"increment": "0.01", "mode": "half_up"},
    "rate": "0.85",
}


def test_the_2026_file_holds_the_pinned_figures() -> None:
    assert yaml.safe_load(PATH.read_text()) == EXPECTED


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = PATH.read_text().splitlines()

    assert lines[-2:] == [PROVISIONAL_HEADER, DERIVATION_HEADER]
