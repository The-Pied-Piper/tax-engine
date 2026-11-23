"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 14.1, as the Quebec take-home manifest
part wires it.

Schedule U line 14.1 "Maximum pensionable earnings": the printed $71,300 of the instructions for
Part B ("enter $71,300", when none of the situations of Table 1 applied), claimed whole.
The salary is the starting input; the TP-1 figures that Schedule U reads (lines 98 and 98.1) are
plain starting inputs here, as in the 5005-R tests. The expected figures are hand-computed from the
printed lines, not an official example.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_U_MAXIMUM_PENSIONABLE_EARNINGS_LINE_14_1,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = ("tp1_schedule_u_line_14_1.yaml",)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_schedule_u
      required: true
      exports:
        - ca-qc/schedule_u_maximum_pensionable_earnings_line_14_1
    capabilities: []
    """)


def schedule_u(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The Schedule U worksheet for a salary."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025)
    )["ca-qc/tp1_schedule_u"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "71300.00"), ("70000", "71300.00"), ("200000", "71300.00")],
)
def test_line_14_1_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = (
        schedule_u(take_home_service, salary)
        .get(SCHEDULE_U_MAXIMUM_PENSIONABLE_EARNINGS_LINE_14_1)
        .value
    )

    assert str(value) == expected
