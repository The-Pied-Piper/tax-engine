"""T1 line 31217 part of the lines the provinces copy: its optional input."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

T1 = FEDERAL_FORMS / "t1_lines_copied_by_provinces"

LINE = "31217"
NAME = "ca/ei_premiums_on_self_employment"
OUTPUT = "ca/ei_premiums_on_self_employment_line_31217"
BASIC = (
    "Line 89 and line 31217: on self-employment and other eligible earnings (complete Schedule 13)"
)
TITLE = "Employment insurance premiums on self-employment and other eligible earnings"


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
