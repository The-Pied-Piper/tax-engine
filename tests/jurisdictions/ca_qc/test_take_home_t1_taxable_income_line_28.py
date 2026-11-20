"""5005-R (2025) line 28 as the Quebec manifest part wires it.

Form text (CRA 5005-R page 3, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 27: Add lines 22 to 26. Net self-employment income =" and "Line 28: Line 21 plus line 27 =".
Lines 22 to 26 are blank for a salary-only filer, so line 27 is one optional input read as 0 and has
no step; line 28 is one core/sum of line 21 and then line 27, rounded through `ca-qc/cent_rounding`.

The part is the real one. The header, the form's export and the line 21 and line 27 figures (plain
starting inputs here) are made up; the total income test runs the chain.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    NET_SELF_EMPLOYMENT_INCOME,
    T1_LINE_21,
    T1_LINE_28,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PART = "t1_taxable_income_line_28.yaml"

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
      - name: ca-qc/t1_line_21
        required: true
      - name: ca-qc/net_self_employment_income
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
        - ca-qc/t1_line_28
    capabilities: []
    """)


def line_28(take_home_service: TakeHomeService, line_21: str, line_27: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(line_21)),
        Artifact(T1_LINE_21, D(line_21)),
        Artifact(NET_SELF_EMPLOYMENT_INCOME, D(line_27)),
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(T1_LINE_28).value


def test_line_28_adds_line_27_to_line_21(take_home_service: TakeHomeService) -> None:
    assert line_28(take_home_service, "70000", "5000") == D("75000.00")


def test_a_self_employment_loss_reduces_line_28(take_home_service: TakeHomeService) -> None:
    # The form prints no floor on line 27 or line 28; a loss is shown in brackets.
    assert line_28(take_home_service, "70000", "-2000") == D("68000.00")
