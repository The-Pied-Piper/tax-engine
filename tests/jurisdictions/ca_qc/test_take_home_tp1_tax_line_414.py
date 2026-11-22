"""Revenu Quebec TP-1 (2025) line 414, "Tax credit for contributions to authorized Québec political
parties", as the Quebec take-home manifest wires it: one `core/record_total` over the line 14
export of `ca-qc/work_chart_414`. The chart is the only source of the line (it is no longer an
input), and its line 14 is always computed, so the line is 0.00 when no contributions are given.
The chain runs the real parts of the chart. The expected figures are hand-computed from the printed
chart, not a Revenu Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_414,
    WORK_CHART_414_CONTRIBUTIONS_INPUT_LINE_1,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import UPSTREAM_PARTS
from tests.jurisdictions.ca_qc.tp1_tax_support import LINE_414_PARTS, tax_sheet

D = Decimal
PART = "tp1_tax_line_414.yaml"
FORM = "ca-qc/tp1_tax"
IDENTIFIER = "ca-qc/tp1_line_414"
EXPORTS = (IDENTIFIER,)
PARTS = (*UPSTREAM_PARTS, *LINE_414_PARTS)


@pytest.mark.parametrize(
    ("contributions", "expected"),
    [(None, "0.00"), ("30", "25.50"), ("100", "80.00"), ("400", "155.00")],
)
def test_line_414_is_work_chart_414_line_14(
    take_home_service: TakeHomeService, contributions: str | None, expected: str
) -> None:
    given = (
        []
        if contributions is None
        else [Artifact(WORK_CHART_414_CONTRIBUTIONS_INPUT_LINE_1, D(contributions))]
    )
    sheet = tax_sheet(take_home_service, "70000", EXPORTS, PARTS, *given)

    assert str(sheet.get(TP1_LINE_414).value) == expected


def test_the_part_is_one_record_total_over_the_chart_export() -> None:
    part: dict[str, Any] = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))

    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step["name"] == "core/record_total"
    assert step["reference"] == "414"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"records": "ca-qc/work_chart_414.work_chart_414_credit_line_14"}
    assert step["produces"] == {"output": IDENTIFIER}
    assert "blank" not in step
