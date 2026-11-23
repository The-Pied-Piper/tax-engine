"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 23, as the Quebec take-home manifest
part wires it.

Schedule U line 23 "Add lines 22 and 22.1", "Deduction for QPP contributions on employment income":
the figure TP-1 line 248 takes.
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
    SCHEDULE_U_LINE_23,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS

D = Decimal

PARTS = (
    *TP1_INCOME_PARTS,
    "tp1_schedule_u_line_10_base.yaml",
    "tp1_schedule_u_line_10.yaml",
    "tp1_schedule_u_line_12_base.yaml",
    "tp1_schedule_u_line_17.yaml",
    "tp1_schedule_u_line_17_4.yaml",
    "tp1_schedule_u_line_18_5.yaml",
    "tp1_schedule_u_line_12.yaml",
    "tp1_schedule_u_line_13.yaml",
    "tp1_schedule_u_line_14.yaml",
    "tp1_schedule_u_line_14_1.yaml",
    "tp1_schedule_u_line_14_3.yaml",
    "tp1_schedule_u_line_14_4.yaml",
    "tp1_schedule_u_line_11.yaml",
    "tp1_schedule_u_line_15.yaml",
    "tp1_schedule_u_line_16.yaml",
    "tp1_schedule_u_line_17_2.yaml",
    "tp1_schedule_u_line_17_3.yaml",
    "tp1_schedule_u_line_17_5.yaml",
    "tp1_schedule_u_line_18_7.yaml",
    "tp1_schedule_u_line_18_8.yaml",
    "tp1_schedule_u_line_19.yaml",
    "tp1_schedule_u_line_20.yaml",
    "tp1_schedule_u_line_21.yaml",
    "tp1_schedule_u_line_22.yaml",
    "tp1_schedule_u_line_23.yaml",
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
        - ca-qc/schedule_u_line_23
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
    [("20000", "165.00"), ("70000", "665.00"), ("200000", "1074.00")],
)
def test_line_23_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_23).value

    assert str(value) == expected


def test_a_salary_below_the_exemption_follows_the_printed_lines(
    take_home_service: TakeHomeService,
) -> None:
    """At a $3,000 salary line 14 is floored at 0 (owner's ruling), so lines 14.4, 15, 16 and 17.5
    are 0.00, line 21 is 0.00, line 22 is 0.00 and line 23 is 0.00."""
    sheet = schedule_u(take_home_service, "3000")

    assert str(sheet.get(SCHEDULE_U_LINE_23).value) == "0.00"
