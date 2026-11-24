"""Trace line for a contribution tier rate: the tier's rate when earnings are inside its band."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.trace.base import TraceLine
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import ContributionTier

__all__ = ["ContributionTierRateLine"]


@dataclass(frozen=True)
class ContributionTierRateLine(TraceLine):
    """The `rate` produced as `output`: `tier`'s rate when `earnings` (worth `earnings_amount`) is
    over the tier's lower bound and under its upper bound, otherwise 0."""

    output: Money
    earnings: Money
    earnings_amount: Decimal
    tier: ContributionTier
    rate: Decimal

    @property
    def amount(self) -> Decimal:
        """The rate of a further dollar of the earnings."""
        return self.rate

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
