"""T1 line 33199 part of the lines the provinces copy: its optional input."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

T1 = FEDERAL_FORMS / "t1_lines_copied_by_provinces"

LINE = "33199"
NAME = "ca/other_dependants_medical_expenses"
OUTPUT = "ca/other_dependants_medical_expenses_line_33199"
BASIC = (
    "Line 111 and line 33199: Allowable amount of medical expenses for other dependants (use "
    "Federal Worksheet)"
)
TITLE = "Allowable amount of medical expenses for other dependants (use Federal Worksheet)"


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
