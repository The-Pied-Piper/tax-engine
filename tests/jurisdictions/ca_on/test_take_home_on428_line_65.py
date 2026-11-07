"""ON428 (2025) line 65, the surtax base, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 65: Line 63 minus line 64 (if negative, enter
"0") =". Line 63 is a copy of line 61 and line 64 is a copy of line 54, so line 65 is one
core/subtract_not_below_zero: line 61 less line 54, floored at zero. The input line 61
(`ca-on/on428_tax_after_minimum_tax_carryover_line_61`) is required, and line 54
(`ca-on/on428_tax_on_split_income_line_54`) is optional: a salary-only caller has no split income,
so a request that leaves line 54 out is read as blank, and the line 65 part reads that blank as 0.
The input kinds come from other parts, so this test declares them as the inputs of its own header
and loads the take-home folder's `on428_line_65.yaml` beside it. The output is
`ca-on/on428_surtax_base_line_65`, exported by the form.

The worked figures are dataset figures, not CRA examples: with line 54 left out, line 65 equals
line 61.
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
LINE_54 = "ca-on/on428_tax_on_split_income_line_54"
LINE_61 = "ca-on/on428_tax_after_minimum_tax_carryover_line_61"
LINE_65 = "ca-on/on428_surtax_base_line_65"
PART = "on428_line_65.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_54}
    required: false
    default: null
  - name: {LINE_61}
    required: true
outputs:
  - {LINE_61}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_65}
capabilities: []
"""


def _line_65(take_home_service: TakeHomeService, line_61: str, line_54: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_61), D(line_61))]
    if line_54 is not None:
        given.append(Artifact(kinds.kind(LINE_54), D(line_54)))
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_65)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_61", "line_65"),
    [
        # A $20,000 salary: line 61 is 300.14 and line 54 is blank (0), so line 65 is 300.14.
        ("300.14", "300.14"),
        # A $70,000 salary: line 61 is 3,311.45 and line 54 is blank (0), so line 65 is 3,311.45.
        ("3311.45", "3311.45"),
        # A $150,000 salary: line 61 is 11,458.12 and line 54 is blank (0), so line 65 is 11,458.12.
        ("11458.12", "11458.12"),
        # Line 61 is 0 and line 54 is blank (0), so line 65 is 0.
        ("0", "0"),
    ],
)
def test_line_65_is_line_61_when_line_54_is_left_out(
    take_home_service: TakeHomeService, line_61: str, line_65: str
) -> None:
    assert _line_65(take_home_service, line_61, None) == D(line_65)


def test_line_65_is_line_61_less_line_54(take_home_service: TakeHomeService) -> None:
    # Line 61 is 300.14 and line 54 is 100.00, so line 65 is 200.14.
    assert _line_65(take_home_service, "300.14", "100.00") == D("200.14")


def test_line_65_is_0_when_line_54_equals_line_61(take_home_service: TakeHomeService) -> None:
    # Line 61 is 300.14 and line 54 is 300.14, so the difference is 0.
    assert _line_65(take_home_service, "300.14", "300.14") == D("0")


def test_line_65_is_0_when_line_54_is_larger_than_line_61(
    take_home_service: TakeHomeService,
) -> None:
    # Line 61 is 300.14 and line 54 is 400.00: the difference is negative, so line 65 is 0.
    assert _line_65(take_home_service, "300.14", "400.00") == D("0")


def test_line_65_is_0_when_line_61_is_0(take_home_service: TakeHomeService) -> None:
    # Line 61 is 0 and line 54 is 100.00: the difference is negative, so line 65 is floored at 0.
    assert _line_65(take_home_service, "0", "100.00") == D("0")
