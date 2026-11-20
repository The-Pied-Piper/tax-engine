"""Revenu Quebec TP-1 (2025) line 430, "Subtract line 425 from line 413", as the Quebec take-home
manifest wires it: one `core/subtract`, rounded half-up to the cent by `ca-qc/cent_rounding`. Line
425 is an optional input, read as 0 when the caller leaves it out. The form prints no floor, so the
figure may be negative; line 432 floors it. The chain runs the real parts of lines 401 to 413 (see
`tp1_tax_support.py`). The expected figures are hand-computed from the printed lines, not a Revenu
Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    TP1_LINE_413,
    TP1_LINE_425,
    TP1_LINE_430,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_tax_support import LINE_430_CHAIN, tax_sheet

D = Decimal
FORM = "ca-qc/tp1_tax"
IDENTIFIER = "ca-qc/tp1_line_430"
EXPORTS = (IDENTIFIER,)
PART = "tp1_tax_line_430.yaml"
PARTS = (*LINE_430_CHAIN, "tp1_tax_line_425_input.yaml", PART)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "8.96"), ("70000", "7641.16"), ("200000", "38002.53")]
)
def test_line_430_with_line_425_blank_is_line_413(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = tax_sheet(take_home_service, salary, EXPORTS, PARTS)

    assert sheet.get(TP1_LINE_430).value == sheet.get(TP1_LINE_413).value
    assert str(sheet.get(TP1_LINE_430).value) == expected


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "-288.96"), ("70000", "7641.16"), ("200000", "38002.53")]
)
def test_line_430_for_a_person_living_alone_is_not_floored(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)
    sheet = tax_sheet(take_home_service, salary, EXPORTS, PARTS, given)

    assert str(sheet.get(TP1_LINE_430).value) == expected


def test_line_425_is_subtracted(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_LINE_425, D("1000.50"))
    sheet = tax_sheet(take_home_service, "70000", EXPORTS, PARTS, given)

    assert sheet.get(TP1_LINE_430).value == sheet.get(TP1_LINE_413).value - D("1000.50")
    assert str(sheet.get(TP1_LINE_430).value) == "6640.66"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_subtract_of_line_425_from_line_413() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract",
        "reference": "430",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/tp1_line_413",
            "less": "ca-qc/tp1_line_425",
        },
        "blank": {"less": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_430
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
