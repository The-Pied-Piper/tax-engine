"""ON428 (2025) line 61, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 61: Line 55 minus line 60 (if negative, enter
"0") =". Line 61 is one core/subtract_not_below_zero: line 55
(`ca-on/on428_tax_with_split_income_line_55`, required) less line 60
(`ca-on/on428_minimum_tax_carryover_line_60`), which is an optional input with blank fallback 0.
A salary-only caller has no Ontario minimum tax carryover, so a request that leaves line 60 out is
read as blank, and the line 61 part reads that blank as 0. Lines 55 and 60 come from other parts,
so this test declares them as the inputs of its header (line 60 optional, as its real inputs part
declares it) and loads the take-home folder's `on428_line_61.yaml` beside it. The output is
`ca-on/on428_tax_after_minimum_tax_carryover_line_61`, exported by the form.
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
LINE_55 = "ca-on/on428_tax_with_split_income_line_55"
LINE_60 = "ca-on/on428_minimum_tax_carryover_line_60"
LINE_61 = "ca-on/on428_tax_after_minimum_tax_carryover_line_61"
PART = "on428_line_61.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_55}
    required: true
  - name: {LINE_60}
    required: false
    default: null
    basis: 'Line 60 and line 61540: Enter whichever is less: amount from line 58 or line 59'
outputs:
  - {LINE_55}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_61}
capabilities: []
"""


def _line_61(take_home_service: TakeHomeService, line_55: str, line_60: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_55), D(line_55))]
    if line_60 is not None:
        given.append(Artifact(kinds.kind(LINE_60), D(line_60)))
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_61)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_55", "line_61"),
    [
        # A $20,000 salary: line 55 is 300.14 and line 60 is blank (0), so line 61 is 300.14.
        ("300.14", "300.14"),
        # A $70,000 salary: line 55 is 3,311.45 and line 60 is blank (0), so line 61 is 3,311.45.
        ("3311.45", "3311.45"),
        # A $150,000 salary: line 55 is 11,458.12 and line 60 is blank (0), so line 61 is 11,458.12.
        ("11458.12", "11458.12"),
    ],
)
def test_line_61_is_line_55_when_line_60_is_left_out(
    take_home_service: TakeHomeService, line_55: str, line_61: str
) -> None:
    assert _line_61(take_home_service, line_55, None) == D(line_61)


def test_line_61_is_line_55_minus_line_60(take_home_service: TakeHomeService) -> None:
    # Line 55 is 3,311.45 and line 60 is 1,000.00, so line 61 is 2,311.45.
    assert _line_61(take_home_service, "3311.45", "1000.00") == D("2311.45")


@pytest.mark.parametrize(
    ("line_55", "line_60", "line_61"),
    [
        # Line 60 above line 55 gives "0", as the form says.
        ("300.14", "1000.00", "0"),
        # Exactly equal: the difference is zero.
        ("3311.45", "3311.45", "0"),
    ],
)
def test_line_61_is_0_when_line_60_is_not_less_than_line_55(
    take_home_service: TakeHomeService, line_55: str, line_60: str, line_61: str
) -> None:
    assert _line_61(take_home_service, line_55, line_60) == D(line_61)
