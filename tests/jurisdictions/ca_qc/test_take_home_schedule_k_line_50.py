"""Schedule K (2025) line 50, the group plan answer, as the real parts wire it.

Form text (Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part B, section 1): "You were covered by
basic prescription drug insurance provided by a group insurance plan (see line 447 in the guide) of
which you, your spouse, your father or your mother was a member, and this plan covered the cost of
medications. ... 50 Yes". The answer is an optional input, a count of 1 for yes and 0 for no; a
request that gives none is read as 0 (owner ruling 19 Nov 2026). `ca/yes_or_no_count` checks it and
refuses a count above 1. The answer does not depend on the salary.

The real input part and line part are composed under a test-local header and form declaration over
the Quebec package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import CountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_GROUP_PLAN_COVERED_CHECKED_LINE_50,
    SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

D = Decimal
INPUT_PART = QUEBEC_PARTS / "tp1_schedule_k_line_50_input.yaml"
LINE_PART = QUEBEC_PARTS / "tp1_schedule_k_line_50.yaml"
FORM = "ca-qc/tp1_schedule_k"
CHECKED = "ca-qc/schedule_k_group_plan_covered_checked_line_50"
HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM_PART = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {CHECKED}
    capabilities: []
    """)


def _line_50(take_home_service: TakeHomeService, salary: str, answer: int | None = None) -> int:
    given: list[Artifact[Any]] = []
    if answer is not None:
        given.append(Artifact(SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, answer))
    worksheets = take_home_service(
        HEADER, FORM_PART, *(part.name for part in (INPUT_PART, LINE_PART))
    ).compute(JurisdictionCode("CA-QC"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet.get(SCHEDULE_K_GROUP_PLAN_COVERED_CHECKED_LINE_50).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_50_is_0_when_the_caller_gives_no_answer(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert _line_50(take_home_service, salary) == 0


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_50_is_1_when_the_answer_is_yes(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert _line_50(take_home_service, salary, 1) == 1


def test_line_50_is_0_when_the_answer_is_no(take_home_service: TakeHomeService) -> None:
    assert _line_50(take_home_service, "70000", 0) == 0


def test_an_answer_above_1_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_50(take_home_service, "70000", 2)


def test_the_input_part_declares_the_optional_answer_with_the_default_0() -> None:
    part = yaml.safe_load(INPUT_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": FORM}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": "ca-qc/schedule_k_group_plan_covered_line_50",
        "title": (
            "You were covered by basic prescription drug insurance provided by a group "
            "insurance plan "
            "of which you, your spouse, your father or your mother was a member, "
            "and this plan covered the cost of medications"
        ),
        "reference": "50",
        "required": False,
        "default": "0",
        "basis": (
            "You were covered by basic prescription drug insurance provided by a group "
            "insurance plan "
            "(see line 447 in the guide) of which you, your spouse, your father or your mother "
            "was a member, and this plan covered the cost of medications"
        ),
    }


def test_the_line_part_is_one_yes_or_no_check() -> None:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "ca/yes_or_no_count",
        "title": "Covered by a group drug plan, checked",
        "consumes": {"count": "ca-qc/schedule_k_group_plan_covered_line_50"},
        "blank": {"count": "pass_on"},
        "produces": {"output": CHECKED},
    }


@pytest.mark.parametrize(
    "kind", [SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, SCHEDULE_K_GROUP_PLAN_COVERED_CHECKED_LINE_50]
)
def test_the_kinds_are_registered_non_negative_counts(kind: CountKind) -> None:
    assert quebec_kinds().kind(kind.identifier) is kind
    assert isinstance(kind, CountKind)
    assert kind.value_type is int
    assert non_negative(kind)
