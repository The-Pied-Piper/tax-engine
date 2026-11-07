"""ON428 (2025) line 69, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 69: Line 62 plus line 68 =". Line 62 is a copy
of line 61, so the step is one core/sum over line 61
(`ca-on/on428_tax_after_minimum_tax_carryover_line_61`) and line 68
(`ca-on/on428_surtax_total_line_68`). Both are required inputs, and both come from other parts,
so this test declares them as the inputs of its header and loads the take-home folder's
`on428_line_69.yaml` beside it. The output is `ca-on/on428_tax_with_surtax_line_69`, exported by
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
LINE_61 = "ca-on/on428_tax_after_minimum_tax_carryover_line_61"
LINE_68 = "ca-on/on428_surtax_total_line_68"
LINE_69 = "ca-on/on428_tax_with_surtax_line_69"
PART = "on428_line_69.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_61}
    required: true
  - name: {LINE_68}
    required: true
outputs:
  - {LINE_61}
  - {LINE_68}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_69}
capabilities: []
"""


def _line_69(take_home_service: TakeHomeService, line_61: str, line_68: str) -> Decimal:
    kinds = bundled_kinds()
    given = [
        Artifact(kinds.kind(LINE_61), D(line_61)),
        Artifact(kinds.kind(LINE_68), D(line_68)),
    ]
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_69)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_61", "line_69"),
    [
        # A $20,000 salary: line 61 is 300.14 and line 68 is 0.00, so line 69 is 300.14.
        ("300.14", "300.14"),
        # A $70,000 salary: line 61 is 3,311.45 and line 68 is 0.00, so line 69 is 3,311.45.
        ("3311.45", "3311.45"),
    ],
)
def test_line_69_is_line_61_when_line_68_is_zero(
    take_home_service: TakeHomeService, line_61: str, line_69: str
) -> None:
    assert _line_69(take_home_service, line_61, "0.00") == D(line_69)


@pytest.mark.parametrize(
    ("line_61", "line_68", "line_69"),
    [
        # A $150,000 salary: line 61 is 11,458.12 and line 68 is 2,644.02, so line 69 is 14,102.14.
        ("11458.12", "2644.02", "14102.14"),
        # Nonzero cents on both lines: 3,311.45 plus 1,234.56 is 4,546.01.
        ("3311.45", "1234.56", "4546.01"),
    ],
)
def test_line_69_is_line_61_plus_line_68(
    take_home_service: TakeHomeService, line_61: str, line_68: str, line_69: str
) -> None:
    assert _line_69(take_home_service, line_61, line_68) == D(line_69)
