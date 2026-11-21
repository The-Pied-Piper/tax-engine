"""T1 line 12500 UCCB/RDSP part: its optional input."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca

T1 = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms" / "t1_uccb_rdsp"

LINE = "12500"
NAME = "ca/rdsp_income"
OUTPUT = "ca/rdsp_income_line_12500"
BASIC = (
    "Line 12 and line 12500: Registered disability savings plan "
    "(RDSP) income (box 131 of the T4A slip)"
)


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_each_t1_line_has_an_optional_input_left_blank_by_a_salary_only_caller() -> None:
    part = _part(T1 / f"t1_uccb_rdsp_line_{LINE}_inputs.yaml")

    assert part["form"] == {"name": "ca/t1_uccb_rdsp"}
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
