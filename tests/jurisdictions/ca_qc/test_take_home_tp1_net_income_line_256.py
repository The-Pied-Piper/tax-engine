"""Revenu Quebec TP-1 (2025) line 256, "Subtract line 254 from line 199.", as the Quebec take-home
manifest part wires it. Line 199 arrives from the TP-1 income form as a record list of one
(`core/record_total`); the subtraction is `core/subtract` with no floor, rounded half-up to the cent
by `ca-qc/cent_rounding`. The salary is the starting input; the upstream forms are the real parts.
The expected figures are hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_INCOME_LESS_DEDUCTIONS_LINE_256,
    TP1_LINE_250,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

LINE = TP1_INCOME_LESS_DEDUCTIONS_LINE_256
EXPORTS = ("ca-qc/tp1_income_less_deductions_line_256",)
PARTS = (
    "tp1_net_income_line_201.yaml",
    "tp1_net_income_line_248.yaml",
    "tp1_net_income_line_254_inputs.yaml",
    "tp1_net_income_line_254.yaml",
    "tp1_net_income_line_256.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_line_256_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = net_income_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


def test_a_deduction_above_income_gives_a_negative_figure(
    take_home_service: TakeHomeService,
) -> None:
    """The form prints no floor on line 256: other deductions of 30,000.00 on a $20,000 salary give
    18,635.00 - 30,000.00 = -11,365.00."""
    given = (TP1_LINE_250, "30000")
    value = net_income_sheet(take_home_service, "20000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "-11365.00"
