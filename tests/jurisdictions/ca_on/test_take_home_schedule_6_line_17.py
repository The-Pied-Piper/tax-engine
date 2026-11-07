"""Schedule 6 (5000-S6, 2025) line 17, the Canada workers benefit base amount, as the Ontario
take-home manifest part wires it: the printed amount, taken whole through core/credit_amount.

Line 17: Base amount 3,000.00

The manifest part is loaded from the package. The header, the salary input and the form's export
are made up here, because the shared scaffold owns them. The figure is the printed $3,000.00
whatever the salary: no salary reaches this line.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import CWB_BASE_AMOUNT
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

PART = "schedule_6_line_17.yaml"

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
        - ca/cwb_base_amount
    """)


def line_17(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_BASE_AMOUNT).value


@pytest.mark.parametrize(
    "salary", ["2000", "6000", "20000", "30000", "35000", "40000", "70000", "0", "200000"]
)
def test_line_17_is_the_printed_3000_whatever_the_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert line_17(take_home_service, salary) == D("3000.00")
