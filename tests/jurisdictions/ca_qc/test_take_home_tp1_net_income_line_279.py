"""Revenu Quebec TP-1 (2025) line 279, "Add lines 275 through 278", as the Quebec take-home
manifest part wires it: `core/sum`, rounded half-up to the cent by `ca-qc/cent_rounding`. Lines 276
(Adjustment of deductions) and 278 (Universal Child Care Benefit and income from a registered
disability savings plan) are optional inputs, read as 0 when the caller leaves them out. The
expected figures are hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_ADJUSTMENT_OF_DEDUCTIONS_LINE_276,
    TP1_BENEFIT_AND_DISABILITY_SAVINGS_INCOME_LINE_278,
    TP1_LINE_279,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

LINE = TP1_LINE_279
EXPORTS = ("ca-qc/tp1_line_279",)
PARTS = (
    "tp1_net_income_line_201.yaml",
    "tp1_net_income_line_248.yaml",
    "tp1_net_income_line_254_input.yaml",
    "tp1_net_income_line_254.yaml",
    "tp1_net_income_line_256.yaml",
    "tp1_net_income_line_260_input.yaml",
    "tp1_net_income_line_275.yaml",
    "tp1_net_income_line_276_input.yaml",
    "tp1_net_income_line_278_input.yaml",
    "tp1_net_income_line_279.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_line_279_with_lines_276_and_278_blank_is_line_275(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = net_income_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


def test_line_276_is_added(take_home_service: TakeHomeService) -> None:
    given = (TP1_ADJUSTMENT_OF_DEDUCTIONS_LINE_276, "100.25")
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "68015.25"


def test_line_278_is_added(take_home_service: TakeHomeService) -> None:
    given = (TP1_BENEFIT_AND_DISABILITY_SAVINGS_INCOME_LINE_278, "250.50")
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "68165.50"
