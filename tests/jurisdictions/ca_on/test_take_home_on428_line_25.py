"""ON428 (2025) line 25, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 25: Line 18 plus line 24 =". Line 25 is one
sum, core/sum of line 18 (the personal amounts subtotal,
`ca-on/on428_personal_amounts_subtotal_line_18`) and line 24 (the CPP and EI credit amounts,
`ca-on/on428_cpp_ei_credit_amounts_line_24`). Both come from other parts, so this test declares
them as the two inputs of its header and loads the take-home folder's `on428_line_25.yaml` beside
it. The output is `ca-on/on428_credits_subtotal_line_25`, exported by the form.
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
LINE_18 = "ca-on/on428_personal_amounts_subtotal_line_18"
LINE_24 = "ca-on/on428_cpp_ei_credit_amounts_line_24"
LINE_25 = "ca-on/on428_credits_subtotal_line_25"
PART = "on428_line_25.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_18}
    required: true
  - name: {LINE_24}
    required: true
outputs:
  - {LINE_18}
  - {LINE_24}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_25}
capabilities: []
"""


def _line_25(take_home_service: TakeHomeService, line_18: str, line_24: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_18), D(line_18)),
        Artifact(kinds.kind(LINE_24), D(line_24)),
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_25)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_18", "line_24", "line_25"),
    [
        # A $20,000 salary: line 18 is 12,747.00 and line 24 is 1,144.75, so line 25 is 13,891.75.
        ("12747.00", "1144.75", "13891.75"),
        # A $70,000 salary: line 18 is 12,747.00 and line 24 is 4,369.23, so line 25 is 17,116.23.
        ("12747.00", "4369.23", "17116.23"),
        # A $150,000 salary: line 18 is 12,747.00 and line 24 is 4,433.58, so line 25 is 17,180.58.
        ("12747.00", "4433.58", "17180.58"),
    ],
)
def test_line_25_is_line_18_plus_line_24(
    take_home_service: TakeHomeService, line_18: str, line_24: str, line_25: str
) -> None:
    assert _line_25(take_home_service, line_18, line_24) == D(line_25)
