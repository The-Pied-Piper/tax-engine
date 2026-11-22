"""Revenu Quebec Work Chart 414 (TP-1.D.GR-V 2025-12) line 11, line 3 "x 75% = 11", as the Quebec
take-home manifest part wires it: `core/apply_rate` of line 3 at the printed 75%
(`ca-qc/work_chart_414_line_11_rate`), rounded half-up to the cent by the dataset. The expected
figures are hand-computed from the printed line (not an official example).
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import WORK_CHART_414_LINE_11
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_414_support import (
    FORM_NAME,
    LINE_11_PARTS,
    chart_sheet,
)

LINE = WORK_CHART_414_LINE_11
EXPORTS = ("ca-qc/work_chart_414_line_11",)


@pytest.mark.parametrize(
    ("contributions", "expected"),
    [
        ("100", "37.50"),  # line 3 is 50.00
        ("30", "0.00"),  # line 3 is 0.00
        ("50.10", "0.08"),  # line 3 0.10 x 75% = 0.075 rounds half up
    ],
)
def test_line_11_is_line_3_times_75_percent(
    take_home_service: TakeHomeService, contributions: str, expected: str
) -> None:
    sheet = chart_sheet(take_home_service, EXPORTS, LINE_11_PARTS, contributions)

    assert str(sheet.get(LINE).value) == expected


def test_the_part_is_line_3_at_the_printed_rate() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / "work_chart_414_line_11.yaml").read_text("utf-8"))

    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "11",
        "unit": "ca/cad",
        "params": {"rate": "ca-qc/work_chart_414_line_11_rate"},
        "consumes": {"base": "ca-qc/work_chart_414_remainder_line_3"},
        "produces": {"output": "ca-qc/work_chart_414_line_11"},
    }
