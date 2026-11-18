"""BC479 (2025) line 14, the home renovation expenses checked against their printed maximum.

Form text (Form BC479, CRA 5010-TC): "Line 14: Enter your home renovation expenses from line 5 of
your Schedule BC(S12). (maximum $10,000) Line 60480 ^ multiplied by 10% = ^". Line 14 is an entry
line: an amount above the printed maximum is rejected with `InputAboveBoundError`, not capped,
before the 10% step reads it. The maximum is a dataset figure
(`ca-bc/home_renovation_expenses_maximum`), never an input.

Two new parts sit ahead of the line 14 step. `bc479_home_renovation_expenses_maximum.yaml` is
`core/credit_amount` over that dataset and produces `ca-bc/bc479_home_renovation_expenses_maximum`;
the maximum is an intermediate step and carries no line number in its title, reference or kind name.
`bc479_line_14_check.yaml` is `core/at_most`, consuming the input
`ca-bc/bc479_home_renovation_expenses_line_14` against that maximum and producing
`ca-bc/bc479_home_renovation_expenses_checked`, the amount the 10% step multiplies. It carries no
title or reference either; only the final step for the line does. A blank input passes through as
blank.

The part layout is checked here on the real files; the behaviour (passing, rejection, trace) is
checked end to end in `end_to_end/test_bc479_home_renovation_expenses_maximum.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_bc.support import british_columbia_kinds
from tests.kinds import non_negative

PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
MAXIMUM_PART = PARTS / "bc479_home_renovation_expenses_maximum.yaml"
CHECK_PART = PARTS / "bc479_line_14_check.yaml"
FORM = "ca-bc/bc479"
INPUT = "ca-bc/bc479_home_renovation_expenses_line_14"
MAXIMUM_DATASET = "ca-bc/home_renovation_expenses_maximum"
MAXIMUM = "ca-bc/bc479_home_renovation_expenses_maximum"
CHECKED = "ca-bc/bc479_home_renovation_expenses_checked"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_maximum_part_is_one_credit_amount_step_with_no_line_number() -> None:
    part = _part(MAXIMUM_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step["name"] == "core/credit_amount"
    assert "title" not in step
    assert "reference" not in step
    assert step["unit"] == "ca/cad"
    assert step["params"] == {"amount": MAXIMUM_DATASET}
    assert step["produces"] == {"output": MAXIMUM}
    assert "consumes" not in step


def test_the_check_part_is_one_at_most_step_with_no_line_number_or_title() -> None:
    part = _part(CHECK_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step["name"] == "core/at_most"
    assert "title" not in step
    assert "reference" not in step
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"amount": INPUT, "bound": MAXIMUM}
    assert step["blank"] == {"amount": "pass_on"}
    assert step["produces"] == {"output": CHECKED}
    assert "params" not in step


@pytest.mark.parametrize("identifier", [MAXIMUM, CHECKED])
def test_the_new_kinds_are_registered_non_negative_decimal_amount_kinds(identifier: str) -> None:
    kind = british_columbia_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert non_negative(kind)
