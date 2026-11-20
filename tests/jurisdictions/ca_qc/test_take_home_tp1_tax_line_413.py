"""Revenu Quebec TP-1 (2025) line 413, "Subtract line 406 from line 401", as the Quebec take-home
manifest wires it: one `core/subtract` of line 406 from line 401, rounded half-up to the cent by
`ca-qc/cent_rounding`. The form prints no floor, so the figure may be negative; line 432 floors it.
The chain runs the real parts of Work Chart 401, the credits lines and the forms they read (see
`tp1_tax_support.py`). The expected figures are hand-computed from the printed lines, not a Revenu
Quebec example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_LIVED_ALONE_LINE_20, TP1_LINE_413
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_tax_support import (
    LINE_401_CHAIN,
    LINE_406_CHAIN,
    tax_sheet,
)

PART = "tp1_tax_line_413.yaml"
FORM = "ca-qc/tp1_tax"
IDENTIFIER = "ca-qc/tp1_line_413"
EXPORTS = (IDENTIFIER,)
# The chain of line 401 and of line 406 share the upstream and net income parts, so the union keeps
# the first occurrence of each part.
CHAIN = tuple(dict.fromkeys((*LINE_401_CHAIN, *LINE_406_CHAIN)))
PARTS = (
    *CHAIN,
    "tp1_tax_line_401.yaml",
    "tp1_tax_line_406.yaml",
    PART,
)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "8.96"), ("70000", "7641.16"), ("200000", "38002.53")]
)
def test_line_413_is_line_401_less_line_406(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = tax_sheet(take_home_service, salary, EXPORTS, PARTS)

    assert str(sheet.get(TP1_LINE_413).value) == expected


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "-288.96"), ("70000", "7641.16"), ("200000", "38002.53")]
)
def test_line_413_for_a_person_living_alone_is_not_floored(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)
    sheet = tax_sheet(take_home_service, salary, EXPORTS, PARTS, given)

    assert str(sheet.get(TP1_LINE_413).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_rounded_subtract_of_line_406_from_line_401() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract",
        "reference": "413",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/tp1_income_tax_on_taxable_income_line_401",
            "less": "ca-qc/tp1_non_refundable_tax_credits_line_406",
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_413
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
