"""ON428 (2025) line 81, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 81: Line 73 minus line 80 (if negative, enter
"0") =". Line 81 is one core/subtract_not_below_zero: line 73
(`ca-on/on428_tax_with_minimum_tax_addition_line_73`, required) less line 80
(`ca-on/on428_ontario_tax_reduction_line_80`, required), not below zero. Line 80 comes from
another part (the Ontario tax reduction), so this test declares lines 73 and 80 as the required
inputs of its header and loads the take-home folder's `on428_line_81.yaml` beside it. The output
is `ca-on/on428_tax_after_tax_reduction_line_81`, exported by the form.
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
ON428_ONTARIO_TAX_REDUCTION_LINE_80 = "ca-on/on428_ontario_tax_reduction_line_80"
LINE_81 = "ca-on/on428_tax_after_tax_reduction_line_81"
PART = "on428_line_81.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_73}
    required: true
  - name: {ON428_ONTARIO_TAX_REDUCTION_LINE_80}
    required: true
outputs:
  - {LINE_73}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_81}
capabilities: []
"""


def _line_81(take_home_service: TakeHomeService, line_73: str, line_80: str) -> Decimal:
    kinds = bundled_kinds()
    given = [
        Artifact(kinds.kind(LINE_73), D(line_73)),
        Artifact(kinds.kind(ON428_ONTARIO_TAX_REDUCTION_LINE_80), D(line_80)),
    ]
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_81)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_73", "line_80", "line_81"),
    [
        # A $20,000 salary: line 73 is 300.14 and line 80 is 287.86, so line 81 is 12.28.
        ("300.14", "287.86", "12.28"),
        # A $70,000 salary: line 73 is 3,311.45 and line 80 is 0, so line 81 is 3,311.45.
        ("3311.45", "0", "3311.45"),
        # A $150,000 salary: line 73 is 14,102.14 and line 80 is 0, so line 81 is 14,102.14.
        ("14102.14", "0", "14102.14"),
    ],
)
def test_line_81_is_line_73_minus_line_80(
    take_home_service: TakeHomeService, line_73: str, line_80: str, line_81: str
) -> None:
    assert _line_81(take_home_service, line_73, line_80) == D(line_81)


@pytest.mark.parametrize(
    ("line_73", "line_80"),
    [
        # Line 80 above line 73 gives "0", as the form says.
        ("300.14", "1000.00"),
        # Exactly equal: the difference is zero.
        ("3311.45", "3311.45"),
    ],
)
def test_line_81_is_0_when_line_80_is_not_less_than_line_73(
    take_home_service: TakeHomeService, line_73: str, line_80: str
) -> None:
    assert _line_81(take_home_service, line_73, line_80) == D("0")
