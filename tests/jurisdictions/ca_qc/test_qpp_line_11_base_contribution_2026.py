"""The 2026 `ca-qc/qpp_line_11_base_contribution` dataset, provisional.

Pins the file as shipped: its figures, rounding, sources and tax year, and the two header
comment lines (the provisional line and the derivation line) that every 2026 file opens with.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/qpp_line_11_base_contribution"
PATH = (
    Path(ca_qc_package.__file__).parent
    / "parameters"
    / "qpp_line_11_base_contribution"
    / "2026.yaml"
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026"
    " form text when Revenu Quebec publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: figure as printed in T4127 (Jan 2026): base QPP rate 5.30% on "
    "the contributory earnings 71,100, maximum 3,768.30 (T4127 Tables 8.3 and "
    "8.4); no rounding applied here."
)
EXPECTED: dict[str, Any] = {
    "family": "ca-qc/qpp_line_11_base_contribution",
    "tax_year": 2026,
    "kind": "contribution_tier",
    "sources": [
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s8/5005-s8-25e.txt",
        "Revenu Quebec, Maximum Pensionable Earnings and Quebec Pension Plan "
        "Contribution Rate (web page, 2026 row; CRA T4127 (Jan 2026) Tables 8.3 "
        "to 8.6, QPP rows)",
    ],
    "rounding": {"increment": "0.01", "mode": "half_up"},
    "rate": "0.053",
    "lower": "0",
    "upper": "71100",
    "maximum": "3768.30",
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
