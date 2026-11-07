"""T2204 (2025) line 6, the line 4 plus line 5, as the Ontario take-home manifest part wires it.

T2204 line 6: "Line 4 plus line 5 = 6". Line 4 (`ca/t2204_premiums_deducted`) is the premiums
deducted, produced by another ticket (#207), so the test header declares it as a required starting
input. Line 5 (`ca/t2204_line_5`, "Residents of other than Quebec (amount from line 9 of Schedule
13)") is the self-employed EI premium a salary-only caller never has: an optional input, read as
blank when left out, and a blank line 5 is read as 0 by the part, which the trace records as a
fallback. A blank line 4 is still refused.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import BlankFallbackLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.refund import (
    T2204_LINE_5,
    T2204_LINE_6,
    T2204_PREMIUMS_DEDUCTED,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

PART = "t2204_line_6.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/t2204_premiums_deducted
        required: true
      - name: ca/t2204_line_5
        required: false
        default: null
        basis: "Residents of other than Quebec (amount from line 9 of Schedule 13)"
    outputs:
      - ca/t2204_premiums_deducted
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_6
    """)


def t2204(take_home_service: TakeHomeService, starting: list[Artifact[Decimal]]) -> Worksheet:
    """The T2204 worksheet for the starting artifacts given; line 5 is left out unless given."""
    (sheet,) = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *starting
    )["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("line_4", "expected"),
    [
        ("1077.48", "1077.48"),
        ("1148.00", "1148.00"),
        ("32.96", "32.96"),
        ("0", "0.00"),
    ],
)
def test_line_6_is_line_4_when_line_5_is_left_blank(
    take_home_service: TakeHomeService, line_4: str, expected: str
) -> None:
    sheet = t2204(take_home_service, [Artifact(T2204_PREMIUMS_DEDUCTED, D(line_4))])

    assert sheet.get(T2204_LINE_6).value == D(expected)


@pytest.mark.parametrize(
    ("line_4", "line_5", "expected"),
    [
        ("32.96", "10.00", "42.96"),
        ("1077.48", "10.00", "1087.48"),
    ],
)
def test_line_6_adds_line_5_to_line_4_when_line_5_is_given(
    take_home_service: TakeHomeService, line_4: str, line_5: str, expected: str
) -> None:
    sheet = t2204(
        take_home_service,
        [
            Artifact(T2204_PREMIUMS_DEDUCTED, D(line_4)),
            Artifact(T2204_LINE_5, D(line_5)),
        ],
    )

    assert sheet.get(T2204_LINE_6).value == D(expected)


def test_a_blank_line_5_is_traced_as_a_fallback_of_0(take_home_service: TakeHomeService) -> None:
    sheet = t2204(take_home_service, [Artifact(T2204_PREMIUMS_DEDUCTED, D("32.96"))])

    assert BlankFallbackLine(T2204_LINE_5, D("0")) in sheet.trace


def test_a_blank_line_4_is_still_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(BlankNotAllowedError, match="may not be left blank"):
        t2204(take_home_service, [Artifact(T2204_PREMIUMS_DEDUCTED, BLANK)])
