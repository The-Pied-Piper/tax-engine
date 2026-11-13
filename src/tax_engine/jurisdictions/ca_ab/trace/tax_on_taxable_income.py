"""Trace line for the tax on taxable income: the one of AB428 line 8 and line 15 with a figure."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.trace.base import TraceLine

__all__ = ["TaxOnTaxableIncomeLine"]


@dataclass(frozen=True)
class TaxOnTaxableIncomeLine(TraceLine):
    """The `used_amount` produced as `output`: the figure of `used`, with `left_blank` blank."""

    output: Money
    used: Money
    used_amount: Decimal
    left_blank: Money

    @property
    def amount(self) -> Decimal:
        """The figure produced."""
        return self.used_amount

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
