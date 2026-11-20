"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 22, as the Quebec take-home manifest
part wires it.

Schedule U line 22 "Amount from line 17.5 or line 21, whichever is less".
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
    SCHEDULE_U_LINE_22,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS

D = Decimal

PARTS = (
    *TP1_INCOME_PARTS,
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
    "tp1_schedule_u_line_17_2.yaml",
    "tp1_schedule_u_line_17_3.yaml",
    "tp1_schedule_u_line_17_5.yaml",
    "tp1_schedule_u_line_18_7.yaml",
    "tp1_schedule_u_line_18_8.yaml",
    "tp1_schedule_u_line_19.yaml",
    "tp1_schedule_u_line_20.yaml",
    "tp1_schedule_u_line_21.yaml",
    "tp1_schedule_u_line_22.yaml",
)

# The TP-1 figures that Schedule U reads, as the TP-1 income steps give them for each salary.

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
        - ca-qc/schedule_u_line_22
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
    [("20000", "0.00"), ("70000", "0.00"), ("200000", "396.00")],
)
def test_line_22_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_22).value

    assert str(value) == expected
