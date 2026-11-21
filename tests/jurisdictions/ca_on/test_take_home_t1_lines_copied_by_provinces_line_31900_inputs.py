"""T1 line 31900 part of the lines the provinces copy: its optional input."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

T1 = FEDERAL_FORMS / "t1_lines_copied_by_provinces"

LINE = "31900"
NAME = "ca/student_loan_interest"
OUTPUT = "ca/student_loan_interest_line_31900"
BASIC = (
    "Line 102 and line 31900: Interest paid on your student loans (go to canada.ca/taxes-students)"
)
TITLE = "Interest paid on your student loans"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_t1_line_has_an_optional_input_left_blank_by_a_salary_only_caller() -> None:
    part = _part(T1 / f"t1_lines_copied_by_provinces_line_{LINE}_inputs.yaml")

    assert part["form"] == {"name": "ca/t1_lines_copied_by_provinces"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": NAME,
        "title": TITLE,
        "reference": LINE,
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": BASIC,
    }
