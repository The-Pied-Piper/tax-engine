"""ON428 (2025) line 88, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 88: Line 86 minus line 87 (if negative, enter
"0") =". Line 88 is one core/subtract_not_below_zero: line 86
(`ca-on/on428_tax_after_lift_credit_line_86`, required) less line 87
(`ca-on/on428_farmers_food_donation_credit_line_87`), which is an optional input with blank
fallback 0. A salary-only caller makes no community food program donation, so a
request that leaves line 87 out is read as blank, and the line 88 part reads that blank as 0.
Lines 86 and 87 come from other parts, so this test declares them as the inputs of its header
(line 87 optional, as its real inputs part declares it) and loads the take-home folder's
`on428_line_88.yaml` beside it. The output is
`ca-on/on428_tax_after_farmers_food_donation_credit_line_88`, exported by the form.
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
LINE_86 = "ca-on/on428_tax_after_lift_credit_line_86"
LINE_87 = "ca-on/on428_farmers_food_donation_credit_line_87"
LINE_88 = "ca-on/on428_tax_after_farmers_food_donation_credit_line_88"
PART = "on428_line_88.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_86}
    required: true
  - name: {LINE_87}
    required: false
    default: null
    basis: 'Line 87 and line 62150: Enter the amount of qualifying donations that have also been
      claimed as a charitable donation. multiplied by 25%'
outputs:
  - {LINE_86}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_88}
capabilities: []
"""


def _line_88(take_home_service: TakeHomeService, line_86: str, line_87: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_86), D(line_86))]
    if line_87 is not None:
        given.append(Artifact(kinds.kind(LINE_87), D(line_87)))
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_88)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_86", "line_88"),
    [
        # A $20,000 salary: line 86 is 0.00 and line 87 is blank (0), so line 88 is 0.00.
        ("0.00", "0.00"),
        # A $70,000 salary: line 86 is 3,311.45 and line 87 is blank (0), so line 88 is 3,311.45.
        ("3311.45", "3311.45"),
        # A $150,000 salary: line 86 is 14,102.14 and line 87 is blank (0), so line 88 is 14,102.14.
        ("14102.14", "14102.14"),
    ],
)
def test_line_88_is_line_86_when_line_87_is_left_out(
    take_home_service: TakeHomeService, line_86: str, line_88: str
) -> None:
    assert _line_88(take_home_service, line_86, None) == D(line_88)


def test_line_88_is_line_86_minus_line_87(take_home_service: TakeHomeService) -> None:
    # Line 86 is 3,311.45 and line 87 is 1,000.00, so line 88 is 2,311.45.
    assert _line_88(take_home_service, "3311.45", "1000.00") == D("2311.45")


@pytest.mark.parametrize(
    ("line_86", "line_87", "line_88"),
    [
        # Line 87 above line 86 gives "0", as the form says.
        ("300.14", "1000.00", "0"),
        # Exactly equal: the difference is zero.
        ("3311.45", "3311.45", "0"),
    ],
)
def test_line_88_is_0_when_line_87_is_not_less_than_line_86(
    take_home_service: TakeHomeService, line_86: str, line_87: str, line_88: str
) -> None:
    assert _line_88(take_home_service, line_86, line_87) == D(line_88)
