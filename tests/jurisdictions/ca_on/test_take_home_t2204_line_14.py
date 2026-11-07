"""T2204 (2025) line 14, the greater of line 8 and line 13, as the Ontario take-home manifest part
wires it: whichever is more, not the sum and not the difference.

T2204 line 14: "Enter whichever is more: amount from line 8 or line 13." The manifest part is loaded
from the package. The header and the form's export are made up here, because the shared scaffold
owns them. Lines 8 and 13 (`ca/t2204_line_8`, `ca/t2204_line_13`) are produced by other tickets, so
the test header declares them as required starting inputs, as the line 8 test does.

The greater of is core/greater_of, over line 8 and then line 13, in the form's order.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.refund import (
    T2204_LINE_8,
    T2204_LINE_13,
    T2204_LINE_14,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

PART = "t2204_line_14.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/t2204_line_8
        required: true
      - name: ca/t2204_line_13
        required: true
    outputs:
      - ca/t2204_line_8
      - ca/t2204_line_13
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_14
    """)


def t2204(take_home_service: TakeHomeService, line_8: str, line_13: str) -> Worksheet:
    """The T2204 worksheet for a line 8 and a line 13."""
    starting = [Artifact(T2204_LINE_8, D(line_8)), Artifact(T2204_LINE_13, D(line_13))]
    (sheet,) = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *starting
    )["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("line_8", "line_13", "expected"),
    [
        # Salary 2,010 with line 4 blank: line 8 is 22.96 and line 13 is 0.
        ("22.96", "0", "22.96"),
        # Salary 1,500 and salary 70,000, both with line 4 blank: nothing to refund.
        ("0", "0", "0.00"),
        # Return DD oracle: salary 70,000 with line 4 given 1,148.00, overpayment 70.52.
        ("0", "70.52", "70.52"),
        # Line 13 above line 8.
        ("10.00", "22.96", "22.96"),
        # Line 8 above line 13.
        ("22.96", "10.00", "22.96"),
        # Exactly equal: either one is the answer.
        ("22.96", "22.96", "22.96"),
    ],
)
def test_line_14_is_the_greater_of_line_8_and_line_13(
    take_home_service: TakeHomeService, line_8: str, line_13: str, expected: str
) -> None:
    assert t2204(take_home_service, line_8, line_13).get(T2204_LINE_14).value == D(expected)
