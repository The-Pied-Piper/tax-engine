"""Schedule 8 (5000-S8, 2025) Part 3 line 4, the earnings subject to the second additional
contribution, as the Ontario manifest part wires it.

The manifest part is loaded from the package. The header, the form's export and the two
upstream figures are made up here, because other parts own them: line 2 and line B (the
amount copied on line 3). Line 4 reads: Line 2 minus line 3 (if negative, enter "0").
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import (
    CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_PART_3_LINE_2,
    CPP_PART_3_LINE_4,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "schedule_8_line_4.yaml"

SCAFFOLD = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/cpp_part_3_line_2
        required: true
      - name: ca/cpp_maximum_pensionable_earnings
        required: true
    outputs:
      - ca/cpp_part_3_line_2
      - ca/cpp_maximum_pensionable_earnings
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/cpp_part_3_line_4
    """)


def line_4(take_home_service: TakeHomeService, line_2: str, line_b: str) -> Decimal:
    worksheets = take_home_service(SCAFFOLD, FORM, PART).compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(CPP_PART_3_LINE_2, D(line_2)),
        Artifact(CPP_MAXIMUM_PENSIONABLE_EARNINGS, D(line_b)),
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(CPP_PART_3_LINE_4).value


def test_line_4_is_zero_when_line_2_is_below_line_b(take_home_service: TakeHomeService) -> None:
    assert line_4(take_home_service, "70000.00", "71300.00") == D("0")


def test_line_4_is_line_2_minus_line_b_above_line_b(take_home_service: TakeHomeService) -> None:
    assert line_4(take_home_service, "81200.00", "71300.00") == D("9900.00")


def test_line_4_is_zero_when_line_2_equals_line_b(take_home_service: TakeHomeService) -> None:
    assert line_4(take_home_service, "71300.00", "71300.00") == D("0")


def test_line_4_is_one_cent_just_above_line_b(take_home_service: TakeHomeService) -> None:
    assert line_4(take_home_service, "71300.01", "71300.00") == D("0.01")
