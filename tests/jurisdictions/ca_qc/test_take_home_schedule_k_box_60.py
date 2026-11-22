"""Schedule K (2025) box 60, the months checked from January to June, as the real parts wire it.

Form text (Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part B, section 1): "Number of months
checked from January to June ... 60". The form prints no table; the box counts the months checked
for line 50, and the answer to line 50 means covered all year (owner's optional-answer ruling, 19
Nov 2026), so a yes is 6 months of the half and a no is 0. The `ca-qc/schedule_k_months_box_60`
dataset holds those two rows and `ca/amount_by_count` reads the checked answer. The months are
hand-computed, not printed, and do not depend on the salary.

The real input part, the line 50 part and the box 60 part are composed under a test-local header
and form declaration over the Quebec package list of `support.py`.
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
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50,
    SCHEDULE_K_MONTHS_JANUARY_TO_JUNE_BOX_60,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

D = Decimal
INPUT_PART = QUEBEC_PARTS / "tp1_schedule_k_line_50_input.yaml"
LINE_50_PART = QUEBEC_PARTS / "tp1_schedule_k_line_50.yaml"
LINE_PART = QUEBEC_PARTS / "tp1_schedule_k_box_60.yaml"
FORM = "ca-qc/tp1_schedule_k"
BOX_60 = "ca-qc/schedule_k_months_january_to_june_box_60"
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
        - {BOX_60}
    capabilities: []
    """)


def _box_60(take_home_service: TakeHomeService, salary: str, answer: int | None = None) -> Decimal:
    given: list[Artifact[Any]] = []
    if answer is not None:
        given.append(Artifact(SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, answer))
    worksheets = take_home_service(
        HEADER, FORM_PART, *(part.name for part in (INPUT_PART, LINE_50_PART, LINE_PART))
    ).compute(JurisdictionCode("CA-QC"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet.get(SCHEDULE_K_MONTHS_JANUARY_TO_JUNE_BOX_60).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_box_60_is_0_by_default(take_home_service: TakeHomeService, salary: str) -> None:
    assert _box_60(take_home_service, salary) == D("0.00")


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_box_60_is_6_when_line_50_is_yes(take_home_service: TakeHomeService, salary: str) -> None:
    assert _box_60(take_home_service, salary, 1) == D("6.00")


def test_box_60_is_0_when_line_50_is_no(take_home_service: TakeHomeService) -> None:
    assert _box_60(take_home_service, "70000", 0) == D("0.00")


def test_an_answer_above_1_is_refused_before_box_60(take_home_service: TakeHomeService) -> None:
    with pytest.raises(InputAboveBoundError):
        _box_60(take_home_service, "70000", 2)


def test_the_part_is_one_amount_by_count_step_on_the_checked_answer() -> None:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "ca/amount_by_count",
        "title": "Number of months checked from January to June",
        "reference": "60",
        "unit": "core/months",
        "params": {"table": "ca-qc/schedule_k_months_box_60"},
        "consumes": {"count": "ca-qc/schedule_k_group_plan_covered_checked_line_50"},
        "produces": {"output": BOX_60},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(BOX_60)

    assert kind is SCHEDULE_K_MONTHS_JANUARY_TO_JUNE_BOX_60
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
