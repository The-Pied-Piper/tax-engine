"""T691 Part 7 line 13 input: an optional amount, read as 0 when blank."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.registrations import artifact_kinds
from tests.federal_forms import FEDERAL_FORMS
from tests.kinds import non_negative

NAME = "ca/t691_line_8_plus_line_12"


def test_line_13_has_an_optional_input_left_blank_by_a_salary_only_caller() -> None:
    part: Any = yaml.safe_load(
        (FEDERAL_FORMS / "t691" / "t691_line_13_inputs.yaml").read_text(encoding="utf-8")
    )

    assert part["form"] == {"name": "ca/t691"}
    (declaration,) = part["inputs"]
    assert {key: declaration[key] for key in declaration if key != "basis"} == {
        "name": NAME,
        "title": "Line 8 plus line 12",
        "reference": "13",
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
