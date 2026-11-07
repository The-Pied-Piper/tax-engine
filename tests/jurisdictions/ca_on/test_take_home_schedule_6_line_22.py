"""Schedule 6 (5000-S6, 2025) line 22, the basic Canada workers benefit before reduction, as the
Ontario take-home manifest parts wire it.

Form text (5000-S6 2025, docs/cra-forms-2025/5000-s6-25e.txt, line 296): "Line 22: Enter whichever
is less: amount from line 20 or line 21." Line 20 is the working income rate amount, 27% of line 18
(`ca/cwb_working_income_rate_line_20`, from schedule_6_line_20.yaml). Line 21 is the printed $1,633
maximum for a filer with no eligible spouse and no eligible dependant (`ca/cwb_maximum`, from
schedule_6_line_21.yaml). Line 22 is one core/lesser_of of the two, in form order, so a tie keeps
line 20.

The test loads the line 1, 5, 6, 17, 18, 20, 21 and 22 parts: line 1 reads the salary, line 5 reads
line 1, line 6 reads line 5, line 17 prints $3,000.00, line 18 reads lines 6 and 17, line 20 reads
line 18, line 21 prints $1,633.00, and line 22 reads lines 20 and 21.

The manifest parts are loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import CWB_BASIC_BENEFIT_LINE_22
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
LINE_1_PART = "schedule_6_line_1.yaml"
LINE_5_PART = "schedule_6_line_5.yaml"
LINE_6_PART = "schedule_6_line_6.yaml"
LINE_17_PART = "schedule_6_line_17.yaml"
LINE_18_PART = "schedule_6_line_18.yaml"
LINE_20_PART = "schedule_6_line_20.yaml"
LINE_21_PART = "schedule_6_line_21.yaml"
LINE_22_PART = "schedule_6_line_22.yaml"

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
        - ca/cwb_basic_benefit_line_22
    """)


def line_22(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(
        HEADER,
        FORM,
        LINE_1_PART,
        LINE_5_PART,
        LINE_6_PART,
        LINE_17_PART,
        LINE_18_PART,
        LINE_20_PART,
        LINE_21_PART,
        LINE_22_PART,
    ).compute(JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_BASIC_BENEFIT_LINE_22).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 18 is $0.00 at $2,000, so line 20 is $0.00, which is less than $1,633.00.
        ("2000", "0.00"),
        # Line 20 is $810.00, which is less than $1,633.00.
        ("6000", "810.00"),
        # Line 20 is $4,590.00 or more, so line 21 of $1,633.00 is the lesser.
        ("20000", "1633.00"),
        ("30000", "1633.00"),
        ("35000", "1633.00"),
        ("40000", "1633.00"),
        ("70000", "1633.00"),
    ],
)
def test_schedule_6_line_22_is_the_lesser_of_line_20_and_line_21(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_22(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2


def test_schedule_6_line_22_takes_line_21_when_line_20_rounds_to_it(
    take_home_service: TakeHomeService,
) -> None:
    # Line 18 is $6,048.15 (line 6 of $9,048.15 less line 17 of $3,000.00). Line 20 is 27% of it,
    # $1,633.0005, which rounds half-up to $1,633.00. That equals line 21, so the result is
    # $1,633.00 whichever of the two is listed first.
    value = line_22(take_home_service, "9048.15")
    assert value == D("1633.00")
    assert value.as_tuple().exponent == -2
