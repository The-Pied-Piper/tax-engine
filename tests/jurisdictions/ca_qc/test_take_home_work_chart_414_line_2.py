"""Revenu Quebec Work Chart 414 (TP-1.D.GR-V 2025-12) line 2, "Enter the amount from line 1 or $50,
whichever is less.", as the Quebec take-home manifest part wires it: `core/capped_amount` of line 1
against the printed $50 (`ca-qc/work_chart_414_line_2_limit`). The expected figures are
hand-computed from the printed line (not an official example).
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import WORK_CHART_414_LESSER_LINE_2
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_414_support import (
    FORM_NAME,
    LINE_2_PARTS,
    chart_sheet,
)

LINE = WORK_CHART_414_LESSER_LINE_2
EXPORTS = ("ca-qc/work_chart_414_lesser_line_2",)


@pytest.mark.parametrize(
    ("contributions", "expected"),
    [("30", "30.00"), ("100", "50.00"), ("400", "50.00")],  # line 1 is 30.00, 100.00, 200.00
)
def test_line_2_is_line_1_or_50_whichever_is_less(
    take_home_service: TakeHomeService, contributions: str, expected: str
) -> None:
    sheet = chart_sheet(take_home_service, EXPORTS, LINE_2_PARTS, contributions)

    assert str(sheet.get(LINE).value) == expected


def test_the_part_is_line_1_capped_at_the_printed_limit() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / "work_chart_414_line_2.yaml").read_text("utf-8"))

    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/capped_amount",
        "reference": "2",
        "unit": "ca/cad",
        "params": {"cap": "ca-qc/work_chart_414_line_2_limit"},
        "consumes": {"base": "ca-qc/work_chart_414_contributions_line_1"},
        "produces": {"output": "ca-qc/work_chart_414_lesser_line_2"},
    }
