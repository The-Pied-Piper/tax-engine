"""The 2026 condition of 5000-G line 31205's count, checked against the printed guide.

5000-G (2025), line 31205: "If your PPIP insurable earnings are less than $2,000, do not claim any
PPIP premiums on line 31205. Instead, claim this amount as an overpayment on your Revenu Québec
Income Tax Return." No condition kind reads "less than", so the dataset
`ca-qc/ppip_premium_line_91_conditions` copies the test as its two complements, "equal to $2,000"
and
"more than $2,000". The count is 0 when either applies and 1 when neither does, so exactly $2,000
gives 0, and so does $2,000.01, and $1,999.99 gives 1.

The count is a whole number, not a dollars-and-cents box, so nothing is rounded.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/ppip_premium_line_91_conditions"
PATH = (
    Path(ca_qc_package.__file__).parent
    / "parameters"
    / "ppip_premium_line_91_conditions"
    / "2026.yaml"
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be "
    "confirmed against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; the 2026 form is"
    " not yet published."
)
EXPECTED: dict[str, Any] = {
    "family": "ca-qc/ppip_premium_line_91_conditions",
    "tax_year": 2026,
    "kind": "conditions",
    "sources": ["https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-g/5000-g-25e.txt"],
    "rounding": "none",
    "count_when_any_applies": "0",
    "conditions": [
        {
            "text": "The PPIP insurable earnings are equal to $2,000",
            "parts": [
                {
                    "tests": [
                        {"reads": "amount", "position": "1", "relation": "equal_to", "than": "2000"}
                    ]
                }
            ],
        },
        {
            "text": "The PPIP insurable earnings are more than $2,000",
            "parts": [
                {
                    "tests": [
                        {
                            "reads": "amount",
                            "position": "1",
                            "relation": "more_than",
                            "than": "2000",
                        }
                    ]
                }
            ],
        },
    ],
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
