"""Revenu Quebec TP-1 (2025) line 377.1, "Multiply line 377 by 14%", as the Quebec take-home
manifest wires it: one `core/apply_rate` over line 377 with the printed rate from the dataset
`ca-qc/tp1_line_377_1_rate`, rounded half-up to the cent by the dataset's rule. The expected figures
are hand-computed from the printed lines, not a Revenu Quebec example: 18,571.00 x 0.14 = 2,599.94;
20,699.00 x 0.14 = 2,897.86 (line 377 at $20,000 for a person living alone).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_LIVED_ALONE_LINE_20, TP1_LINE_377_1
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import LINE_377_1_PARTS, chain_sheet

D = Decimal
FORM = "ca-qc/tp1_credits"
PART = "tp1_credits_line_377_1.yaml"
IDENTIFIER = "ca-qc/tp1_line_377_1"
EXPORTS = (IDENTIFIER,)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_377_1_when_the_filer_does_not_live_alone(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = chain_sheet(take_home_service, salary, EXPORTS, LINE_377_1_PARTS)

    assert str(sheet.get(TP1_LINE_377_1).value) == "2599.94"


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "2897.86"), ("70000", "2599.94"), ("200000", "2599.94")]
)
def test_line_377_1_for_a_person_living_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)
    sheet = chain_sheet(take_home_service, salary, EXPORTS, LINE_377_1_PARTS, given)

    assert str(sheet.get(TP1_LINE_377_1).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_apply_rate_over_line_377() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "377.1",
        "unit": "ca/cad",
        "params": {"rate": "ca-qc/tp1_line_377_1_rate"},
        "consumes": {"base": "ca-qc/tp1_line_377"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_377_1
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
