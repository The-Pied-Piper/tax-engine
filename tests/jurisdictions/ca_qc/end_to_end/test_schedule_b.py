"""Revenu Quebec TP-1.D.B-V (2025-12) Schedule B, lines 10 to 34, as one chain.

The chain runs the real form declaration and the real parts of the Schedule B lines and of the forms
they read: TP-1 net income (line 275), line 199, Work Chart 201 and Schedule U (whose TP-1 slip
figures are plain starting inputs, as in its own tests). The salary is $20,000, $70,000 and
$200,000. Lines 12 and 33 are left blank, read as 0. The expected figures are hand-computed from the
printed lines (not an official example): line 10 and line 14 are line 275; line 18 is line 14 less
42,090.00 (not below zero); line 31 is line 18 at 18.75%; line 20 is 2,128.00 only for a person
living alone whose line 18 is not more than 64,699; line 34 is line 32 less line 33.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LINE_10,
    SCHEDULE_B_LINE_14,
    SCHEDULE_B_LINE_16,
    SCHEDULE_B_LINE_18,
    SCHEDULE_B_LINE_20,
    SCHEDULE_B_LINE_30,
    SCHEDULE_B_LINE_31,
    SCHEDULE_B_LINE_32,
    SCHEDULE_B_LINE_34,
    SCHEDULE_B_LIVED_ALONE_LINE_20,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import LINE_31_PARTS, schedule_b_sheet

FORM = (QUEBEC_PARTS / "schedule_b.yaml").read_text(encoding="utf-8")
PARTS = (
    *LINE_31_PARTS,
    "schedule_b_line_32.yaml",
    "schedule_b_line_33_input.yaml",
    "schedule_b_line_34.yaml",
)
# salary: lines 10, 14, 16, 18 and 31 (the same whether or not the filer lives alone)
FAMILY_INCOME = {
    "20000": ("18635.00", "18635.00", "42090.00", "0.00", "0.00"),
    "70000": ("67915.00", "67915.00", "42090.00", "25825.00", "4842.19"),
    "200000": ("197506.00", "197506.00", "42090.00", "155416.00", "29140.50"),
}
# salary: lines 20, 30, 32 and 34, by the answer to "lived alone"
RELIEF = {
    ("20000", 0): ("0.00", "0.00", "0.00", "0.00"),
    ("70000", 0): ("0.00", "0.00", "0.00", "0.00"),
    ("200000", 0): ("0.00", "0.00", "0.00", "0.00"),
    ("20000", 1): ("2128.00", "2128.00", "2128.00", "2128.00"),
    # Line 31 (4,842.19) is more than line 30 (2,128.00): line 32 is entered as 0.
    ("70000", 1): ("2128.00", "2128.00", "0.00", "0.00"),
    # Line 18 is more than 64,699: line 20 is 0.
    ("200000", 1): ("0.00", "0.00", "0.00", "0.00"),
}


def _sheet(take_home_service: TakeHomeService, salary: str, alone: int | None) -> Worksheet:
    given: list[Artifact[Any]] = []
    if alone is not None:
        given.append(Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, alone))
    return schedule_b_sheet(take_home_service, salary, (), PARTS, *given, form=FORM)


@pytest.mark.parametrize("salary", list(FAMILY_INCOME))
def test_the_family_income_lines_from_line_10_to_line_31(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = _sheet(take_home_service, salary, None)

    kinds = (
        SCHEDULE_B_LINE_10,
        SCHEDULE_B_LINE_14,
        SCHEDULE_B_LINE_16,
        SCHEDULE_B_LINE_18,
        SCHEDULE_B_LINE_31,
    )
    assert tuple(str(sheet.get(kind).value) for kind in kinds) == FAMILY_INCOME[salary]


@pytest.mark.parametrize(("salary", "alone"), list(RELIEF))
def test_the_amount_for_a_person_living_alone_from_line_20_to_line_34(
    take_home_service: TakeHomeService, salary: str, alone: int
) -> None:
    sheet = _sheet(take_home_service, salary, alone)

    kinds = (SCHEDULE_B_LINE_20, SCHEDULE_B_LINE_30, SCHEDULE_B_LINE_32, SCHEDULE_B_LINE_34)
    assert tuple(str(sheet.get(kind).value) for kind in kinds) == RELIEF[(salary, alone)]


def test_a_caller_who_gives_no_answer_gets_the_default_not_alone(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000", None)

    assert str(sheet.get(SCHEDULE_B_LINE_34).value) == "0.00"
