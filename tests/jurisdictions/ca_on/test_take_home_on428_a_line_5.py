"""Schedule ON428-A lines 4 and 5, from the Ontario take-home manifest's own part file.

Line 4 "Applicable rate 5.05%" is a printed figure, held in the `ca-on/lift_rate` dataset, so it has
no step. Line 5 "Line 3 multiplied by the percentage from line 4 (maximum $875) =" prints two
operations, so it is two steps: the rate (`core/apply_rate`) and then the maximum
(`core/capped_amount`). Both results are read here: the figure before the maximum and line 5.
The part file is composed here under a test-local header and form declaration (the real ones
belong to the manifest's other parts), with line 3 given as the starting amount because its own
part is another ticket's.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_on.catalog import (
    LIFT_CREDIT_BEFORE_MAXIMUM,
    LIFT_EMPLOYMENT_INCOME,
    LIFT_MAXIMUM_CREDIT,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

ONTARIO = JurisdictionCode("CA-ON")
PART = "on428_a_line_5.yaml"
FORM_NAME = "ca-on/on428_a"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca-on/lift_employment_income
    required: true
outputs:
  - ca-on/lift_employment_income
"""
FORM = """\
form:
  name: ca-on/on428_a
  required: true
  exports:
    - ca-on/lift_credit_before_maximum
    - ca-on/lift_maximum_credit
"""


def lift_lines(take_home_service: TakeHomeService, line_3: str) -> tuple[Decimal, Decimal]:
    """The figure before the maximum (line 5's first operation) and line 5 itself."""
    service = take_home_service(HEADER, FORM, PART)
    (worksheet,) = service.compute(
        ONTARIO,
        2025,
        Artifact(LIFT_EMPLOYMENT_INCOME, Decimal(line_3)),
    )[FORM_NAME]
    return (
        worksheet.get(LIFT_CREDIT_BEFORE_MAXIMUM).value,
        worksheet.get(LIFT_MAXIMUM_CREDIT).value,
    )


@pytest.mark.parametrize(
    ("line_3", "expected"),
    [
        # The ticket's $70,000 salary: 5.05% is 3,535.00, which the $875 maximum caps.
        ("70000.00", "3535.00"),
        # Under the maximum, the figure before it is line 5.
        ("10000.00", "505.00"),
        # The first salary that reaches the maximum: 875.01 before it, 875.00 on line 5.
        ("17327.00", "875.01"),
        # One salary below that: 874.963 rounds half-up to 874.96, under the maximum.
        ("17326.00", "874.96"),
        ("0.00", "0.00"),
    ],
)
def test_line_5_is_line_3_times_the_rate_before_the_maximum(
    take_home_service: TakeHomeService, line_3: str, expected: str
) -> None:
    before_maximum, _ = lift_lines(take_home_service, line_3)
    assert before_maximum == Decimal(expected)


@pytest.mark.parametrize(
    ("line_3", "expected"),
    [
        ("70000.00", "875.00"),
        ("10000.00", "505.00"),
        ("17327.00", "875.00"),
        ("17326.00", "874.96"),
        ("0.00", "0.00"),
    ],
)
def test_line_5_is_capped_at_the_maximum_of_875(
    take_home_service: TakeHomeService, line_3: str, expected: str
) -> None:
    _, line_5 = lift_lines(take_home_service, line_3)
    assert line_5 == Decimal(expected)
