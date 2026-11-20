"""The 2026 `ca-qc/quebec_abatement_rate` dataset, provisional.

Pins the file as shipped: its figures, rounding, sources and tax year, and the two header
comment lines (the provisional line and the derivation line) that every 2026 file opens with.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/quebec_abatement_rate"
PATH = Path(ca_qc_package.__file__).parent / "parameters" / "quebec_abatement_rate" / "2026.yaml"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026), Table 8.2; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: figure as printed in T4127 (Jan 2026) Table 8.2, Quebec row, "
    "abatement 0.165 (16.5%); no rounding applied here."
)
EXPECTED: dict[str, Any] = {
    "family": "ca-qc/quebec_abatement_rate",
    "tax_year": 2026,
    "kind": "rate",
    "sources": [
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
    ],
    "rounding": {"increment": "0.01", "mode": "half_up"},
    "rate": "0.165",
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
