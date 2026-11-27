"""Shared set-up of the 5005-R Step 5 Part A tests (lines 71 to 77): the real Steps 3 and 4 chain,
the real form declarations and the real Schedule 8 and Schedule 6 imports, so taxable income is
read from the salary through the real lines. The header is made up."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.basic_personal_amount_support import (
    STEP_3_PARTS,
    STEP_4_PARTS,
    T1_FORM,
    TAX_FORM,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import T1_BIRTH_YEAR_PARTS, real_import

D = Decimal
HEADER = (
    dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    imports:
    """)
    + real_import("ca/schedule_8")
    + "  - ca/schedule_6\n"
)


def form(export: str) -> str:
    """The tax and credits declaration, test-local: its one export is the line under test. (The real
    declaration exports the basic personal amount, whose lines are not composed here.)"""
    return dedent(f"""\
        form:
          name: {TAX_FORM}
          required: true
          exports:
            - {export}
        capabilities: []
        """)


# Part A of Step 5 as printed: lines 71 to 77. Line 72 and line 74 and line 76 are the columns.
COLUMNS = (
    (D("0.00"), D("0.145"), D("0.00")),
    (D("57375.00"), D("0.205"), D("8319.38")),
    (D("114750.00"), D("0.26"), D("20081.25")),
    (D("177882.00"), D("0.29"), D("36495.57")),
    (D("253414.00"), D("0.33"), D("58399.85")),
)


def part(line: int) -> str:
    return f"t1_tax_and_credits_line_{line}.yaml"


def sheets(
    take_home_service: TakeHomeService, salary: str, export: str, *lines: int
) -> tuple[Worksheet, Worksheet]:
    """The T1 taxable-income sheet and the tax and credits sheet for `salary`, with the Part A
    parts of the named `lines` composed and `export` (a kind identifier) as the form's export."""
    parts = (
        "t1_taxable_income.yaml",
        *STEP_3_PARTS,
        *STEP_4_PARTS,
        *T1_BIRTH_YEAR_PARTS,
        *(part(line) for line in lines),
    )
    worksheets = take_home_service(HEADER, form(export), *parts).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (t1,) = worksheets[T1_FORM]
    (sheet,) = worksheets[TAX_FORM]
    return t1, sheet
