"""Shared helpers of the Schedule K Part C line tests (lines 77 to 84).

Part C reads line 48 of Part A. Most tests give line 48 straight to the form (the header takes it as
an input), so a test can put it on either side of every printed column edge: $5,000 or less is
column A, more than $5,000 is column B, and more than $14,669 prints $766 on line 83. The salary
tests run the real Part A chain (see `schedule_k_support.py`) and the Part C `parts` under test.
Every figure below is hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_K_PREMIUM_INCOME_LINE_48
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_support import FORM_NAME, form_part, schedule_k_sheet

D = Decimal
PART_A = (
    "tp1_schedule_k_line_36.yaml",
    "tp1_schedule_k_line_37.yaml",
    "tp1_schedule_k_line_40.yaml",
    "tp1_schedule_k_line_41.yaml",
    "tp1_schedule_k_line_44_input.yaml",
    "tp1_schedule_k_line_44_amounts.yaml",
    "tp1_schedule_k_line_44.yaml",
    "tp1_schedule_k_line_46.yaml",
    "tp1_schedule_k_line_48.yaml",
)
PART_C = (
    "tp1_schedule_k_line_78.yaml",
    "tp1_schedule_k_line_79.yaml",
    "tp1_schedule_k_line_80.yaml",
    "tp1_schedule_k_line_81.yaml",
    "tp1_schedule_k_line_82.yaml",
    "tp1_schedule_k_line_83.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca-qc/schedule_k_premium_income_line_48
        required: true
    outputs:
      - ca-qc/schedule_k_premium_income_line_48
    """)

# Printed lines 78 to 83 for a line 48 given straight to Part C: line 48 -> (78, 79, 80, 81, 82,
# 83). Column A holds $5,000 or less, column B more than $5,000; line 83 is capped at $766.
COLUMNS = {
    "0.00": ("0.00", "0.00", "0.0784", "0.00", "0.00", "0.00"),
    "5000.00": ("0.00", "5000.00", "0.0784", "392.00", "0.00", "392.00"),
    "5000.01": ("5000.00", "0.01", "0.1176", "0.00", "392.00", "392.00"),
    "8000.00": ("5000.00", "3000.00", "0.1176", "352.80", "392.00", "744.80"),
    "14669.00": ("5000.00", "9669.00", "0.1176", "1137.07", "392.00", "766.00"),
    "20000.00": ("5000.00", "15000.00", "0.1176", "1764.00", "392.00", "766.00"),
}
# The same lines for the three salaries, where line 48 is 0.00, 48,025.00 and 177,616.00.
SALARY_COLUMNS = {
    "20000": ("0.00", "0.00", "0.0784", "0.00", "0.00", "0.00"),
    "70000": ("5000.00", "43025.00", "0.1176", "5059.74", "392.00", "766.00"),
    "200000": ("5000.00", "172616.00", "0.1176", "20299.64", "392.00", "766.00"),
}
INDEX = {"78": 0, "79": 1, "80": 2, "81": 3, "82": 4, "83": 5}


def part_c(
    take_home_service: TakeHomeService, line_48: str, export: str, parts: tuple[str, ...]
) -> Worksheet:
    """The Schedule K worksheet of `parts` for a line 48 given straight to Part C."""
    (sheet,) = take_home_service(HEADER, form_part(export), *parts).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(SCHEDULE_K_PREMIUM_INCOME_LINE_48, D(line_48))
    )[FORM_NAME]
    return sheet


def salary_sheet(
    take_home_service: TakeHomeService, salary: str, export: str, parts: tuple[str, ...]
) -> Worksheet:
    """The Schedule K worksheet of Part A and the Part C `parts`, run from a salary."""
    return schedule_k_sheet(take_home_service, salary, export, PART_A + parts)
