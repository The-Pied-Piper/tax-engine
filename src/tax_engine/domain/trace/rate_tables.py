"""Trace lines for rate tables and tiers: a bracket's column, a contribution or surcharge
tier, a taper, a rate by income band and its application, and an amount by count.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction as ExactFraction

from tax_engine.domain.artifact import ArtifactKind, Money
from tax_engine.domain.parameters.contribution_tier import ContributionTier
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rate_table import RateTableRow
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.parameters.taper import Taper
from tax_engine.domain.trace.base import TraceLine

__all__ = [
    "BracketColumnLine",
    "ContributionTierLine",
    "SurchargeTierLine",
    "TaperedAmountLine",
    "RateByIncomeBandLine",
    "ChosenRateAppliedLine",
    "AmountByCountLine",
]


@dataclass(frozen=True)
class BracketColumnLine(TraceLine):
    """The bracket a base falls in: `rate` on the `excess` over `lower`, plus `tax_at_start`."""

    lower: Decimal
    rate: Decimal
    excess: Decimal
    tax_at_start: Decimal
    tax: Decimal

    @property
    def amount(self) -> Decimal:
        """The tax the bracket's column gives."""
        return self.tax


@dataclass(frozen=True)
class ContributionTierLine(TraceLine):
    """The `result` produced as `output`: `tier`'s rate on `contributory`, the part of `earnings`
    (worth `earnings_amount`) inside the tier's band, rounded with `rounding`, at most the tier's
    maximum."""

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


@dataclass(frozen=True)
class SurchargeTierLine(TraceLine):
    """One tier of a surcharge produced as `output`: `rate` of `base` (worth `base_amount`) over
    `threshold`, not below zero, at most the tier's `maximum` when it has one (`None` otherwise),
    rounded with `rounding` to `part`.

    `base_amount` is the whole base, not the part over the threshold; a base that does not reach
    the threshold still gets its line, with a zero part.
    """

    output: Money
    base: Money
    base_amount: Decimal
    threshold: Decimal
    rate: Rate
    rounding: RoundingRule
    part: Decimal
    maximum: Decimal | None = None

    @property
    def amount(self) -> Decimal:
        """The rounded part charged by this tier."""
        return self.part


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


@dataclass(frozen=True)
class RateByIncomeBandLine(TraceLine):
    """`rate` produced as `output`, the rate of the table's `row` that `income` (worth
    `income_amount`) falls in; `row` is `None` for a figure of exactly 0, which takes the table's
    rate at zero.

    Its own class, not a `BracketColumnLine` or `SurchargeTierLine`: the row chooses one rate for
    the whole figure, and nothing is charged or rounded.
    """

    output: ArtifactKind[Rate]
    income: Money
    income_amount: Decimal
    row: RateTableRow | None
    rate: Rate

    @property
    def amount(self) -> Decimal:
        """The chosen rate's value."""
        return self.rate.value


@dataclass(frozen=True)
class ChosenRateAppliedLine(TraceLine):
    """The `result` produced as `output` by `base` (worth `base_amount`) × `rate_kind` (worth
    `rate`), rounded once with `rounding`.

    Its own class, not a `RateAppliedLine`: the rate is an artifact chosen earlier, not a rate
    dataset's, so the line names the kind it came from.
    """

    output: Money
    base: Money
    base_amount: Decimal
    rate_kind: ArtifactKind[Rate]
    rate: Rate
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded product."""
        return self.result


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
