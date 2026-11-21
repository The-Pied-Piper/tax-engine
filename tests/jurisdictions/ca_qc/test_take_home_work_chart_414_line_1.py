"""Revenu Quebec Work Chart 414 (TP-1.D.GR-V 2025-12) line 1, "Contributions to authorized Québec
municipal political parties (maximum $200)", as the Quebec take-home manifest parts wire it. The
contributions are the chart's only input, optional (a blank is read as 0); the step is
`core/capped_amount` against the printed $200 (`ca-qc/work_chart_414_line_1_maximum`). The expected
figures are hand-computed from the printed line (not an official example).
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    WORK_CHART_414_CONTRIBUTIONS_INPUT_LINE_1,
    WORK_CHART_414_CONTRIBUTIONS_LINE_1,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.work_chart_414_support import (
    FORM_NAME,
    LINE_1_PARTS,
    chart_sheet,
)
from tests.kinds import non_negative

LINE = WORK_CHART_414_CONTRIBUTIONS_LINE_1
INPUT = "ca-qc/work_chart_414_contributions_input_line_1"
IDENTIFIER = "ca-qc/work_chart_414_contributions_line_1"
EXPORTS = (IDENTIFIER,)


@pytest.mark.parametrize(
    ("contributions", "expected"),
    [
        (None, "0.00"),  # left blank
        ("150.25", "150.25"),  # below the maximum
        ("200", "200.00"),  # the maximum itself
        ("400", "200.00"),  # above it
    ],
)
def test_line_1_is_the_contributions_up_to_200(
    take_home_service: TakeHomeService, contributions: str | None, expected: str
) -> None:
    sheet = chart_sheet(take_home_service, EXPORTS, LINE_1_PARTS, contributions)

    assert str(sheet.get(LINE).value) == expected


def _part(name: str) -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_input_part_declares_the_one_optional_contributions_input() -> None:
    part = _part("work_chart_414_line_1_input.yaml")

    assert part["form"] == {"name": FORM_NAME}
    (declared,) = part["inputs"]
    assert declared["name"] == INPUT
    assert declared["reference"] == "1"
    assert declared["required"] is False


def test_the_step_is_the_contributions_capped_at_the_printed_maximum() -> None:
    part = _part("work_chart_414_line_1.yaml")

    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/capped_amount",
        "reference": "1",
        "unit": "ca/cad",
        "params": {"cap": "ca-qc/work_chart_414_line_1_maximum"},
        "consumes": {"base": INPUT},
        "produces": {"output": IDENTIFIER},
    }


def test_the_input_kind_is_registered_and_non_negative() -> None:
    kind = quebec_kinds().kind(INPUT)

    assert kind is WORK_CHART_414_CONTRIBUTIONS_INPUT_LINE_1
    assert non_negative(kind)
