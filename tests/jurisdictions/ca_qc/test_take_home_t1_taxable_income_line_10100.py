"""5005-R (2025) line 10100, employment income, as the Quebec manifest part wires it.

The step is one core/sum over its one input, rounded through `ca-qc/cent_rounding`, and it prints
the line once, with its printed title and reference. The header and the form's export are made up.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import EMPLOYMENT_INCOME_LINE_10100
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PARTS = ("t1_taxable_income_line_10100.yaml",)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/t1_taxable_income
      required: true
      exports:
        - ca-qc/employment_income_line_10100
    capabilities: []
    """)


def sheet_of(take_home_service: TakeHomeService, *artifacts: Artifact) -> Worksheet:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D("70000")), *artifacts
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet


def test_line_10100_is_the_salary(take_home_service: TakeHomeService) -> None:
    sheet = sheet_of(take_home_service)
    assert sheet.get(EMPLOYMENT_INCOME_LINE_10100).value == D("70000.00")


def test_line_10100_is_listed_once_with_its_title_and_reference(
    take_home_service: TakeHomeService,
) -> None:
    sheet = sheet_of(take_home_service)
    assert sheet.reference("employment_income_line_10100") == "10100"
    assert sheet.title("employment_income_line_10100") == "Employment income"
