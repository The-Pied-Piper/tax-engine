"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, line 13, as the Quebec take-home manifest
part wires it.

Schedule U line 13 "Personal QPP exemption": the printed $3,500 of the instructions for Part B
("enter $3,500", when none of the situations of Table 1 applied), claimed whole.
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
    SCHEDULE_U_PERSONAL_QPP_EXEMPTION_LINE_13,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = ("tp1_schedule_u_line_13.yaml",)

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
        - ca-qc/schedule_u_personal_qpp_exemption_line_13
    capabilities: []
    """)


def schedule_u(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The Schedule U worksheet for a salary."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )["ca-qc/tp1_schedule_u"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "3500.00"), ("70000", "3500.00"), ("200000", "3500.00")],
)
def test_line_13_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = (
        schedule_u(take_home_service, salary).get(SCHEDULE_U_PERSONAL_QPP_EXEMPTION_LINE_13).value
    )

    assert str(value) == expected
