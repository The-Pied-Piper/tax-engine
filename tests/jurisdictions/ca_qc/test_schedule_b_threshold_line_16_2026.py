"""The 2026 `ca-qc/schedule_b_threshold_line_16` dataset, provisional.

Pins the file as shipped: its figures, rounding, sources and tax year, and the two header
comment lines (the provisional line and the derivation line) that every 2026 file opens with.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/schedule_b_threshold_line_16"
PATH = (
    Path(ca_qc_package.__file__).parent
    / "parameters"
    / "schedule_b_threshold_line_16"
    / "2026.yaml"
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from Quebec Finance, Parameters of the Personal Income "
    "Tax System for 2026 (Nov 2025), Table 3; to be confirmed against the 2026 "
    "form text when Revenu Quebec publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: figure as printed in the Quebec Finance parameters for 2026: "
    "reduction threshold of the credit for a person living alone 42,955 (Table "
    "3); no rounding applied here."
)
EXPECTED: dict[str, Any] = {
    "family": "ca-qc/schedule_b_threshold_line_16",
    "tax_year": 2026,
    "kind": "credit",
    "sources": [
        "Revenu Quebec TP-1.D.B-V (2025-12), Schedule B, Part A",
        "Quebec Ministere des Finances, Parameters of the Personal Income Tax "
        "System for 2026 (Nov 2025), Table 3, "
        "https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTEN_IncomeTax2026.pdf",
    ],
    "rounding": {"increment": "0.01", "mode": "half_up"},
    "amount": "42955",
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
