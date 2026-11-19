"""Worksheet NL428 (2025) line 58440's inputs, from the real part.

Form text (Worksheet NL428, CRA 5001-D, 2025, 5001-d-25e.txt, confirmed 2026-11-19): "Line 58440 -
Disability amount for self. Complete this calculation if you were under 18 years of age on December
31, 2025." and "Line 3: Total child care and attendant care expenses for you, claimed by you or
another person". The first is a yes or no answer, the existing shared count
`ca/under_18_on_december_31`; the second is the existing shared amount
`ca/disability_self_care_expenses`. Both are optional and left blank by a salary-only caller.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl

PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
INPUT_PART = PARTS / "worksheet_nl428_line_58440_input.yaml"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_input_part_declares_the_under_18_answer_and_the_care_expenses() -> None:
    under_18, care = _part(INPUT_PART)["inputs"]

    assert under_18["name"] == "ca/under_18_on_december_31"
    assert under_18["reference"] == "58440"
    assert under_18["required"] is False
    assert under_18["default"] is None
    assert under_18["basis"] == (
        "Complete this calculation if you were under 18 years of age on December 31, 2025."
    )
    assert care["name"] == "ca/disability_self_care_expenses"
    assert care["reference"] == "3"
    assert care["unit"] == "ca/cad"
    assert care["required"] is False
    assert care["default"] is None
