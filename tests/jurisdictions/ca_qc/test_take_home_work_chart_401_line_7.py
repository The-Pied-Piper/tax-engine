"""Revenu Quebec Work Chart 401 (TP-1.D.GR-V 2025-12) line 7, "+ 7": 0 00 (column A), 7,455 70 (B),
17,571 30 (C) and 23,114 10 (D). Line 7 is one `core/bracket_column_tax_at_start` step over line 1
with `ca-qc/work_chart_401_brackets`: the printed amount of the column the taxable income falls in,
taken as printed and not recomputed. A line 1 at a bound is in the lower column. The expected
figures are read from the printed chart (not an official example).
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_TOTAL_DEDUCTIONS_LINE_298,
    WORK_CHART_401_TAX_AT_START_LINE_7,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_401_support import chart_sheet

LINE = WORK_CHART_401_TAX_AT_START_LINE_7
EXPORTS = ("ca-qc/work_chart_401_tax_at_start_line_7",)
PARTS = (
    "work_chart_401_line_1.yaml",
    "work_chart_401_line_7.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "0.00"),
        ("70000", "7455.70"),
        ("200000", "23114.10"),
    ],
)
def test_line_7_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "deductions", "expected"),
    [
        ("70000", "14660", "0.00"),  # line 1 53,255.00 is column A
        ("70000", "14659.99", "7455.70"),  # line 1 53,255.01 is column B
        ("200000", "91011", "7455.70"),  # line 1 106,495.00 is column B
        ("200000", "91010.99", "17571.30"),  # line 1 106,495.01 is column C
        ("200000", "67916", "17571.30"),  # line 1 129,590.00 is column C
        ("200000", "67915.99", "23114.10"),  # line 1 129,590.01 is column D
    ],
)
def test_line_7_at_the_edges(
    take_home_service: TakeHomeService, salary: str, deductions: str, expected: str
) -> None:
    given = (TP1_TOTAL_DEDUCTIONS_LINE_298, deductions)
    sheet = chart_sheet(take_home_service, salary, EXPORTS, PARTS, given)

    assert str(sheet.get(LINE).value) == expected
