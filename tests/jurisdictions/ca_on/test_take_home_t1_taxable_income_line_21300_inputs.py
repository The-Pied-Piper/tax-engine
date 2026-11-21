"""T1 line 21300 UCCB/RDSP part: its optional input."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca

T1 = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms" / "t1_taxable_income"

LINE = "21300"
NAME = "ca/uccb_repayment"
OUTPUT = "ca/uccb_repayment_line_21300"
BASIC = (
    "Line 40 and line 21300: Universal child care benefit (UCCB) "
    "repayment (box 12 of all RC62 slips)"
)


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
