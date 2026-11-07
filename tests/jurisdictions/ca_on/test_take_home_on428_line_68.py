"""ON428 (2025) line 68, computed from the real part files through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 68: Line 66 plus line 67 =  (If line 65 is less
than $5,710, enter "0" on line 68.)". Line 68 is one sum, core/sum of line 66 (the Ontario surtax
at the 20 percent tier, `ca-on/on428_surtax_20_percent_tier_line_66`) and
line 67 (the Ontario surtax at the 36 percent tier, `ca-on/on428_surtax_36_percent_tier_line_67`).
Both lines are required inputs: the take-home calculator always produces them. The output is
`ca-on/on428_surtax_total_line_68`, exported by the form. The "enter 0" instruction needs no step:
both tiers give 0 at or below their thresholds, so the sum is 0.

This test declares lines 66 and 67 as the inputs of its header and loads the take-home folder's
`on428_line_68.yaml` beside it.
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
LINE_66 = "ca-on/on428_surtax_20_percent_tier_line_66"
LINE_67 = "ca-on/on428_surtax_36_percent_tier_line_67"
LINE_68 = "ca-on/on428_surtax_total_line_68"
PART = "on428_line_68.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_66}
    required: true
  - name: {LINE_67}
    required: true
outputs:
  - {LINE_66}
  - {LINE_67}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_68}
capabilities: []
"""


def _line_68(take_home_service: TakeHomeService, line_66: str, line_67: str) -> Decimal:
    kinds = bundled_kinds()
    given = [
        Artifact(kinds.kind(LINE_66), D(line_66)),
        Artifact(kinds.kind(LINE_67), D(line_67)),
    ]
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_68)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_66", "line_67", "line_68"),
    [
        # A $20,000 salary: line 66 is 0.00 and line 67 is 0.00, so line 68 is 0.00.
        ("0", "0", "0.00"),
        # A $70,000 salary: line 66 is 0.00 and line 67 is 0.00, so line 68 is 0.00.
        ("0", "0", "0.00"),
        # A $150,000 salary: line 66 is 1,149.62 and line 67 is 1,494.40, so line 68 is 2,644.02.
        ("1149.62", "1494.40", "2644.02"),
        # Line 67 is 0 (the 36 percent tier is not reached), so line 68 is line 66.
        ("1149.62", "0", "1149.62"),
        # Line 66 is 0 (the 20 percent tier is not reached), so line 68 is line 67.
        ("0", "0.01", "0.01"),
    ],
)
def test_line_68_is_line_66_plus_line_67(
    take_home_service: TakeHomeService, line_66: str, line_67: str, line_68: str
) -> None:
    assert _line_68(take_home_service, line_66, line_67) == D(line_68)
