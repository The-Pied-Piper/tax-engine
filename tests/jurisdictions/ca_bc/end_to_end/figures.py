"""Figures of the real British Columbia worksheets for the end-to-end tests of the printed sums.

The bundled engine runs over the real manifest, with the salary and, where stated, optional inputs
typed in.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds
from tests import medical_support

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
SALARY = "70000"


def kind(name: str) -> AmountKind:
    found = artifact_kinds().kind(f"ca-bc/{name}")
    assert isinstance(found, AmountKind)
    return found


def sheet(form: str, year: int, medical_expenses: str | None = None, **given: str) -> Worksheet:
    """The `ca-bc/<form>` worksheet at the salary, with each `name=amount` typed in and, when
    given, the one T1 line 33099 amount (`ca/medical_expenses`)."""
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    if medical_expenses is not None:
        artifacts.append(medical_support.medical_expenses(medical_expenses))
    artifacts += [Artifact(kind(name), D(amount)) for name, amount in given.items()]
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, tuple(artifacts))
    )
    (found,) = worksheets[f"ca-bc/{form}"]
    return found


def figure(worksheet: Worksheet, name: str) -> Decimal:
    return worksheet.get(kind(name)).value
