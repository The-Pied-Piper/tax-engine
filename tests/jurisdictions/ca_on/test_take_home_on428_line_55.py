"""ON428 (2025) line 55, computed from the real part files through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 55: Line 53 plus line 54 =".
Line 55 is one sum, core/sum of line 53 (the tax minus credits,
`ca-on/on428_tax_minus_credits_line_53`, a temporary catalog kind until line 53 has its own) and
line 54 (the Ontario tax on split income, Form T1206, `ca-on/on428_tax_on_split_income_line_54`). Line 54
is an optional input: a caller with no split income leaves it out, it is read as blank, and the
line 55 part reads that blank as 0. The output is `ca-on/on428_tax_with_split_income_line_55`,
exported by the form.

This test declares lines 53 and 54 as the inputs of its header (line 54 optional, as its real
inputs part declares it) and loads the take-home folder's `on428_line_55.yaml` beside it.
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
LINE_53 = "ca-on/on428_tax_minus_credits_line_53"
LINE_54 = "ca-on/on428_tax_on_split_income_line_54"
LINE_55 = "ca-on/on428_tax_with_split_income_line_55"
PART = "on428_line_55.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_53}
    required: true
  - name: {LINE_54}
    required: false
    default: null
    basis: 'Line 54 and line 61510: Ontario tax on split income (complete Form T1206)'
outputs:
  - {LINE_53}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_55}
capabilities: []
"""


def _line_55(take_home_service: TakeHomeService, line_53: str, line_54: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_53), D(line_53))]
    if line_54 is not None:
        given.append(Artifact(kinds.kind(LINE_54), D(line_54)))
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_55)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_53", "line_55"),
    [
        # A $20,000 salary: line 53 is 300.14 and line 54 is blank (0), so line 55 is 300.14.
        ("300.14", "300.14"),
        # A $70,000 salary: line 53 is 3,311.45 and line 54 is blank (0), so line 55 is 3,311.45.
        ("3311.45", "3311.45"),
        # A $150,000 salary: line 53 is 11,458.12 and line 54 is blank (0), so line 55 is 11,458.12.
        ("11458.12", "11458.12"),
    ],
)
def test_line_55_is_line_53_when_line_54_is_left_out(
    take_home_service: TakeHomeService, line_53: str, line_55: str
) -> None:
    assert _line_55(take_home_service, line_53, None) == D(line_55)


def test_line_55_is_line_53_plus_line_54(take_home_service: TakeHomeService) -> None:
    # Line 53 is 3,311.45 and line 54 is 100.00, so line 55 is 3,411.45.
    assert _line_55(take_home_service, "3311.45", "100.00") == D("3411.45")
