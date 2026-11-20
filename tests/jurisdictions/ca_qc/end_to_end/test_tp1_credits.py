"""Revenu Quebec TP-1.D-V (2025-12), page 4, lines 350 to 399, as one chain.

The chain runs the real form declaration and the real parts of the credit lines and of the forms
they read: Schedule B (line 34), TP-1 net income (line 275), line 199, Work Chart 201 and Schedule
U (whose TP-1 slip figures are plain starting inputs, as in its own tests). The salary is $20,000,
$70,000 and $200,000. Every optional line (358, 388, 397.1, 390, 391, 392, 395, 396, 398 and 398.1)
is left blank, read as 0; the answer to "lived alone" is the default (not alone) unless given. The
expected figures are hand-computed from the printed lines (not an official example): line 350 is
the printed 18,571.00; line 359 is line 350 less line 358; line 361 is Schedule B line 34; line 377
is lines 359 and 361; line 377.1 is line 377 at 14%; lines 388, 389 and 397 are 0.00; line 399 adds
lines 377.1, 389 and 397.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361,
    TP1_BASIC_PERSONAL_AMOUNT_LINE_350,
    TP1_LINE_359,
    TP1_LINE_377,
    TP1_LINE_377_1,
    TP1_LINE_389,
    TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_399,
    TP1_UNION_DUES_CREDIT_LINE_397,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.tp1_credits_support import LINE_399_PARTS, chain_sheet

FORM = (QUEBEC_PARTS / "tp1_credits.yaml").read_text(encoding="utf-8")
KINDS = (
    TP1_BASIC_PERSONAL_AMOUNT_LINE_350,
    TP1_LINE_359,
    TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361,
    TP1_LINE_377,
    TP1_LINE_377_1,
    TP1_LINE_389,
    TP1_UNION_DUES_CREDIT_LINE_397,
    TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_399,
)
# Lines 350, 359, 361, 377, 377.1, 389, 397 and 399, by salary and the answer to "lived alone".
NOT_ALONE = ("18571.00", "18571.00", "0.00", "18571.00", "2599.94", "0.00", "0.00", "2599.94")
ALONE = ("18571.00", "18571.00", "2128.00", "20699.00", "2897.86", "0.00", "0.00", "2897.86")
EXPECTED = {
    ("20000", 0): NOT_ALONE,
    ("70000", 0): NOT_ALONE,
    ("200000", 0): NOT_ALONE,
    ("20000", 1): ALONE,
    # Schedule B line 31 is more than line 30 at $70,000, and line 18 is more than 64,699 at
    # $200,000: line 34 is 0.00 either way, so a person living alone gets nothing more there.
    ("70000", 1): NOT_ALONE,
    ("200000", 1): NOT_ALONE,
}


def _sheet(take_home_service: TakeHomeService, salary: str, alone: int | None) -> Worksheet:
    given: list[Artifact[Any]] = []
    if alone is not None:
        given.append(Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, alone))
    return chain_sheet(take_home_service, salary, (), LINE_399_PARTS, *given, form=FORM)


@pytest.mark.parametrize(("salary", "alone"), list(EXPECTED))
def test_the_lines_from_350_to_399(
    take_home_service: TakeHomeService, salary: str, alone: int
) -> None:
    sheet = _sheet(take_home_service, salary, alone)

    assert tuple(str(sheet.get(kind).value) for kind in KINDS) == EXPECTED[(salary, alone)]


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_caller_who_gives_no_answer_gets_the_default_not_alone(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = _sheet(take_home_service, salary, None)

    assert tuple(str(sheet.get(kind).value) for kind in KINDS) == EXPECTED[(salary, 0)]


def test_the_form_exports_line_399(take_home_service: TakeHomeService) -> None:
    sheet = _sheet(take_home_service, "70000", None)

    assert str(sheet.get(TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_399).value) == "2599.94"
