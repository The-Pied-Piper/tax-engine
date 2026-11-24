"""The Ontario return summary's average tax rate steps and figures (2025 and 2026).

The return reads T1 line 43500 "Total payable" (`ca/total_payable`), the CPP (Schedule 8 line 25 and
line 28, which is line 12 plus line 22) and the EI premium (T2204 line 16) from their forms, adds
them with `core/sum` into `ca/return_total_deductions`, and `core/divide`s the total by the salary
(T1 line 10100, `ca/return_employment_income`), rounded once by the dataset
`ca/take_home_average_rate_rounding` (half-up to 0.0001). No form prints any of it, so the steps
carry no title and no reference. The figures run through the real engine; the $70,000 deductions are
the take-home answer's own (16,531.32 in 2025, 16,213.75 in 2026), and the rates are the quotients
checked by hand: 16,531.32 / 70,000 = 0.236160 -> 0.2362; 16,213.75 / 70,000 = 0.231625 -> 0.2316.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_on
from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import QuotientLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
RETURN_PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests" / "2025" / "return.yaml"
)
AVERAGE = "ca-on/average_tax_rate"
DEDUCTIONS = "ca/return_total_deductions"
OUTPUTS = [
    "ca/total_payable",
    "ca/return_employment_income",
    "ca/return_cpp_base_contributions",
    "ca/return_cpp_enhanced_contributions",
    "ca/return_ei_premium",
    DEDUCTIONS,
    AVERAGE,
]

# year, salary, total deductions, average rate.
CASES = [
    (2025, "0", "0.00", "0"),
    (2025, "100", "0.00", "0"),
    (2025, "70000", "16531.32", "0.2362"),
    (2026, "70000", "16213.75", "0.2316"),
]


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(RETURN_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def _producing(output: str) -> dict[str, Any]:
    (step,) = [step for step in _steps() if step["produces"]["output"] == output]
    return step


def _summary(year: int, salary: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"), year, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (summary,) = worksheets["ca-on/return"]
    return summary


def _value(summary: Worksheet, name: str) -> Decimal:
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


def test_the_steps_read_the_figures_add_them_and_divide_by_the_salary() -> None:
    present = [step["produces"]["output"] for step in _steps()]

    assert [output for output in present if output in OUTPUTS] == OUTPUTS


def test_the_figures_are_read_from_their_forms_exports() -> None:
    reads = {
        "ca/total_payable": "ca/t1_tax_and_credits.total_payable",
        "ca/return_employment_income": "ca/t1_employment_income.employment_income_line_10100",
        "ca/return_cpp_base_contributions": (
            "ca/schedule_8.schedule_8_cpp_base_contributions_on_return"
        ),
        "ca/return_cpp_enhanced_contributions": (
            "ca/schedule_8.schedule_8_cpp_enhanced_contributions_on_return"
        ),
        "ca/return_ei_premium": "ca/t2204.t2204_line_16",
    }
    for output, records in reads.items():
        step = _producing(output)
        assert step["name"] == "core/record_total"
        assert step["unit"] == "ca/cad"
        assert step["consumes"] == {"records": records}


def test_the_deductions_are_the_sum_and_the_rate_is_the_rounded_quotient() -> None:
    total = _producing(DEDUCTIONS)
    divide = _producing(AVERAGE)

    assert total["name"] == "core/sum"
    assert total["params"] == {"rounding": "ca-on/exact_rounding"}
    assert total["consumes"]["parts"] == [
        "ca/total_payable",
        "ca/return_cpp_base_contributions",
        "ca/return_cpp_enhanced_contributions",
        "ca/return_ei_premium",
    ]
    assert divide["name"] == "core/divide"
    assert divide["unit"] == "core/percent"
    assert divide["params"] == {"rounding": "ca/take_home_average_rate_rounding"}
    assert divide["consumes"] == {
        "dividend": DEDUCTIONS,
        "divisor": "ca/return_employment_income",
    }


def test_no_average_rate_step_has_a_title_or_a_reference() -> None:
    for output in OUTPUTS:
        step = _producing(output)
        assert "title" not in step
        assert "reference" not in step


@pytest.mark.parametrize(("year", "salary", "deductions", "rate"), CASES)
def test_the_average_rate_is_the_deductions_over_the_salary_half_up_to_four_places(
    year: int, salary: str, deductions: str, rate: str
) -> None:
    summary = _summary(year, salary)

    assert _value(summary, DEDUCTIONS) == D(deductions)
    assert _value(summary, AVERAGE) == D(rate)
    if D(salary) > 0:
        assert (D(deductions) / D(salary)).quantize(D("0.0001"), rounding="ROUND_HALF_UP") == D(
            rate
        )


def test_the_trace_records_one_quotient_line_of_the_deductions_over_the_salary() -> None:
    summary = _summary(2025, "70000")
    kinds = bundled_kinds()

    (line,) = [
        line
        for line in summary.trace
        if isinstance(line, QuotientLine) and line.output == kinds.kind(AVERAGE)
    ]
    assert line.dividend == kinds.kind(DEDUCTIONS)
    assert line.dividend_amount == D("16531.32")
    assert line.divisor_amount == D("70000")
    assert line.result == D("0.2362")
