"""Trace line for an amount the filer gave, produced unchanged."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.trace.base import TraceLine

__all__ = ["GivenAmountLine"]


@dataclass(frozen=True)
class GivenAmountLine(TraceLine):
    """The `given_amount` the filer gave, produced unchanged as `output`, from the `given` kind."""

    output: Money
    given: Money
    given_amount: Decimal

    @property
    def amount(self) -> Decimal:
        """The amount given, as it was given."""
        return self.given_amount
