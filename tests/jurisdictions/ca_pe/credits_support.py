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
FORM_NAME = "ca-pe/pe428"
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
    """The test-local declaration of the PE428 form, exporting the lines a test reads."""
    listed = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: {FORM_NAME}\n  required: true\n  exports:\n{listed}capabilities: []\n"


def compute(
    service: TaxComputationService, salary: str, given: dict[str, str] | None = None
) -> Any:
    """The PE428 form's worksheet for a salary and any optional inputs a test types in."""
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


# Lines 9 to 25 of the form, composed with the federal parts the CPP and EI lines read.
BASE_PARTS = (
    *FEDERAL_PARTS,
    "pe428_line_9.yaml",
    "pe428_line_10_input.yaml",
    "pe428_line_10.yaml",
    "pe428_line_13_input.yaml",
    "pe428_line_13.yaml",
    "pe428_line_16_input.yaml",
    "pe428_line_16.yaml",
    "pe428_line_17_input.yaml",
    "pe428_line_18_input.yaml",
    "pe428_line_19.yaml",
    "pe428_line_20.yaml",
    "pe428_line_21.yaml",
    "pe428_line_22.yaml",
    "pe428_line_23.yaml",
    "pe428_line_24.yaml",
    "pe428_line_25.yaml",
)

CHAIN_30 = (
    *BASE_PARTS,
    "pe428_line_27_input.yaml",
    "pe428_line_27.yaml",
    "pe428_line_28_input.yaml",
    "pe428_line_29_input.yaml",
    "pe428_line_30.yaml",
)

CHAIN_34 = (
    *CHAIN_30,
    "pe428_line_31_input.yaml",
    "pe428_line_32_input.yaml",
    "pe428_line_33_input.yaml",
    "pe428_line_33.yaml",
    "pe428_line_34.yaml",
)

CHAIN_39 = (
    *CHAIN_34,
    "pe428_line_35.yaml",
    "pe428_line_36_input.yaml",
    "pe428_line_37_input.yaml",
    "pe428_line_38_input.yaml",
    "pe428_line_39.yaml",
)

CHAIN_48 = (*CHAIN_39, "pe428_line_47_input.yaml", "pe428_line_48.yaml")

CHAIN_50 = (*CHAIN_48, "pe428_line_50.yaml")

DONATION_PARTS = form_part_names("schedule_9")

CHAIN_53 = (
    *CHAIN_50,
    *DONATION_PARTS,
    "pe428_line_51.yaml",
    "pe428_line_52.yaml",
    "pe428_line_53.yaml",
)

CHAIN_54 = (*CHAIN_53, "pe428_line_54.yaml")

PART_A = tuple(f"pe428_line_{number}.yaml" for number in (1, 3, 4, 5, 6, 7, 8))
ALL_PARTS = (*CHAIN_54, *form_part_names("t1_taxable_income"), *PART_A)

CHAIN_57 = (*ALL_PARTS, "pe428_line_56_input.yaml", "pe428_line_57.yaml")

CHAIN_59 = (*CHAIN_57, "pe428_line_59.yaml")

CHAIN_62 = (*CHAIN_59, "pe428_line_60_input.yaml", "pe428_line_61_input.yaml", "pe428_line_62.yaml")
