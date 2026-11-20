"""Revenu Quebec Work Chart 401 (TP-1.D.GR-V 2025-12) line 3, "- 3", as the Quebec take-home
manifest part wires it: 0 00 (column A), 53,255 00 (B), 106,495 00 (C) and 129,590 00 (D). Line 2 is
a copy of line 1 and has no step. Line 3 is one `core/bracket_column_lower_bound` step over line 1
with `ca-qc/brackets_work_chart_401`: the printed lower bound of the column the taxable income falls
in, and a line 1 at a bound is in the lower column ("or less", "but not more than"). The expected
figures are hand-computed from the printed chart (not an official example).
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_TOTAL_DEDUCTIONS_LINE_298,
    WORK_CHART_401_LOWER_BOUND_LINE_3,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_401_support import chart_sheet

LINE = WORK_CHART_401_LOWER_BOUND_LINE_3
EXPORTS = ("ca-qc/work_chart_401_lower_bound_line_3",)
PARTS = ("work_chart_401_line_1.yaml", "work_chart_401_line_3.yaml")


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "53255.00"), ("200000", "129590.00")],
)
def test_line_3_is_the_lower_bound_of_the_column(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "deductions", "expected"),
    [
        # Line 1 is the salary's 18,635.00 / 67,915.00 / 197,506.00 less line 298.
        ("20000", "18635", "0.00"),  # line 1 0.00
        ("70000", "14660", "0.00"),  # line 1 53,255.00
        ("70000", "14659.99", "53255.00"),  # line 1 53,255.01
        ("200000", "91011", "53255.00"),  # line 1 106,495.00
        ("200000", "91010.99", "106495.00"),  # line 1 106,495.01
        ("200000", "67916", "106495.00"),  # line 1 129,590.00
        ("200000", "67915.99", "129590.00"),  # line 1 129,590.01
    ],
)
def test_a_line_1_at_a_bound_is_in_the_lower_column(
    take_home_service: TakeHomeService, salary: str, deductions: str, expected: str
) -> None:
    given = (TP1_TOTAL_DEDUCTIONS_LINE_298, deductions)
    sheet = chart_sheet(take_home_service, salary, EXPORTS, PARTS, given)

    assert str(sheet.get(LINE).value) == expected
