"""5005-R (2025) Step 3 as one chain: line 34 to line 57 (line 23600), net income.

Form text (CRA 5005-R page 4, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 48 and line 22215: Deduction for CPP or QPP enhanced contributions on employment income",
"Line 54 and line 23300: Add lines 35 to 53.", "Line 55 and line 23400: Line 34 minus line 54",
"Line 56 and line 23500: If not, enter "0" on line 23500." and "Line 57 and line 23600: Line 55
minus line 56 (if negative, enter "0")".

The chain runs the real parts and the real form declaration, with the real Schedule 8 import (and
its Quebec dataset swap) and the real Schedule 6, whose line 7 reads the form's signed net income
through the neutral name the declaration supplies. The header is made up. The expected figures are
computed here from the printed lines (hand figures, not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import CWB_NET_INCOME_LINE_7
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    NET_INCOME,
    NET_INCOME_SIGNED,
    T1_LINE_48,
    T1_LINE_54,
    T1_LINE_55,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import real_import

D = Decimal
PARTS = (
    "t1_employment_income_line_10400_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100_inputs.yaml",
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
    # Step 4 parts: the form declaration now exports taxable income, which needs its producer.
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
    ("salary", "line_48", "line_57"),
    [
        ("20000", "165.00", "19835.00"),
        ("70000", "665.00", "69335.00"),
        ("200000", "1074.00", "198926.00"),
    ],
)
def test_the_chain_of_a_salary_only_filer_ends_in_net_income(
    take_home_service: TakeHomeService, salary: str, line_48: str, line_57: str
) -> None:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]

    line_33 = D(salary)
    line_54 = D(line_48)
    line_55 = line_33 - line_54
    line_57_figure = line_55 - D(0)
    assert sheet.get(TOTAL_INCOME).value == line_33
    assert sheet.get(T1_LINE_48).value == D(line_48)
    assert sheet.get(T1_LINE_54).value == line_54
    assert sheet.get(T1_LINE_55).value == line_55
    assert sheet.get(NET_INCOME).value == line_57_figure
    assert sheet.get(NET_INCOME_SIGNED).value == line_57_figure
    assert line_57_figure == D(line_57)


def test_schedule_6_line_7_reads_the_signed_net_income(take_home_service: TakeHomeService) -> None:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )
    (schedule_6,) = worksheets["ca/schedule_6"]
    assert schedule_6.get(CWB_NET_INCOME_LINE_7).value == D("69335.00")
