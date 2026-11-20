"""The 2026 `ca-qc/solidarity_living_alone_amount` dataset, provisional.

Pins the file as shipped: its figures, rounding, sources and tax year, and the two header
comment lines (the provisional line and the derivation line) that every 2026 file opens with.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/solidarity_living_alone_amount"
PATH = (
    Path(ca_qc_package.__file__).parent
    / "parameters"
    / "solidarity_living_alone_amount"
    / "2026.yaml"
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be "
    "confirmed against the 2026 form text when Revenu Quebec publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file. Table 4 of the "
    "Quebec Finance parameters for 2026 prints the same figure for July 2026 to "
    "June 2027 (the credit paid on the 2025 return); the July 2027 to June 2028 "
    "figure, which a 2026 return receives, is not yet published."
)
EXPECTED: dict[str, Any] = {
    "family": "ca-qc/solidarity_living_alone_amount",
    "tax_year": 2026,
    "kind": "credit",
    "sources": [
        "https://www.revenuquebec.ca/en/citizens/tax-credits/solidarity-tax-credit/calculation-of-the-credit/"
    ],
    "rounding": {"increment": "0.01", "mode": "half_up"},
    "amount": "172",
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
