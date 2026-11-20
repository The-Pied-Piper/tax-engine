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

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_U_LINE_23,
    TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2,
    TP1_PENSIONABLE_SALARY_LINE_98_1,
    TP1_QPP_CONTRIBUTION_LINE_98,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
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

# The TP-1 figures that Schedule U reads, as the TP-1 income steps give them for each salary.
UPSTREAM_98 = {"20000": "1056.00", "70000": "4256.00", "200000": "4339.20", "3000": "0"}
UPSTREAM_98_2 = {"20000": "0", "70000": "0", "200000": "396.00", "3000": "0"}
UPSTREAM_98_1 = {"20000": "20000", "70000": "70000", "200000": "81200", "3000": "3000"}

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
      - name: ca-qc/tp1_qpp_contribution_line_98
        required: true
      - name: ca-qc/tp1_additional_qpp_contribution_line_98_2
        required: true
      - name: ca-qc/tp1_pensionable_salary_line_98_1
        required: true
    outputs:
      - ca/employment_income
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
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(TP1_QPP_CONTRIBUTION_LINE_98, D(UPSTREAM_98[salary])),
        Artifact(TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2, D(UPSTREAM_98_2[salary])),
        Artifact(TP1_PENSIONABLE_SALARY_LINE_98_1, D(UPSTREAM_98_1[salary])),
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
    """At a $3,000 salary line 14.4 is -500.00, so line 15 and line 16 are -5.00 (the form prints no
    floor on line 14); line 17.5 is 32.00 but line 21 is 0.00, so line 22 is 0.00 and line 23 is
    -5.00."""
    sheet = schedule_u(take_home_service, "3000")

    assert str(sheet.get(SCHEDULE_U_LINE_23).value) == "-5.00"
