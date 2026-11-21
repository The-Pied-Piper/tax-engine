"""Revenu Quebec Work Chart 401 (TP-1.D.GR-V 2025-12) line 5, "x 5": 14% (A), 19% (B), 24% (C) and
25.75% (D). Line 5 is one `core/bracket_column_rate` step over line 1 with
`ca-qc/brackets_work_chart_401`: the printed rate of the column the taxable income falls in, as a
fraction. A line 1 at a bound is in the lower column. The expected figures are read from the printed
chart (not an official example).
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_297,
    WORK_CHART_401_COLUMN_RATE_LINE_5,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_401_support import chart_sheet

LINE = WORK_CHART_401_COLUMN_RATE_LINE_5
EXPORTS = ("ca-qc/work_chart_401_column_rate_line_5",)
PARTS = (
    "work_chart_401_line_1.yaml",
    "work_chart_401_line_5.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "0.14"),
        ("70000", "0.19"),
        ("200000", "0.2575"),
    ],
)
def test_line_5_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "deductions", "expected"),
    [
        ("70000", "14660", "0.14"),  # line 1 53,255.00 is column A
        ("70000", "14659.99", "0.19"),  # line 1 53,255.01 is column B
        ("200000", "91011", "0.19"),  # line 1 106,495.00 is column B
        ("200000", "91010.99", "0.24"),  # line 1 106,495.01 is column C
        ("200000", "67916", "0.24"),  # line 1 129,590.00 is column C
        ("200000", "67915.99", "0.2575"),  # line 1 129,590.01 is column D
    ],
)
def test_line_5_at_the_edges(
    take_home_service: TakeHomeService, salary: str, deductions: str, expected: str
) -> None:
    given = (TP1_LINE_297, deductions)
    sheet = chart_sheet(take_home_service, salary, EXPORTS, PARTS, given)

    assert str(sheet.get(LINE).value) == expected
