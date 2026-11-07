"""ON428 (2025) line 35, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 35: Add lines 31 to 34." Line 35 is one
core/sum over line 31 alone (`ca-on/on428_credits_with_disability_line_31`). Lines 32 to 34 are
left out because the take-home filer never has them. Line 31 comes from another part, so this test
declares it as the single input of its header and loads the take-home folder's `on428_line_35.yaml`
beside it. The output is `ca-on/on428_credits_with_transfers_line_35`, exported by the form.
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
LINE_31 = "ca-on/on428_credits_with_disability_line_31"
LINE_35 = "ca-on/on428_credits_with_transfers_line_35"
PART = "on428_line_35.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_31}
    required: true
outputs:
  - {LINE_31}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_35}
capabilities: []
"""


def _line_35(take_home_service: TakeHomeService, line_31: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_31), D(line_31)),
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_35)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_31", "line_35"),
    [
        # A $20,000 salary: line 31 is 13,891.75, so line 35 is 13,891.75.
        ("13891.75", "13891.75"),
        # A $70,000 salary: line 31 is 17,116.23, so line 35 is 17,116.23.
        ("17116.23", "17116.23"),
        # A $150,000 salary: line 31 is 17,180.58, so line 35 is 17,180.58.
        ("17180.58", "17180.58"),
        # No amount on line 31, so line 35 is 0.
        ("0", "0"),
    ],
)
def test_line_35_is_line_31_alone(
    take_home_service: TakeHomeService, line_31: str, line_35: str
) -> None:
    assert _line_35(take_home_service, line_31) == D(line_35)
