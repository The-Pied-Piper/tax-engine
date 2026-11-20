"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part B line 34, "Subtract line 33 from line 32. Carry the
result to line 361 of your return. Age amount, amount for a person living alone and amount for
retirement income", as the Quebec take-home manifest wires it: one `core/subtract`, rounded half-up
to the cent by `ca-qc/cent_rounding`. The form prints no floor, so the result can be negative. Line
33 (the amount claimed on the spouse's line 361) is an optional input, read as 0 when the caller
leaves it out. The expected figures are hand-computed from the printed lines, not a Revenu Quebec
example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LINE_33,
    SCHEDULE_B_LINE_34,
    SCHEDULE_B_LIVED_ALONE_LINE_20,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import LINE_31_PARTS, schedule_b_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds

D = Decimal
PART = "schedule_b_line_34.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_line_34"
EXPORTS = (IDENTIFIER,)
PARTS = (*LINE_31_PARTS, "schedule_b_line_32.yaml", "schedule_b_line_33_input.yaml", PART)
ALONE = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)


def line_34(take_home_service: TakeHomeService, salary: str, *given: Artifact[Any]) -> str:
    sheet = schedule_b_sheet(take_home_service, salary, EXPORTS, PARTS, *given)
    return str(sheet.get(SCHEDULE_B_LINE_34).value)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_34_is_0_by_default(take_home_service: TakeHomeService, salary: str) -> None:
    assert line_34(take_home_service, salary) == "0.00"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2128.00"), ("70000", "0.00"), ("200000", "0.00")],
)
def test_line_34_when_alone_with_line_33_blank(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_34(take_home_service, salary, ALONE) == expected


def test_line_33_is_subtracted(take_home_service: TakeHomeService) -> None:
    given = (ALONE, Artifact(SCHEDULE_B_LINE_33, D("500.25")))

    assert line_34(take_home_service, "20000", *given) == "1627.75"


def test_a_line_33_above_line_32_gives_a_negative_result_as_the_form_prints_no_floor(
    take_home_service: TakeHomeService,
) -> None:
    given = (ALONE, Artifact(SCHEDULE_B_LINE_33, D("3000")))

    assert line_34(take_home_service, "20000", *given) == "-872.00"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_subtract_of_line_33_from_line_32_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract",
        "title": (
            "Age amount, amount for a person living alone and amount for retirement income"
        ),
        "reference": "34",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/schedule_b_line_32",
            "less": "ca-qc/schedule_b_line_33",
        },
        "blank": {"less": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is SCHEDULE_B_LINE_34
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
