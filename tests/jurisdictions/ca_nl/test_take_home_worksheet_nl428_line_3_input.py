"""NL428 worksheet (2025) line 3's input, as the Newfoundland and Labrador part declares it.

Form text (Worksheet NL428, CRA 5001-D, 5001-d-25e.txt), under line 58440: "Line 3: Total child
care and attendant care expenses for you, claimed by you or another person". A salary-only caller
has none, so the input is optional. The real part is read directly, as the worksheet's other lines
are another ticket's.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl

PART = (
    Path(tax_engine.jurisdictions.ca_nl.__file__).parent
    / "manifests"
    / "2025"
    / "worksheet_nl428_line_3_input.yaml"
)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_belongs_to_the_worksheet_form() -> None:
    assert _part()["form"] == {"name": "ca-nl/nl428_worksheet"}


def test_the_part_declares_the_one_optional_input_as_printed() -> None:
    (declaration,) = _part()["inputs"]

    assert declaration["name"] == "ca/disability_self_care_expenses"
    assert declaration["title"] == (
        "Total child care and attendant care expenses for you, claimed by you or another person"
    )
    assert declaration["reference"] == "3"
    assert declaration["unit"] == "ca/cad"
    assert declaration["required"] is False
