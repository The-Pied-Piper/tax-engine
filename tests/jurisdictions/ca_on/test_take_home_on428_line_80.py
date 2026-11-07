"""ON428 (2025) line 80, the Ontario tax reduction, computed from the real part file.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 80: Line 78 minus line 79 (if negative,
enter "0") Ontario tax reduction =". Line 79 is a copy of line 73, so line 80 is one subtraction
floored at zero: line 78 (`ca-on/on428_tax_reduction_doubled_line_78`) less line 73
(`ca-on/on428_tax_with_minimum_tax_addition_line_73`), read through core/subtract_not_below_zero.
A result below zero is entered as 0.

The inputs are lines 78 and 73, both produced by other parts, so this test declares them as the
inputs of its header and loads the take-home folder's `on428/on428_line_80.yaml` beside it. The
output is `ca-on/on428_ontario_tax_reduction_line_80`, exported by the form.
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
LINE_73 = "ca-on/on428_tax_with_minimum_tax_addition_line_73"
LINE_78 = "ca-on/on428_tax_reduction_doubled_line_78"
LINE_80 = "ca-on/on428_ontario_tax_reduction_line_80"
PART = "on428_line_80.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_78}
    required: true
  - name: {LINE_73}
    required: true
outputs:
  - {LINE_78}
  - {LINE_73}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_80}
capabilities: []
"""


def _line_80(take_home_service: TakeHomeService, line_78: str, line_73: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_78), D(line_78)),
        Artifact(kinds.kind(LINE_73), D(line_73)),
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_80)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_78", "line_73", "line_80"),
    [
        # A $20,000 salary: line 78 is 588.00 and line 73 is 300.14, so line 80 is 287.86.
        ("588.00", "300.14", "287.86"),
        # A $70,000 salary: line 78 is 588.00 and line 73 is 3,311.45, so line 80 floors to 0.00.
        ("588.00", "3311.45", "0.00"),
        # A $150,000 salary: line 78 is 588.00 and line 73 is 14,102.14, so line 80 floors to 0.00.
        ("588.00", "14102.14", "0.00"),
        # Line 78 equal to line 73: the difference is 0, so line 80 is 0.00.
        ("300.14", "300.14", "0.00"),
        # Line 73 above line 78: the difference is negative, so line 80 floors to 0.00.
        ("100.00", "300.14", "0.00"),
        # Line 78 above line 73: the difference is positive, so line 80 is 488.00.
        ("588.00", "100.00", "488.00"),
    ],
)
def test_line_80_is_line_78_minus_line_73_not_below_zero(
    take_home_service: TakeHomeService, line_78: str, line_73: str, line_80: str
) -> None:
    assert _line_80(take_home_service, line_78, line_73) == D(line_80)
