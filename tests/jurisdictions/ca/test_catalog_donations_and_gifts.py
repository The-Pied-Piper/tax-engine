"""Registered and money kinds of the federal catalog family `donations_and_gifts` (Schedule 9)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    DONATIONS_AND_GIFTS_AMOUNT_LINE_12,
    DONATIONS_AND_GIFTS_LINE_12,
    DONATIONS_AND_GIFTS_LINE_13,
    DONATIONS_AND_GIFTS_LINE_13_LIMIT,
    DONATIONS_AND_GIFTS_LINE_14,
)
from tests.kinds import non_negative

KINDS = [
    ("ca/donations_and_gifts_line_12", DONATIONS_AND_GIFTS_LINE_12),
    ("ca/donations_and_gifts_amount_line_12", DONATIONS_AND_GIFTS_AMOUNT_LINE_12),
    ("ca/donations_and_gifts_line_13_limit", DONATIONS_AND_GIFTS_LINE_13_LIMIT),
    ("ca/donations_and_gifts_line_13", DONATIONS_AND_GIFTS_LINE_13),
    ("ca/donations_and_gifts_line_14", DONATIONS_AND_GIFTS_LINE_14),
]


@pytest.mark.parametrize(("identifier", "kind"), KINDS, ids=[name for name, _ in KINDS])
def test_each_schedule_9_kind_is_registered_non_negative_money(
    registry: ArtifactRegistry, identifier: str, kind: ArtifactKind[Any]
) -> None:
    # Lines 12, 13 and 14 are amounts of the donations claimed; line 14 is line 12 less line 13,
    # which is never above it, and the printed $200 is a figure that is never negative.
    assert registry.get(identifier) is kind
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
