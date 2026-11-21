"""5005-R (2025) Step 2 as one chain: line 1 to line 33 (line 15000), total income.

Form text (CRA 5005-R page 3, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 21: Add lines 1 to 20.", "Line 28: Line 21 plus line 27" and "Line 33 and line 15000: Line 28
plus line 32". The chain is built from the real parts (lines 2, 21, 27, 28, 32 and 33); the header
and the form's exports are made up. The expected figures are computed here from the printed lines,
with lines 2, 27 and 32 read as 0 for a salary-only filer (hand figures, not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import T1_LINE_21, T1_LINE_28, TOTAL_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PARTS = (
    "t1_employment_income_line_10400_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_21.yaml",
    "t1_taxable_income_line_27_inputs.yaml",
    "t1_taxable_income_line_27.yaml",
    "t1_taxable_income_line_28.yaml",
    "t1_taxable_income_line_32_inputs.yaml",
    "t1_taxable_income_line_32.yaml",
    "t1_taxable_income_line_15000.yaml",
)

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
        - ca-qc/t1_line_21
        - ca-qc/t1_line_28
        - ca-qc/total_income
    capabilities: []
    """)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_the_chain_of_a_salary_only_filer_ends_in_the_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]

    line_21 = D(salary) + D(0)
    line_28 = line_21 + D(0)
    line_33 = line_28 + D(0)
    assert sheet.get(T1_LINE_21).value == line_21
    assert sheet.get(T1_LINE_28).value == line_28
    assert sheet.get(TOTAL_INCOME).value == line_33
    assert line_33 == D(f"{salary}.00")
