"""ON428 (2025) line 66, the 20% surtax tier, computed from the real part file through the real
engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "(Line 65 minus $5,710) multiplied by 20% (if negative,
enter "0") =". One calculation: 20% of line 65 above $5,710, never below 0, rounded half-up to the
cent. The input is `ca-on/on428_surtax_base_line_65` (line 65), produced by another part, so this
test declares it as an input in a header of its own and loads the take-home folder's
`on428_line_66.yaml` beside it. The output is `ca-on/on428_surtax_20_percent_tier_line_66`,
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
LINE_65 = "ca-on/on428_surtax_base_line_65"
LINE_66 = "ca-on/on428_surtax_20_percent_tier_line_66"
PART = "on428_line_66.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_65}
    required: true
outputs:
  - {LINE_65}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_66}
capabilities: []
"""


def _line_66(take_home_service: TakeHomeService, line_65: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_65), D(line_65)),
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_66)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_65", "line_66"),
    [
        # A $20,000 salary: line 65 is 300.14, below 5,710, so line 66 is 0.
        ("300.14", "0.00"),
        # A $70,000 salary: line 65 is 3,311.45, below 5,710, so line 66 is 0.
        ("3311.45", "0.00"),
        # A $150,000 salary: line 65 is 11,458.12; 5,748.12 x 20% = 1,149.624, so 1,149.62.
        ("11458.12", "1149.62"),
        # Line 65 is 0, so line 66 is 0.
        ("0", "0.00"),
        # Exactly 5,710: nothing above the threshold.
        ("5710", "0.00"),
        # 0.01 x 20% = 0.002, rounded down to 0.00.
        ("5710.01", "0.00"),
        # 0.02 x 20% = 0.004, rounded down to 0.00.
        ("5710.02", "0.00"),
        # 0.03 x 20% = 0.006, rounded up to 0.01.
        ("5710.03", "0.01"),
    ],
)
def test_line_66_is_20_percent_of_line_65_above_5710(
    take_home_service: TakeHomeService, line_65: str, line_66: str
) -> None:
    assert _line_66(take_home_service, line_65) == D(line_66)
