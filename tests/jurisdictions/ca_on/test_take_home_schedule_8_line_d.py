"""Schedule 8 Part 2 line D, from the Ontario take-home manifest's own part file.

Line D "Your additional maximum pensionable earnings for 2025 (maximum $81,200)" is the row of the
monthly proration table for the months on line A. The part file is composed here under a
test-local header and form declaration (the real ones belong to the manifest's other parts), with
the line A input as the manifest declares it: optional, "12" when left out.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog import (
    CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_MONTHS,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

ONTARIO = JurisdictionCode("CA-ON")
PART = "schedule_8_line_d.yaml"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/cpp_months
    required: false
    default: "12"
    basis: Enter "12" on line A below unless any of the following conditions apply
outputs:
  - ca/cpp_months
"""
FORM = """\
form:
  name: ca/schedule_8
  required: true
  exports:
    - ca/cpp_additional_maximum_pensionable_earnings
"""


def line_d(take_home_service: TakeHomeService, *starting: Artifact[int]) -> Decimal:
    service = take_home_service(HEADER, FORM, PART)
    (worksheet,) = service.compute(ONTARIO, 2025, *starting)["ca/schedule_8"]
    return worksheet.get(CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS).value


def test_line_d_is_the_twelve_month_figure_when_line_a_is_left_out(
    take_home_service: TakeHomeService,
) -> None:
    assert line_d(take_home_service) == Decimal("81200.00")


def test_line_d_is_the_row_for_the_months_on_line_a(take_home_service: TakeHomeService) -> None:
    assert line_d(take_home_service, Artifact(CPP_MONTHS, 5)) == Decimal("33833.33")
