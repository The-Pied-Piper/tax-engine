"""T691 Part 5 line 11 input: an optional amount, read as 0 when blank."""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

NAME = "ca/t691_line_7_minus_line_10"


def test_part_5_line_11_has_an_optional_input_left_blank_by_a_salary_only_caller() -> None:
    part: Any = yaml.safe_load(
        (FEDERAL_FORMS / "t691" / "t691_part_5_line_11_inputs.yaml").read_text(encoding="utf-8")
    )

    assert part["form"] == {"name": "ca/t691"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": NAME,
        "title": "Line 7 minus line 10",
        "reference": "Part 5 line 11",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": 'Line 7 minus line 10 (if negative, enter "0")',
    }
