"""Schedule 8 (5000-S8, 2025) Part 2 line E, the maximum basic exemption, as the Ontario
manifest part wires it: the row of the monthly proration table for the months on line A.

The manifest part is loaded from the package. The header, the form's export and the months
input (line A, "Enter "12" on line A below unless any of the following conditions apply") are
made up here, because the shared scaffold owns them. The figure is the printed 12-month row,
$3,500.00, whatever the salary: no salary reaches this line.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import CPP_BASIC_EXEMPTION, CPP_MONTHS
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "schedule_8_line_e.yaml"

SCAFFOLD = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/cpp_months
        required: false
        default: "12"
        basis: 'Enter "12" on line A below unless any of the following conditions apply'
    outputs:
      - ca/cpp_months
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/cpp_basic_exemption
    """)


def line_e(take_home_service: TakeHomeService, *artifacts: Artifact[int]) -> Decimal:
    worksheets = take_home_service(SCAFFOLD, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *artifacts
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(CPP_BASIC_EXEMPTION).value


def test_line_e_is_3500_for_the_default_twelve_months(take_home_service: TakeHomeService) -> None:
    assert line_e(take_home_service) == D("3500.00")


def test_line_e_is_3500_for_twelve_months_given(take_home_service: TakeHomeService) -> None:
    assert line_e(take_home_service, Artifact(CPP_MONTHS, 12)) == D("3500.00")


def test_line_e_is_the_printed_row_for_fewer_months(take_home_service: TakeHomeService) -> None:
    assert line_e(take_home_service, Artifact(CPP_MONTHS, 7)) == D("2041.67")
