"""Revenu Quebec TP-1.D-V (2025-12), page 4, lines 401 to 413, as one chain.

The chain runs the real form declaration and the real parts of lines 401, 406 and 413 and of the
forms they read: Work Chart 401 (line 8), the credits lines (line 399), Schedule B, the TP-1 net
income lines and Schedule U (whose TP-1 slip figures are plain starting inputs, as in its own
tests). The salary is $20,000, $70,000 and $200,000. The answer to "lived alone" is the default
(not alone) unless given. Each expected figure is recomputed in the test from the printed lines:
line 413 is line 401 less line 406. The expected figures are hand-computed from the printed forms
(not an official example).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    TP1_INCOME_TAX_ON_TAXABLE_INCOME_LINE_401,
    TP1_LINE_413,
    TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_406,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.tp1_tax_support import LINE_401_CHAIN, LINE_406_CHAIN, tax_sheet

D = Decimal
FORM = (QUEBEC_PARTS / "tp1_tax.yaml").read_text(encoding="utf-8")
PARTS = (
    *dict.fromkeys((*LINE_401_CHAIN, *LINE_406_CHAIN)),
    "tp1_tax_line_401.yaml",
    "tp1_tax_line_406.yaml",
    "tp1_tax_line_413.yaml",
)
# salary, lived alone: lines 401, 406 and 413 as the printed lines give them.
EXPECTED = {
    ("20000", 0): ("2608.90", "2599.94", "8.96"),
    ("70000", 0): ("10241.10", "2599.94", "7641.16"),
    ("200000", 0): ("40602.47", "2599.94", "38002.53"),
    ("20000", 1): ("2608.90", "2897.86", "-288.96"),
    # Schedule B line 34 is 0.00 at these salaries, so living alone changes nothing.
    ("70000", 1): ("10241.10", "2599.94", "7641.16"),
    ("200000", 1): ("40602.47", "2599.94", "38002.53"),
}


def _given(alone: int | None) -> list[Artifact[Any]]:
    return [] if alone is None else [Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, alone)]


@pytest.mark.parametrize(("salary", "alone"), list(EXPECTED))
def test_the_chain_from_line_401_to_line_413(
    take_home_service: TakeHomeService, salary: str, alone: int
) -> None:
    sheet = tax_sheet(take_home_service, salary, (), PARTS, *_given(alone), form=FORM)

    line_401 = sheet.get(TP1_INCOME_TAX_ON_TAXABLE_INCOME_LINE_401).value
    line_406 = sheet.get(TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_406).value
    assert (str(line_401), str(line_406)) == EXPECTED[(salary, alone)][:2]
    assert sheet.get(TP1_LINE_413).value == line_401 - line_406
    assert str(sheet.get(TP1_LINE_413).value) == EXPECTED[(salary, alone)][2]


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_caller_who_gives_no_answer_gets_the_default_not_alone(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = tax_sheet(take_home_service, salary, (), PARTS, form=FORM)

    assert str(sheet.get(TP1_LINE_413).value) == EXPECTED[(salary, 0)][2]


def test_the_form_exports_line_413(take_home_service: TakeHomeService) -> None:
    sheet = tax_sheet(take_home_service, "70000", (), PARTS, form=FORM)

    assert str(sheet.get(TP1_LINE_413).value) == "7641.16"
