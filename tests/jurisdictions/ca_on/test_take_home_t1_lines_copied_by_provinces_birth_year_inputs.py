"""The T1's year of birth input, owned by the form of the lines the provinces copy."""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

T1 = FEDERAL_FORMS / "t1_lines_copied_by_provinces"


def _part(name: str) -> dict[str, Any]:
    part = yaml.safe_load((T1 / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_t1_declares_the_optional_year_of_birth_left_blank_by_a_salary_only_caller() -> None:
    part = _part("t1_lines_copied_by_provinces_birth_year_inputs.yaml")

    assert part["form"] == {"name": "ca/t1_lines_copied_by_provinces"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": "ca/birth_year",
        "title": "Year of birth",
        "required": False,
        "default": None,
        "basis": (
            'Enter your date of birth in the "Step 1 - Identification and other information" '
            "area on page 1 of your return."
        ),
    }


def test_the_form_exports_the_year_of_birth_for_the_provinces_to_read() -> None:
    form = _part("t1_lines_copied_by_provinces.yaml")["form"]

    assert "ca/birth_year" in form["exports"]
