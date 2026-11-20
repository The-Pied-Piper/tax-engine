"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 17.3, as the Quebec take-home manifest
part wires it.

Schedule U line 17.3 "Subtract line 17.2 from line 17. If the result is negative, enter 0": the QPP
contribution (TP-1 line 98) less line 17.2, not below 0.
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
    SCHEDULE_U_LINE_17_3,
    TP1_QPP_CONTRIBUTION_GIVEN_LINE_98,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS

D = Decimal

PARTS = (
    *TP1_INCOME_PARTS,
    "tp1_schedule_u_line_17.yaml",
    "tp1_schedule_u_line_12_base.yaml",
    "tp1_schedule_u_line_12.yaml",
    "tp1_schedule_u_line_13.yaml",
    "tp1_schedule_u_line_14.yaml",
    "tp1_schedule_u_line_14_1.yaml",
    "tp1_schedule_u_line_14_3.yaml",
    "tp1_schedule_u_line_14_4.yaml",
    "tp1_schedule_u_line_17_2.yaml",
    "tp1_schedule_u_line_17_3.yaml",
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
        - ca-qc/schedule_u_line_17_3
    capabilities: []
    """)


def schedule_u(
    take_home_service: TakeHomeService, salary: str, line_98: str | None = None
) -> Worksheet:
    """The Schedule U worksheet for a salary, and for a line 98 figure other than the salary's."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        *([Artifact(TP1_QPP_CONTRIBUTION_GIVEN_LINE_98, D(line_98))] if line_98 else []),
    )["ca-qc/tp1_schedule_u"]
    return sheet


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_17_3_is_zero_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    """Line 17 is the contribution line 17.2 recomputes, so the excess is nothing."""
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_17_3).value

    assert str(value) == "0.00"


def test_a_line_98_over_line_17_2_gives_the_excess(take_home_service: TakeHomeService) -> None:
    """Line 98 of 1,100.00 less line 17.2 of 1,056.00."""
    sheet = schedule_u(take_home_service, "20000", "1100.00")

    assert str(sheet.get(SCHEDULE_U_LINE_17_3).value) == "44.00"


def test_a_line_98_under_line_17_2_is_floored_at_zero(take_home_service: TakeHomeService) -> None:
    """Line 98 of 1,000.00 less line 17.2 of 1,056.00 is negative, so the line prints 0."""
    sheet = schedule_u(take_home_service, "20000", "1000.00")

    assert str(sheet.get(SCHEDULE_U_LINE_17_3).value) == "0.00"


def test_a_salary_below_the_exemption_follows_the_printed_lines(
    take_home_service: TakeHomeService,
) -> None:
    """Line 14 is floored at 0 below the exemption (owner's ruling), so line 14.4 and line 17.2 are 0
    and line 17 (0) less it is 0.00."""
    assert str(schedule_u(take_home_service, "3000").get(SCHEDULE_U_LINE_17_3).value) == "0.00"
