"""Revenu Quebec TP-1 (2025) line 298, "Add lines 287 through 297. Total deductions", as the Quebec
take-home manifest part wires it: `core/sum` of lines 287, 289, 290, 291, 292, 293, 295 and 297,
each its own optional input read as 0 when left out, rounded half-up to the cent by
`ca-qc/cent_rounding`. The expected figures are hand-computed from the printed lines, not an
official example.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_287,
    TP1_LINE_297,
    TP1_TOTAL_DEDUCTIONS_LINE_298,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

LINE = TP1_TOTAL_DEDUCTIONS_LINE_298
EXPORTS = ("ca-qc/tp1_total_deductions_line_298",)
PARTS = (
    "tp1_net_income_line_298_inputs.yaml",
    "tp1_net_income_line_298.yaml",
)


def test_line_298_with_every_line_blank_is_zero(take_home_service: TakeHomeService) -> None:
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS).get(LINE).value

    assert str(value) == "0.00"


def test_two_printed_lines_are_each_added(take_home_service: TakeHomeService) -> None:
    given = ((TP1_LINE_287, "1000.50"), (TP1_LINE_297, "250.25"))
    value = net_income_sheet(take_home_service, "70000", EXPORTS, PARTS, *given).get(LINE).value

    assert str(value) == "1250.75"
