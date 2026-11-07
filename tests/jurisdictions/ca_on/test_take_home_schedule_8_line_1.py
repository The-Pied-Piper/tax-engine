"""Schedule 8 (5000-S8, 2025) Part 3 line 1, the total CPP pensionable earnings, as the Ontario
take-home manifest part wires it: the salary capped at the printed "(maximum $81,200 per slip)".

The manifest part is loaded from the package. The header, the salary input and the form's export
are made up here, because the shared scaffold owns them. The caller has no T4, so line 1 reads the
salary typed once (T1 line 10100) in place of box 26.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.rc381_cpp_qpp import (
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "schedule_8_line_1.yaml"

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
      name: ca/schedule_8
      required: true
      exports:
        - ca/t4_cpp_pensionable_earnings_outside_quebec
    """)


def line_1(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # A $70,000 salary is under the maximum, so line 1 is the salary.
        ("70000", "70000.00"),
        # $90,000 is above the $81,200 ceiling, so line 1 is the printed maximum.
        ("90000", "81200.00"),
        # At the maximum and a cent either side of it.
        ("81200", "81200.00"),
        ("81200.01", "81200.00"),
        ("81199.99", "81199.99"),
        ("0", "0.00"),
    ],
)
def test_line_1_is_the_salary_capped_at_the_per_slip_maximum(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    result = line_1(take_home_service, salary)

    assert result == D(expected)
    # Dollars and cents, from the cap dataset's rounding rule.
    assert result.as_tuple().exponent == -2
