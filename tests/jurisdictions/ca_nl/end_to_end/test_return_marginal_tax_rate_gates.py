"""The gated Newfoundland and Labrador marginal tax rate, 2025, through the real engine.

The salary-only case, 2025. Newfoundland and Labrador's low-income tax reduction absorbs the
provincial tax at low salaries, so the provincial part opens late and is steepest while the
reduction is phased out.

The provincial part is counted only while NL428 line 105 "Line 94 minus line 104 (if negative,
enter "0")" is above zero, and the low-income tax reduction slope (16%, NL428 line 102) only while
NL428 line 101 and line 104 are both above zero. Each boundary below is found cent by cent from the
engine, and each rate is the hand-worked figure of `test_return_marginal_tax_rate_values.py`; each
other salary pins the structure: the gates are 0 or 1 and open with the amounts they read, the
provincial part is its gate times its rate, and the total is the exact sum of the three parts.

- line 105 is 0.00 at a salary of 24,140.18 and 0.01 at 24,140.19 (the reduction absorbs the tax);
- line 101 is 0.00 at 24,134.34 and 0.01 at 24,134.35 (the net income passes the low-income
  threshold of 23,928); line 104 is 0.01 at 30,428.50 and 0.00 at 30,428.51 (the reduction is used
  up); in between the provincial part is 8.7% x 0.99 - 8.7% x 0.0659 + 16% x 0.99 = 0.2387967, and
  after it 0.0803967.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
NEWFOUNDLAND = JurisdictionCode("CA-NL")
RETURN = "ca-nl/return"

LINE_105 = "ca-nl/newfoundland_and_labrador_tax_return"
TAX_GATE = "ca-nl/newfoundland_and_labrador_rate_gate"
REDUCTION_RATE = "ca-nl/marginal_newfoundland_and_labrador_rate_with_reduction"
INCOME_GATE = "ca-nl/income_over_low_income_threshold_gate"
REDUCTION_GATE = "ca-nl/low_income_tax_reduction_gate"
PHASE_OUT_GATE = "ca-nl/low_income_reduction_phase_out_gate"
FEDERAL = "ca-nl/marginal_federal_rate"
PROVINCIAL = "ca-nl/newfoundland_and_labrador_marginal_rate"
CONTRIBUTION = "ca-nl/marginal_contribution_rate"
MARGINAL = "ca-nl/marginal_tax_rate"

SALARIES = [
    "0",
    "100",
    "2000",
    "11750",
    "24134.35",
    "24140.19",
    "28000",
    "30428.51",
    "70000",
    "250000",
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Newfoundland and Labrador manifest, as the calculator loads it,
    # salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEWFOUNDLAND, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("salary", SALARIES)
def test_2025_the_total_is_the_exact_sum_of_the_gated_parts(salary: str) -> None:
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == (
        _value(summary, FEDERAL) + _value(summary, PROVINCIAL) + _value(summary, CONTRIBUTION)
    )
    assert _value(summary, PROVINCIAL) == _value(summary, TAX_GATE) * _value(
        summary, REDUCTION_RATE
    )


@pytest.mark.parametrize("salary", SALARIES)
def test_2025_each_gate_opens_with_the_amount_it_reads(salary: str) -> None:
    summary = _summary(salary)

    for gate, amount in (
        (TAX_GATE, LINE_105),
        (INCOME_GATE, "ca-nl/income_over_low_income_threshold_return"),
        (REDUCTION_GATE, "ca-nl/low_income_tax_reduction_return"),
    ):
        assert _value(summary, gate) == (D("1") if _value(summary, amount) > 0 else D("0"))
    assert _value(summary, PHASE_OUT_GATE) == (
        _value(summary, INCOME_GATE) * _value(summary, REDUCTION_GATE)
    )


@pytest.mark.parametrize("salary", ["0", "100", "2000"])
def test_2025_the_marginal_tax_rate_is_0_where_nothing_is_paid(salary: str) -> None:
    # No income tax, and no CPP or EI yet (the EI band of T2204 line 16 starts above 2,000).
    summary = _summary(salary)

    assert _value(summary, MARGINAL) == D("0")
    assert _value(summary, PROVINCIAL) == D("0")


@pytest.mark.parametrize(
    ("salary", "gate", "provincial"),
    [
        ("24140.18", "0", "0"),
        ("24140.19", "1", "0.2387967"),
        ("30428.50", "1", "0.2387967"),
        ("30428.51", "1", "0.0803967"),
    ],
)
def test_2025_the_provincial_part_follows_line_105_and_the_reduction_phase_out(
    salary: str, gate: str, provincial: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TAX_GATE) == D(gate)
    assert _value(summary, PROVINCIAL) == D(provincial)


@pytest.mark.parametrize(
    ("salary", "income_gate", "reduction_gate"),
    [
        ("24134.34", "0", "1"),
        ("24134.35", "1", "1"),
        ("30428.50", "1", "1"),
        ("30428.51", "1", "0"),
    ],
)
def test_2025_the_phase_out_gates_open_where_lines_101_and_104_turn_positive_or_zero(
    salary: str, income_gate: str, reduction_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, INCOME_GATE) == D(income_gate)
    assert _value(summary, REDUCTION_GATE) == D(reduction_gate)
