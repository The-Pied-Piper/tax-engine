"""ON428-A (2025) line 19, computed from the real part file through the real engine.

ON428-A Part A, "If you were single at the end of the year": line 18 "Applicable rate 5%" and
line 19 "Line 17 multiplied by the percentage from line 18 =". Line 18 is a printed figure, held
in the `ca-on/lift_single_rate` dataset, so line 19 is one calculation: 5% of line 17. The input is
`ca-on/lift_single_excess_over_threshold` (line 17, "Line 15 minus line 16 (if negative, enter
"0")"), produced by another part, so this test declares it as an input in a header of its own and
loads the take-home folder's `on428_a/on428_a_line_19.yaml` beside it. The output is
`ca-on/lift_reduction`, exported by the form.
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
LINE_17 = "ca-on/lift_single_excess_over_threshold"
LINE_19 = "ca-on/lift_reduction"
PART = "on428_a_line_19.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_17}
    required: true
outputs:
  - {LINE_17}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428_a
  required: true
  exports:
    - {LINE_19}
capabilities: []
"""


def _line_19(take_home_service: TakeHomeService, line_17: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_17), D(line_17)),
    )["ca-on/on428_a"][0]
    value = worksheet.get(kinds.kind(LINE_19)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_17", "line_19"),
    [
        # A $70,000 salary: line 17 is 36,835.00, and 5% of it is 1,841.75, in cents already.
        ("36835.00", "1841.75"),
        # A $40,000 salary: line 17 is 7,135.00, and 5% of it is 356.75.
        ("7135.00", "356.75"),
        # Line 17 is 0, under the threshold, so line 19 is 0.
        ("0", "0.00"),
        # 10.10 x 5% = 0.505, a tie, rounded half-up to 0.51.
        ("10.10", "0.51"),
        # 10.09 x 5% = 0.5045, rounded down to 0.50.
        ("10.09", "0.50"),
    ],
)
def test_line_19_is_5_percent_of_line_17(
    take_home_service: TakeHomeService, line_17: str, line_19: str
) -> None:
    assert _line_19(take_home_service, line_17) == D(line_19)
