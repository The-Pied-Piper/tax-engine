"""`TaxComputationService.compute` runs a `TaxCalculationRequest`."""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

ON = JurisdictionCode("CA-ON")
TAX_KIND = artifact_kinds().kind("ca/t2204_premiums_deducted")


def test_compute_runs_the_forms_of_the_request() -> None:
    sheets = build_tax_computation().compute(
        TaxCalculationRequest(ON, 2025, (Artifact(EMPLOYMENT_INCOME, Decimal(70000)),))
    )
    (sheet,) = sheets["ca/t2204"]
    assert sheet.get(TAX_KIND).value == Decimal("1077.48")


def test_a_request_holds_its_artifacts_as_a_tuple() -> None:
    salary = Artifact(EMPLOYMENT_INCOME, Decimal(1))
    assert TaxCalculationRequest(ON, 2025, [salary]).artifacts == (salary,)  # type: ignore[arg-type]
    assert TaxCalculationRequest(ON, 2025).artifacts == ()
