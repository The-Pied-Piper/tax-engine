"""T691 Part 7 line 14 input: the one optional amount the five provinces' forms read."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.registrations import artifact_kinds
from tests.federal_forms import FEDERAL_FORMS
from tests.kinds import non_negative

T691 = FEDERAL_FORMS / "t691"
NAME = "ca/t691_additional_taxes_for_minimum_tax_carryover"
TITLE = "Additional taxes paid for minimum tax carryover"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_line_14_has_an_optional_input_left_blank_by_a_salary_only_caller() -> None:
    part = _part(T691 / "t691_line_14_inputs.yaml")

    assert part["form"] == {"name": "ca/t691"}
    (declaration,) = part["inputs"]
    assert {key: declaration[key] for key in declaration if key != "basis"} == {
        "name": NAME,
        "title": TITLE,
        "reference": "14",
        "unit": "ca/cad",
        "required": False,
        "default": None,
    }
    assert declaration["basis"]


def test_the_input_kind_is_a_non_negative_decimal_amount() -> None:
    kind = artifact_kinds().kind(NAME)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
