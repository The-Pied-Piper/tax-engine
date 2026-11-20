"""Trace line for an amount shared among a count of people: the basic housing amount of the
solidarity tax credit divided by the number of owners or tenants."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import ArtifactKind, Money
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine

__all__ = ["DivideByCountLine"]


@dataclass(frozen=True)
class DivideByCountLine(TraceLine):
    """The `result` produced as `output`: `amount_kind` (worth `amount_value`) divided by `count`
    units of `count_kind`, the exact quotient rounded once with `rounding`.

    A count of 0 gives 0; `rounding` is still recorded.
    """

    output: Money
    amount_kind: Money
    amount_value: Decimal
    count_kind: ArtifactKind[int]
    count: int
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded quotient."""
        return self.result

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
