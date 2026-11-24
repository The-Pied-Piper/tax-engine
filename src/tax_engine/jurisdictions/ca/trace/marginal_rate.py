"""Trace lines for the capabilities that produce the rate of a further dollar of a form's figure."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import ContributionTier
from tax_engine.jurisdictions.ca.parameter_shapes.taper import Taper

__all__ = [
    "ContributionTierRateLine",
    "LesserOfRateLine",
    "RateFigureLine",
    "TaperedAmountRateLine",
]


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


@dataclass(frozen=True)
class LesserOfRateLine(TraceLine):
    """The `rate` produced as `output`: the rate of the least of `parts`, each an amount kind with
    its value and its rate; of equal least amounts, the smallest of their rates."""

    output: Money
    parts: tuple[tuple[Money, Decimal, Decimal], ...]
    rate: Decimal

    @property
    def amount(self) -> Decimal:
        """The rate of a further dollar of the least amount."""
        return self.rate

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


@dataclass(frozen=True)
class RateFigureLine(TraceLine):
    """The `output`: the rate of the `rate` dataset, as it is, with no rounding."""

    output: Money
    rate: Rate

    @property
    def amount(self) -> Decimal:
        """The dataset's rate."""
        return self.rate.value

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


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
