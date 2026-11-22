"""The federal T1 employment income form asks the take-home caller for the gross salary only.

The part `t1_employment_income_line_10100_inputs.yaml` declares the one input of T1 line 10100,
employment income, and gives it to the form `ca/t1_employment_income`; every other form reads it
as that form's export. The provinces other than Quebec import the federal forms, so this one
part serves them all; Quebec's own part is tested in the `ca_qc` test of the same name.
"""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

PART = FEDERAL_FORMS / "t1_employment_income" / "t1_employment_income_line_10100_inputs.yaml"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "inputs"]
    return part


def _inputs() -> list[dict[str, Any]]:
    return list(_part()["inputs"])


def test_the_salary_belongs_to_the_t1_employment_income_form() -> None:
    assert _part()["form"] == {"name": "ca/t1_employment_income"}


def test_the_salary_is_the_only_required_input() -> None:
    required = [declaration["name"] for declaration in _inputs() if declaration["required"]]

    assert required == ["ca/employment_income"]
    assert len(_inputs()) == 1


def test_the_salary_input_is_the_printed_employment_income_in_canadian_dollars() -> None:
    assert _inputs()[0] == {
        "name": "ca/employment_income",
        "title": "Employment income",
        "reference": "10100",
        "unit": "ca/cad",
        "required": True,
        "whole_cents": True,
    }
    assert list(_inputs()[0]) == [
        "name",
        "title",
        "reference",
        "unit",
        "required",
        "whole_cents",
    ]
