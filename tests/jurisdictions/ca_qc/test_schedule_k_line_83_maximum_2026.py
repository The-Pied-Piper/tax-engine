"""The 2026 `ca-qc/schedule_k_line_83_maximum` dataset, provisional.

Pins the file as shipped: its figures, rounding, sources and tax year, and the two header
comment lines (the provisional line and the derivation line) that every 2026 file opens with.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/schedule_k_line_83_maximum"
PATH = (
    Path(ca_qc_package.__file__).parent / "parameters" / "schedule_k_line_83_maximum" / "2026.yaml"
)
PROVISIONAL_HEADER = (
    "# Provisional: derived from the published 2026-27 premium-year maximum, "
    "not printed on a 2026 form; to be confirmed against the 2026 form text when Revenu "
    "Quebec publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: 789 is RAMQ's maximum annual premium from 1 July 2026 (RAMQ release of 30 June "
    "2026); the 2025 form's line 83 maximum, 766, is the maximum of the premium year that began "
    "in July 2025, so the 2026 line 83 maximum is the one that begins in July 2026."
)
EXPECTED: dict[str, Any] = {
    "family": "ca-qc/schedule_k_line_83_maximum",
    "tax_year": 2026,
    "kind": "amount",
    "title": "maximum premium",
    "unit": "ca/cad",
    "sources": [
        "Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part C",
        "Regie de l'assurance maladie du Quebec, release of 30 June 2026 "
        "(annual premium maximums 766 and 789)",
    ],
    "rounding": {"increment": "0.01", "mode": "half_up"},
    "amount": "789",
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
