"""Revenu Quebec TP-1 (2025) line 470, "Subtract line 468 from line 450", as the Quebec take-home
manifest wires it: one `core/subtract`, rounded half-up to the cent by `ca-qc/cent_rounding`. The
form prints no floor, so the line is signed: negative is a refund and positive is a balance due. The
chain runs the real parts of every line that line 450 and line 468 read (see
`tp1_totals_support.py`). The expected figures are hand-computed from the printed lines, not a
Revenu Quebec example: at $20,000 line 450 is 8.96 and line 468 is 584.02, so line 470 is -575.06.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450,
    TP1_LINE_453,
    TP1_LINE_468,
    TP1_LINE_470,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_470_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

D = Decimal
PART = "tp1_totals_line_470.yaml"
IDENTIFIER = "ca-qc/tp1_line_470"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_470_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_470_PARTS)

    assert str(sheet.get(TP1_LINE_470).value) == EXPECTED[salary]["470"]


@pytest.mark.parametrize("salary", SALARIES)
def test_line_470_is_line_450_less_line_468(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_470_PARTS)

    assert sheet.get(TP1_LINE_470).value == (
        sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450).value - sheet.get(TP1_LINE_468).value
    )


def test_a_line_468_equal_to_line_450_gives_zero(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_LINE_453, D("8396.16"))
    sheet = totals_sheet(take_home_service, "70000", totals_form(IDENTIFIER), LINE_470_PARTS, given)

    assert str(sheet.get(TP1_LINE_470).value) == "0.00"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_signed_subtract_of_line_468_from_line_450() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract",
        "reference": "470",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/tp1_income_tax_and_contributions_line_450",
            "less": "ca-qc/tp1_line_468",
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_470
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
