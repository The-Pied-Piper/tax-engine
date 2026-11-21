"""Revenu Quebec Work Chart 414 (TP-1.D.GR-V 2025-12) line 3, "Subtract line 2 from line 1.", as the
Quebec take-home manifest part wires it: line 1 less line 2, rounded half-up to the cent by
`ca-qc/cent_rounding` (line 2 never exceeds line 1, so the capability may or may not floor at
zero). The expected figures are hand-computed from the printed line (not an official example).
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import WORK_CHART_414_REMAINDER_LINE_3
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.work_chart_414_support import (
    FORM_NAME,
    LINE_3_PARTS,
    chart_sheet,
)

LINE = WORK_CHART_414_REMAINDER_LINE_3
EXPORTS = ("ca-qc/work_chart_414_remainder_line_3",)


@pytest.mark.parametrize(
    ("contributions", "expected"),
    [("30", "0.00"), ("100", "50.00"), ("400", "150.00")],  # line 1 less line 2
)
def test_line_3_is_line_1_less_line_2(
    take_home_service: TakeHomeService, contributions: str, expected: str
) -> None:
    sheet = chart_sheet(take_home_service, EXPORTS, LINE_3_PARTS, contributions)

    assert str(sheet.get(LINE).value) == expected


def test_the_part_takes_line_2_off_line_1() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / "work_chart_414_line_3.yaml").read_text("utf-8"))

    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step["name"] in {"core/subtract", "core/subtract_not_below_zero"}
    assert step["reference"] == "3"
    assert step["params"] == {"rounding": "ca-qc/cent_rounding"}
    assert step["consumes"] == {
        "amount": "ca-qc/work_chart_414_contributions_line_1",
        "less": "ca-qc/work_chart_414_lesser_line_2",
    }
    assert step["produces"] == {"output": "ca-qc/work_chart_414_remainder_line_3"}
