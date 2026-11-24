"""Registered and money kinds of the federal catalog family `take_home_average_rate`."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    RETURN_CPP_BASE_CONTRIBUTIONS,
    RETURN_CPP_ENHANCED_CONTRIBUTIONS,
    RETURN_EI_PREMIUM,
    RETURN_TOTAL_DEDUCTIONS,
)
from tests.kinds import non_negative

# Each kind is a return's own copy of a printed figure, or their sum: money, never negative.
KINDS = (
    RETURN_CPP_BASE_CONTRIBUTIONS,
    RETURN_CPP_ENHANCED_CONTRIBUTIONS,
    RETURN_EI_PREMIUM,
    RETURN_TOTAL_DEDUCTIONS,
)


def test_the_average_rate_kinds_are_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    for kind in KINDS:
        assert kind.identifier.startswith("ca/return_"), kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert registry.get(kind.identifier) is kind


def test_the_average_rate_kinds_are_the_whole_family() -> None:
    assert len({kind.identifier for kind in KINDS}) == 4
