"""T1 line 33099 medical expenses part: its optional input.

Form text (5006-R, 2025, 5006-r-25e.txt): "Line 107 and line 33099: Medical expenses for self,
spouse or common-law partner and your dependent children under 18 years of age". A salary-only
caller has none, so the input is optional and left blank.
"""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

T1 = FEDERAL_FORMS / "t1_medical_expenses"

BASIC = (
    "Line 107 and line 33099: Medical expenses for self, spouse or common-law partner "
    "and your dependent children under 18 years of age"
)


def test_the_t1_line_has_an_optional_input_left_blank_by_a_salary_only_caller() -> None:
    part: dict[str, Any] = yaml.safe_load(
        (T1 / "t1_medical_expenses_line_33099_inputs.yaml").read_text(encoding="utf-8")
    )

    assert part["form"] == {"name": "ca/t1_medical_expenses"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": "ca/medical_expenses",
        "title": declaration["title"],
        "reference": "33099",
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": BASIC,
    }
