"""The T1 form of the lines the provinces copy: its declaration and exports."""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

PART = FEDERAL_FORMS / "t1_lines_copied_by_provinces" / "t1_lines_copied_by_provinces.yaml"


def test_the_form_is_required_has_the_t1_title_and_exports_the_five_lines() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {
        "name": "ca/t1_lines_copied_by_provinces",
        "title": "T1 Income Tax and Benefit Return",
        "required": True,
        "exports": [
            "ca/self_employment_cpp_qpp_contributions_line_31000",
            "ca/student_loan_interest_line_31900",
            "ca/medical_expenses_line_33099",
            "ca/other_dependants_medical_expenses_line_33199",
            "ca/minimum_tax_carryover_line_40427",
        ],
    }
    assert part["capabilities"] == []
