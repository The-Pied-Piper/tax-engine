"""Trace line for a tapered amount rate: how fast a tapered amount falls for a further dollar."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine
from tax_engine.jurisdictions.ca.parameter_shapes.taper import Taper

__all__ = ["TaperedAmountRateLine"]


@dataclass(frozen=True)
class TaperedAmountRateLine(TraceLine):
    """The `result` produced as `output`: how fast `taper`'s supplement falls for a further dollar
    of `base` (worth `base_amount`), the supplement over the range between the taper's threshold
    and the end of its range, otherwise 0, rounded with `rounding`."""

    output: Money
    base: Money
    base_amount: Decimal
    taper: Taper
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rate the amount falls by."""
        return self.result

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
