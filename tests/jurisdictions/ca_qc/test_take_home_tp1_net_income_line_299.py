"""Revenu Quebec TP-1 (2025) line 299, "Subtract line 298 from line 279. If the result is negative,
enter 0. Taxable income", as the Quebec take-home manifest part wires it:
`core/subtract_not_below_zero`, rounded half-up to the cent by `ca-qc/cent_rounding`. Line 298 (the
printed sum of lines 287 to 297) is one optional input, default 0. The expected figures are
hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_297,
    TP1_TAXABLE_INCOME_LINE_299,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

LINE = TP1_TAXABLE_INCOME_LINE_299
EXPORTS = ("ca-qc/tp1_taxable_income_line_299",)
PARTS = (
    "tp1_net_income_line_201.yaml",
    "tp1_net_income_line_248.yaml",
    "tp1_net_income_line_254_inputs.yaml",
    "tp1_net_income_line_254.yaml",
    "tp1_net_income_line_256.yaml",
    "tp1_net_income_line_260_input.yaml",
    "tp1_net_income_line_275.yaml",
    "tp1_net_income_line_276_input.yaml",
    "tp1_net_income_line_278_input.yaml",
    "tp1_net_income_line_279.yaml",
    "tp1_net_income_line_298_inputs.yaml",
    "tp1_net_income_line_298.yaml",
    "tp1_net_income_line_299.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_line_299_with_line_298_blank_is_line_279(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = net_income_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


def test_line_298_is_subtracted(take_home_service: TakeHomeService) -> None:
    given = (TP1_LINE_297, "1000")
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "66915.00"


def test_a_negative_result_is_entered_as_zero(take_home_service: TakeHomeService) -> None:
    given = (TP1_LINE_297, "30000")
    value = net_income_sheet(take_home_service, "20000", EXPORTS, PARTS, given).get(LINE).value

    assert str(value) == "0.00"
