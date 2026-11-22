"""Revenu Quebec Schedule U (2025, TP-1.D.U-V) Part B, lines 10 to 23, as one chain.

Lines 10 to 23 are built from the real parts; lines 10, 12, 17, 17.4 and 18.5 read the TP-1 figures
of lines 98, 98.1 and 98.2 from the real TP-1 income parts. The expected figures are hand-computed
from the printed lines (not an official example); the salary is $20,000, $70,000 and $200,000.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_U_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS_LINE_18_8,
    SCHEDULE_U_LINE_11,
    SCHEDULE_U_LINE_14,
    SCHEDULE_U_LINE_14_3,
    SCHEDULE_U_LINE_14_4,
    SCHEDULE_U_LINE_15,
    SCHEDULE_U_LINE_16,
    SCHEDULE_U_LINE_17_2,
    SCHEDULE_U_LINE_17_3,
    SCHEDULE_U_LINE_17_5,
    SCHEDULE_U_LINE_18_7,
    SCHEDULE_U_LINE_19,
    SCHEDULE_U_LINE_20,
    SCHEDULE_U_LINE_21,
    SCHEDULE_U_LINE_22,
    SCHEDULE_U_LINE_23,
    SCHEDULE_U_MAXIMUM_PENSIONABLE_EARNINGS_LINE_14_1,
    SCHEDULE_U_PENSIONABLE_SALARY_LINE_12,
    SCHEDULE_U_PERSONAL_QPP_EXEMPTION_LINE_13,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS

D = Decimal
PARTS = (
    *TP1_INCOME_PARTS,
    "tp1_schedule_u_line_10_base.yaml",
    "tp1_schedule_u_line_10.yaml",
    "tp1_schedule_u_line_11.yaml",
    "tp1_schedule_u_line_12_base.yaml",
    "tp1_schedule_u_line_12.yaml",
    "tp1_schedule_u_line_13.yaml",
    "tp1_schedule_u_line_14.yaml",
    "tp1_schedule_u_line_14_1.yaml",
    "tp1_schedule_u_line_14_3.yaml",
    "tp1_schedule_u_line_14_4.yaml",
    "tp1_schedule_u_line_15.yaml",
    "tp1_schedule_u_line_16.yaml",
    "tp1_schedule_u_line_17_2.yaml",
    "tp1_schedule_u_line_17.yaml",
    "tp1_schedule_u_line_17_3.yaml",
    "tp1_schedule_u_line_17_4.yaml",
    "tp1_schedule_u_line_17_5.yaml",
    "tp1_schedule_u_line_18_5.yaml",
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
        - ca-qc/schedule_u_line_16
        - ca-qc/schedule_u_line_17_5
        - ca-qc/schedule_u_line_23
    capabilities: []
    """)

# salary: (line 98, line 98.1, line 98.2, then lines 11, 12, 13, 14, 14.1, 14.3 and 14.4, then
# lines 15, 16, 17.2, 17.3 and 17.5, then lines 18.7, 18.8, 19, 20, 21, 22 and 23)
CHAIN = {
    "20000": (
        "1056.00",
        "20000",
        "0.00",
        ("165.00", "20000.00", "3500.00", "16500.00", "71300.00", "67800.00", "16500.00"),
        (
            "165.00",
            "165.00",
            "1056.00",
            "0.00",
            "0.00",
            "0.00",
            "81200.00",
            "9900.00",
            "0.00",
            "0.00",
            "0.00",
            "165.00",
        ),
    ),
    "70000": (
        "4256.00",
        "70000",
        "0.00",
        ("665.00", "70000.00", "3500.00", "66500.00", "71300.00", "67800.00", "66500.00"),
        (
            "665.00",
            "665.00",
            "4256.00",
            "0.00",
            "0.00",
            "0.00",
            "81200.00",
            "9900.00",
            "0.00",
            "0.00",
            "0.00",
            "665.00",
        ),
    ),
    "200000": (
        "4339.20",
        "81200",
        "396.00",
        ("678.00", "71300.00", "3500.00", "67800.00", "71300.00", "67800.00", "67800.00"),
        (
            "678.00",
            "678.00",
            "4339.20",
            "0.00",
            "396.00",
            "9900.00",
            "81200.00",
            "9900.00",
            "9900.00",
            "396.00",
            "396.00",
            "1074.00",
        ),
    ),
}


@pytest.mark.parametrize("salary", list(CHAIN))
def test_lines_11_to_23_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    line_98, line_98_1, line_98_2, early, late = CHAIN[salary]
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        ),
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
    late_kinds = (
        SCHEDULE_U_LINE_15,
        SCHEDULE_U_LINE_16,
        SCHEDULE_U_LINE_17_2,
        SCHEDULE_U_LINE_17_3,
        SCHEDULE_U_LINE_17_5,
        SCHEDULE_U_LINE_18_7,
        SCHEDULE_U_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS_LINE_18_8,
        SCHEDULE_U_LINE_19,
        SCHEDULE_U_LINE_20,
        SCHEDULE_U_LINE_21,
        SCHEDULE_U_LINE_22,
        SCHEDULE_U_LINE_23,
    )
    assert [str(sheet.get(kind).value) for kind in late_kinds] == list(late)
