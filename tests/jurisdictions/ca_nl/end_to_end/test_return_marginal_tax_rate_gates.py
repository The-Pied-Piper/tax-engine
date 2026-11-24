"""The gates of the Newfoundland and Labrador marginal rate open at their cent boundaries.

The provincial part of the marginal rate (`ca-nl/newfoundland_and_labrador_marginal_rate`) is
counted only while NL428 line 105 "Line 94 minus line 104 (if negative, enter "0")" is above zero,
and the low-income tax reduction slope (16%, NL428 line 103) only while NL428 line 101 and line
104 are both above zero. Each boundary below is found cent by cent from the engine, and each figure
is the hand-worked rate of `test_return_marginal_tax_rate_values.py`:

- 2025: line 105 is 0.00 at a salary of 24,140.18 (the low-income reduction absorbs the tax) and
  0.01 at 24,140.19; line 101 is 0.00 at 24,134.34 and 0.01 at 24,134.35 (the net income passes
  the low-income threshold of 23,928); line 104 is 0.01 at 30,428.50 and 0.00 at 30,428.51.
- 2026: line 105 is 0.00 at 25,100.03 and 0.01 at 25,100.04; line 104 is 0.01 at 30,763.60 and
  0.00 at 30,763.61.

Below the line 105 boundary the provincial part is 0; from it, while the reduction is phased out,
it is 8.7% x N - 8.7% x the credit-earning contributions + 16% x N, where N is the net income
rate; once the reduction is used up it is the bracket rate after the credits alone.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
NEWFOUNDLAND = JurisdictionCode("CA-NL")
PROVINCIAL = "ca-nl/newfoundland_and_labrador_marginal_rate"
TAX_GATE = "ca-nl/newfoundland_and_labrador_rate_gate"
INCOME_GATE = "ca-nl/income_over_low_income_threshold_gate"
REDUCTION_GATE = "ca-nl/low_income_tax_reduction_gate"


def _value(year: int, salary: str, name: str) -> Decimal:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEWFOUNDLAND, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-nl/return"]
    value = summary.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("year", "salary", "gate", "provincial"),
    [
        (2025, "24140.18", "0", "0"),
        (2025, "24140.19", "1", "0.2387967"),
        (2025, "30428.50", "1", "0.2387967"),
        (2025, "30428.51", "1", "0.0803967"),
        (2026, "25100.03", "0", "0"),
        (2026, "25100.04", "1", "0.2388054"),
        (2026, "30763.60", "1", "0.2388054"),
        (2026, "30763.61", "1", "0.0804054"),
    ],
)
def test_the_provincial_part_follows_line_105_and_the_reduction_phase_out(
    year: int, salary: str, gate: str, provincial: str
) -> None:
    assert _value(year, salary, TAX_GATE) == D(gate)
    assert _value(year, salary, PROVINCIAL) == D(provincial)


@pytest.mark.parametrize(
    ("salary", "income_gate", "reduction_gate"),
    [
        ("24134.34", "0", "1"),
        ("24134.35", "1", "1"),
        ("30428.50", "1", "1"),
        ("30428.51", "1", "0"),
    ],
)
def test_the_phase_out_gates_open_where_lines_101_and_104_turn_positive_or_zero(
    salary: str, income_gate: str, reduction_gate: str
) -> None:
    assert _value(2025, salary, INCOME_GATE) == D(income_gate)
    assert _value(2025, salary, REDUCTION_GATE) == D(reduction_gate)
