"""T1 line 33199 medical expenses part: one sum step reading the blank as 0."""

from __future__ import annotations

from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

T1 = FEDERAL_FORMS / "t1_medical_expenses"


def test_the_t1_line_is_one_sum_step_that_reads_its_blank_as_zero() -> None:
    part: dict[str, Any] = yaml.safe_load(
        (T1 / "t1_medical_expenses_line_33199.yaml").read_text(encoding="utf-8")
    )

    assert part["form"] == {"name": "ca/t1_medical_expenses"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": step["title"],
        "reference": "33199",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": ["ca/other_dependants_medical_expenses"]},
        "blank": {"ca/other_dependants_medical_expenses": "0"},
        "produces": {"output": "ca/other_dependants_medical_expenses_line_33199"},
    }
