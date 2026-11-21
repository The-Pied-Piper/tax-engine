"""T1 line 31000 part of the lines the provinces copy: its optional input."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

T1 = FEDERAL_FORMS / "t1_lines_copied_by_provinces"

LINE = "31000"
NAME = "ca/self_employment_cpp_qpp_contributions"
OUTPUT = "ca/self_employment_cpp_qpp_contributions_line_31000"
BASIC = "Line 87 and line 31000: on self-employment income and other earnings"
TITLE = "Base CPP or QPP contributions on self-employment income and other earnings"


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
