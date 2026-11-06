"""Schedule 8 Part 3a line 25, from the Ontario take-home manifest's own part file.

Line 25 "Enter the amount from line 15", and line 15 is the amount from line 11. The part file is
composed here under a test-local header and form declaration (the real ones belong to the
manifest's other parts), with line 11 given as a starting amount because its own part is another
ticket's.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog import (
    CPP_PART_3_LINE_11,
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

ONTARIO = JurisdictionCode("CA-ON")
PART = "schedule_8_line_25.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/cpp_part_3_line_11
    required: true
outputs:
  - ca/cpp_part_3_line_11
"""
FORM = """\
form:
  name: ca/schedule_8
  required: true
  exports:
    - ca/schedule_8_cpp_base_contributions_on_return
"""


def line_25(take_home_service: TakeHomeService, line_11: str) -> Decimal:
    artifact = Artifact(CPP_PART_3_LINE_11, Decimal(line_11))
    (sheet,) = take_home_service(HEADER, FORM, PART).compute(ONTARIO, 2025, artifact)[
        "ca/schedule_8"
    ]
    return sheet.get(SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value


def test_line_25_is_line_11_at_a_70000_salary(take_home_service: TakeHomeService) -> None:
    assert line_25(take_home_service, "3291.75") == Decimal("3291.75")


def test_line_25_is_line_11_at_its_printed_maximum_for_a_90000_salary(
    take_home_service: TakeHomeService,
) -> None:
    assert line_25(take_home_service, "3356.10") == Decimal("3356.10")


def test_line_25_carries_zero_unchanged(take_home_service: TakeHomeService) -> None:
    assert line_25(take_home_service, "0.00") == Decimal("0.00")


def test_line_25_carries_one_cent_unchanged(take_home_service: TakeHomeService) -> None:
    assert line_25(take_home_service, "0.01") == Decimal("0.01")
