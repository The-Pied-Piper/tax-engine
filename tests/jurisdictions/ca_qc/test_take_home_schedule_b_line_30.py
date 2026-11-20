"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part B line 30, "Add lines 20 through 28", as the Quebec
take-home manifest wires it: one `core/sum` over line 20 alone (lines 21, 22, 23, 27 and 28 are not
built), rounded half-up to the cent by `ca-qc/cent_rounding`. The expected figures are hand-computed
from the printed lines, not a Revenu Quebec example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LINE_30,
    SCHEDULE_B_LIVED_ALONE_LINE_20,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import LINE_20_PARTS, schedule_b_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = "schedule_b_line_30.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_line_30"
EXPORTS = (IDENTIFIER,)
PARTS = (*LINE_20_PARTS, PART)


def line_30(take_home_service: TakeHomeService, salary: str, *given: Artifact[Any]) -> str:
    sheet = schedule_b_sheet(take_home_service, salary, EXPORTS, PARTS, *given)
    return str(sheet.get(SCHEDULE_B_LINE_30).value)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_30_is_0_when_not_alone(take_home_service: TakeHomeService, salary: str) -> None:
    assert line_30(take_home_service, salary) == "0.00"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2128.00"), ("70000", "2128.00"), ("200000", "0.00")],
)
def test_line_30_is_line_20_when_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)

    assert line_30(take_home_service, salary, given) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_sum_of_line_20_alone() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "30",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {"parts": ["ca-qc/schedule_b_line_20"]},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SCHEDULE_B_LINE_30
    assert isinstance(SCHEDULE_B_LINE_30, AmountKind)
    assert non_negative(SCHEDULE_B_LINE_30)
