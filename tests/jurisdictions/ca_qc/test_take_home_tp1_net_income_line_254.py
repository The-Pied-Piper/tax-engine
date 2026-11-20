"""Revenu Quebec TP-1 (2025) line 254, "Add lines 201 through 207, 214 through 231, and 234 through
252. Total deductions", as the Quebec take-home manifest part wires it: line 201, line 248 and the
other deductions. Lines 205 to 207, 214 to 231 and 234 to 252 (line 248.1 included, line 248
apart) are one optional input (`ca-qc/tp1_other_deductions_lines_205_to_252`), read as 0 when the
caller leaves it out. The sum is `core/sum`, rounded half-up to the cent by `ca-qc/cent_rounding`.
The expected figures are
hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_OTHER_DEDUCTIONS_LINES_205_TO_252,
    TP1_TOTAL_DEDUCTIONS_LINE_254,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

LINE = TP1_TOTAL_DEDUCTIONS_LINE_254
EXPORTS = ("ca-qc/tp1_total_deductions_line_254",)
PARTS = (
    "tp1_net_income_line_201.yaml",
    "tp1_net_income_line_248.yaml",
    "tp1_net_income_line_254_input.yaml",
    "tp1_net_income_line_254.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "1365.00"), ("70000", "2085.00"), ("200000", "2494.00")],
)
def test_line_254_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = net_income_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


def test_the_other_deductions_are_added(take_home_service: TakeHomeService) -> None:
    given = (TP1_OTHER_DEDUCTIONS_LINES_205_TO_252, "1000.50")
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "3085.50"


def test_the_sum_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    given = (TP1_OTHER_DEDUCTIONS_LINES_205_TO_252, "0.005")
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "2085.01"
