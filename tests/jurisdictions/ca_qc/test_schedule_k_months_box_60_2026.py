"""The 2026 `ca-qc/schedule_k_months_box_60` dataset, provisional.

Pins the file as shipped: its figures, rounding, sources and tax year, and the two header
comment lines (the provisional line and the derivation line) that every 2026 file opens with.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/schedule_k_months_box_60"
PATH = Path(ca_qc_package.__file__).parent / "parameters" / "schedule_k_months_box_60" / "2026.yaml"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be "
    "confirmed against the 2026 form text when Revenu Quebec publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; the 2026 form is"
    " not yet published."
)
EXPECTED: dict[str, Any] = {
    "family": "ca-qc/schedule_k_months_box_60",
    "tax_year": 2026,
    "kind": "amount_by_count",
    "sources": ["Revenu Quebec TP-1.D.K-V (2025-12)"],
    "rounding": {"increment": "0.01", "mode": "half_up"},
    "amounts": {"0": "0", "1": "6"},
}


def test_the_2026_file_holds_the_pinned_figures() -> None:
    assert yaml.safe_load(PATH.read_text()) == EXPECTED


def test_the_2026_file_is_for_tax_year_2026_of_this_family() -> None:
    data = yaml.safe_load(PATH.read_text())

    assert data["family"] == FAMILY
    assert data["tax_year"] == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = PATH.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
