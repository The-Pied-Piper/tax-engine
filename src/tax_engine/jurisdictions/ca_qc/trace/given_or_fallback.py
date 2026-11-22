"""Trace line for a figure the filer gave, or the figure taken in its place when it was blank."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.trace.base import TraceLine

__all__ = ["GivenOrFallbackLine"]


@dataclass(frozen=True)
class GivenOrFallbackLine(TraceLine):
    """The `result` produced as `output`: the `given` figure, or, when `given_was_blank`, the
    `fallback` figure taken in its place."""

    output: Money
    given: Money
    fallback: Money
    given_was_blank: bool
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The figure produced."""
        return self.result

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
