"""ON428 (2025) line 90, computed from the real part files through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 90: Line 88 plus line 89 Enter this amount on
line 42800 of your return. Ontario tax =".
Line 90 is one sum, core/sum of line 88 (the Ontario tax after the farmers' food donation credit,
`ca-on/on428_tax_after_farmers_food_donation_credit_line_88`) and
line 89 (the Ontario health premium, `ca-on/on428_ontario_health_premium_line_89`).
Both lines are required inputs: the take-home calculator always produces them. The output is
`ca-on/on428_ontario_tax_line_90`, exported by the form. The "Enter this amount on line 42800 of
your return" instruction needs no step: the T1 General reads line 90 for its line 42800.

This test declares lines 88 and 89 as the inputs of its header and loads the take-home folder's
`on428_line_90.yaml` beside it.
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
LINE_88 = "ca-on/on428_tax_after_farmers_food_donation_credit_line_88"
LINE_89 = "ca-on/on428_ontario_health_premium_line_89"
LINE_90 = "ca-on/on428_ontario_tax_line_90"
PART = "on428_line_90.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_88}
    required: true
  - name: {LINE_89}
    required: true
outputs:
  - {LINE_88}
  - {LINE_89}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_90}
capabilities: []
"""


def _line_90(take_home_service: TakeHomeService, line_88: str, line_89: str) -> Decimal:
    kinds = bundled_kinds()
    given = [
        Artifact(kinds.kind(LINE_88), D(line_88)),
        Artifact(kinds.kind(LINE_89), D(line_89)),
    ]
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_90)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_88", "line_89", "line_90"),
    [
        # A $20,000 salary: line 88 is 0.00 and line 89 is 0.00, so line 90 is 0.00.
        ("0.00", "0.00", "0.00"),
        # A $70,000 salary: line 88 is 3,311.45 and line 89 is 600.00, so line 90 is 3,911.45.
        ("3311.45", "600.00", "3911.45"),
        # A $150,000 salary: line 88 is 14,102.14 and line 89 is 750.00, so line 90 is 14,852.14.
        ("14102.14", "750.00", "14852.14"),
        # Exact cents: 0.01 plus 0.02 is 0.03, with no rounding to the dollar.
        ("0.01", "0.02", "0.03"),
    ],
)
def test_line_90_is_line_88_plus_line_89(
    take_home_service: TakeHomeService, line_88: str, line_89: str, line_90: str
) -> None:
    assert _line_90(take_home_service, line_88, line_89) == D(line_90)
