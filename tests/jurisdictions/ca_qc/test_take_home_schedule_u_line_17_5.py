"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 17.5, as the Quebec take-home manifest
part wires it.

Schedule U line 17.5 "Add lines 17.3 and 17.4": the excess over the base contribution plus the
additional QPP contribution (TP-1 line 98.2), rounded half-up to the cent.
The salary is the starting input; the TP-1 figures that Schedule U reads (lines 98, 98.1 and 98.2)
are plain starting inputs here, as in the 5005-R tests. The expected figures are hand-computed from
the printed lines, not an official example.
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
    SCHEDULE_U_LINE_17_5,
    TP1_ADDITIONAL_QPP_CONTRIBUTION_GIVEN_LINE_98_2,
    TP1_QPP_CONTRIBUTION_GIVEN_LINE_98,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS

D = Decimal

PARTS = (
    *TP1_INCOME_PARTS,
    "tp1_schedule_u_line_17.yaml",
    "tp1_schedule_u_line_17_4.yaml",
    "tp1_schedule_u_line_12_base.yaml",
    "tp1_schedule_u_line_12.yaml",
    "tp1_schedule_u_line_13.yaml",
    "tp1_schedule_u_line_14.yaml",
    "tp1_schedule_u_line_14_1.yaml",
    "tp1_schedule_u_line_14_3.yaml",
    "tp1_schedule_u_line_14_4.yaml",
    "tp1_schedule_u_line_17_2.yaml",
    "tp1_schedule_u_line_17_3.yaml",
    "tp1_schedule_u_line_17_5.yaml",
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
        - ca-qc/schedule_u_line_17_5
    capabilities: []
    """)


def schedule_u(
    take_home_service: TakeHomeService,
    salary: str,
    line_98: str | None = None,
    line_98_2: str | None = None,
) -> Worksheet:
    """The Schedule U worksheet for a salary, and for line 98 and 98.2 figures other than the
    salary's."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        *([Artifact(TP1_QPP_CONTRIBUTION_GIVEN_LINE_98, D(line_98))] if line_98 else []),
        *(
            [Artifact(TP1_ADDITIONAL_QPP_CONTRIBUTION_GIVEN_LINE_98_2, D(line_98_2))]
            if line_98_2
            else []
        ),
    )["ca-qc/tp1_schedule_u"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "0.00"), ("200000", "396.00")],
)
def test_line_17_5_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_17_5).value

    assert str(value) == expected


def test_line_17_5_adds_the_excess_and_the_additional_contribution(
    take_home_service: TakeHomeService,
) -> None:
    """Line 17.3 of 44.00 (line 98 of 1,100.00) plus line 17.4 of 396.00."""
    sheet = schedule_u(take_home_service, "20000", "1100.00", "396.00")

    assert str(sheet.get(SCHEDULE_U_LINE_17_5).value) == "440.00"


def test_a_salary_below_the_exemption_follows_the_printed_lines(
    take_home_service: TakeHomeService,
) -> None:
    """Line 14 is floored at 0 below the exemption (owner's ruling), so line 17.2 and line 17.3 are 0
    and line 17.4 is 0."""
    assert str(schedule_u(take_home_service, "3000").get(SCHEDULE_U_LINE_17_5).value) == "0.00"
