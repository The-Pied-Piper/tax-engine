"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part A line 14, "Add lines 10 and 12. Family income", as
the Quebec take-home manifest wires it: one `core/sum`, rounded half-up to the cent by
`ca-qc/cent_rounding`. Line 12 (the spouse's line 275) is an optional input, read as 0 when the
caller leaves it out. The expected figures are hand-computed from the printed lines (line 10 is line
275 at a salary of 20,000 / 70,000 / 200,000), not a Revenu Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_LINE_12, SCHEDULE_B_LINE_14
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import LINE_275, schedule_b_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

D = Decimal
PART = "schedule_b_line_14.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_line_14"
EXPORTS = (IDENTIFIER,)
PARTS = ("schedule_b_line_10.yaml", "schedule_b_line_12_input.yaml", PART)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_14_is_line_10_when_line_12_is_left_blank(
    take_home_service: TakeHomeService, salary: str
) -> None:
    value = schedule_b_sheet(take_home_service, salary, EXPORTS, PARTS).get(SCHEDULE_B_LINE_14)

    assert str(value.value) == LINE_275[salary]


def test_line_12_is_added(take_home_service: TakeHomeService) -> None:
    given = Artifact(SCHEDULE_B_LINE_12, D("10000.50"))
    value = schedule_b_sheet(take_home_service, "70000", EXPORTS, PARTS, given)

    assert str(value.get(SCHEDULE_B_LINE_14).value) == "77915.50"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_sum_of_lines_10_and_12_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": "Family income",
        "reference": "14",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {"parts": ["ca-qc/schedule_b_line_10", "ca-qc/schedule_b_line_12"]},
        "blank": {"ca-qc/schedule_b_line_12": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SCHEDULE_B_LINE_14
    assert isinstance(SCHEDULE_B_LINE_14, AmountKind)
    assert non_negative(SCHEDULE_B_LINE_14)
