"""Revenu Quebec Work Chart 401 (TP-1.D.GR-V 2025-12) line 4, "Subtract line 3 from line 2", as the
Quebec take-home manifest part wires it. Line 2 is a copy of line 1 and has no step. Line 4 is
`core/subtract_not_below_zero` of line 3 from line 1, rounded half-up to the cent. The expected
figures are hand-computed from the printed chart (not an official example).
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_297,
    WORK_CHART_401_INCOME_OVER_LOWER_BOUND_LINE_4,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_401_support import chart_sheet

LINE = WORK_CHART_401_INCOME_OVER_LOWER_BOUND_LINE_4
EXPORTS = ("ca-qc/work_chart_401_income_over_lower_bound_line_4",)
PARTS = (
    "work_chart_401_line_1.yaml",
    "work_chart_401_line_3.yaml",
    "work_chart_401_line_4.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # 18,635.00 less 0.00; 67,915.00 less 53,255.00; 197,506.00 less 129,590.00.
        ("20000", "18635.00"),
        ("70000", "14660.00"),
        ("200000", "67916.00"),
    ],
)
def test_line_4_is_line_1_less_the_columns_lower_bound(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "deductions", "expected"),
    [
        ("20000", "18635", "0.00"),  # line 1 0.00, column A
        ("70000", "14660", "53255.00"),  # line 1 53,255.00 is column A: less 0.00
        ("70000", "14659.99", "0.01"),  # line 1 53,255.01 is column B: less 53,255.00
    ],
)
def test_line_4_at_the_edges(
    take_home_service: TakeHomeService, salary: str, deductions: str, expected: str
) -> None:
    given = (TP1_LINE_297, deductions)
    sheet = chart_sheet(take_home_service, salary, EXPORTS, PARTS, given)

    assert str(sheet.get(LINE).value) == expected
