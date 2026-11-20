"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part B line 32, "Subtract line 31 from line 30. If the
result is negative, enter 0. Amount to which you or, if applicable, your spouse is entitled", as the
Quebec take-home manifest wires it: one `core/subtract_not_below_zero`, rounded half-up to the cent
by `ca-qc/cent_rounding`. The expected figures are hand-computed from the printed lines, not a
Revenu Quebec example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LINE_32,
    SCHEDULE_B_LIVED_ALONE_LINE_20,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import LINE_31_PARTS, schedule_b_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = "schedule_b_line_32.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_line_32"
EXPORTS = (IDENTIFIER,)
PARTS = (*LINE_31_PARTS, PART)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_32_is_0_when_not_alone(take_home_service: TakeHomeService, salary: str) -> None:
    value = schedule_b_sheet(take_home_service, salary, EXPORTS, PARTS).get(SCHEDULE_B_LINE_32)

    assert str(value.value) == "0.00"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 30 is 2,128.00 and line 31 is 0.00.
        ("20000", "2128.00"),
        # Line 31 is 4,842.19, more than line 30 (2,128.00): the negative result is entered as 0.
        ("70000", "0.00"),
        # Line 30 is 0.00 (line 18 is above 64,699) and line 31 is 29,140.50.
        ("200000", "0.00"),
    ],
)
def test_line_32_when_alone(take_home_service: TakeHomeService, salary: str, expected: str) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)
    sheet = schedule_b_sheet(take_home_service, salary, EXPORTS, PARTS, given)

    assert str(sheet.get(SCHEDULE_B_LINE_32).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_subtract_not_below_zero_of_line_31_from_line_30() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "title": "Amount to which you or, if applicable, your spouse is entitled",
        "reference": "32",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/schedule_b_line_30",
            "less": "ca-qc/schedule_b_line_31",
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SCHEDULE_B_LINE_32
    assert isinstance(SCHEDULE_B_LINE_32, AmountKind)
    assert non_negative(SCHEDULE_B_LINE_32)
