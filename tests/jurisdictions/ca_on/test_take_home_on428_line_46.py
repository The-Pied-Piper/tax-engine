"""ON428 (2025) line 46, credit amounts at the Ontario credit rate, computed from the real part file
through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 45: Ontario non-refundable tax credit rate 5.05% /
Line 46 and line 58840: Line 44 multiplied by the percentage from line 45 =". Line 45 is a printed
rate, held in the `ca-on/credit_rate` dataset, so line 46 is one calculation: 5.05% of line 44,
rounded half-up to the cent. The input is `ca-on/on428_total_credit_amounts_line_44` (line 44),
produced by another part, so this test declares it as an input in a header of its own and loads
the take-home folder's `on428_line_46.yaml` beside it. The output is
`ca-on/on428_credit_amounts_at_credit_rate_line_46`, exported by the form.
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
LINE_44 = "ca-on/on428_total_credit_amounts_line_44"
LINE_46 = "ca-on/on428_credit_amounts_at_credit_rate_line_46"
PART = "on428_line_46.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_44}
    required: true
outputs:
  - {LINE_44}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_46}
capabilities: []
"""


def _line_46(take_home_service: TakeHomeService, line_44: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_44), D(line_44)),
    )["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_46)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_44", "line_46"),
    [
        # A $20,000 salary: line 44 is 13,891.75, and 5.05% of it is 701.53.
        ("13891.75", "701.53"),
        # A $70,000 salary: line 44 is 17,116.23, and 5.05% of it is 864.37.
        ("17116.23", "864.37"),
        # A $150,000 salary: line 44 is 17,180.58, and 5.05% of it is 867.62.
        ("17180.58", "867.62"),
        # Line 44 is 0, so line 46 is 0.
        ("0", "0.00"),
        # 10.89 x 5.05% = 0.549945, rounded to the nearest cent, 0.55.
        ("10.89", "0.55"),
        # 10.80 x 5.05% = 0.5454, rounded to the nearest cent, 0.55.
        ("10.80", "0.55"),
        # 0.10 x 5.05% = 0.00505, a tie, rounded half-up to 0.01.
        ("0.10", "0.01"),
        # 0.09 x 5.05% = 0.004545, rounded down to 0.00.
        ("0.09", "0.00"),
    ],
)
def test_line_46_is_5_05_percent_of_line_44(
    take_home_service: TakeHomeService, line_44: str, line_46: str
) -> None:
    assert _line_46(take_home_service, line_44) == D(line_46)
