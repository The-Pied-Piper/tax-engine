"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.contribution_tier`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.contribution_tier import ContributionTierLine


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
