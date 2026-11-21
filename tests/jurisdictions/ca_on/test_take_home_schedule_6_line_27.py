"""Schedule 6 (5000-S6, 2025) line 27, the reduction amount, as the Ontario take-home manifest
parts wire it.

Form text (5000-S6 2025): "Line 26: Rate 15%"
and "Line 27: Line 25 multiplied by the percentage from line 26". Line 25 is the net income over
the base amount (`ca/cwb_net_income_over_base_amount`, from schedule_6_line_25.yaml), and line 26
is the printed 15%, which is the rate dataset `ca/cwb_reduction_rate`, so line 27 is one
core/apply_rate of line 25 by that rate, rounded half-up to the cent.

The test loads the same parts as test_take_home_schedule_6_line_25.py, which compose line 25 from
the real salary, Schedule 8 and T1 taxable-income parts, then the line 27 part under test.
The manifest parts are loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import CWB_REDUCTION_LINE_27
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
# The parts of test_take_home_schedule_6_line_25.py, then the line 27 part under test.
PARTS = (
    "salary.yaml",
    *form_part_names("schedule_8"),
    *form_part_names("t1_taxable_income", "t1_employment_income"),
    "schedule_6_line_7.yaml",
    "schedule_6_line_9.yaml",
    "schedule_6_line_10.yaml",
    "schedule_6_line_11.yaml",
    "schedule_6_line_12.yaml",
    "schedule_6_line_13.yaml",
    "schedule_6_line_14_inputs.yaml",
    "schedule_6_line_15.yaml",
    "schedule_6_line_24.yaml",
    "schedule_6_line_25.yaml",
    "schedule_6_line_27.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_6
      required: true
      exports:
        - ca/cwb_reduction_line_27
    """)


def line_27(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_REDUCTION_LINE_27).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 25 is $0.00 at $20,000 (line 15 is below the base amount), so 15% of it is $0.00.
        ("20000", "0.00"),
        # Line 25 is $2,880.00, and 15% of $2,880.00 is $432.00.
        ("30000", "432.00"),
    ],
)
def test_schedule_6_line_27_is_line_25_times_the_15_percent_rate(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_27(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 25 is $2,880.30 (a $30,000.30 salary). 15% of it is $432.045, a tie, which rounds
        # half-up to $432.05.
        ("30000.30", "432.05"),
        # Line 25 is $2,880.10 (a $30,000.10 salary). 15% of it is $432.015, a tie, which rounds
        # half-up to $432.02.
        ("30000.10", "432.02"),
    ],
)
def test_schedule_6_line_27_rounds_half_up_to_the_cent_from_the_rate_dataset(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_27(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2
