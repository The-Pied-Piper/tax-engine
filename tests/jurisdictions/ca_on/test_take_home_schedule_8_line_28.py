"""Schedule 8 (5000-S8, 2025) Part 3 line 28, as the Ontario take-home manifest part wires it.

Form text: Line 28: Line 26 plus line 27 (CRA 5000-S8 2025). The line's export is
`ca/schedule_8_cpp_enhanced_contributions_on_return`, which carries to T1 line 22215.

Lines 26 and 27 are pure copies of lines 12 and 22, so the part sums lines 12 and 22 directly.
The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them, and lines 12 and 22 are plain inputs because the sibling
line parts are separate tickets. The figures are the ticket's worked cases: a $70,000 salary
(line 12 is 665.00, line 22 is 0) and a $90,000 salary (line 12 is 678.00, line 22 is 396.00).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import (
    CPP_PART_3_LINE_12,
    CPP_PART_3_LINE_22,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "schedule_8_line_28.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/cpp_part_3_line_12
        required: true
      - name: ca/cpp_part_3_line_22
        required: true
    outputs:
      - ca/cpp_part_3_line_12
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/schedule_8_cpp_enhanced_contributions_on_return
    """)


def line_28(take_home_service: TakeHomeService, line_12: str, line_22: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(CPP_PART_3_LINE_12, D(line_12)),
        Artifact(CPP_PART_3_LINE_22, D(line_22)),
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value


def test_line_28_is_line_12_when_line_22_is_zero(take_home_service: TakeHomeService) -> None:
    assert line_28(take_home_service, "665.00", "0") == D("665.00")


def test_line_28_is_line_12_plus_line_22(take_home_service: TakeHomeService) -> None:
    assert line_28(take_home_service, "678.00", "396.00") == D("1074.00")


def test_line_28_is_zero_when_both_lines_are_zero(take_home_service: TakeHomeService) -> None:
    assert line_28(take_home_service, "0", "0") == D("0")


def test_line_28_applies_no_rounding(take_home_service: TakeHomeService) -> None:
    assert line_28(take_home_service, "0.01", "0.02") == D("0.03")
