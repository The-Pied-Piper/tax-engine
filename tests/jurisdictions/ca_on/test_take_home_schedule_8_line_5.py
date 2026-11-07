"""Schedule 8 (5000-S8, 2025) Part 3 line 5, as the Ontario take-home manifest part wires it.

Form text: Line 5: Line 2 minus line 4 (if negative, enter "0") (CRA 5000-S8 2025).

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them, and lines 2 and 4 are plain inputs because the sibling line
parts are separate tickets. The figures are the ticket's worked cases: a $70,000 salary (line 2 is
70000.00, line 4 is 0) and a $90,000 salary (line 2 is 81200.00, line 4 is 9900.00).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import (
    CPP_PART_3_LINE_2,
    CPP_PART_3_LINE_4,
    CPP_PART_3_LINE_5,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "schedule_8_line_5.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/cpp_part_3_line_2
        required: true
      - name: ca/cpp_part_3_line_4
        required: true
    outputs:
      - ca/cpp_part_3_line_2
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/cpp_part_3_line_5
    """)


def line_5(take_home_service: TakeHomeService, line_2: str, line_4: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(CPP_PART_3_LINE_2, D(line_2)),
        Artifact(CPP_PART_3_LINE_4, D(line_4)),
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(CPP_PART_3_LINE_5).value


def test_line_5_is_line_2_when_line_4_is_zero(take_home_service: TakeHomeService) -> None:
    assert line_5(take_home_service, "70000.00", "0") == D("70000.00")


def test_line_5_is_line_2_minus_line_4(take_home_service: TakeHomeService) -> None:
    assert line_5(take_home_service, "81200.00", "9900.00") == D("71300.00")


def test_line_5_is_zero_when_line_4_exceeds_line_2(take_home_service: TakeHomeService) -> None:
    assert line_5(take_home_service, "100", "250") == D("0")
