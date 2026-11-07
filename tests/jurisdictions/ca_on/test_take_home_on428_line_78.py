"""ON428 (2025) line 78, the doubled tax reduction, computed from the real part file through the
real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 78: Amount from line 77 above multiplied by 2 =".
One calculation: line 77 times 2, from the `ca-on/tax_reduction_multiplier` fraction dataset (2 over
1). The product is a dollars-and-cents box, so the dataset rounds it half-up to the cent (increment
0.01), and line 78 prints 588.00 with its cents. The input is
`ca-on/on428_tax_reduction_line_77` (line 77), produced by another part, so this test
declares it as an input in a header of its own and loads the take-home folder's
`on428_line_78.yaml` beside it. The output is `ca-on/on428_tax_reduction_doubled_line_78`,
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
LINE_77 = "ca-on/on428_tax_reduction_line_77"
LINE_78 = "ca-on/on428_tax_reduction_doubled_line_78"
PART = "on428_line_78.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_77}
    required: true
outputs:
  - {LINE_77}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_78}
capabilities: []
"""


def _line_78(take_home_service: TakeHomeService, line_77: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_77), D(line_77)),
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_78)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_77", "line_78"),
    [
        # A $20,000 salary: line 77 is 294.00, so line 78 is 588.00.
        ("294.00", "588.00"),
        # A $70,000 salary: line 77 is 294.00, so line 78 is 588.00.
        ("294.00", "588.00"),
        # A $150,000 salary: line 77 is 294.00, so line 78 is 588.00.
        ("294.00", "588.00"),
        # Line 77 is 0, so line 78 is 0.
        ("0", "0.00"),
        # 0.01 x 2 = 0.02, exact: nothing to round.
        ("0.01", "0.02"),
    ],
)
def test_line_78_is_line_77_multiplied_by_2(
    take_home_service: TakeHomeService, line_77: str, line_78: str
) -> None:
    assert _line_78(take_home_service, line_77) == D(line_78)
