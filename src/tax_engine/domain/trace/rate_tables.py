"""Trace lines for rate tables and tiers: a bracket's column or one figure of it, a contribution
or surcharge tier, a rate by income band and its application, an amount by income band.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import ArtifactKind, Money
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rate_table import RateTableRow
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine

__all__ = [
    "AmountByBandLine",
    "BracketColumnLine",
    "BracketColumnFigureLine",
    "SurchargeTierLine",
    "RateByIncomeBandLine",
    "ChosenRateAppliedLine",
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

    @property
    def label(self) -> str | None:
        """None: the line is not about one figure."""
        return None


@dataclass(frozen=True)
class BracketColumnFigureLine(TraceLine):
    """One figure of the bracket column that `base` (worth `base_amount`) falls in, produced as
    `output`: `figure`, which is the figure called `name` ("lower bound", "rate" or "tax at
    start"), printed unrounded.

    Its own class, not a `BracketColumnLine`: the line names one figure of the column and
    rounds nothing, where the column line gives the whole tax.
    """

    output: Money
    base: Money
    base_amount: Decimal
    name: str
    figure: Decimal

    @property
    def amount(self) -> Decimal:
        """The figure."""
        return self.figure

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


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

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


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

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


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

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


@dataclass(frozen=True)
class AmountByBandLine(TraceLine):
    """The band of a chart that `base` (worth `base_amount`) falls in, its `over` the lower bound,
    produced as `output`: the band's `flat_amount` (`minus`, `rate` and `plus` `None`) or its
    sloped `minus`, `rate` and `plus` (`flat_amount` `None`), rounded with `rounding` to `result`.
    """

    output: Money
    base: Money
    base_amount: Decimal
    over: Decimal
    flat_amount: Decimal | None
    minus: Decimal | None
    rate: Rate | None
    plus: Decimal | None
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The rounded figure."""
        return self.result

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
