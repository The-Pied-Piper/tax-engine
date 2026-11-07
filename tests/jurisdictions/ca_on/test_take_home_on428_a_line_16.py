"""ON428-A (2025) line 16, the Ontario LIFT individual income threshold, as the Ontario take-home
manifest part wires it: the printed amount, taken whole through core/credit_amount.

Line 16: Individual income threshold 32,500.00

The manifest part is loaded from the package. The header, the salary input and the form's export
are made up here, because the shared scaffold owns them. The figure is the printed $32,500.00
whatever the salary: no salary reaches this line.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import LIFT_INDIVIDUAL_INCOME_THRESHOLD
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

PART = "on428_a_line_16.yaml"

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
        - ca-on/lift_individual_income_threshold
    """)


def line_16(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-on/on428_a"]
    return sheet.get(LIFT_INDIVIDUAL_INCOME_THRESHOLD).value


@pytest.mark.parametrize("salary", ["70000", "30000", "0", "32500", "200000"])
def test_line_16_is_the_printed_32500_whatever_the_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert line_16(take_home_service, salary) == D("32500.00")
