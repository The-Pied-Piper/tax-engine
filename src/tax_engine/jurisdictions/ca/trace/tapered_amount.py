"""Trace line for a tapered amount: a base plus a supplement, reduced above a threshold."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction as ExactFraction

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine
from tax_engine.jurisdictions.ca.parameter_shapes.taper import Taper

__all__ = ["TaperedAmountLine"]


@dataclass(frozen=True)
class TaperedAmountLine(TraceLine):
    """The `result` produced as `output`: `taper`'s base plus its supplement less `reduction`, not
    below the base, rounded with `rounding`.

    `reduction` is the supplement's share for how far `base` (worth `base_amount`) sits above the
    taper's threshold, recorded as an exact fraction and before the floor at zero, so it can
    exceed the supplement; a base at or below the threshold gets a zero reduction.
    """

    output: Money
    base: Money
    base_amount: Decimal
    taper: Taper
    rounding: RoundingRule
    reduction: ExactFraction
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The tapered amount: the rounded result."""
        return self.result
