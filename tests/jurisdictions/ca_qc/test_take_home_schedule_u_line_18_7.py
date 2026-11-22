"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 18.7, as the Quebec take-home manifest
part wires it.

Schedule U line 18.7 "Subtract line 18.6 from line 18.5. If the result is negative, enter 0": line
18.5 (line 98.1) less line 18.6 (line 14.1), not below 0.
The salary is the starting input; the TP-1 figures that Schedule U reads are plain starting
inputs here, as in the 5005-R tests. The expected figures are hand-computed from the printed
lines, not an official example.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_U_LINE_18_7,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS

D = Decimal

PARTS = (
    *TP1_INCOME_PARTS,
    "tp1_schedule_u_line_18_5.yaml",
    "tp1_schedule_u_line_14_1.yaml",
    "tp1_schedule_u_line_18_7.yaml",
)

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
        - ca-qc/schedule_u_line_18_7
    capabilities: []
    """)


def schedule_u(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The Schedule U worksheet for a salary."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        ),
    )["ca-qc/tp1_schedule_u"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "0.00"), ("200000", "9900.00")],
)
def test_line_18_7_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_18_7).value

    assert str(value) == expected
