"""Schedule K (2025) box 62, the months checked in the year, as the real parts wire it.

Form text (Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part B, section 1): "Add boxes 60 and
61. = 62". `core/sum` adds the two boxes, which are 6 months each when the answer to line 50 is yes
and 0 each when it is no, so box 62 is 12 or 0. The months are hand-computed, not printed, and do
not depend on the salary. The real form declaration is checked on its own: it exports box 62.

The real input part and the parts of line 50 and boxes 60, 61 and 62 are composed under a test-local
header and form declaration over the Quebec package list of `support.py`.
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
    SCHEDULE_K_MONTHS_TOTAL_BOX_62,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

D = Decimal
INPUT_PART = QUEBEC_PARTS / "tp1_schedule_k_line_50_input.yaml"
LINE_PARTS = (
    QUEBEC_PARTS / "tp1_schedule_k_line_50.yaml",
    QUEBEC_PARTS / "tp1_schedule_k_box_60.yaml",
    QUEBEC_PARTS / "tp1_schedule_k_box_61.yaml",
)
LINE_PART = QUEBEC_PARTS / "tp1_schedule_k_box_62.yaml"
FORM_DECLARATION = QUEBEC_PARTS / "tp1_schedule_k.yaml"
FORM = "ca-qc/tp1_schedule_k"
BOX_62 = "ca-qc/schedule_k_months_total_box_62"
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
        - {BOX_62}
    capabilities: []
    """)


def _box_62(take_home_service: TakeHomeService, salary: str, answer: int | None = None) -> Decimal:
    given: list[Artifact[Any]] = []
    if answer is not None:
        given.append(Artifact(SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, answer))
    worksheets = take_home_service(
        HEADER, FORM_PART, *(part.name for part in (INPUT_PART, *LINE_PARTS, LINE_PART))
    ).compute(JurisdictionCode("CA-QC"), 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet.get(SCHEDULE_K_MONTHS_TOTAL_BOX_62).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_box_62_is_0_by_default(take_home_service: TakeHomeService, salary: str) -> None:
    assert _box_62(take_home_service, salary) == D("0.00")


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_box_62_is_12_when_line_50_is_yes(take_home_service: TakeHomeService, salary: str) -> None:
    assert _box_62(take_home_service, salary, 1) == D("12.00")


def test_box_62_is_0_when_line_50_is_no(take_home_service: TakeHomeService) -> None:
    assert _box_62(take_home_service, "70000", 0) == D("0.00")


def test_an_answer_above_1_is_refused_before_box_62(take_home_service: TakeHomeService) -> None:
    with pytest.raises(InputAboveBoundError):
        _box_62(take_home_service, "70000", 2)


def test_the_part_is_one_sum_of_boxes_60_and_61() -> None:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "62",
        "unit": "core/months",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-qc/schedule_k_months_january_to_june_box_60",
                "ca-qc/schedule_k_months_july_to_december_box_61",
            ]
        },
        "produces": {"output": BOX_62},
    }


def test_the_form_declaration_exports_box_62() -> None:
    declaration = yaml.safe_load(FORM_DECLARATION.read_text(encoding="utf-8"))

    assert declaration["form"]["name"] == FORM
    assert declaration["form"]["required"] is True
    assert BOX_62 in declaration["form"]["exports"]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(BOX_62)

    assert kind is SCHEDULE_K_MONTHS_TOTAL_BOX_62
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
