"""Registered and money kinds of the federal catalog family `t691` (Form T691 Parts 5 and 7)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    T691_ADDITIONAL_TAXES_FOR_MINIMUM_TAX_CARRYOVER_LINE_14,
    T691_BASIC_FEDERAL_TAX,
    T691_LINE_1_AMOUNT,
    T691_LINE_1_MINUS_LINE_2_OF_PART_7,
    T691_LINE_2_AMOUNT,
    T691_LINE_7_MINUS_LINE_10,
    T691_LINE_8_PLUS_LINE_12,
    T691_LINE_13_AMOUNT,
    T691_MINIMUM_AMOUNT,
    T691_PART_5_LINE_11_AMOUNT,
)
from tests.kinds import non_negative

# Each kind with whether it is non-negative: lines 1 and 14 and Part 5 line 11 are never below 0,
# and so is line 1 minus line 2 (the form's intent, Part 7 being completed only when minimum tax is
# payable); the form prints no floor on lines 2 and 13, so those are signed.
KINDS = [
    ("ca/t691_minimum_amount", T691_MINIMUM_AMOUNT, True),
    ("ca/t691_basic_federal_tax", T691_BASIC_FEDERAL_TAX, False),
    ("ca/t691_line_8_plus_line_12", T691_LINE_8_PLUS_LINE_12, False),
    ("ca/t691_line_1_amount", T691_LINE_1_AMOUNT, True),
    ("ca/t691_line_2_amount", T691_LINE_2_AMOUNT, False),
    ("ca/t691_line_13_amount", T691_LINE_13_AMOUNT, False),
    ("ca/t691_line_1_minus_line_2_of_part_7", T691_LINE_1_MINUS_LINE_2_OF_PART_7, True),
    ("ca/t691_line_7_minus_line_10", T691_LINE_7_MINUS_LINE_10, True),
    ("ca/t691_part_5_line_11_amount", T691_PART_5_LINE_11_AMOUNT, True),
    (
        "ca/t691_additional_taxes_for_minimum_tax_carryover_line_14",
        T691_ADDITIONAL_TAXES_FOR_MINIMUM_TAX_CARRYOVER_LINE_14,
        True,
    ),
]


@pytest.mark.parametrize(
    ("identifier", "kind", "expected"), KINDS, ids=[name for name, _, _ in KINDS]
)
def test_each_t691_kind_is_registered_money_and_signed_as_the_form_prints_it(
    registry: ArtifactRegistry, identifier: str, kind: ArtifactKind[Any], expected: bool
) -> None:
    assert registry.get(identifier) is kind
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert non_negative(kind) is expected
