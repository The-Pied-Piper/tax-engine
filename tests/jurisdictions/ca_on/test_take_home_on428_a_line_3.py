"""ON428-A (2025) line 3, as the Ontario take-home manifest part wires it.

Form text (ON428-A, CRA 5006-a-25e.txt in docs/cra-forms-2025): "Line 1: Amount from line 10100
of your return / Line 2: Amount from line 10400 of your return / Line 3: Line 1 plus line 2 =".
Line 1 is the salary input (`ca/employment_income`). Line 2 (line 10400) is left out, because the
take-home filer has none, so line 3 is one core/sum over line 1 alone.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Employment income is a plain starting input here.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import LIFT_EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "on428_a/on428_a_line_3.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-on/on428_a
      required: true
      exports:
        - ca-on/lift_employment_income
    """)


def line_3(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    )
    (sheet,) = worksheets["ca-on/on428_a"]
    return sheet.get(LIFT_EMPLOYMENT_INCOME).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("70000", "70000.00"),
        ("10000", "10000.00"),
        ("0", "0"),
    ],
)
def test_line_3_is_line_1(take_home_service: TakeHomeService, salary: str, expected: str) -> None:
    assert line_3(take_home_service, salary) == D(expected)
