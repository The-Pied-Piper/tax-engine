"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 14, as the Quebec take-home manifest
part wires it.

Schedule U line 14 "Subtract line 13 from line 12": the pensionable salary (TP-1 line 98.1) less the
personal QPP exemption. The line prints no floor, so the figure can be negative.
The salary is the starting input; the TP-1 figures that Schedule U reads (lines 98 and 98.1) are
plain starting inputs here, as in the 5005-R tests. The expected figures are hand-computed from the
printed lines, not an official example.
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
    SCHEDULE_U_LINE_14,
    TP1_PENSIONABLE_SALARY_LINE_98_1,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
    "tp1_schedule_u_line_12.yaml",
    "tp1_schedule_u_line_13.yaml",
    "tp1_schedule_u_line_14.yaml",
)

# The TP-1 figures (lines 98 and 98.1) that Schedule U reads, as the TP-1 income steps give them
# for each salary.
UPSTREAM_98_1 = {"20000": "20000", "70000": "70000", "200000": "81200", "3000": "3000"}

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
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
        - ca-qc/schedule_u_line_14
    capabilities: []
    """)


def schedule_u(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The Schedule U worksheet for a salary."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(TP1_PENSIONABLE_SALARY_LINE_98_1, D(UPSTREAM_98_1[salary])),
    )["ca-qc/tp1_schedule_u"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "16500.00"), ("70000", "66500.00"), ("200000", "67800.00")],
)
def test_line_14_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_14).value

    assert str(value) == expected


def test_a_salary_below_the_exemption_gives_a_negative_figure(
    take_home_service: TakeHomeService,
) -> None:
    """The form prints no "if negative, enter 0" on this line, so the figure is signed."""
    assert str(schedule_u(take_home_service, "3000").get(SCHEDULE_U_LINE_14).value) == "-500.00"
