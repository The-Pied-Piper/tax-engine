"""T1 (5006-R, 2025) line 15000, total income, as the Ontario take-home manifest part wires it.

Form text (5006-R page 3): "Line 21: Add lines 1 to 20." then "Line 28: Line 21 plus line 27" then
"Line 33 and line 15000: Line 28 plus line 32 Total income". Lines 21, 28 and 34 are copies of the
line before them, so the part is one sum with no step of their own.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Employment income (`ca/employment_income`, line 10100) and
other employment income (`ca/other_employment_income`, line 10400, owned by another ticket) are
plain starting inputs here. The UCCB (line 11700) and the RDSP income (line 12500) are the form's
own steps, composed beside it. The sum is core/sum over line 10100, line 10400, line 11700 and line
12500, in that order; each of the last two reads as 0 when the caller gives none.
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
    TOTAL_INCOME,
    UCCB_INCOME,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PARTS = (
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_15000.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
      - name: ca/other_employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca/t1_taxable_income
      required: true
      exports:
        - ca/total_income
    """)


def line_15000(
    take_home_service: TakeHomeService,
    salary: str,
    other: str,
    uccb: str | None = None,
    rdsp: str | None = None,
) -> Decimal:
    given = [
        Artifact(kind, D(amount))
        for kind, amount in ((UCCB_INCOME, uccb), (RDSP_INCOME, rdsp))
        if amount is not None
    ]
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(OTHER_EMPLOYMENT_INCOME, D(other)),
        *given,
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]
    return sheet.get(TOTAL_INCOME).value


@pytest.mark.parametrize(
    ("salary", "other", "expected"),
    [
        # Line 10400 adds to line 10100.
        ("70000", "1500", "71500.00"),
        ("0", "0", "0"),
    ],
)
def test_line_15000_is_line_10100_plus_line_10400(
    take_home_service: TakeHomeService, salary: str, other: str, expected: str
) -> None:
    assert line_15000(take_home_service, salary, other) == D(expected)


def test_line_15000_adds_the_uccb_and_the_rdsp_income(take_home_service: TakeHomeService) -> None:
    # Line 7 (line 11700) and line 12 (line 12500) of the 5006-R are among lines 1 to 20 that line
    # 21, and so line 15000, add.
    assert line_15000(take_home_service, "70000", "1500", "1200.50", "300.25") == D("73000.75")


def test_line_15000_reads_a_blank_rdsp_income_as_zero(take_home_service: TakeHomeService) -> None:
    assert line_15000(take_home_service, "70000", "0", uccb="1200.50") == D("71200.50")


def test_line_15000_reads_a_blank_uccb_as_zero(take_home_service: TakeHomeService) -> None:
    assert line_15000(take_home_service, "70000", "0", rdsp="300.25") == D("70300.25")
