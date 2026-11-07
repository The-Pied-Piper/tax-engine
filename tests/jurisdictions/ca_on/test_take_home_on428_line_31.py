"""ON428 (2025) line 31, the total of the credits with the disability amounts, as the Ontario
take-home manifest part wires it.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 31: Add lines 28 to 30." Line 28 is the
`ca-on/on428_credits_with_pension_line_28` input here, a plain starting input. Lines 29 and 30 (the
disability amounts) belong to other tickets and are left out. Line 31 is one core/sum over
line 28 alone.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_on.catalog import (
    ON428_CREDITS_WITH_DISABILITY_LINE_31,
    ON428_CREDITS_WITH_PENSION_LINE_28,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "on428_line_31.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca-on/on428_credits_with_pension_line_28
        required: true
    outputs:
      - ca-on/on428_credits_with_pension_line_28
    """)
FORM = dedent("""\
    form:
      name: ca-on/on428
      required: true
      exports:
        - ca-on/on428_credits_with_disability_line_31
    """)


def line_31(take_home_service: TakeHomeService, line_28: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(ON428_CREDITS_WITH_PENSION_LINE_28, D(line_28)),
    )
    (sheet,) = worksheets["ca-on/on428"]
    return sheet.get(ON428_CREDITS_WITH_DISABILITY_LINE_31).value


@pytest.mark.parametrize(
    ("line_28", "expected"),
    [
        # Line 28 at salaries of $20,000, $70,000 and $150,000.
        ("13891.75", "13891.75"),
        ("17116.23", "17116.23"),
        ("17180.58", "17180.58"),
        ("0", "0"),
    ],
)
def test_line_31_is_line_28_with_lines_29_and_30_left_out(
    take_home_service: TakeHomeService, line_28: str, expected: str
) -> None:
    assert line_31(take_home_service, line_28) == D(expected)
