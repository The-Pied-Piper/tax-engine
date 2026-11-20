"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, lines 10 to 16, as one chain.

Lines 11 to 16 are built from the real parts. Lines 10 and 12 take the TP-1 figures of lines 98 and
98.1, which are plain starting inputs here, as the TP-1 income steps give them for the salary. The
expected figures are hand-computed from the printed lines (not an official example); the salary is
$20,000, $70,000 and $200,000.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_U_LINE_11,
    SCHEDULE_U_LINE_14,
    SCHEDULE_U_LINE_14_3,
    SCHEDULE_U_LINE_14_4,
    SCHEDULE_U_LINE_15,
    SCHEDULE_U_LINE_16,
    SCHEDULE_U_MAXIMUM_PENSIONABLE_EARNINGS_LINE_14_1,
    SCHEDULE_U_PENSIONABLE_SALARY_LINE_12,
    SCHEDULE_U_PERSONAL_QPP_EXEMPTION_LINE_13,
    TP1_PENSIONABLE_SALARY_LINE_98_1,
    TP1_QPP_CONTRIBUTION_LINE_98,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PARTS = (
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
    inputs:
      - name: ca/employment_income
        required: true
      - name: ca-qc/tp1_qpp_contribution_line_98
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
        - ca-qc/schedule_u_line_16
    capabilities: []
    """)

# salary: (line 98, line 98.1, then lines 11, 12, 13, 14, 14.1, 14.3, 14.4, 15 and 16)
CHAIN = {
    "20000": (
        "1056.00",
        "20000",
        ("165.00", "20000.00", "3500.00", "16500.00", "71300.00", "67800.00", "16500.00"),
        ("165.00", "165.00"),
    ),
    "70000": (
        "4256.00",
        "70000",
        ("665.00", "70000.00", "3500.00", "66500.00", "71300.00", "67800.00", "66500.00"),
        ("665.00", "665.00"),
    ),
    "200000": (
        "4339.20",
        "81200",
        ("678.00", "71300.00", "3500.00", "67800.00", "71300.00", "67800.00", "67800.00"),
        ("678.00", "678.00"),
    ),
}


@pytest.mark.parametrize("salary", list(CHAIN))
def test_lines_11_to_16_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    line_98, line_98_1, early, late = CHAIN[salary]
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(TP1_QPP_CONTRIBUTION_LINE_98, D(line_98)),
        Artifact(TP1_PENSIONABLE_SALARY_LINE_98_1, D(line_98_1)),
    )["ca-qc/tp1_schedule_u"]

    kinds = (
        SCHEDULE_U_LINE_11,
        SCHEDULE_U_PENSIONABLE_SALARY_LINE_12,
        SCHEDULE_U_PERSONAL_QPP_EXEMPTION_LINE_13,
        SCHEDULE_U_LINE_14,
        SCHEDULE_U_MAXIMUM_PENSIONABLE_EARNINGS_LINE_14_1,
        SCHEDULE_U_LINE_14_3,
        SCHEDULE_U_LINE_14_4,
    )
    assert [str(sheet.get(kind).value) for kind in kinds] == list(early)
    assert [
        str(sheet.get(kind).value) for kind in (SCHEDULE_U_LINE_15, SCHEDULE_U_LINE_16)
    ] == list(late)
