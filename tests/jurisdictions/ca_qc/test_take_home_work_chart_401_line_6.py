"""Revenu Quebec Work Chart 401 (TP-1.D.GR-V 2025-12) line 6, "Multiply line 4 by line 5", as the
Quebec take-home manifest part wires it: `core/multiply_by_rate`, rounded half-up to the cent by
`ca-qc/cent_rounding`. The expected figures are hand-computed from the printed lines (14,660.00 x
19%, 67,916.00 x 25.75%), not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_TOTAL_DEDUCTIONS_LINE_298,
    WORK_CHART_401_TAX_ON_EXCESS_LINE_6,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_401_support import chart_sheet

LINE = WORK_CHART_401_TAX_ON_EXCESS_LINE_6
EXPORTS = ("ca-qc/work_chart_401_tax_on_excess_line_6",)
PARTS = (
    "work_chart_401_line_1.yaml",
    "work_chart_401_line_3.yaml",
    "work_chart_401_line_4.yaml",
    "work_chart_401_line_5.yaml",
    "work_chart_401_line_6.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "2608.90"),
        ("70000", "2785.40"),
        ("200000", "17488.37"),
    ],
)
def test_line_6_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "deductions", "expected"),
    [
        ("20000", "18635", "0.00"),  # line 1 0.00
        ("200000", "67915.99", "0.00"),  # line 4 0.01 x 25.75% = 0.002575, rounds down
        ("200000", "67915.90", "0.03"),  # line 4 0.10 x 25.75% = 0.02575, rounds half up
        ("70000", "14659.95", "0.01"),  # line 4 0.05 x 19% = 0.0095, rounds up
    ],
)
def test_line_6_at_the_edges(
    take_home_service: TakeHomeService, salary: str, deductions: str, expected: str
) -> None:
    given = (TP1_TOTAL_DEDUCTIONS_LINE_298, deductions)
    sheet = chart_sheet(take_home_service, salary, EXPORTS, PARTS, given)

    assert str(sheet.get(LINE).value) == expected
