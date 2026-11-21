"""Revenu Quebec Work Chart 414 (TP-1.D.GR-V 2025-12) line 10, line 2 "x 85% = 10", as the Quebec
take-home manifest part wires it: `core/apply_rate` of line 2 at the printed 85%
(`ca-qc/work_chart_414_line_10_rate`), rounded half-up to the cent by the dataset. The expected
figures are hand-computed from the printed line (not an official example).
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import WORK_CHART_414_LINE_10
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_414_support import (
    FORM_NAME,
    LINE_10_PARTS,
    chart_sheet,
)

LINE = WORK_CHART_414_LINE_10
EXPORTS = ("ca-qc/work_chart_414_line_10",)


@pytest.mark.parametrize(
    ("contributions", "expected"),
    [
        ("30", "25.50"),  # 30.00 x 85%
        ("100", "42.50"),  # line 2 is 50.00
        ("0.01", "0.01"),  # 0.0085 rounds half up
    ],
)
def test_line_10_is_line_2_times_85_percent(
    take_home_service: TakeHomeService, contributions: str, expected: str
) -> None:
    sheet = chart_sheet(take_home_service, EXPORTS, LINE_10_PARTS, contributions)

    assert str(sheet.get(LINE).value) == expected


def test_the_part_is_line_2_at_the_printed_rate() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / "work_chart_414_line_10.yaml").read_text("utf-8"))

    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "10",
        "unit": "ca/cad",
        "params": {"rate": "ca-qc/work_chart_414_line_10_rate"},
        "consumes": {"base": "ca-qc/work_chart_414_lesser_line_2"},
        "produces": {"output": "ca-qc/work_chart_414_line_10"},
    }
