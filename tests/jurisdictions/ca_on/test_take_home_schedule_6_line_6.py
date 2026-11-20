"""Schedule 6 (5000-S6, 2025) line 6, family working income, as the Ontario take-home manifest parts
wire it.

Form text (5000-S6 2025): "Line 6: Add the amounts
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
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
# The real T1 taxable-income parts (with the Schedule 8 parts its line 23300 reads), composed beside
# the form under test, which imports T1 lines 10100 and 10400 from the T1.
T1_PARTS = (
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    "t1_taxable_income_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
)
LINE_1_PART = "schedule_6_line_1.yaml"
LINE_10400_PART = "t1_employment_income_line_10400_inputs.yaml"
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
        HEADER, FORM, *T1_PARTS, LINE_1_PART, LINE_5_PART, LINE_6_PART
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
        # Family working income (line 6) at salaries of $2,000 and $70,000. Column 2 is left out,
        # so each line 6 is line 5 column 1 alone, which is line 1 alone, which is the salary
        # (line 10100) alone.
        ("2000", "2000.00"),
        ("70000", "70000.00"),
    ],
)
def test_schedule_6_line_6_is_line_5_column_1_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_6(take_home_service, salary)
    assert value == D(expected)


def test_a_sub_cent_line_5_is_carried_unrounded_to_line_6(
    take_home_service: TakeHomeService,
) -> None:
    # 5000-S6 prints no rounding rule for line 6, so the sum is carried exactly, not rounded to the
    # cent.
    assert line_6(take_home_service, "70000.004") == D("70000.004")
