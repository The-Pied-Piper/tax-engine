"""Trace line for a contribution tier: a rate on the earnings inside a band, capped."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import ContributionTier

__all__ = ["ContributionTierLine"]


@dataclass(frozen=True)
class ContributionTierLine(TraceLine):
    """The `result` produced as `output`: `tier`'s rate on `contributory`, at most the tier's
    maximum.

    `contributory` is the part of `earnings` (worth `earnings_amount`) inside the tier's band,
    rounded with `rounding`.
    """

    output: Money
    earnings: Money
    earnings_amount: Decimal
    tier: ContributionTier
    rounding: RoundingRule
    contributory: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The contribution: the rounded, capped result."""
        return self.result

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
