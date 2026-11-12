"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.contribution_tier`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.contribution_tier import ContributionTierLine


@english_renderer
class ContributionTierRenderer:
    """English text for ContributionTierLine."""

    line_class = ContributionTierLine

    def render(self, line: ContributionTierLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        tier = line.tier
        return (
            f"{EnglishFigures.percent(tier.rate.value)}% of the part of "
            f"{names.figure(line.earnings, line.earnings_amount)} between "
            f"{EnglishFigures.money(tier.lower)} and {EnglishFigures.money(tier.upper)}, which is "
            f"{EnglishFigures.money(line.contributory)}, at most "
            f"{EnglishFigures.money(tier.maximum)}, "
            f"gives {names.shown(line.label, line.result)} "
            f"({EnglishFigures.rounding(line.rounding)})"
        )
