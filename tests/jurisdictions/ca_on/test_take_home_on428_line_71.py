"""ON428 (2025) line 71, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 71: Line 69 minus line 70 (if negative, enter
"0") =". Line 71 is one core/subtract_not_below_zero: line 69
(`ca-on/on428_tax_with_surtax_line_69`, required) less line 70, the Ontario dividend tax credit from
line 57
(`ca-on/on428_dividend_tax_credit_line_57`). Line 70 is a copy of line 57, so the part reads line 57
directly, and line 57 is an optional input with blank fallback 0. A salary-only caller has no
dividend income, so a request that leaves line 57 out is read as blank, and the line 71 part reads
that blank as 0. The output is `ca-on/on428_tax_after_dividend_credit_line_71`, exported by the
form.

Line 69 is built by another part, so this test declares it as a required input of its header as a
temporary stand-in. Line 57 is declared as its real inputs part declares it, and the test loads the
test data folder's `on428_line_71.yaml` beside it.
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
LINE_69 = "ca-on/on428_tax_with_surtax_line_69"
LINE_57 = "ca-on/on428_dividend_tax_credit_line_57"
LINE_71 = "ca-on/on428_tax_after_dividend_credit_line_71"
PART = "on428_line_71.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_69}
    required: true
  - name: {LINE_57}
    required: false
    default: null
    basis: 'Line 57 and line and line 61520: Ontario dividend tax credit (use Worksheet ON428)'
outputs:
  - {LINE_69}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_71}
capabilities: []
"""


def _line_71(take_home_service: TakeHomeService, line_69: str, line_57: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_69), D(line_69))]
    if line_57 is not None:
        given.append(Artifact(kinds.kind(LINE_57), D(line_57)))
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(LINE_71)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_69", "line_71"),
    [
        # A $20,000 salary: line 69 is 300.14 and line 57 is blank (0), so line 71 is 300.14.
        ("300.14", "300.14"),
        # A $70,000 salary: line 69 is 3,311.45 and line 57 is blank (0), so line 71 is 3,311.45.
        ("3311.45", "3311.45"),
        # A $150,000 salary: line 69 is 14,102.14 and line 57 is blank (0), so line 71 is 14,102.14.
        ("14102.14", "14102.14"),
    ],
)
def test_line_71_is_line_69_when_line_57_is_left_out(
    take_home_service: TakeHomeService, line_69: str, line_71: str
) -> None:
    assert _line_71(take_home_service, line_69, None) == D(line_71)


def test_line_71_is_line_69_minus_line_57(take_home_service: TakeHomeService) -> None:
    # Line 69 is 3,311.45 and line 57 is 1,000.00, so line 71 is 2,311.45.
    assert _line_71(take_home_service, "3311.45", "1000.00") == D("2311.45")


@pytest.mark.parametrize(
    ("line_69", "line_57", "line_71"),
    [
        # Line 57 above line 69 gives "0", as the form says.
        ("300.14", "1000.00", "0"),
        # Exactly equal: the difference is zero.
        ("3311.45", "3311.45", "0"),
    ],
)
def test_line_71_is_0_when_line_57_is_not_less_than_line_69(
    take_home_service: TakeHomeService, line_69: str, line_57: str, line_71: str
) -> None:
    assert _line_71(take_home_service, line_69, line_57) == D(line_71)
