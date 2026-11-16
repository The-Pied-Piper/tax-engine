"""The kind of T1 line 47900, "Provincial or territorial credits", in the `ca` catalog.

`ca/provincial_credits_line_47900` is the figure of the T1 line 47900 part: a non-negative amount
(a credit total), registered under its identifier beside `ca/provincial_credits` and listed in the
catalog snapshot.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.refundable_credits import (
    PROVINCIAL_CREDITS,
    PROVINCIAL_CREDITS_LINE_47900,
)
from tests.jurisdictions.ca.catalog_snapshot import REGISTERED, SIGNED
from tests.kinds import non_negative

IDENTIFIER = "ca/provincial_credits_line_47900"


def test_the_kind_is_the_registered_one(registry: ArtifactRegistry) -> None:
    assert registry.get(IDENTIFIER) is PROVINCIAL_CREDITS_LINE_47900


def test_the_kind_is_a_non_negative_amount_beside_the_provincial_credits() -> None:
    assert isinstance(PROVINCIAL_CREDITS_LINE_47900, AmountKind)
    assert PROVINCIAL_CREDITS_LINE_47900.identifier == IDENTIFIER
    assert non_negative(PROVINCIAL_CREDITS_LINE_47900) is True
    assert PROVINCIAL_CREDITS_LINE_47900 is not PROVINCIAL_CREDITS
    assert IDENTIFIER not in SIGNED


def test_the_kind_is_in_the_catalog_snapshot() -> None:
    assert IDENTIFIER in REGISTERED
