"""Revenu Quebec TP-1 (2025) net income and taxable income, lines 201 to 299, as one chain.

The chain runs the real parts of the net income lines and of the forms they read: TP-1 line 199,
Work Chart 201 and Schedule U (whose TP-1 slip figures are plain starting inputs, as in its own
tests). The salary is $20,000, $70,000 and $200,000. The expected figures are hand-computed from the
printed lines (not an official example).
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_DEDUCTION_FOR_WORKERS_LINE_201,
    TP1_INCOME_LESS_DEDUCTIONS_LINE_256,
    TP1_LINE_279,
    TP1_NET_INCOME_LINE_275,
    TP1_QPP_DEDUCTION_LINE_248,
    TP1_TAXABLE_INCOME_LINE_299,
    TP1_TOTAL_DEDUCTIONS_LINE_254,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

EXPORTS = ("ca-qc/tp1_net_income_line_275", "ca-qc/tp1_taxable_income_line_299")
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
    "tp1_net_income_line_298_input.yaml",
    "tp1_net_income_line_299.yaml",
)
# salary: lines 201, 248, 254, 256, 275, 279 and 299
FIGURES = {
    "20000": ("1200.00", "165.00", "1365.00", "18635.00", "18635.00", "18635.00", "18635.00"),
    "70000": ("1420.00", "665.00", "2085.00", "67915.00", "67915.00", "67915.00", "67915.00"),
    "200000": ("1420.00", "1074.00", "2494.00", "197506.00", "197506.00", "197506.00", "197506.00"),
}


@pytest.mark.parametrize("salary", list(FIGURES))
def test_the_chain_from_line_201_to_line_275(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = net_income_sheet(take_home_service, salary, EXPORTS, PARTS)

    kinds = (
        TP1_DEDUCTION_FOR_WORKERS_LINE_201,
        TP1_QPP_DEDUCTION_LINE_248,
        TP1_TOTAL_DEDUCTIONS_LINE_254,
        TP1_INCOME_LESS_DEDUCTIONS_LINE_256,
        TP1_NET_INCOME_LINE_275,
        TP1_LINE_279,
        TP1_TAXABLE_INCOME_LINE_299,
    )
    assert tuple(str(sheet.get(kind).value) for kind in kinds) == FIGURES[salary]
