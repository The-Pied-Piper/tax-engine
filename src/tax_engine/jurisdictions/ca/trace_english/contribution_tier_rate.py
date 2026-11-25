"""English text for the trace line of `tax_engine.jurisdictions.ca.trace.contribution_tier_rate`."""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.contribution_tier_rate import ContributionTierRateLine


@english_renderer
class ContributionTierRateRenderer:
    """English text for ContributionTierRateLine."""

    line_class = ContributionTierRateLine

    def render(self, line: ContributionTierRateLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        tier = line.tier
        return (
            f"A further dollar is charged {EnglishFigures.percent(tier.rate.value)}% only when "
            f"{names.figure(line.earnings, line.earnings_amount)} is at least "
            f"{EnglishFigures.money(tier.lower)} and under {EnglishFigures.money(tier.upper)}, "
            f"which gives {names.shown(line.label, line.rate)}"
        )
