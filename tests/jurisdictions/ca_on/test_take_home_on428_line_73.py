"""ON428 (2025) line 73, computed from the real part files through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 73: Line 71 plus line 72 =".
Line 73 is one sum, core/sum of line 71 (the tax after the dividend tax credit,
`ca-on/on428_tax_after_dividend_credit_line_71`) and
line 72 (the additional tax for minimum tax purposes from Worksheet ON428,
`ca-on/on428_additional_tax_for_minimum_tax_line_72`). Line 72 is an optional input: a caller with
no minimum tax leaves it out, it is read as blank, and the line 73 part reads that blank as 0. The
output is `ca-on/on428_tax_with_minimum_tax_addition_line_73`, exported by the form.

This test declares lines 71 and 72 as the inputs of its header (line 72 optional, as its real
inputs part declares it) and loads the take-home folder's `on428_line_73.yaml` beside it.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
LINE_71 = "ca-on/on428_tax_after_dividend_credit_line_71"
LINE_72 = "ca-on/on428_additional_tax_for_minimum_tax_line_72"
LINE_73 = "ca-on/on428_tax_with_minimum_tax_addition_line_73"
PART = "on428_line_73.yaml"

BASIS = (
    "Line 72: If you entered an amount on line 11 of Part 5 of Form T691, use Worksheet ON428 to "
    "calculate your additional tax for minimum tax purposes"
)
HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_71}
    required: true
  - name: {LINE_72}
    required: false
    default: null
    basis: '{BASIS}'
outputs:
  - {LINE_71}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_73}
capabilities: []
"""


def _line_73(take_home_service: TakeHomeService, line_71: str, line_72: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_71), D(line_71))]
    if line_72 is not None:
        given.append(Artifact(kinds.kind(LINE_72), D(line_72)))
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_73)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_71", "line_73"),
    [
        # A $20,000 salary: line 71 is 300.14 and line 72 is blank (0), so line 73 is 300.14.
        ("300.14", "300.14"),
        # A $70,000 salary: line 71 is 3,311.45 and line 72 is blank (0), so line 73 is 3,311.45.
        ("3311.45", "3311.45"),
        # A $150,000 salary: line 71 is 14,102.14 and line 72 is blank (0), so line 73 is 14,102.14.
        ("14102.14", "14102.14"),
    ],
)
def test_line_73_is_line_71_when_line_72_is_left_out(
    take_home_service: TakeHomeService, line_71: str, line_73: str
) -> None:
    assert _line_73(take_home_service, line_71, None) == D(line_73)


def test_line_73_is_line_71_plus_line_72(take_home_service: TakeHomeService) -> None:
    # Line 71 is 3,311.45 and line 72 is 100.00, so line 73 is 3,411.45.
    assert _line_73(take_home_service, "3311.45", "100.00") == D("3411.45")
