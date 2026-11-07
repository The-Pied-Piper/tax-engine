"""Schedule 6 (5000-S6, 2025) line 18, the working income over the base amount, as the Ontario
take-home manifest parts wire it.

Form text (5000-S6 2025, docs/cra-forms-2025/5000-s6-25e.txt, line 286): "Line 18: Line 16 minus
line 17 (if negative, enter "0")". Line 16 is a copy of line 6 (family working income, "Family
working income from line 6", no step) and line 17 is the base amount, 3,000.00. Line 18 is one
core/subtract_not_below_zero of the base amount (line 17) from family working income (line 6), so
the test loads the line 1, 5, 6, 17 and 18 parts: line 1 reads the salary, line 5 reads line 1,
line 6 reads line 5, line 17 prints $3,000.00 and line 18 reads lines 6 and 17.

The manifest parts are loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import (
    CWB_WORKING_INCOME_OVER_BASE_AMOUNT,
)
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
LINE_1_PART = "schedule_6_line_1.yaml"
LINE_5_PART = "schedule_6_line_5.yaml"
LINE_6_PART = "schedule_6_line_6.yaml"
LINE_17_PART = "schedule_6_line_17.yaml"
LINE_18_PART = "schedule_6_line_18.yaml"

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
        - ca/cwb_working_income_over_base_amount
    """)


def line_18(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(
        HEADER, FORM, LINE_1_PART, LINE_5_PART, LINE_6_PART, LINE_17_PART, LINE_18_PART
    ).compute(JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_WORKING_INCOME_OVER_BASE_AMOUNT).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 18 is line 6 (the salary) less line 17 ($3,000.00), floored at zero. At $2,000 the
        # difference is -$1,000.00, so line 18 prints "0".
        ("2000", "0.00"),
        ("6000", "3000.00"),
        ("20000", "17000.00"),
        ("30000", "27000.00"),
        ("35000", "32000.00"),
        ("40000", "37000.00"),
        ("70000", "67000.00"),
    ],
)
def test_schedule_6_line_18_is_line_6_less_the_base_amount_not_below_zero(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_18(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2
