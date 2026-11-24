"""The Newfoundland and Labrador return part's average tax rate steps (2025).

The return part reads T1 line 43500 "Total payable", the CPP (Schedule 8 lines 25 and 28) and the
EI premium (T2204 line 16) into its own figures with `core/record_total`, adds them with
`core/sum` into `ca/return_total_deductions`, then divides that by the salary with `core/divide`,
rounded once by the `ca/take_home_average_rate_rounding` dataset (half-up to 0.0001), into
`ca-nl/average_tax_rate`. No step is printed on a form, so none carries a title or a reference.
The figures are in `test_take_home_return_average_tax_rate.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl

RETURN_PART = (
    Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025" / "return.yaml"
)


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(RETURN_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def _producing(output: str) -> dict[str, Any]:
    (step,) = [step for step in _steps() if step["produces"]["output"] == output]
    return step


def test_the_return_part_adds_the_deductions_and_divides_them_by_the_salary() -> None:
    total = _producing("ca/total_payable")
    deductions = _producing("ca/return_total_deductions")
    divide = _producing("ca-nl/average_tax_rate")

    assert total["name"] == "core/record_total"
    assert total["unit"] == "ca/cad"
    assert total["consumes"] == {"records": "ca/t1_tax_and_credits.total_payable"}
    assert divide["name"] == "core/divide"
    assert divide["unit"] == "core/percent"
    assert deductions["name"] == "core/sum"
    assert deductions["params"] == {"rounding": "ca-nl/exact_rounding"}
    assert deductions["consumes"]["parts"] == [
        "ca/total_payable",
        "ca/return_cpp_base_contributions",
        "ca/return_cpp_enhanced_contributions",
        "ca/return_ei_premium",
    ]
    assert divide["params"] == {"rounding": "ca/take_home_average_rate_rounding"}
    assert divide["consumes"] == {
        "dividend": "ca/return_total_deductions",
        "divisor": "ca/return_employment_income",
    }


def test_the_divisor_is_the_total_of_the_t1_line_10100_export() -> None:
    salary = _producing("ca/return_employment_income")

    assert salary["name"] == "core/record_total"
    assert salary["unit"] == "ca/cad"
    assert salary["consumes"] == {"records": "ca/t1_employment_income.employment_income_line_10100"}


def test_the_steps_carry_no_title_and_no_reference() -> None:
    for output in (
        "ca/total_payable",
        "ca/return_cpp_base_contributions",
        "ca/return_cpp_enhanced_contributions",
        "ca/return_ei_premium",
        "ca/return_total_deductions",
        "ca-nl/average_tax_rate",
    ):
        step = _producing(output)
        assert "title" not in step
        assert "reference" not in step
