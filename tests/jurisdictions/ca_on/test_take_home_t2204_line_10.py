"""T2204 (2025) line 10, the required EI premium, as the Ontario take-home manifest part wires it.

T2204 line 10: "Amount from line 1 × 1.64% = (maximum $1,077.48)". The part is a contribution tier
(`ca/ei_premium`: rate 1.64%, from $0 up to $65,700, maximum $1,077.48, rounded half-up to the cent)
read on line 1, so line 10 is the line 1 amount times 1.64%, capped at the printed maximum.

The manifest part is loaded from the package. The header, the line 1 input and the form's export are
made up here, because the shared scaffold owns them. Line 1 is produced by another part (#261), so
the test header declares `ca/t2204_line_1` as a required starting input, as the line 1 test does for
the $2,000 of line 7.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.refund import T2204_LINE_1, T2204_LINE_10
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

PART = "t2204_line_10.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/t2204_line_1
        required: true
    outputs:
      - ca/t2204_line_1
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_10
    """)


def t2204(take_home_service: TakeHomeService, line_1: str) -> Worksheet:
    """The T2204 worksheet for a line 1 amount, the only starting input."""
    starting = [Artifact(T2204_LINE_1, D(line_1))]
    (sheet,) = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *starting
    )["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("line_1", "expected"),
    [
        # Line 1 of 0 (the note on line 1 under $2,000) gives no premium.
        ("0", "0.00"),
        # Below the $65,700 limit the premium is 1.64% of line 1: 30,000 x 1.64% = 492.00.
        ("30000", "492.00"),
        # 2,010 x 1.64% = 32.964, which rounds half-up to 32.96.
        ("2010", "32.96"),
        # At and above the limit the premium is capped at the printed maximum of $1,077.48.
        ("70000", "1077.48"),
        ("100000", "1077.48"),
    ],
)
def test_line_10_is_1_64_percent_of_line_1_up_to_the_maximum(
    take_home_service: TakeHomeService, line_1: str, expected: str
) -> None:
    assert t2204(take_home_service, line_1).get(T2204_LINE_10).value == D(expected)


@pytest.mark.parametrize("line_1", ["65700.00", "65700.01", "65701"])
def test_line_10_is_not_raised_just_above_65700(
    take_home_service: TakeHomeService, line_1: str
) -> None:
    # The tier stops at $65,700, so a line 1 just above it still gives the maximum, not more.
    assert t2204(take_home_service, line_1).get(T2204_LINE_10).value == D("1077.48")
