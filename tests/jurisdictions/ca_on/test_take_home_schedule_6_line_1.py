"""Schedule 6 (5000-S6, 2025) line 1, employment income (column 1 "You"), as the Ontario take-home
manifest part wires it.

Form text (5000-S6 2025, docs/cra-forms-2025/5000-s6-25e.txt, lines 130-133): "Line 1: Employment
income and other employment income from line 10100 and line 10400 of the return", then "Column 1
You". Line 1 is a calculation: the sum of T1 line 10100 and T1 line 10400. Line 10400 (other
employment income) is out of scope for the take-home calculator, so the sum has one part. Line 1 is
therefore one core/sum over employment income (`ca/employment_income`, line 10100) alone.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import CWB_EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "schedule_6_line_1.yaml"

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
      name: ca/schedule_6
      required: true
      exports:
        - ca/cwb_employment_income
    """)


def line_1(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_EMPLOYMENT_INCOME).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Employment income (line 10100) at salaries of $2,000, $6,000, $20,000, $30,000, $35,000,
        # $40,000 and $70,000. Line 10400 is out of scope, so each line 1 is the salary alone.
        ("2000", "2000.00"),
        ("6000", "6000.00"),
        ("20000", "20000.00"),
        ("30000", "30000.00"),
        ("35000", "35000.00"),
        ("40000", "40000.00"),
        ("70000", "70000.00"),
    ],
)
def test_schedule_6_line_1_is_employment_income_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_1(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2
