"""T1 (5006-R, 2025) line 15000, total income, as the Ontario take-home manifest part wires it.

Form text (5006-R page 3): "Line 21: Add lines 1 to 20." then "Line 28: Line 21 plus line 27" then
"Line 33 and line 15000: Line 28 plus line 32 Total income". Lines 21, 28 and 34 are copies of the
line before them, so the part is one sum with no step of their own.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Employment income (`ca/employment_income`, line 10100) and
other employment income (`ca/other_employment_income`, line 10400, owned by another ticket) are
plain starting inputs here. The sum is core/sum over line 10100 and then line 10400, in that order.
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
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "t1_taxable_income_line_15000.yaml"

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


def line_15000(take_home_service: TakeHomeService, salary: str, other: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(OTHER_EMPLOYMENT_INCOME, D(other)),
    )
    (sheet,) = worksheets["ca/t1_taxable_income"]
    return sheet.get(TOTAL_INCOME).value


@pytest.mark.parametrize(
    ("salary", "other", "expected"),
    [
        ("70000", "0", "70000.00"),
        ("90000", "0", "90000.00"),
        # Line 10400 adds to line 10100.
        ("70000", "1500", "71500.00"),
        ("0", "0", "0"),
    ],
)
def test_line_15000_is_line_10100_plus_line_10400(
    take_home_service: TakeHomeService, salary: str, other: str, expected: str
) -> None:
    assert line_15000(take_home_service, salary, other) == D(expected)
