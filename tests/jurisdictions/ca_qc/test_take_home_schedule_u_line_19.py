"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 19, as the Quebec take-home manifest
part wires it.

Schedule U line 19 "Subtract line 18.9 from line 18.8. If the result is negative, enter 0": line
18.8 less line 18.9 (line 14.1), not below 0.
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
    SCHEDULE_U_LINE_19,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
    "tp1_schedule_u_line_14_1.yaml",
    "tp1_schedule_u_line_18_8.yaml",
    "tp1_schedule_u_line_19.yaml",
)

# The TP-1 figures that Schedule U reads, as the TP-1 income steps give them for each salary.


HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
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
        - ca-qc/schedule_u_line_19
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
    [("20000", "9900.00"), ("70000", "9900.00"), ("200000", "9900.00")],
)
def test_line_19_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_19).value

    assert str(value) == expected
