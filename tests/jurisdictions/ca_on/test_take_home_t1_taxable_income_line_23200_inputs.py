"""T1 line 23200 UCCB/RDSP part: its optional input."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

T1 = FEDERAL_FORMS / "t1_taxable_income"

LINE = "23200"
NAME = "ca/rdsp_income_repayment"
OUTPUT = "ca/rdsp_income_repayment_line_23200"
BASIC = "Line 52 and line 23200: Other deductions (specify)"


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
