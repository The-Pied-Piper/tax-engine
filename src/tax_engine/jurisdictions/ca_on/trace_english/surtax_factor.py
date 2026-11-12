"""English text for the trace lines of `tax_engine.jurisdictions.ca_on.trace.surtax_factor`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca_on.trace.surtax_factor import SurtaxFactorLine


@english_renderer
class SurtaxFactorRenderer:
    """English text for SurtaxFactorLine."""

    line_class = SurtaxFactorLine

    def render(self, line: SurtaxFactorLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        base = names.figure(line.base, line.base_amount)
        one = EnglishFigures.money(Decimal(1))
        tiers = line.tiers
        if not tiers:
            reason = f"is over no surtax threshold, so no rate is added to {one}"
        else:
            thresholds = EnglishFigures.listing([EnglishFigures.money(t.threshold) for t in tiers])
            rates = EnglishFigures.listing(
                [f"{EnglishFigures.percent(t.rate.value)}%" for t in tiers]
            )
            if len(tiers) == 1:
                reason = (
                    f"is over the surtax threshold of {thresholds}, "
                    f"so its rate {rates} is added to {one}"
                )
            else:
                reason = (
                    f"is over the surtax thresholds of {thresholds}, "
                    f"so their rates {rates} are added to {one}"
                )
        return f"{base} {reason}, gives {EnglishFigures.money(line.factor)}"
