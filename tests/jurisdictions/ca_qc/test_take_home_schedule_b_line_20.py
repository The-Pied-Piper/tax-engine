"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part B line 20, the amount for a person living alone, as
the Quebec take-home manifest wires it, in five steps (as ON428 line 80 and NL428 line 40):

Line 20: "If, throughout 2025, you maintained and ordinarily lived in a dwelling in which you lived
alone or only with one or more individuals under the age of 18, or with one or more of your
children, grandchildren or great-grandchildren 18 or older who were full-time students ... enter
$2,128." Part A: "You are not entitled to any of these amounts if ... you did not have a spouse on
December 31, 2025, and the amount on line 18 is more than $64,699."

The answer "lived alone" is an optional input with the default 0 (not alone, owner ruling 19 Nov
2026), checked by `ca/yes_or_no_count`. The expected figures are hand-computed from the printed
lines (line 18 is 0.00 / 25,825.00 / 155,416.00 at a salary of 20,000 / 70,000 / 200,000), not a
Revenu Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LINE_18_GATE_COUNT_LINE_20,
    SCHEDULE_B_LINE_20,
    SCHEDULE_B_LIVED_ALONE_CHECKED_LINE_20,
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    SCHEDULE_B_LIVING_ALONE_AMOUNT_IF_ALONE_LINE_20,
    SCHEDULE_B_LIVING_ALONE_AMOUNT_LINE_20,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import schedule_b_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

D = Decimal
INPUT_PART = "schedule_b_line_20_input.yaml"
PART = "schedule_b_line_20.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_line_20"
EXPORTS = (IDENTIFIER,)
PARTS = (
    "schedule_b_line_10.yaml",
    "schedule_b_line_16.yaml",
    "schedule_b_line_18.yaml",
    INPUT_PART,
    PART,
)
ALONE = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)


def line_20(take_home_service: TakeHomeService, salary: str, *given: Artifact[Any]) -> str:
    sheet = schedule_b_sheet(take_home_service, salary, EXPORTS, PARTS, *given)
    return str(sheet.get(SCHEDULE_B_LINE_20).value)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_20_is_0_when_the_caller_gives_no_answer(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert line_20(take_home_service, salary) == "0.00"


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_20_is_0_when_the_answer_is_no(
    take_home_service: TakeHomeService, salary: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 0)

    assert line_20(take_home_service, salary, given) == "0.00"


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "2128.00"),
        ("70000", "2128.00"),
        # Line 18 is 155,416.00, more than 64,699: not entitled to the amount.
        ("200000", "0.00"),
    ],
)
def test_line_20_when_the_answer_is_yes(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_20(take_home_service, salary, ALONE) == expected


def test_an_answer_above_1_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(InputAboveBoundError):
        line_20(take_home_service, "70000", Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 2))


def _part(name: str) -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_input_part_declares_the_optional_answer_with_the_default_0() -> None:
    part = _part(INPUT_PART)

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": FORM}
    (declaration,) = part["inputs"]
    assert declaration["name"] == "ca-qc/schedule_b_lived_alone_line_20"
    assert declaration["reference"] == "20"
    assert declaration["required"] is False
    assert declaration["default"] == "0"
    assert "lived alone" in declaration["basis"]


def test_the_line_part_is_five_steps_and_only_the_last_carries_the_reference() -> None:
    part = _part(PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    steps = part["capabilities"]
    assert [step["name"] for step in steps] == [
        "ca/yes_or_no_count",
        "core/credit_amount",
        "ca/count_by_conditions",
        "core/times_count",
        "core/times_count",
    ]
    assert [step.get("reference") for step in steps] == [None, None, None, None, "20"]
    assert [step["produces"]["output"] for step in steps] == [
        "ca-qc/schedule_b_lived_alone_checked_line_20",
        "ca-qc/schedule_b_living_alone_amount_line_20",
        "ca-qc/schedule_b_line_18_gate_count_line_20",
        "ca-qc/schedule_b_living_alone_amount_if_alone_line_20",
        IDENTIFIER,
    ]
    assert steps[0]["blank"] == {"count": "0"}
    assert steps[1]["params"] == {"amount": "ca-qc/schedule_b_living_alone_amount_line_20"}
    assert steps[2]["params"] == {"conditions": "ca-qc/schedule_b_line_20_conditions"}
    assert steps[2]["consumes"] == {"counts": [], "amounts": ["ca-qc/schedule_b_line_18"]}
    assert steps[3]["consumes"] == {
        "amount": "ca-qc/schedule_b_living_alone_amount_line_20",
        "count": "ca-qc/schedule_b_lived_alone_checked_line_20",
    }
    assert steps[4]["consumes"] == {
        "amount": "ca-qc/schedule_b_living_alone_amount_if_alone_line_20",
        "count": "ca-qc/schedule_b_line_18_gate_count_line_20",
    }


@pytest.mark.parametrize(
    "kind",
    [
        SCHEDULE_B_LIVED_ALONE_LINE_20,
        SCHEDULE_B_LIVED_ALONE_CHECKED_LINE_20,
        SCHEDULE_B_LINE_18_GATE_COUNT_LINE_20,
    ],
)
def test_the_count_kinds_are_registered_non_negative_counts(kind: CountKind) -> None:
    assert quebec_kinds().kind(kind.identifier) is kind
    assert isinstance(kind, CountKind)
    assert kind.value_type is int
    assert non_negative(kind)


@pytest.mark.parametrize(
    "kind",
    [
        SCHEDULE_B_LIVING_ALONE_AMOUNT_LINE_20,
        SCHEDULE_B_LIVING_ALONE_AMOUNT_IF_ALONE_LINE_20,
        SCHEDULE_B_LINE_20,
    ],
)
def test_the_amount_kinds_are_registered_non_negative_amounts(kind: AmountKind) -> None:
    assert quebec_kinds().kind(kind.identifier) is kind
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
