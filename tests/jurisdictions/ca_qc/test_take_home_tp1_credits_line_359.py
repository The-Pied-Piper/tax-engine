"""Revenu Quebec TP-1 (2025) line 359, "Subtract line 358 from line 350", as the Quebec take-home
manifest wires it: one `core/subtract`, rounded half-up to the cent by `ca-qc/cent_rounding`. Line
358 is an optional input, read as 0 when the caller leaves it out. The form prints no floor, so the
figure is signed. The expected figures are hand-computed from the printed lines, not a Revenu Quebec
example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_INCOME_REPLACEMENT_ADJUSTMENT_LINE_358,
    TP1_LINE_359,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import (
    LINE_359_PARTS,
    PART_A_FORM,
    credits_sheet,
)

D = Decimal
FORM = PART_A_FORM  # a split part of the TP-1 credits form, read by TP-752.PC-V
IDENTIFIER = "ca-qc/tp1_line_359"
EXPORTS = (IDENTIFIER,)
PART = "tp1_credits_line_359.yaml"


def test_line_359_with_line_358_blank_is_line_350(take_home_service: TakeHomeService) -> None:
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_359_PARTS, name=FORM)

    assert str(sheet.get(TP1_LINE_359).value) == "18571.00"


def test_line_358_is_subtracted(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_INCOME_REPLACEMENT_ADJUSTMENT_LINE_358, D("1000.50"))
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_359_PARTS, given, name=FORM)

    assert str(sheet.get(TP1_LINE_359).value) == "17570.50"


def test_a_line_358_above_line_350_is_not_floored(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_INCOME_REPLACEMENT_ADJUSTMENT_LINE_358, D("20000"))
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_359_PARTS, given, name=FORM)

    assert str(sheet.get(TP1_LINE_359).value) == "-1429.00"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_subtract_of_line_358_from_line_350() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract",
        "reference": "359",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/tp1_basic_personal_amount_line_350",
            "less": "ca-qc/tp1_income_replacement_adjustment_line_358",
        },
        "blank": {"less": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_359
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
