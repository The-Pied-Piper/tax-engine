"""Revenu Quebec TP-1 (2025) line 377, "Add lines 359 through 376", as the Quebec take-home manifest
wires it: one `core/sum` of lines 359 and 361 (lines 367 and 376 are not built), rounded half-up to
the cent by `ca-qc/cent_rounding`. The chain runs the real parts of Schedule B and of the forms it
reads (see `tp1_credits_support.py`). The expected figures are hand-computed from the printed lines,
not a Revenu Quebec example: line 359 is 18,571.00 and line 361 is 0.00, or 2,128.00 at $20,000 for
a person living alone.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_LIVED_ALONE_LINE_20, TP1_LINE_377
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import LINE_377_PARTS, chain_sheet

D = Decimal
FORM = "ca-qc/tp1_credits"
PART = "tp1_credits_line_377.yaml"
IDENTIFIER = "ca-qc/tp1_line_377"
EXPORTS = (IDENTIFIER,)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_377_is_line_359_when_the_filer_does_not_live_alone(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = chain_sheet(take_home_service, salary, EXPORTS, LINE_377_PARTS)

    assert str(sheet.get(TP1_LINE_377).value) == "18571.00"


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "20699.00"), ("70000", "18571.00"), ("200000", "18571.00")]
)
def test_line_377_adds_line_361_for_a_person_living_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)
    sheet = chain_sheet(take_home_service, salary, EXPORTS, LINE_377_PARTS, given)

    assert str(sheet.get(TP1_LINE_377).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_sum_of_lines_359_and_361() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "377",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-qc/tp1_line_359",
                "ca-qc/tp1_age_living_alone_retirement_amount_line_361",
            ]
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_377
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
