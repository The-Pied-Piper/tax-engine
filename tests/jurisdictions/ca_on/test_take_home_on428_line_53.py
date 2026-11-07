"""ON428 (2025) line 53, tax minus credits, computed from the real part file through the engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 53: Line 51 minus line 52 (if negative, enter
"0") =". Line 51 is a copy of line 8 and line 52 is a copy of line 50, so line 53 is one
calculation: line 8 minus line 50, not below zero. The inputs are
`ca-on/on428_tax_on_taxable_income_line_8` (line 8) and
`ca-on/on428_non_refundable_credits_line_50` (line 50), both produced by other parts,
so this test declares them as inputs in a header of its own and loads the take-home folder's
`on428/on428_line_53.yaml` beside it. The output is `ca-on/on428_tax_minus_credits_line_53`,
exported by the form.
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
LINE_8 = "ca-on/on428_tax_on_taxable_income_line_8"
LINE_50 = "ca-on/on428_non_refundable_credits_line_50"
LINE_53 = "ca-on/on428_tax_minus_credits_line_53"
PART = "on428_line_53.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_8}
    required: true
  - name: {LINE_50}
    required: true
outputs:
  - {LINE_8}
  - {LINE_50}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_53}
capabilities: []
"""


def _line_53(take_home_service: TakeHomeService, line_8: str, line_50: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_8), D(line_8)),
        Artifact(kinds.kind(LINE_50), D(line_50)),
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_53)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_8", "line_50", "line_53"),
    [
        # A $20,000 salary: line 8 is 1,001.67 and line 50 is 701.53, so line 53 is 300.14.
        ("1001.67", "701.53", "300.14"),
        # A $70,000 salary: line 8 is 4,175.82 and line 50 is 864.37, so line 53 is 3,311.45.
        ("4175.82", "864.37", "3311.45"),
        # A $150,000 salary: line 8 is 12,325.74 and line 50 is 867.62, so line 53 is 11,458.12.
        ("12325.74", "867.62", "11458.12"),
        # Credits larger than tax: 100.00 minus 150.00 is negative, so the line enters 0.
        ("100.00", "150.00", "0.00"),
        # Credits equal to tax: 500.00 minus 500.00 is 0.
        ("500.00", "500.00", "0.00"),
        # No tax and no credits: 0 minus 0 is 0.
        ("0", "0", "0.00"),
        # A cents difference: 0.10 minus 0.09 is 0.01.
        ("0.10", "0.09", "0.01"),
    ],
)
def test_line_53_is_line_8_minus_line_50_not_below_zero(
    take_home_service: TakeHomeService, line_8: str, line_50: str, line_53: str
) -> None:
    assert _line_53(take_home_service, line_8, line_50) == D(line_53)
