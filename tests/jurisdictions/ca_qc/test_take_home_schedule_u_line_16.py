"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 16, as the Quebec take-home manifest
part wires it.

Schedule U line 16 "Amount from line 11 or line 15, whichever is less": the QPP contribution amount
of Part B.
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
    SCHEDULE_U_LINE_16,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS

D = Decimal

PARTS = (
    *TP1_INCOME_PARTS,
    "tp1_schedule_u_line_10_base.yaml",
    "tp1_schedule_u_line_10.yaml",
    "tp1_schedule_u_line_12_base.yaml",
    "tp1_schedule_u_line_11.yaml",
    "tp1_schedule_u_line_12.yaml",
    "tp1_schedule_u_line_13.yaml",
    "tp1_schedule_u_line_14.yaml",
    "tp1_schedule_u_line_14_1.yaml",
    "tp1_schedule_u_line_14_3.yaml",
    "tp1_schedule_u_line_14_4.yaml",
    "tp1_schedule_u_line_15.yaml",
    "tp1_schedule_u_line_16.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_schedule_u
      required: true
      exports:
        - ca-qc/schedule_u_line_16
    capabilities: []
    """)


def schedule_u(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The Schedule U worksheet for a salary."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    )["ca-qc/tp1_schedule_u"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "165.00"), ("70000", "665.00"), ("200000", "678.00")],
)
def test_line_16_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_16).value

    assert str(value) == expected


def test_a_salary_below_the_exemption_gives_a_negative_figure(
    take_home_service: TakeHomeService,
) -> None:
    """The form prints no "if negative, enter 0" on this line, so the figure is signed."""
    assert str(schedule_u(take_home_service, "3000").get(SCHEDULE_U_LINE_16).value) == "-5.00"
