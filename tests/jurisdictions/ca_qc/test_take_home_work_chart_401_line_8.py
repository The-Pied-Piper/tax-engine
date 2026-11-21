"""Revenu Quebec Work Chart 401 (TP-1.D.GR-V 2025-12) line 8, "Add lines 6 and 7. Income tax on
taxable income", as the Quebec take-home manifest part wires it: `core/sum` of line 6 and line 7,
rounded half-up to the cent by `ca-qc/cent_rounding`. The form carries the result to TP-1 line 401.
The expected figures are hand-computed from the printed lines (not an official example).
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_297,
    WORK_CHART_401_INCOME_TAX_LINE_8,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_401_support import chart_sheet

LINE = WORK_CHART_401_INCOME_TAX_LINE_8
EXPORTS = ("ca-qc/work_chart_401_income_tax_line_8",)
PARTS = (
    "work_chart_401_line_1.yaml",
    "work_chart_401_line_3.yaml",
    "work_chart_401_line_4.yaml",
    "work_chart_401_line_5.yaml",
    "work_chart_401_line_6.yaml",
    "work_chart_401_line_7.yaml",
    "work_chart_401_line_8.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # 0.00 + 2,608.90; 7,455.70 + 2,785.40; 23,114.10 + 17,488.37.
        ("20000", "2608.90"),
        ("70000", "10241.10"),
        ("200000", "40602.47"),
    ],
)
def test_line_8_is_line_6_plus_line_7(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = chart_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "deductions", "expected"),
    [
        ("20000", "18635", "0.00"),  # line 1 0.00
        ("70000", "14660", "7455.70"),  # line 1 53,255.00, column A: 53,255.00 x 14% + 0.00
        ("70000", "14659.99", "7455.70"),  # line 1 53,255.01, column B: 0.01 x 19% + 7,455.70
        ("200000", "67916", "23114.10"),  # line 1 129,590.00, column C: 23,095.00 x 24% + 17,571.30
        (
            "200000",
            "67915.90",
            "23114.13",
        ),  # line 1 129,590.10, column D: 0.10 x 25.75% + 23,114.10
    ],
)
def test_line_8_at_the_edges(
    take_home_service: TakeHomeService, salary: str, deductions: str, expected: str
) -> None:
    given = (TP1_LINE_297, deductions)
    sheet = chart_sheet(take_home_service, salary, EXPORTS, PARTS, given)

    assert str(sheet.get(LINE).value) == expected


def test_the_real_form_declaration_exports_line_8() -> None:
    declaration = yaml.safe_load((QUEBEC_PARTS / "work_chart_401.yaml").read_text(encoding="utf-8"))

    assert declaration["form"]["name"] == "ca-qc/work_chart_401"
    assert declaration["form"]["required"] is True
    assert declaration["form"]["exports"] == ["ca-qc/work_chart_401_income_tax_line_8"]
