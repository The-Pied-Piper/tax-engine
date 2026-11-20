"""Revenu Quebec TP-1 (2025) line 465, "Add lines 451.2 through 463. Income tax paid and other
credits", as the Quebec take-home manifest wires it: one `core/sum`, rounded half-up to the cent by
`ca-qc/cent_rounding`. Line 456 is a step and lines 451.2, 451.3, 452 to 455, 457 to 460, 462 and
463 are optional inputs, read as 0 when left blank. The chain runs the real Schedule P parts (see
`tp1_totals_support.py`). The expected figures are hand-computed from the printed lines, not a
Revenu Quebec example: line 456 is 584.02 at $20,000 and 0.00 at the other salaries."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_INCOME_TAX_PAID_AND_OTHER_CREDITS_LINE_465,
    TP1_LINE_451_2,
    TP1_LINE_451_3,
    TP1_LINE_452,
    TP1_LINE_453,
    TP1_LINE_454,
    TP1_LINE_455,
    TP1_LINE_457,
    TP1_LINE_458,
    TP1_LINE_459,
    TP1_LINE_460,
    TP1_LINE_462,
    TP1_LINE_463,
    TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_465_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

D = Decimal
PART = "tp1_totals_line_465.yaml"
IDENTIFIER = "ca-qc/tp1_income_tax_paid_and_other_credits_line_465"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_465_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_465_PARTS)

    assert (
        str(sheet.get(TP1_INCOME_TAX_PAID_AND_OTHER_CREDITS_LINE_465).value)
        == EXPECTED[salary]["465"]
    )


OPTIONAL = (
    "ca-qc/tp1_line_451_2",
    "ca-qc/tp1_line_451_3",
    "ca-qc/tp1_line_452",
    "ca-qc/tp1_line_453",
    "ca-qc/tp1_line_454",
    "ca-qc/tp1_line_455",
    "ca-qc/tp1_line_457",
    "ca-qc/tp1_line_458",
    "ca-qc/tp1_line_459",
    "ca-qc/tp1_line_460",
    "ca-qc/tp1_line_462",
    "ca-qc/tp1_line_463",
)
PARTS = [
    *OPTIONAL[:6],
    "ca-qc/tp1_work_premium_tax_credits_line_456",
    *OPTIONAL[6:],
]


def test_line_465_is_line_456_when_every_optional_line_is_blank(
    take_home_service: TakeHomeService,
) -> None:
    sheet = totals_sheet(take_home_service, "20000", totals_form(IDENTIFIER), LINE_465_PARTS)

    assert sheet.get(TP1_INCOME_TAX_PAID_AND_OTHER_CREDITS_LINE_465).value == (
        sheet.get(TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456).value
    )


def test_every_optional_line_is_added(take_home_service: TakeHomeService) -> None:
    kinds = (
        TP1_LINE_451_2,
        TP1_LINE_451_3,
        TP1_LINE_452,
        TP1_LINE_453,
        TP1_LINE_454,
        TP1_LINE_455,
        TP1_LINE_457,
        TP1_LINE_458,
        TP1_LINE_459,
        TP1_LINE_460,
        TP1_LINE_462,
        TP1_LINE_463,
    )
    given = [Artifact(kind, D(amount)) for amount, kind in enumerate(kinds, start=1)]
    sheet = totals_sheet(
        take_home_service, "20000", totals_form(IDENTIFIER), LINE_465_PARTS, *given
    )

    # 1 + 2 + ... + 12 = 78, and the work premium of 584.02.
    assert str(sheet.get(TP1_INCOME_TAX_PAID_AND_OTHER_CREDITS_LINE_465).value) == "662.02"


def test_an_amount_with_cents_is_added_whole(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_LINE_453, D("1000.50"))
    sheet = totals_sheet(take_home_service, "70000", totals_form(IDENTIFIER), LINE_465_PARTS, given)

    assert str(sheet.get(TP1_INCOME_TAX_PAID_AND_OTHER_CREDITS_LINE_465).value) == "1000.50"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_sum_of_line_456_and_the_optional_lines() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": "Income tax paid and other credits",
        "reference": "465",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {"parts": PARTS},
        "blank": {name: "0" for name in OPTIONAL},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_INCOME_TAX_PAID_AND_OTHER_CREDITS_LINE_465
    assert isinstance(kind, AmountKind)
    assert kind.non_negative
