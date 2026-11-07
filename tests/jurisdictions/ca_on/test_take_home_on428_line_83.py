"""ON428 (2025) line 83, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 83: Line 81 minus line 82 (if negative, enter
"0") =". Line 83 is one core/subtract_not_below_zero: line 81
(`ca-on/on428_tax_after_tax_reduction_line_81`, required) less line 82, the provincial foreign tax
credit (`ca-on/on428_provincial_foreign_tax_credit_line_82`, Form T2036). Line 82 is an optional
input with blank fallback 0: a salary-only caller has no foreign tax credit, so a request that
leaves line 82 out is read as blank, and the line 83 part reads that blank as 0. The output is
`ca-on/on428_tax_after_foreign_tax_credit_line_83`, exported by the form.

Line 81 is built by another part, so this test declares it as a required input of its header, as
the ON428 line tests do. Line 82 is declared as its real inputs part
declares it, and the test loads the test data folder's `on428_line_83.yaml` beside it.
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
LINE_81 = "ca-on/on428_tax_after_tax_reduction_line_81"
LINE_82 = "ca-on/on428_provincial_foreign_tax_credit_line_82"
LINE_83 = "ca-on/on428_tax_after_foreign_tax_credit_line_83"
PART = "on428_line_83.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_81}
    required: true
  - name: {LINE_82}
    required: false
    default: null
    basis: 'Line 82: Provincial foreign tax credit (complete Form T2036)'
outputs:
  - {LINE_81}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_83}
capabilities: []
"""


def _line_83(take_home_service: TakeHomeService, line_81: str, line_82: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_81), D(line_81))]
    if line_82 is not None:
        given.append(Artifact(kinds.kind(LINE_82), D(line_82)))
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_83)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_81", "line_83"),
    [
        # A $20,000 salary: line 81 is 12.28 and line 82 is blank (0), so line 83 is 12.28.
        ("12.28", "12.28"),
        # A $70,000 salary: line 81 is 3,311.45 and line 82 is blank (0), so line 83 is 3,311.45.
        ("3311.45", "3311.45"),
        # A $150,000 salary: line 81 is 14,102.14 and line 82 is blank (0), so line 83 is 14,102.14.
        ("14102.14", "14102.14"),
    ],
)
def test_line_83_is_line_81_when_line_82_is_left_out(
    take_home_service: TakeHomeService, line_81: str, line_83: str
) -> None:
    assert _line_83(take_home_service, line_81, None) == D(line_83)


def test_line_83_is_line_81_minus_line_82(take_home_service: TakeHomeService) -> None:
    # Line 81 is 3,311.45 and line 82 is 1,000.00, so line 83 is 2,311.45.
    assert _line_83(take_home_service, "3311.45", "1000.00") == D("2311.45")


@pytest.mark.parametrize(
    ("line_81", "line_82", "line_83"),
    [
        # Line 82 above line 81 gives "0", as the form says.
        ("12.28", "1000.00", "0"),
        # Exactly equal: the difference is zero.
        ("3311.45", "3311.45", "0"),
    ],
)
def test_line_83_is_0_when_line_82_is_not_less_than_line_81(
    take_home_service: TakeHomeService, line_81: str, line_82: str, line_83: str
) -> None:
    assert _line_83(take_home_service, line_81, line_82) == D(line_83)
