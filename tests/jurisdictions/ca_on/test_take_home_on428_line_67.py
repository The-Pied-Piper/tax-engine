"""ON428 (2025) line 67, the 36% surtax tier, computed from the real part file through the real
engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 67: (Line 65 minus $7,307) multiplied by 36%
(if negative, enter "0") =". The $7,307 threshold and the 36% rate are held in the
`ca-on/surtax_line_67` dataset, so line 67 is one calculation: line 65 minus 7,307, times 36%,
rounded half-up to the cent, and 0 when line 65 is under the threshold. The input is
`ca-on/on428_surtax_base_line_65` (line 65), produced by another part, so this test declares it
as an input in a header of its own and loads the take-home folder's `on428/on428_line_67.yaml`
beside it. The output is `ca-on/on428_surtax_36_percent_tier_line_67`, exported by the form.
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
LINE_67 = "ca-on/on428_surtax_36_percent_tier_line_67"
PART = "on428_line_67.yaml"

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
    - {LINE_67}
capabilities: []
"""


def _line_67(take_home_service: TakeHomeService, line_65: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_65), D(line_65)),
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_67)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_65", "line_67"),
    [
        # A $20,000 salary: line 65 is 300.14, under 7,307, so line 67 is 0.
        ("300.14", "0.00"),
        # A $70,000 salary: line 65 is 3,311.45, under 7,307, so line 67 is 0.
        ("3311.45", "0.00"),
        # A $150,000 salary: line 65 is 11,458.12, and (11,458.12 - 7,307) x 36% = 1,494.4032,
        # rounded to 1,494.40.
        ("11458.12", "1494.40"),
        # Line 65 is 0, so line 67 is 0.
        ("0", "0.00"),
        # Line 65 is exactly the threshold, so line 67 is 0.
        ("7307", "0.00"),
        # 0.01 x 36% = 0.0036, rounded down to 0.00.
        ("7307.01", "0.00"),
        # 0.02 x 36% = 0.0072, rounded to 0.01.
        ("7307.02", "0.01"),
        # 0.04 x 36% = 0.0144, rounded down to 0.01.
        ("7307.04", "0.01"),
    ],
)
def test_line_67_is_36_percent_of_line_65_over_7307(
    take_home_service: TakeHomeService, line_65: str, line_67: str
) -> None:
    assert _line_67(take_home_service, line_65) == D(line_67)
