"""T2204 (2025) line 13, line 9 less line 12 (not below zero), as the Ontario take-home manifest
part wires it: the premiums deducted on line 4 and the line 10 amount, read directly, and the
difference.

T2204 line 13: "Line 9 minus line 12 (if negative, enter "0") = 13". For an Ontario resident, line 9
is a copy of line 4 (`ca/t2204_premiums_deducted`) and line 12 is a copy of line 10
(`ca/t2204_line_10`), so the part takes those two amounts as starting inputs and outputs
`ca/t2204_line_13`. The manifest
part is loaded from the package. The header and the form's export are made up here, because the
shared scaffold owns them. Both inputs are declared as required, as the line 7 test does for line 3.

The blank-line-4 take-home case (line 4 computed from the salary) is covered by the line 4 ticket's
part (#207), not here. These tests start from a line 4 amount given directly.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.refund import (
    T2204_LINE_10,
    T2204_LINE_13,
    T2204_PREMIUMS_DEDUCTED,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

PART = "t2204_line_13.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/t2204_premiums_deducted
        required: true
      - name: ca/t2204_line_10
        required: true
    outputs:
      - ca/t2204_premiums_deducted
      - ca/t2204_line_10
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_13
    """)


def t2204(take_home_service: TakeHomeService, line_4: str, line_10: str) -> Worksheet:
    """The T2204 worksheet for a line 4 and a line 10."""
    starting = [
        Artifact(T2204_PREMIUMS_DEDUCTED, D(line_4)),
        Artifact(T2204_LINE_10, D(line_10)),
    ]
    (sheet,) = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *starting
    )["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("line_4", "line_10", "expected"),
    [
        # The Return DD overpayment: 1,148.00 less 1,077.48 is 70.52.
        ("1148.00", "1077.48", "70.52"),
        # Line 4 equal to line 10: the difference is 0.
        ("1077.48", "1077.48", "0.00"),
        # Another equal pair, with a smaller amount.
        ("492.00", "492.00", "0.00"),
        # Line 4 below line 10: the difference is negative, so line 13 is "0".
        ("0.00", "1077.48", "0.00"),
        # Line 4 below line 10 again, with small amounts: negative, so line 13 is "0".
        ("10.00", "32.96", "0.00"),
        # Line 4 above line 10 with a large amount: 2,000.00 less 32.96 is 1,967.04.
        ("2000.00", "32.96", "1967.04"),
    ],
)
def test_line_13_is_line_9_less_line_12_and_not_below_zero(
    take_home_service: TakeHomeService, line_4: str, line_10: str, expected: str
) -> None:
    assert t2204(take_home_service, line_4, line_10).get(T2204_LINE_13).value == D(expected)
