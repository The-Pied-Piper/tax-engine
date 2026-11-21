"""T1 line 11700 UCCB/RDSP part: its optional input."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca

T1 = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms" / "t1_taxable_income"

LINE = "11700"
NAME = "ca/uccb_income"
OUTPUT = "ca/uccb_income_line_11700"
BASIC = "Line 7 and line 11700: Universal child care benefit (UCCB) (see the RC62 slip)"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_each_t1_line_has_an_optional_input_left_blank_by_a_salary_only_caller() -> None:
    part = _part(T1 / f"t1_taxable_income_line_{LINE}_inputs.yaml")

    assert part["form"] == {"name": "ca/t1_taxable_income"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": NAME,
        "title": declaration["title"],
        "reference": LINE,
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": BASIC,
    }
