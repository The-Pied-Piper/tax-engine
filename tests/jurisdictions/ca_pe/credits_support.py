"""Test support for the PE428 credit lines (Form PE428, CRA 5002-C, lines 9 to 26).

Every line test builds the engine over the real part of its line under a test-local header and a
test-local form declaration that exports the line it reads, because the shared scaffold owns the
real ones. The salary is typed in; the federal parts the CPP and EI lines read are the real ones.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds

D = Decimal
FORM_NAME = "ca-pe/pe428_credits"
HEADER = dedent("""\
    jurisdiction: CA-PE
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The T1 employment income form owns the salary input; Schedule 8, T2204 and the T1 lines copied by
# provinces give the CPP and EI amounts and the self-employed amounts the credits copy.
SALARY_PARTS = form_part_names("t1_employment_income")
FEDERAL_PARTS = (
    *SALARY_PARTS,
    *form_part_names("schedule_8", "t2204", "t1_lines_copied_by_provinces"),
)


def form(*exports: str) -> str:
    """The test-local declaration of the credits form, exporting the lines a test reads."""
    listed = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: {FORM_NAME}\n  required: true\n  exports:\n{listed}capabilities: []\n"


def compute(
    service: TaxComputationService, salary: str, given: dict[str, str] | None = None
) -> Any:
    """The credits form's worksheet for a salary and any optional inputs a test types in."""
    kinds = prince_edward_island_kinds()
    inputs: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    for identifier, amount in (given or {}).items():
        inputs.append(Artifact(kinds.kind(identifier), D(amount)))
    worksheets = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-PE"), 2025, tuple(inputs))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def value(sheet: Any, identifier: str) -> Decimal:
    """The amount of the line `identifier` on the worksheet."""
    return D(sheet.get(prince_edward_island_kinds().kind(identifier)).value)
