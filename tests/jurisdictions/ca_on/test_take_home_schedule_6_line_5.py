"""Schedule 6 (5000-S6, 2025) line 5, working income (column 1 "You"), as the Ontario take-home
manifest parts wire it.

Form text (5000-S6 2025, docs/cra-forms-2025/5000-s6-25e.txt, lines 152-154): "Line 5: Add lines 1
to 4. Enter the result, even if it is "0". Working income". Line 5 is a calculation: the sum of
lines 1 to 4. Lines 2 (scholarships), 3 (self-employment) and 4 (tax-exempt working income on a
reserve, volunteer allowance) are out of scope for the take-home calculator, so the sum has one
part: line 1. Line 5 is therefore one core/sum over line 1 alone (`ca/cwb_employment_income`, from
schedule_6_line_1.yaml), so the test loads both parts: line 1 reads the salary and line 5 reads
line 1's output.

The manifest parts are loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import WORKING_INCOME
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
LINE_1_PART = "schedule_6_line_1.yaml"
LINE_5_PART = "schedule_6_line_5.yaml"

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
        - ca/working_income
    """)


def line_5(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, LINE_1_PART, LINE_5_PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(WORKING_INCOME).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Working income (line 5) at salaries of $2,000, $6,000, $20,000, $30,000, $35,000, $40,000
        # and $70,000. Lines 2 to 4 are out of scope, so each line 5 is line 1 alone, which is the
        # salary (line 10100) alone.
        ("2000", "2000.00"),
        ("6000", "6000.00"),
        ("20000", "20000.00"),
        ("30000", "30000.00"),
        ("35000", "35000.00"),
        ("40000", "40000.00"),
        ("70000", "70000.00"),
    ],
)
def test_schedule_6_line_5_is_line_1_to_4_sum_with_only_line_1(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_5(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2
