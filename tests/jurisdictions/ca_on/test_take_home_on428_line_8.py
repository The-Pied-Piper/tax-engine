"""ON428 (2025) line 8, Ontario tax on taxable income, computed from the real part file through the
real engine.

Form text (Form ON428, CRA 5006-c-25e.txt, repo copy docs/cra-forms-2025/5006-c-25e.txt): "Line 8:
Line 6 plus line 7 Ontario tax on taxable income =".

Line 8 is one sum, core/sum of line 6 (`ca-on/on428_excess_times_column_rate_line_6`) and line 7
(`ca-on/on428_tax_at_column_start_line_7`). Both lines are required inputs: the take-home calculator
always produces them. The output is `ca-on/on428_tax_on_taxable_income_line_8`, exported by the
form. The sum has no rounding step: line 6 is already rounded to the cent and line 7 is a printed
amount in cents, so their sum is exact.

This test declares lines 6 and 7 as the inputs of its header and loads the take-home folder's
`on428_line_8.yaml` beside it. The inputs are given directly, as Artifacts, so this test does not
compose the salary or the parts that produce lines 6 and 7; those are pinned by their own tests.

Figures (worked, hand computed; the line 6 and line 7 tests pin the same inputs): line 6 is
1,001.67, 1,505.08 and 4,815.65, and line 7 is 0.00, 2,670.74 and 7,510.09, at a $20,000, $70,000
and $150,000 salary; so line 8 is 1,001.67, 4,175.82 and 12,325.74.
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
LINE_6 = "ca-on/on428_excess_times_column_rate_line_6"
LINE_7 = "ca-on/on428_tax_at_column_start_line_7"
LINE_8 = "ca-on/on428_tax_on_taxable_income_line_8"
PART = "on428_line_8.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_6}
    required: true
  - name: {LINE_7}
    required: true
outputs:
  - {LINE_6}
  - {LINE_7}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_8}
capabilities: []
"""


def _line_8(take_home_service: TakeHomeService, line_6: str, line_7: str) -> Decimal:
    kinds = bundled_kinds()
    given = [
        Artifact(kinds.kind(LINE_6), D(line_6)),
        Artifact(kinds.kind(LINE_7), D(line_7)),
    ]
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_8)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_6", "line_7", "line_8"),
    [
        # A $20,000 salary: line 6 is 1,001.67 and line 7 is 0.00, so line 8 is 1,001.67.
        ("1001.67", "0.00", "1001.67"),
        # A $70,000 salary: line 6 is 1,505.08 and line 7 is 2,670.74, so line 8 is 4,175.82.
        ("1505.08", "2670.74", "4175.82"),
        # A $150,000 salary: line 6 is 4,815.65 and line 7 is 7,510.09, so line 8 is 12,325.74.
        ("4815.65", "7510.09", "12325.74"),
        # A zero line 6 and a zero line 7 (a salary of zero) give zero.
        ("0.00", "0.00", "0.00"),
        # A cents case: 1,001.67 plus 0.01 is 1,001.68.
        ("1001.67", "0.01", "1001.68"),
        # No rounding step: the sum of two cent amounts is exact, 0.01 plus 0.02 is 0.03.
        ("0.01", "0.02", "0.03"),
    ],
)
def test_line_8_is_line_6_plus_line_7(
    take_home_service: TakeHomeService, line_6: str, line_7: str, line_8: str
) -> None:
    assert _line_8(take_home_service, line_6, line_7) == D(line_8)
