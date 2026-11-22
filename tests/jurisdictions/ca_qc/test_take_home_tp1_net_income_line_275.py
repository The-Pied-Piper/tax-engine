"""Revenu Quebec TP-1 (2025) line 275, "Add lines 256 and 260. If the result is negative, enter 0.
Net income", as the Quebec take-home manifest part wires it: `core/sum_not_below_zero`, rounded
half-up to the cent by `ca-qc/cent_rounding`. Line 260 (Adjustment of investment expenses) is an
optional input, read as 0 when the caller leaves it out. The expected figures are hand-computed from
the printed lines, not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_INVESTMENT_EXPENSES_ADJUSTMENT_LINE_260,
    TP1_LINE_250,
    TP1_NET_INCOME_LINE_275,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

LINE = TP1_NET_INCOME_LINE_275
EXPORTS = ("ca-qc/tp1_net_income_line_275",)
PARTS = (
    "tp1_net_income_line_201.yaml",
    "tp1_net_income_line_248.yaml",
    "tp1_net_income_line_254_inputs.yaml",
    "tp1_net_income_line_254.yaml",
    "tp1_net_income_line_256.yaml",
    "tp1_net_income_line_260_input.yaml",
    "tp1_net_income_line_275.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_line_275_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = net_income_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


def test_line_260_is_added(take_home_service: TakeHomeService) -> None:
    given = (TP1_INVESTMENT_EXPENSES_ADJUSTMENT_LINE_260, "100.25")
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "68015.25"


def test_a_negative_result_is_entered_as_zero(take_home_service: TakeHomeService) -> None:
    """Other deductions of 30,000.00 on a $20,000 salary make line 256 -11,365.00; line 275 is 0."""
    given = (TP1_LINE_250, "30000")
    value = net_income_sheet(take_home_service, "20000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "0.00"
