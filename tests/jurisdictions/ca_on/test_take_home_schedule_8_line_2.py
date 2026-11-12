"""Schedule 8 (CPP) Part 3 line 2, computed from the real part file through the real engine.

T1-2025 Schedule 8 (form 5000-S8), Part 3, line 2: "Enter whichever is less: amount from line D of
Part 2 or line 1." (cra-docs/docs/cra-forms-2025/5000-s8-25e.txt). Line D is the additional maximum
pensionable earnings, line 1 the T4 pensionable earnings outside Quebec. Both are produced by other
lines' parts, so this test declares them as inputs in a header of its own and loads the take-home
folder's `schedule_8_line_2.yaml` beside it.
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
LINE_D = "ca/cpp_additional_maximum_pensionable_earnings"
LINE_1 = "ca/t4_cpp_pensionable_earnings_outside_quebec"
LINE_2 = "ca/cpp_part_3_line_2"
PART = "schedule_8_line_2.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_D}
    required: true
  - name: {LINE_1}
    required: true
outputs:
  - {LINE_1}
capabilities: []
"""

FORM = f"""\
form:
  name: ca/schedule_8
  required: true
  exports:
    - {LINE_2}
capabilities: []
"""


def _line_2(take_home_service: TakeHomeService, line_d: str, line_1: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = take_home_service(HEADER, FORM, PART).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_D), D(line_d)),
        Artifact(kinds.kind(LINE_1), D(line_1)),
    )["ca/schedule_8"][0]
    value = worksheet.get(kinds.kind(LINE_2)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_d", "line_1", "line_2"),
    [
        # A $70,000 salary: line 1 is below line D, so line 1.
        ("81200.00", "70000.00", "70000.00"),
        # The $90,000 salary: line 1 is capped at 81,200.00, level with line D.
        ("81200.00", "81200.00", "81200.00"),
        # One cent either side of line D, and nothing.
        ("81200.00", "81199.99", "81199.99"),
        ("81200.00", "0", "0.00"),
        # Line D is the lesser when line 1 is above it.
        ("81200.00", "90000.00", "81200.00"),
    ],
)
def test_line_2_is_the_lesser_of_line_d_and_line_1(
    take_home_service: TakeHomeService, line_d: str, line_1: str, line_2: str
) -> None:
    assert _line_2(take_home_service, line_d, line_1) == D(line_2)
