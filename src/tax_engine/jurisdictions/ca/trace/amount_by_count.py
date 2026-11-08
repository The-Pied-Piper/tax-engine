"""Trace line for an amount read from a table by a count."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import ArtifactKind, Money
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine

__all__ = ["AmountByCountLine"]


@dataclass(frozen=True)
class AmountByCountLine(TraceLine):
    """The `result` produced as `output`: the table's `row` for `count` of `count_kind`, rounded
    with `rounding`.

    Its own class, not a `CreditAmountLine`: the figure is one row of a table, chosen by a count
    an artifact holds.
    """

    output: Money
    count_kind: ArtifactKind[int]
    count: int
    row: Decimal
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded result."""
        return self.result

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
