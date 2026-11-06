"""Schedule 8 Part 3 line 12, from the Ontario take-home manifest's own part file.

Line 12 "amount from line 7 multiplied by 1% (maximum $678.00)": line 7 is given as a starting
amount, since its own part is another ticket's. The part file is composed here under a test-local
header and form declaration (the real ones belong to the manifest's other parts).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog import (
    CPP_PART_3_LINE_7,
    CPP_PART_3_LINE_12,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

ONTARIO = JurisdictionCode("CA-ON")
PART = "schedule_8_line_12.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/cpp_part_3_line_7
    required: true
outputs:
  - ca/cpp_part_3_line_7
"""
FORM = """\
form:
  name: ca/schedule_8
  required: true
  exports:
    - ca/cpp_part_3_line_12
"""


def line_12(take_home_service: TakeHomeService, line_7: str) -> Decimal:
    service = take_home_service(HEADER, FORM, PART)
    (worksheet,) = service.compute(
        ONTARIO,
        2025,
        Artifact(CPP_PART_3_LINE_7, Decimal(line_7)),
    )["ca/schedule_8"]
    return worksheet.get(CPP_PART_3_LINE_12).value


@pytest.mark.parametrize(
    ("line_7", "expected"),
    [
        # The $70,000 salary: line 7 is 70,000 less 3,500, which is 66,500; 1% of it is 665.00.
        ("66500.00", "665.00"),
        # The $90,000 salary: line 7 is the printed maximum of 67,800; 1% of it is 678.00.
        ("67800.00", "678.00"),
        # A line 7 above the printed maximum is still the maximum.
        ("70000.00", "678.00"),
        # Nothing on line 7 is nothing on line 12.
        ("0.00", "0.00"),
        # Rounded half-up to the cent: 1% of 0.50 is 0.005, a tie, up to 0.01.
        ("0.50", "0.01"),
        # 1% of 0.49 is 0.0049, down to 0.00.
        ("0.49", "0.00"),
    ],
)
def test_line_12_is_1_percent_of_line_7_to_the_cent_and_at_most_678(
    take_home_service: TakeHomeService, line_7: str, expected: str
) -> None:
    assert line_12(take_home_service, line_7) == Decimal(expected)
