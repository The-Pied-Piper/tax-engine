"""ON428 (2025) line 44, computed from the real part files through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 44 and line 58800: Line 35 plus line 43 =".
Line 44 is one sum, core/sum of line 35 (the credits with transfers,
`ca-on/on428_credits_with_transfers_line_35`) and line 43 (the medical expenses allowable,
`ca-on/on428_medical_expenses_line_43`, "Line 43 and line 58769: Line 41 plus line 42 ="). Lines
35 and 43 come from other parts, so this test declares them as the inputs of its header (line 43
optional, as its real inputs part declares it) and loads the take-home folder's `on428_line_44.yaml`
beside it. A salary-only caller has no medical expenses, so a request that leaves line 43 out is
read as blank, and the line 44 part reads that blank as 0. The output is
`ca-on/on428_total_credit_amounts_line_44`, exported by the form.
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
LINE_35 = "ca-on/on428_credits_with_transfers_line_35"
LINE_43 = "ca-on/on428_medical_expenses_line_43"
LINE_44 = "ca-on/on428_total_credit_amounts_line_44"
PART = "on428_line_44.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_35}
    required: true
  - name: {LINE_43}
    required: false
    default: null
    basis: 'Line 43 and line 58769: Line 41 plus line 42'
outputs:
  - {LINE_35}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_44}
capabilities: []
"""


def _line_44(take_home_service: TakeHomeService, line_35: str, line_43: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_35), D(line_35))]
    if line_43 is not None:
        given.append(Artifact(kinds.kind(LINE_43), D(line_43)))
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_44)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_35", "line_44"),
    [
        # A $20,000 salary: line 35 is 13,891.75 and line 43 is blank (0), so line 44 is 13,891.75.
        ("13891.75", "13891.75"),
        # A $70,000 salary: line 35 is 17,116.23 and line 43 is blank (0), so line 44 is 17,116.23.
        ("17116.23", "17116.23"),
        # A $150,000 salary: line 35 is 17,180.58 and line 43 is blank (0), so line 44 is 17,180.58.
        ("17180.58", "17180.58"),
    ],
)
def test_line_44_is_line_35_when_line_43_is_left_out(
    take_home_service: TakeHomeService, line_35: str, line_44: str
) -> None:
    assert _line_44(take_home_service, line_35, None) == D(line_44)


def test_line_44_is_line_35_plus_line_43(take_home_service: TakeHomeService) -> None:
    # Line 35 is 17,116.23 and line 43 is 1,000.00, so line 44 is 18,116.23.
    assert _line_44(take_home_service, "17116.23", "1000.00") == D("18116.23")
