"""Revenu Quebec TP-1 (2025) line 201, "Deduction for workers", as the Quebec take-home manifest
part wires it: the result of Work Chart 201 line 9 ("Carry the result to line 201 of your
return"). The chart is its own form, so line 9 arrives as that form's export and the one step is
`core/record_total` over it. The salary is the starting input; the chart and the TP-1 income steps
are the real parts. The expected figures are hand-computed from the printed chart (6% of the salary,
at most $1,420), not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_DEDUCTION_FOR_WORKERS_LINE_201,
    WORK_CHART_201_LINE_107,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

LINE = TP1_DEDUCTION_FOR_WORKERS_LINE_201
EXPORTS = ("ca-qc/tp1_deduction_for_workers_line_201",)
PARTS = ("tp1_net_income_line_201.yaml",)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "1200.00"), ("70000", "1420.00"), ("200000", "1420.00")],
)
def test_line_201_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = net_income_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


def test_a_negative_chart_line_9_is_carried_as_printed(take_home_service: TakeHomeService) -> None:
    """Work Chart 201 line 1 is signed, so a negative line 107 (a loss) can take line 9 below zero
    (6% of -5,000.00 = -300.00, under the maximum): line 201 carries it as printed."""
    given = (WORK_CHART_201_LINE_107, "-25000")
    value = net_income_sheet(take_home_service, "20000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "-300.00"
