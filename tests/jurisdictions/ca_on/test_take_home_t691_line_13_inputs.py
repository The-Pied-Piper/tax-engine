"""T691 Part 7 line 13 input: an optional amount, read as 0 when blank."""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

NAME = "ca/t691_line_8_plus_line_12"


def test_line_13_has_an_optional_input_left_blank_by_a_salary_only_caller() -> None:
    part: Any = yaml.safe_load(
        (FEDERAL_FORMS / "t691" / "t691_line_13_inputs.yaml").read_text(encoding="utf-8")
    )

    assert part["form"] == {"name": "ca/t691"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": NAME,
        "title": "Line 8 plus line 12",
        "reference": "13",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": "Line 8 plus line 12",
    }
