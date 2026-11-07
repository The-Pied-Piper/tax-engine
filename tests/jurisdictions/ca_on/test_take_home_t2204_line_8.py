"""T2204 (2025) line 8, line 6 less line 7, as the Ontario take-home manifest part wires it: the
difference, not below zero.

T2204 line 8: "Line 6 minus line 7 (if negative, enter 0)". The manifest part is loaded from the
package. The header and the form's export are made up here, because the shared scaffold owns
them. Lines 6 and 7 (`ca/t2204_line_6`, `ca/t2204_line_7`) are produced by other tickets, so the
test header declares them as required starting inputs, as the line 7 test does.

The difference is core/subtract_not_below_zero.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.refund import (
    T2204_LINE_6,
    T2204_LINE_7,
    T2204_LINE_8,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

PART = "t2204_line_8.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/t2204_line_6
        required: true
      - name: ca/t2204_line_7
        required: true
    outputs:
      - ca/t2204_line_6
      - ca/t2204_line_7
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_8
    """)


def t2204(take_home_service: TakeHomeService, line_6: str, line_7: str) -> Worksheet:
    """The T2204 worksheet for a line 6 and a line 7."""
    starting = [Artifact(T2204_LINE_6, D(line_6)), Artifact(T2204_LINE_7, D(line_7))]
    (sheet,) = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *starting
    )["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("line_6", "line_7", "expected"),
    [
        # Line 6 above line 7: the plain difference.
        ("32.96", "10.00", "22.96"),
        # Line 7 above line 6 (negative difference): line 8 is "0".
        ("1077.48", "1148.00", "0.00"),
        # Exactly equal: the difference is 0, not negative.
        ("1077.48", "1077.48", "0.00"),
        # Both zero.
        ("0", "0", "0.00"),
        # Line 6 zero, line 7 positive.
        ("0", "10.00", "0.00"),
    ],
)
def test_line_8_is_line_6_less_line_7_and_not_below_zero(
    take_home_service: TakeHomeService, line_6: str, line_7: str, expected: str
) -> None:
    assert t2204(take_home_service, line_6, line_7).get(T2204_LINE_8).value == D(expected)
