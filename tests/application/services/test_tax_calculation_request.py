"""`TaxComputationService.calculate` runs a `TaxCalculationRequest`; `compute` is the same call."""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.calculation_request import TaxCalculationRequest
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

ON = JurisdictionCode("CA-ON")


def test_calculate_answers_the_same_as_compute() -> None:
    service = build_tax_computation()
    salary = Artifact(EMPLOYMENT_INCOME, Decimal(70000))
    by_request = service.calculate(TaxCalculationRequest(ON, 2025, (salary,)))
    by_arguments = service.compute(ON, 2025, salary)
    assert by_request.keys() == by_arguments.keys()
    for form, sheets in by_request.items():
        assert [s.trace for s in sheets] == [s.trace for s in by_arguments[form]]


def test_a_request_holds_its_artifacts_as_a_tuple() -> None:
    salary = Artifact(EMPLOYMENT_INCOME, Decimal(1))
    assert TaxCalculationRequest(ON, 2025, [salary]).artifacts == (salary,)  # type: ignore[arg-type]
    assert TaxCalculationRequest(ON, 2025).artifacts == ()
