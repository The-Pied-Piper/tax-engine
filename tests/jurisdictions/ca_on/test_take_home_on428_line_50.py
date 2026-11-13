"""ON428 (2025) line 50, as the Ontario take-home manifest part wires it.

Form text (ON428, CRA 5006-c-25e.txt): "Line 50 and line 61500: Line 46
plus line 49 Enter this amount on line 52. Ontario non-refundable tax credits =". Line 49 is
"Line 49 and line 58969: Line 47 plus line 48" (donations), an optional input with blank fallback
0, in its own part file (on428_line_49_inputs.yaml). Line 50 is one core/sum over line 46 then
line 49.

Line 46 is `ca-on/on428_credit_amounts_at_credit_rate_line_46` (produced by another part), a plain
starting input here. The header and the form's export are made up here, because the shared
scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_on.catalog import (
    ON428_CREDIT_AMOUNTS_AT_CREDIT_RATE_LINE_46,
    ON428_DONATIONS_CREDIT_LINE_49,
    ON428_NON_REFUNDABLE_CREDITS_LINE_50,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "on428_line_50.yaml"
INPUTS_PART = "on428_line_49_inputs.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca-on/on428_credit_amounts_at_credit_rate_line_46
        required: true
    outputs:
      - ca-on/on428_credit_amounts_at_credit_rate_line_46
    """)
FORM = dedent("""\
    form:
      name: ca-on/on428
      required: true
      exports:
        - ca-on/on428_non_refundable_credits_line_50
    """)


def line_50(
    take_home_service: TakeHomeService, line_46: str, donations: str | None = None
) -> Decimal:
    artifacts = [Artifact(ON428_CREDIT_AMOUNTS_AT_CREDIT_RATE_LINE_46, D(line_46))]
    if donations is not None:
        artifacts.append(Artifact(ON428_DONATIONS_CREDIT_LINE_49, D(donations)))
    worksheets = take_home_service(HEADER, FORM, PART, INPUTS_PART).compute(
        JurisdictionCode("CA-ON"), 2025, *artifacts
    )
    (sheet,) = worksheets["ca-on/on428"]
    return sheet.get(ON428_NON_REFUNDABLE_CREDITS_LINE_50).value


@pytest.mark.parametrize(
    ("line_46", "expected"),
    [
        # Worked figures, computed by hand from the printed form (not a CRA example).
        ("701.53", "701.53"),
        ("864.37", "864.37"),
        ("867.62", "867.62"),
    ],
)
def test_line_50_is_line_46_when_the_donations_credit_is_left_out(
    take_home_service: TakeHomeService, line_46: str, expected: str
) -> None:
    assert line_50(take_home_service, line_46) == D(expected)


def test_line_50_adds_the_donations_credit_to_line_46(take_home_service: TakeHomeService) -> None:
    assert line_50(take_home_service, "864.37", "100.00") == D("964.37")
