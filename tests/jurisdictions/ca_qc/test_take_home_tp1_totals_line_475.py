"""Revenu Quebec TP-1 (2025) line 475, "Amount from line 470, if it is positive", as the Quebec
take-home manifest wires it: one `core/greater_of` of line 470 and the zero of
`ca-qc/tp1_zero_line_474_475`, since no capability returns the positive part of a signed amount
(owner decision, 19 Nov 2026). The chain runs the real parts of every line that line 470 reads (see
`tp1_totals_support.py`). The expected figures are hand-computed from the printed lines, not a
Revenu Quebec example: line 470 is -575.06 at $20,000, so line 475 is 0.00."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_453,
    TP1_LINE_470,
    TP1_LINE_475,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_475_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

D = Decimal
PART = "tp1_totals_line_475.yaml"
IDENTIFIER = "ca-qc/tp1_line_475"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_475_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_475_PARTS)

    assert str(sheet.get(TP1_LINE_475).value) == EXPECTED[salary]["475"]


@pytest.mark.parametrize("salary", ["70000", "200000"])
def test_a_positive_line_470_is_carried_whole(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_475_PARTS)

    assert sheet.get(TP1_LINE_475).value == sheet.get(TP1_LINE_470).value


def test_a_line_470_of_zero_gives_zero(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_LINE_453, D("8396.16"))
    sheet = totals_sheet(take_home_service, "70000", totals_form(IDENTIFIER), LINE_475_PARTS, given)

    assert str(sheet.get(TP1_LINE_470).value) == "0.00"
    assert str(sheet.get(TP1_LINE_475).value) == "0.00"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_greater_of_line_470_and_zero() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/greater_of",
        "reference": "475",
        "unit": "ca/cad",
        "consumes": {"amounts": ["ca-qc/tp1_line_470", "ca-qc/tp1_zero_line_474_475"]},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_475
    assert isinstance(kind, AmountKind)
    assert kind.non_negative
