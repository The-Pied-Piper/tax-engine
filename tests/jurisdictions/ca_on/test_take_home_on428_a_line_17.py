"""ON428-A (2025) line 17, as the Ontario take-home manifest part wires it: adjusted net income over
the individual threshold, not below zero.

Form text (ON428-A, CRA 5006-a-25e.txt in docs/cra-forms-2025): "Line 15: Amount from line 13
above / Line 16: Individual income threshold 32,500.00 / Line 17: Line 15 minus line 16 (if
negative, enter "0") =". Line 15 is a copy of line 13, so the step reads line 13
(`ca-on/lift_adjusted_net_income`) directly. Line 16 is
`ca-on/lift_individual_income_threshold`, a plain starting input here. Line 17 is one
core/subtract_not_below_zero: line 13 less line 16, floored at zero.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Both upstream kinds are plain starting inputs here.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_on.catalog import (
    LIFT_ADJUSTED_NET_INCOME,
    LIFT_INDIVIDUAL_INCOME_THRESHOLD,
    LIFT_SINGLE_EXCESS_OVER_THRESHOLD,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "on428_a_line_17.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca-on/lift_adjusted_net_income
        required: true
      - name: ca-on/lift_individual_income_threshold
        required: true
    outputs:
      - ca-on/lift_adjusted_net_income
    """)
FORM = dedent("""\
    form:
      name: ca-on/on428_a
      required: true
      exports:
        - ca-on/lift_single_excess_over_threshold
    """)


def line_17(take_home_service: TakeHomeService, line_13: str, line_16: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(LIFT_ADJUSTED_NET_INCOME, D(line_13)),
        Artifact(LIFT_INDIVIDUAL_INCOME_THRESHOLD, D(line_16)),
    )
    (sheet,) = worksheets["ca-on/on428_a"]
    return sheet.get(LIFT_SINGLE_EXCESS_OVER_THRESHOLD).value


@pytest.mark.parametrize(
    ("line_13", "line_16", "expected"),
    [
        # Return DD oracle: salary 70,000, line 13 69,335.00 over the 32,500.00 threshold.
        ("69335.00", "32500.00", "36835.00"),
        # Salary 40,000, inside the reduction range.
        ("39635.00", "32500.00", "7135.00"),
        # Salary 30,000, under the threshold: floored at zero.
        ("29735.00", "32500.00", "0"),
    ],
)
def test_line_17_is_line_13_less_line_16_not_below_zero(
    take_home_service: TakeHomeService, line_13: str, line_16: str, expected: str
) -> None:
    assert line_17(take_home_service, line_13, line_16) == D(expected)
