"""ON428 (2025) line 6, line 4 multiplied by the percentage from line 5, computed from the real part
file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): each
Part A column prints "Line 6: Line 4 multiplied by the percentage from line 5 =". Line 5 is a
rate held as a fraction (0.0915 is 9.15%), so line 6 is line 4 times line 5, with no division by
100.

Line 4 and line 5 are given directly as test-header inputs, as Artifacts, so this test does not
compose the T1 lines, the salary or the line 1 to line 5 parts. Line 6 is one
`core/multiply_by_rate` over line 4 and line 5, with the shared `ca-on/cent_rounding` dataset,
output `ca-on/on428_excess_times_column_rate_line_6`, in the one part `on428_line_6.yaml`. The
product is rounded half-up to the cent once, by that dataset's rule. The form declaration is
test-local: it exports line 6.

Figures (worked, hand computed): line 4 is 19,835.00, 16,449.00 and 43,151.00 at a $20,000, $70,000
and $150,000 salary; line 5 is 0.0505, 0.0915 and 0.1116; so line 6 is 1,001.67, 1,505.08 and
4,815.65 (19,835 × 0.0505 = 1,001.6675; 16,449 × 0.0915 = 1,505.0835; 43,151 × 0.1116 = 4,815.6516).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
CODE = JurisdictionCode("CA-ON")
FORM_NAME = "ca-on/on428"
LINE_4 = "ca-on/on428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-on/on428_bracket_column_rate_line_5"
LINE_6 = "ca-on/on428_excess_times_column_rate_line_6"
PART = "on428_line_6.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_4}
    required: true
  - name: {LINE_5}
    required: true
outputs:
  - {LINE_4}
  - {LINE_5}
capabilities: []
"""

FORM = f"""\
form:
  name: {FORM_NAME}
  required: true
  exports:
    - {LINE_6}
capabilities: []
"""


def _line_6(take_home_service: TakeHomeService, line_4: str, line_5: str) -> Decimal:
    kinds = bundled_kinds()
    given = [
        Artifact(kinds.kind(LINE_4), D(line_4)),
        Artifact(kinds.kind(LINE_5), D(line_5)),
    ]
    worksheet = take_home_service(HEADER, FORM, PART).compute(CODE, 2025, *given)[FORM_NAME][0]
    value = worksheet.get(kinds.kind(LINE_6)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_4", "line_5", "expected"),
    [
        # The worked figures for a $20,000 salary: 19,835.00 at 5.05% is 1,001.6675, to the cent.
        ("19835.00", "0.0505", "1001.67"),
        # The worked figures for a $70,000 salary: 16,449.00 at 9.15% is 1,505.0835, to the cent.
        ("16449.00", "0.0915", "1505.08"),
        # The worked figures for a $150,000 salary: 43,151.00 at 11.16% is 4,815.6516, to the cent.
        ("43151.00", "0.1116", "4815.65"),
    ],
)
def test_line_6_is_line_4_times_the_fraction_of_line_5_to_the_cent(
    take_home_service: TakeHomeService, line_4: str, line_5: str, expected: str
) -> None:
    assert _line_6(take_home_service, line_4, line_5) == D(expected)


@pytest.mark.parametrize(
    ("line_4", "line_5", "expected"),
    [
        # A product exactly on the half cent rounds up: 1.00 × 0.005 is 0.005, which is 0.01.
        ("1.00", "0.005", "0.01"),
        # A product just under the half cent rounds down: 1.00 × 0.0049 is 0.0049, which is 0.00.
        ("1.00", "0.0049", "0.00"),
        # A line 4 of zero (the lower bound of column 1 at a zero income) gives zero.
        ("0.00", "0.0915", "0.00"),
    ],
)
def test_line_6_rounds_half_up_to_the_cent_once(
    take_home_service: TakeHomeService, line_4: str, line_5: str, expected: str
) -> None:
    assert _line_6(take_home_service, line_4, line_5) == D(expected)


def test_the_kind_is_registered_and_not_negative() -> None:
    kind = bundled_kinds().kind(LINE_6)

    assert kind.identifier == LINE_6
    assert non_negative(kind)
