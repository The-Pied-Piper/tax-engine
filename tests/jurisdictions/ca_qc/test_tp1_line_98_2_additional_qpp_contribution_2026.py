"""The 2026 `ca-qc/tp1_line_98_2_additional_qpp_contribution` dataset, provisional.

Pins the file as shipped: its figures, rounding, sources and tax year, and the two header
comment lines (the provisional line and the derivation line) that every 2026 file opens with.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/tp1_line_98_2_additional_qpp_contribution"
PATH = (
    Path(ca_qc_package.__file__).parent
    / "parameters"
    / "tp1_line_98_2_additional_qpp_contribution"
    / "2026.yaml"
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026"
    " form text when Revenu Quebec publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: figure as printed in T4127 (Jan 2026): QPP: second additional "
    "rate 4% from 74,600 to 85,000, maximum 416; no rounding applied here."
)
EXPECTED: dict[str, Any] = {
    "family": "ca-qc/tp1_line_98_2_additional_qpp_contribution",
    "tax_year": 2026,
    "kind": "contribution_tier",
    "sources": [
        "Revenu Quebec TP-1.D-V (2025-12)",
        "Revenu Quebec, Maximum Pensionable Earnings and Quebec Pension Plan "
        "Contribution Rate (web page)",
        "Revenu Quebec, Maximum Pensionable Earnings and Quebec Pension Plan "
        "Contribution Rate (web page, 2026 row; CRA T4127 (Jan 2026) Tables 8.3 "
        "to 8.6, QPP rows)",
    ],
    "rounding": {"increment": "0.01", "mode": "half_up"},
    "rate": "0.04",
    "lower": "0",
    "upper": "10400",
    "maximum": "416",
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
