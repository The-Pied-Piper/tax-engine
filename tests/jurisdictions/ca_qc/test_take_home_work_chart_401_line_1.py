"""Revenu Quebec Work Chart 401 (TP-1.D.GR-V 2025-12) line 1, "Taxable income (line 299 of your
return)", as the Quebec take-home manifest part wires it. The net income form is its own form, so
line 299 arrives as that form's export and the one step is `core/record_total` over it. Line 2 is a
copy of line 1 and has no step. The salary is the starting input; the net income lines are the real
parts. The expected figures are hand-computed from the printed lines (not an official example).
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import WORK_CHART_401_TAXABLE_INCOME_LINE_1
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_401_support import chart_sheet

LINE = WORK_CHART_401_TAXABLE_INCOME_LINE_1
EXPORTS = ("ca-qc/work_chart_401_taxable_income_line_1",)
PARTS = ("work_chart_401_line_1.yaml",)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_line_1_is_the_taxable_income_of_the_return(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected
