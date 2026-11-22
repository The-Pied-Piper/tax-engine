"""Revenu Quebec Work Chart 414 (TP-1.D.GR-V 2025-12), lines 1 to 14, as one chain.

The chain runs the real parts of the chart under the chart's own form declaration (which exports
line 14 for TP-1 line 414). Contributions of $30, $100 and $400 give a line 1 of 30.00, 100.00
and 200.00 (capped at the printed $200). Each expected figure is recomputed in the test from the
printed lines: line 2 is the lesser of line 1 and $50, line 10 is line 2 x 85%, line 3 is line 1
less line 2, line 11 is line 3 x 75% and line 14 is lines 10 and 11 added, up to $155. The expected
figures are hand-computed from the printed chart (not an official example). TP-1 lines 414 and 425
are run in `test_tp1_tax.py`.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    WORK_CHART_414_CONTRIBUTIONS_LINE_1,
    WORK_CHART_414_CREDIT_LINE_14,
    WORK_CHART_414_LESSER_LINE_2,
    WORK_CHART_414_LINE_10,
    WORK_CHART_414_LINE_11,
    WORK_CHART_414_REMAINDER_LINE_3,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_414_support import LINE_14_PARTS, chart_sheet

D = Decimal
FORM = (QUEBEC_PARTS / "work_chart_414.yaml").read_text(encoding="utf-8")
# contributions: line 1 and the credit as the printed lines give them.
CASES = {"30": ("30.00", "25.50"), "100": ("100.00", "80.00"), "400": ("200.00", "155.00")}


def _cent(value: Decimal) -> Decimal:
    return value.quantize(D("0.01"), rounding=ROUND_HALF_UP)


@pytest.mark.parametrize("contributions", list(CASES))
def test_the_chain_from_line_1_to_line_14(
    take_home_service: TakeHomeService, contributions: str
) -> None:
    line_1, line_14 = CASES[contributions]
    sheet = chart_sheet(take_home_service, (), LINE_14_PARTS, contributions, form=FORM)

    line_2 = min(D(line_1), D("50"))
    line_10 = _cent(line_2 * D("0.85"))
    line_3 = D(line_1) - line_2
    line_11 = _cent(line_3 * D("0.75"))
    figures = (
        (WORK_CHART_414_CONTRIBUTIONS_LINE_1, D(line_1)),
        (WORK_CHART_414_LESSER_LINE_2, line_2),
        (WORK_CHART_414_LINE_10, line_10),
        (WORK_CHART_414_REMAINDER_LINE_3, line_3),
        (WORK_CHART_414_LINE_11, line_11),
        (WORK_CHART_414_CREDIT_LINE_14, min(line_10 + line_11, D("155"))),
    )
    assert tuple(sheet.get(kind).value for kind, _ in figures) == tuple(v for _, v in figures)
    assert str(sheet.get(WORK_CHART_414_CREDIT_LINE_14).value) == line_14
