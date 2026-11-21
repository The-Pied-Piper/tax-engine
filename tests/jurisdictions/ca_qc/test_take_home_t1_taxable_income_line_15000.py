"""5005-R (2025) line 33 and line 15000, total income, as the Quebec manifest part wires it.

Form text (CRA 5005-R page 3, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 32 and line 14700: Add lines 29 to 31 (see line 25000 in Step 4). =" and "Line 33 and line
15000: Line 28 plus line 32 =". Lines 29 to 31 are blank for a salary-only filer, so line 32 is one
optional input read as 0 and has no step; line 33 is one core/sum of line 28 and then line 32,
rounded through `ca-qc/cent_rounding`.

The part is the real one. The header, the form's export and the line 28 and line 32 figures (plain
starting inputs here) are made up; the total income test runs the chain.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import T1_LINE_28, T1_LINE_32, TOTAL_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PART = "t1_taxable_income_line_15000.yaml"

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/t1_taxable_income
      required: true
      exports:
        - ca-qc/total_income
    inputs:
      - name: ca/employment_income
        required: true
      - name: ca-qc/t1_line_28
        required: true
      - name: ca-qc/t1_line_32
        required: true
    capabilities: []
    """)


def line_33(take_home_service: TakeHomeService, line_28: str, line_32: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(line_28)),
        Artifact(T1_LINE_28, D(line_28)),
        Artifact(T1_LINE_32, D(line_32)),
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(TOTAL_INCOME).value


def test_line_33_adds_line_32_to_line_28(take_home_service: TakeHomeService) -> None:
    assert line_33(take_home_service, "70000", "3000") == D("73000.00")
