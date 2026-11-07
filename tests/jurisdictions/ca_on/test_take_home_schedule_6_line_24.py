"""Schedule 6 (2025) line 24, the Canada workers benefit base amount for a filer with no eligible
spouse and no eligible dependant, as the Ontario take-home manifest part wires it: the printed
amount, taken whole through core/credit_amount.

Line 24: If you had an eligible spouse or an eligible dependant, enter $30,639. If not, enter
$26,855.

The manifest part is loaded from the package. The header, the salary input and the form's export
are made up here, because the shared scaffold owns them. The figure is the printed $26,855.00
whatever the salary: no salary reaches this line, and the filer takes the "If not" branch.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog import CWB_REDUCTION_THRESHOLD
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

PART = "schedule_6_line_24.yaml"

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
        - ca/cwb_reduction_threshold
    """)


def line_24(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_REDUCTION_THRESHOLD).value


@pytest.mark.parametrize(
    "salary", ["2000", "6000", "20000", "30000", "35000", "40000", "70000", "0", "200000"]
)
def test_line_24_is_the_printed_26855_whatever_the_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    value = line_24(take_home_service, salary)
    assert value == D("26855.00")
    assert value.as_tuple().exponent == -2
