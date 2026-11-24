"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.marginal_rate`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.marginal_rate import (
    ContributionTierRateLine,
    LesserOfRateLine,
    RateFigureLine,
    TaperedAmountRateLine,
)


@english_renderer
class ContributionTierRateRenderer:
    """English text for ContributionTierRateLine."""

    line_class = ContributionTierRateLine

    def render(self, line: ContributionTierRateLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        tier = line.tier
        return (
            f"A further dollar is charged {EnglishFigures.percent(tier.rate.value)}% only when "
            f"{names.figure(line.earnings, line.earnings_amount)} is over "
            f"{EnglishFigures.money(tier.lower)} and under {EnglishFigures.money(tier.upper)}, "
            f"which gives {names.shown(line.label, line.rate)}"
        )


@english_renderer
class LesserOfRateRenderer:
    """English text for LesserOfRateLine."""

    line_class = LesserOfRateLine

    def render(self, line: LesserOfRateLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        shown = ", ".join(names.figure(kind, amount) for kind, amount, _rate in line.parts)
        return (
            f"A further dollar follows the least of {shown}, "
            f"which gives {names.shown(line.label, line.rate)}"
        )


@english_renderer
class RateFigureRenderer:
    """English text for RateFigureLine."""

    line_class = RateFigureLine

    def render(self, line: RateFigureLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return f"The rate is {names.shown(line.label, line.rate.value)}"


@english_renderer
class TaperedAmountRateRenderer:
    """English text for TaperedAmountRateLine."""

    line_class = TaperedAmountRateLine

    def render(self, line: TaperedAmountRateLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        taper = line.taper
        end = taper.threshold + taper.range
        return (
            f"{EnglishFigures.money(taper.supplement)} falls over "
            f"{EnglishFigures.money(taper.range)} of "
            f"{names.figure(line.base, line.base_amount)} between "
            f"{EnglishFigures.money(taper.threshold)} and {EnglishFigures.money(end)}, which gives "
            f"{names.shown(line.label, line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )
