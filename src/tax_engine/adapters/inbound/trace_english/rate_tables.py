"""English text for the trace lines of `tax_engine.domain.trace.rate_tables`: one renderer class
per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.domain.trace.rate_tables import (
    AmountByCountLine,
    BracketColumnLine,
    ChosenRateAppliedLine,
    ContributionTierLine,
    RateByIncomeBandLine,
    SurchargeTierLine,
    TaperedAmountLine,
)


@english_renderer
class BracketColumnRenderer:
    """English text for BracketColumnLine."""

    line_class = BracketColumnLine

    def render(self, line: BracketColumnLine) -> str:
        """The English sentence for `line`."""
        lower = line.lower
        rate = line.rate
        excess = line.excess
        tax_at_start = line.tax_at_start
        return (
            f"{EnglishFigures.percent(rate)}% on {EnglishFigures.money(excess)} "
            f"over {EnglishFigures.money(lower)} plus {EnglishFigures.money(tax_at_start)}"
        )


@english_renderer
class ContributionTierRenderer:
    """English text for ContributionTierLine."""

    line_class = ContributionTierLine

    def render(self, line: ContributionTierLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        earnings = line.earnings
        tier = line.tier
        rule = line.rounding
        contributory = line.contributory
        return (
            f"{output.label}: {EnglishFigures.percent(tier.rate.value)}% of {earnings.label} "
            f"between {EnglishFigures.money(tier.lower)} and {EnglishFigures.money(tier.upper)} "
            f"({EnglishFigures.money(contributory)}), "
            f"at most {EnglishFigures.money(tier.maximum)} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class SurchargeTierRenderer:
    """English text for SurchargeTierLine."""

    line_class = SurchargeTierLine

    def render(self, line: SurchargeTierLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        base = line.base
        amount = line.base_amount
        threshold = line.threshold
        rate = line.rate
        rule = line.rounding
        maximum = line.maximum
        at_most = "" if maximum is None else f", at most {EnglishFigures.money(maximum)}"
        return (
            f"{output.label}: {EnglishFigures.percent(rate.value)}% of {base.label} "
            f"{EnglishFigures.money(amount)} over {EnglishFigures.money(threshold)}{at_most} "
            f"({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class TaperedAmountRenderer:
    """English text for TaperedAmountLine."""

    line_class = TaperedAmountLine

    def render(self, line: TaperedAmountLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        base = line.base
        amount = line.base_amount
        taper = line.taper
        rule = line.rounding
        reduction = line.reduction
        return (
            f"{output.label}: {EnglishFigures.money(taper.base)} "
            f"plus {EnglishFigures.money(taper.supplement)} less {EnglishFigures.exact(reduction)} "
            f"for {base.label} {EnglishFigures.money(amount)} "
            f"over {EnglishFigures.money(taper.threshold)} (range "
            f"{EnglishFigures.money(taper.range)}), "
            f"not below {EnglishFigures.money(taper.base)} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class RateByIncomeBandRenderer:
    """English text for RateByIncomeBandLine."""

    line_class = RateByIncomeBandLine

    def render(self, line: RateByIncomeBandLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        income = line.income
        amount = line.income_amount
        row = line.row
        rate = line.rate
        if row is None:
            band = "which is 0"
        elif row.not_more_than is None:
            band = f"more than {EnglishFigures.money(row.more_than)}"
        else:
            band = (
                f"more than {EnglishFigures.money(row.more_than)} "
                f"but not more than {EnglishFigures.money(row.not_more_than)}"
            )
        return (
            f"{output.label}: {income.label} {EnglishFigures.money(amount)}, "
            f"{band}: {EnglishFigures.percent(rate.value)}%"
        )


@english_renderer
class ChosenRateAppliedRenderer:
    """English text for ChosenRateAppliedLine."""

    line_class = ChosenRateAppliedLine

    def render(self, line: ChosenRateAppliedLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        base = line.base
        amount = line.base_amount
        rate_kind = line.rate_kind
        rate = line.rate
        rule = line.rounding
        return (
            f"{output.label}: {rate_kind.label} {EnglishFigures.percent(rate.value)}% of "
            f"{base.label} {EnglishFigures.money(amount)} ({EnglishFigures.rounding(rule)})"
        )


@english_renderer
class AmountByCountRenderer:
    """English text for AmountByCountLine."""

    line_class = AmountByCountLine

    def render(self, line: AmountByCountLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        count_kind = line.count_kind
        count = line.count
        row = line.row
        rule = line.rounding
        return (
            f"{output.label}: {EnglishFigures.money(row)} for {count_kind.label} {count} "
            f"({EnglishFigures.rounding(rule)})"
        )
