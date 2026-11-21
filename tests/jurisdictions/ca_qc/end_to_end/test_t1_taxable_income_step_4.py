"""5005-R (2025) Step 4 as one chain: line 58 to line 70 (line 26000), taxable income.

Form text (CRA 5005-R page 5, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 58: Enter the amount from line 57 of the previous page.", "Line 69 and line 25700: Add lines
59 to 68." and "Line 70 and line 26000: Line 58 minus line 69 (if negative, enter "0") Taxable
income =".

The chain runs the real parts (Steps 2 and 3 included) and the real form declaration, with the real
Schedule 8 import and Schedule 6. The header is made up. The expected figures are computed here from
the printed lines (hand figures, not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.taxable_income import DEDUCTIONS_FROM_NET_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    NET_INCOME,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import real_import

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
    "t1_taxable_income_line_22215.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23500_inputs.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
    "t1_taxable_income_line_26000.yaml",
)
HEADER = (
    dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    imports:
    """)
    + real_import("ca/schedule_8")
    + "  - ca/schedule_6\n"
)
# The real form declaration: its exports and its `supplies`.
FORM = (QUEBEC_PARTS / "t1_taxable_income.yaml").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("salary", "line_57", "line_70"),
    [
        ("20000", "19835.00", "19835.00"),
        ("70000", "69335.00", "69335.00"),
        ("200000", "198926.00", "198926.00"),
    ],
)
def test_the_chain_of_a_salary_only_filer_ends_in_taxable_income(
    take_home_service: TakeHomeService, salary: str, line_57: str, line_70: str
) -> None:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]

    line_58 = sheet.get(NET_INCOME).value
    line_69 = sheet.get(DEDUCTIONS_FROM_NET_INCOME).value
    assert line_58 == D(line_57)
    assert line_69 == D("0")
    assert sheet.get(TAXABLE_INCOME).value == line_58 - line_69
    assert sheet.get(TAXABLE_INCOME).value == D(line_70)
