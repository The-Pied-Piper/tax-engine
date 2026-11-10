"""Schedule 6 (5000-S6, 2025) line 6, family working income, as the Ontario take-home manifest parts
wire it.

Form text (5000-S6 2025, docs/cra-forms-2025/5000-s6-25e.txt, line 156): "Line 6: Add the amounts
from line 5 in columns 1 and 2. Enter this amount on line 16. Family working income". Line 6 is a
calculation: the sum of line 5 over the columns. The take-home calculator is single with no eligible
spouse, so column 2 (`ca/cwb_spouse_working_income`) is left out and the sum has one part: line 5
column 1 (`ca/working_income`, from schedule_6_line_5.yaml). Line 6 is therefore one core/sum over
line 5 column 1 alone, so the test loads all three parts: line 1 reads the salary, line 5 reads
line 1's output, and line 6 reads line 5's output.

The manifest parts are loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import CWB_FAMILY_WORKING_INCOME
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
LINE_1_PART = "schedule_6_line_1.yaml"
LINE_10400_PART = "t1_taxable_income_line_10400_inputs.yaml"
LINE_5_PART = "schedule_6_line_5.yaml"
LINE_6_PART = "schedule_6_line_6.yaml"

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
        - ca/cwb_family_working_income
    """)


def line_6(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(
        HEADER, FORM, LINE_10400_PART, LINE_1_PART, LINE_5_PART, LINE_6_PART
    ).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_FAMILY_WORKING_INCOME).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Family working income (line 6) at salaries of $2,000, $6,000, $20,000, $30,000, $35,000,
        # $40,000 and $70,000. Column 2 is left out, so each line 6 is line 5 column 1 alone, which
        # is line 1 alone, which is the salary (line 10100) alone.
        ("2000", "2000.00"),
        ("6000", "6000.00"),
        ("20000", "20000.00"),
        ("30000", "30000.00"),
        ("35000", "35000.00"),
        ("40000", "40000.00"),
        ("70000", "70000.00"),
    ],
)
def test_schedule_6_line_6_is_line_5_column_1_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_6(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2
