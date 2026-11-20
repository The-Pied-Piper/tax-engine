"""Revenu Quebec Work Chart 401 (TP-1.D.GR-V 2025-12), lines 1 to 8, as one chain.

The chain runs the real parts of the chart, under the chart's own form declaration (which exports
line 8 for TP-1 line 401), and of the forms line 1 reads: the TP-1 net income lines for line 299
(whose TP-1 slip figures are plain starting inputs, as in its own tests). The salary is $20,000,
$70,000 and $200,000, which fall in columns A, B and D. Each expected figure is recomputed in the
test from the printed lines: line 2 copies line 1, line 4 is line 2 less line 3, line 6 is line 4
times line 5 and line 8 is line 6 plus line 7. The expected figures are hand-computed from the
printed chart (not an official example).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    WORK_CHART_401_COLUMN_RATE_LINE_5,
    WORK_CHART_401_INCOME_OVER_LOWER_BOUND_LINE_4,
    WORK_CHART_401_INCOME_TAX_LINE_8,
    WORK_CHART_401_LOWER_BOUND_LINE_3,
    WORK_CHART_401_TAX_AT_START_LINE_7,
    WORK_CHART_401_TAX_ON_EXCESS_LINE_6,
    WORK_CHART_401_TAXABLE_INCOME_LINE_1,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import form_part
from tests.jurisdictions.ca_qc.work_chart_401_support import chart_sheet

D = Decimal

# The net income form (the first of the shared parts) is declared here, exporting line 299 that
# line 1 reads; the chart declares itself in `work_chart_401.yaml`.
FORM = form_part("ca-qc/tp1_taxable_income_line_299")

PARTS = (
    "work_chart_401.yaml",
    "work_chart_401_line_1.yaml",
    "work_chart_401_line_3.yaml",
    "work_chart_401_line_4.yaml",
    "work_chart_401_line_5.yaml",
    "work_chart_401_line_6.yaml",
    "work_chart_401_line_7.yaml",
    "work_chart_401_line_8.yaml",
)
# The printed columns: the lower bound (line 3), the rate (line 5) and the amount (line 7).
COLUMNS = {
    "A": (D("0.00"), D("0.14"), D("0.00")),
    "B": (D("53255.00"), D("0.19"), D("7455.70")),
    "C": (D("106495.00"), D("0.24"), D("17571.30")),
    "D": (D("129590.00"), D("0.2575"), D("23114.10")),
}
# salary: line 1 (and line 2), the column, and the figures the printed lines give.
CASES = {
    "20000": ("18635.00", "A", "2608.90"),
    "70000": ("67915.00", "B", "10241.10"),
    "200000": ("197506.00", "D", "40602.47"),
}


@pytest.mark.parametrize("salary", list(CASES))
def test_the_chain_from_line_1_to_line_8(take_home_service: TakeHomeService, salary: str) -> None:
    line_1, column, line_8 = CASES[salary]
    lower, rate, amount = COLUMNS[column]
    sheet = chart_sheet(take_home_service, salary, (), PARTS, form=FORM)

    over = D(line_1) - lower
    on_excess = (over * rate).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    figures = (
        (WORK_CHART_401_TAXABLE_INCOME_LINE_1, D(line_1)),
        (WORK_CHART_401_LOWER_BOUND_LINE_3, lower),
        (WORK_CHART_401_INCOME_OVER_LOWER_BOUND_LINE_4, over),
        (WORK_CHART_401_COLUMN_RATE_LINE_5, rate),
        (WORK_CHART_401_TAX_ON_EXCESS_LINE_6, on_excess),
        (WORK_CHART_401_TAX_AT_START_LINE_7, amount),
        (WORK_CHART_401_INCOME_TAX_LINE_8, on_excess + amount),
    )
    assert tuple(sheet.get(kind).value for kind, _ in figures) == tuple(v for _, v in figures)
    assert str(sheet.get(WORK_CHART_401_INCOME_TAX_LINE_8).value) == line_8
