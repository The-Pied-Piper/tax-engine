"""T1 (2025) line 23600 as a signed amount, net income before its floor, from the real part files.

T1 line 23600: "Line 56 and line 23600: Line 54 minus line 55 (if negative, enter "0")" (5006-R,
page 4). Schedule 6 line 7 and ON428-A line 6 print the amount before that floor: "Net income from
line 23600 of the return (or the amount you would have entered if the instructions on line 23600
said "if negative, show in brackets")" (5000-s6-25e.txt lines 193-197; 5006-a-25e.txt line 27).

The signed part, `t1_taxable_income_line_23600_signed.yaml`, subtracts the social benefits
repayment (line 23500, `ca/social_benefits_repayment`) from the net income before adjustments (line
23400, `ca/net_income_before_adjustments`) with `core/subtract`, with no floor, and its output is
`ca/net_income_signed`. The floored part `t1_taxable_income_line_23600.yaml` is unchanged: it still
gives `ca/net_income`, not below zero.

Line 23400 is a part of its own, so this test declares it as a required starting
input in a header of its own. Line 23500 is an optional input declared in the take-home folder's
`t1_taxable_income_inputs.yaml`, which this test loads beside the part: a request that leaves it
out reads it as its default, "0".
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
CODE = JurisdictionCode("CA-ON")
FORM = "ca/t1_taxable_income"
LINE_23400 = "ca/net_income_before_adjustments"
LINE_23500 = "ca/social_benefits_repayment"
LINE_23600_SIGNED = "ca/net_income_signed"
HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_23400}
    required: true
outputs:
  - {LINE_23400}
capabilities: []
"""
# The part under test beside the optional line 23500 input.
PARTS = ("t1_taxable_income_inputs.yaml", "t1_taxable_income_line_23600_signed.yaml")
FORM_TEXT = f"""\
form:
  name: {FORM}
  required: true
  exports:
    - {LINE_23600_SIGNED}
capabilities: []
"""


def _line_23600_signed(
    take_home_service: TakeHomeService, line_23400: str, line_23500: str | None
) -> Decimal:
    kinds = bundled_kinds()
    starting = [Artifact(kinds.kind(LINE_23400), D(line_23400))]
    if line_23500 is not None:
        starting.append(Artifact(kinds.kind(LINE_23500), D(line_23500)))
    worksheets = take_home_service(HEADER, FORM_TEXT, *PARTS).compute(CODE, 2025, *starting)
    (sheet,) = worksheets[FORM]
    value = sheet.get(kinds.kind(LINE_23600_SIGNED)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_23400", "line_23500", "expected"),
    [
        # A $70,000 salary: line 23400 is 69,335.00, and line 23500 is left out, so it is 0.
        ("69335.00", None, "69335.00"),
        # The $90,000 salary, above the CPP ceiling: line 23400 is 88,926.00, line 23500 left out.
        ("88926.00", None, "88926.00"),
        # Line 23500 given as 1,000: line 23600 is line 23400 less it.
        ("69335.00", "1000", "68335.00"),
        # Line 23500 above line 23400: the difference is negative and is kept as it is, in
        # brackets on Schedule 6 line 7 and ON428-A line 6, not floored at "0".
        ("1000.00", "5000", "-4000.00"),
        # Line 23400 negative with line 23500 left out: the signed amount is the line 23400 amount.
        ("-500.00", None, "-500.00"),
    ],
)
def test_line_23600_signed_is_line_23400_less_line_23500_without_a_floor(
    take_home_service: TakeHomeService, line_23400: str, line_23500: str | None, expected: str
) -> None:
    assert _line_23600_signed(take_home_service, line_23400, line_23500) == D(expected)


def test_the_line_23600_signed_kind_is_registered_and_signed() -> None:
    # Signed: Schedule 6 line 7 and ON428-A line 6 print a negative net income in brackets, so the
    # kind the part produces may not be negative. The kind is declared in the catalog already.
    kind = bundled_kinds().kind(LINE_23600_SIGNED)

    assert kind.identifier == LINE_23600_SIGNED
    assert non_negative(kind) is False
