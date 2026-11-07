"""ON428 (2025) line 77, the tax reduction, computed from the real part file through the engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 77: Add lines 74 to 76. =". Lines 75 and 76
(the reduction for dependent children and for dependants with an impairment, $544 each) are left
out: a single filer with no such dependants has none of them. So line 77 is one calculation: a sum
of the single part, line 74 (`ca-on/on428_basic_reduction_line_74`), read through core/sum. Line 74
is the $294.00 basic reduction at every salary, and line 78 reads line 77 later.

The input is `ca-on/on428_basic_reduction_line_74` (line 74), produced by another part, so this test
declares it as an input in a header of its own and loads the take-home folder's
`on428_line_77.yaml` beside it. The output is `ca-on/on428_tax_reduction_line_77`, exported by
the form.
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
LINE_74 = "ca-on/on428_basic_reduction_line_74"
LINE_77 = "ca-on/on428_tax_reduction_line_77"
PART = "on428_line_77.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_74}
    required: true
outputs:
  - {LINE_74}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_77}
capabilities: []
"""


def _line_77(take_home_service: TakeHomeService, line_74: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_74), D(line_74)),
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_77)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_74", "line_77"),
    [
        # A $20,000 salary: line 74 is the $294.00 basic reduction, so line 77 is 294.00.
        ("294.00", "294.00"),
        # A $70,000 salary: line 74 is the $294.00 basic reduction, so line 77 is 294.00.
        ("294.00", "294.00"),
        # A $150,000 salary: line 74 is the $294.00 basic reduction, so line 77 is 294.00.
        ("294.00", "294.00"),
        # Line 74 at zero: 0 is the sum of line 74 alone, so line 77 is 0.00.
        ("0", "0.00"),
        # Line 77 is the sum of the single part, not a fixed figure: 100.00 gives 100.00.
        ("100.00", "100.00"),
    ],
)
def test_line_77_is_line_74_with_lines_75_and_76_left_out(
    take_home_service: TakeHomeService, line_74: str, line_77: str
) -> None:
    assert _line_77(take_home_service, line_74) == D(line_77)
