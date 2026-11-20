"""Revenu Quebec TP-1 (2025) line 479, "Subtract line 477 from line 475. Balance due", as the Quebec
take-home manifest wires it: one `core/subtract`, rounded half-up to the cent by
`ca-qc/cent_rounding`. Line 477 is an optional input, read as 0 when left blank. The note "You are
not required to pay a balance of less than $2" is a payment note and is not built: the line prints
the exact balance (owner decision, 19 Nov 2026). The chain runs the real parts of every line that
line 475 reads (see `tp1_totals_support.py`). The expected figures are hand-computed from the
printed lines, not a Revenu Quebec example: at $70,000 line 475 is 8,396.16, so line 479 is
8,396.16."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_AMOUNT_TRANSFERRED_BY_SPOUSE_LINE_477,
    TP1_BALANCE_DUE_LINE_479,
    TP1_LINE_453,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_479_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

D = Decimal
PART = "tp1_totals_line_479.yaml"
IDENTIFIER = "ca-qc/tp1_balance_due_line_479"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_479_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_479_PARTS)

    assert str(sheet.get(TP1_BALANCE_DUE_LINE_479).value) == EXPECTED[salary]["479"]


def test_line_477_is_subtracted(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_AMOUNT_TRANSFERRED_BY_SPOUSE_LINE_477, D("396.16"))
    sheet = totals_sheet(take_home_service, "70000", totals_form(IDENTIFIER), LINE_479_PARTS, given)

    assert str(sheet.get(TP1_BALANCE_DUE_LINE_479).value) == "8000.00"


def test_a_balance_of_less_than_two_dollars_is_printed_exactly(
    take_home_service: TakeHomeService,
) -> None:
    given = Artifact(TP1_LINE_453, D("8395.00"))
    sheet = totals_sheet(take_home_service, "70000", totals_form(IDENTIFIER), LINE_479_PARTS, given)

    assert str(sheet.get(TP1_BALANCE_DUE_LINE_479).value) == "1.16"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_subtract_of_line_477_from_line_475() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract",
        "title": "Balance due",
        "reference": "479",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/tp1_line_475",
            "less": "ca-qc/tp1_amount_transferred_by_spouse_line_477",
        },
        "blank": {"less": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_BALANCE_DUE_LINE_479
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
