"""Schedule 6 (5000-S6, 2025) line 20, the working income rate amount, as the Ontario take-home
manifest parts wire it.

Form text (5000-S6 2025): "Line 19: Rate 27%"
and "Line 20: Line 18 multiplied by the percentage from line 19". Line 18 is the working income
over the base amount and line 19 is the printed 27%, which is the rate dataset `ca/cwb_rate`, so
line 20 is one core/apply_rate of line 18 by that rate, rounded half-up to the cent.

The test loads the line 1, 5, 6, 17, 18 and 20 parts: line 1 reads the salary, line 5 reads line 1,
line 6 reads line 5, line 17 prints $3,000.00, line 18 reads lines 6 and 17, and line 20 reads
line 18.

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
    CWB_WORKING_INCOME_RATE_LINE_20,
)
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
LINE_1_PART = "schedule_6_line_1.yaml"
LINE_10400_PART = "t1_taxable_income_line_10400_inputs.yaml"
LINE_5_PART = "schedule_6_line_5.yaml"
LINE_6_PART = "schedule_6_line_6.yaml"
LINE_17_PART = "schedule_6_line_17.yaml"
LINE_18_PART = "schedule_6_line_18.yaml"
LINE_20_PART = "schedule_6_line_20.yaml"

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
        - ca/cwb_working_income_rate_line_20
    """)


def line_20(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(
        HEADER,
        FORM,
        LINE_10400_PART,
        LINE_1_PART,
        LINE_5_PART,
        LINE_6_PART,
        LINE_17_PART,
        LINE_18_PART,
        LINE_20_PART,
    ).compute(JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_WORKING_INCOME_RATE_LINE_20).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 18 is $0.00 at $2,000 (floored at zero), so 27% of it is $0.00.
        ("2000", "0.00"),
        # Line 18 is $3,000.00, and 27% of $3,000.00 is $810.00.
        ("6000", "810.00"),
        ("20000", "4590.00"),
        ("30000", "7290.00"),
        ("35000", "8640.00"),
        ("40000", "9990.00"),
        ("70000", "18090.00"),
    ],
)
def test_schedule_6_line_20_is_line_18_times_the_27_percent_rate(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_20(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2


def test_schedule_6_line_20_rounds_half_up_to_the_cent_from_the_rate_dataset(
    take_home_service: TakeHomeService,
) -> None:
    # Line 18 is $3,001.01 (line 6 of $6,001.01 less line 17 of $3,000.00). 27% of it is
    # $810.2727, which rounds half-up to $810.27.
    value = line_20(take_home_service, "6001.01")
    assert value == D("810.27")
    assert value.as_tuple().exponent == -2
