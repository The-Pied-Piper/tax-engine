"""5005-R (2025) line 21 as the Quebec manifest part wires it.

Form text (CRA 5005-R page 3, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 21: Add lines 1 to 20." Line 1 is the salary (line 10100) and line 2 is the optional "Other
employment income" (line 10400), read as 0 when the caller leaves it out; lines 3 to 20 are blank
for a salary-only filer and not built, except line 7 (line 11700, the UCCB) and line 12 (line 12500,
the RDSP income), the form's own steps, read as 0 when the caller gives none. The step is core/sum
over line 1, line 2, line 7 and line 12, in that order, rounded through `ca-qc/cent_rounding`.

The part is loaded from the package, with the real line 2 input part. The header and the form's
export are made up here.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import (
    EMPLOYMENT_INCOME,
    OTHER_EMPLOYMENT_INCOME,
    RDSP_INCOME,
    UCCB_INCOME,
)
from tax_engine.jurisdictions.ca_qc.catalog import T1_LINE_21
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PART = "t1_taxable_income_line_21.yaml"
INPUTS = "t1_employment_income_line_10400_inputs.yaml"
LINE_10100_PART = "t1_employment_income_line_10100.yaml"
LINE_10400_PART = "t1_employment_income_line_10400.yaml"
UCCB_AND_RDSP_PARTS = (
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
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
    capabilities: []
    """)


def line_21(
    take_home_service: TakeHomeService,
    salary: str,
    *other: str,
    uccb: str | None = None,
    rdsp: str | None = None,
) -> Decimal:
    given = [Artifact(OTHER_EMPLOYMENT_INCOME, D(amount)) for amount in other]
    given += [
        Artifact(kind, D(amount))
        for kind, amount in ((UCCB_INCOME, uccb), (RDSP_INCOME, rdsp))
        if amount is not None
    ]
    worksheets = take_home_service(
        HEADER,
        FORM,
        "t1_employment_income.yaml",
        INPUTS,
        LINE_10100_PART,
        LINE_10400_PART,
        *UCCB_AND_RDSP_PARTS,
        PART,
    ).compute(JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary)), *given)
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(T1_LINE_21).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_21_of_a_salary_only_filer_is_the_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert line_21(take_home_service, salary) == D(salary)


def test_line_21_adds_line_2_to_line_1(take_home_service: TakeHomeService) -> None:
    assert line_21(take_home_service, "70000", "1500") == D("71500.00")


def test_line_21_adds_the_uccb_and_the_rdsp_income(take_home_service: TakeHomeService) -> None:
    # Line 7 (line 11700) and line 12 (line 12500) are among lines 1 to 20.
    assert line_21(take_home_service, "70000", "1500", uccb="1200.50", rdsp="300.25") == D(
        "73000.75"
    )
