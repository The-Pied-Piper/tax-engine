"""Schedule 8 Part 3 line 22, from the Ontario take-home manifest's own part file.

Line 22 "amount from line 4 multiplied by 4% (maximum $396.00)". The part file is composed here
under a test-local header and form declaration (the real ones belong to the manifest's other
parts), with line 4 given as a starting amount because its own part file is not part of this one.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog import CPP_PART_3_LINE_4, CPP_PART_3_LINE_22
from tests.jurisdictions.ca_on.conftest import TakeHomeService

ONTARIO = JurisdictionCode("CA-ON")
PART = "schedule_8_line_22.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: []
"""
FORM = """\
form:
  name: ca/schedule_8
  required: true
  exports:
    - ca/cpp_part_3_line_22
inputs:
  - name: ca/cpp_part_3_line_4
    required: true
"""


def line_22(take_home_service: TakeHomeService, line_4: str) -> Decimal:
    service = take_home_service(HEADER, FORM, PART)
    (worksheet,) = service.compute(ONTARIO, 2025, Artifact(CPP_PART_3_LINE_4, Decimal(line_4)))[
        "ca/schedule_8"
    ]
    return worksheet.get(CPP_PART_3_LINE_22).value


@pytest.mark.parametrize(
    ("line_4", "expected"),
    [
        # 4% of 0.12 is 0.0048, down to nothing.
        ("0.12", "0.00"),
        # 4% of 0.125 is 0.005, a tie, rounded half-up to a cent.
        ("0.125", "0.01"),
        # Mid-band: 4% x 3,700 = 148.00.
        ("3700", "148.00"),
        # Line 4 above its printed maximum cannot take line 22 past $396.00.
        ("10000", "396.00"),
    ],
)
def test_line_22_is_4_percent_of_line_4_at_most_396(
    take_home_service: TakeHomeService, line_4: str, expected: str
) -> None:
    assert line_22(take_home_service, line_4) == Decimal(expected)
