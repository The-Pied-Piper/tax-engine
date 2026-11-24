"""The gates of the Newfoundland and Labrador marginal rate open at their cent boundaries, 2026.

The cases and the reasoning are those of `test_return_marginal_tax_rate_gates.py`, for the 2026
datasets: line 105 is 0.00 at a salary of 25,100.03 and 0.01 at 25,100.04, and line 104 is 0.01 at
30,763.60 and 0.00 at 30,763.61. The figures are the hand-worked rates of
`test_return_marginal_tax_rate_values.py`.
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
    ("salary", "gate", "provincial"),
    [
        ("25100.03", "0", "0"),
        ("25100.04", "1", "0.2388054"),
        ("30763.60", "1", "0.2388054"),
        ("30763.61", "1", "0.0804054"),
    ],
)
def test_the_provincial_part_follows_line_105_and_the_reduction_phase_out(
    salary: str, gate: str, provincial: str
) -> None:
    assert _value(2026, salary, TAX_GATE) == D(gate)
    assert _value(2026, salary, PROVINCIAL) == D(provincial)
