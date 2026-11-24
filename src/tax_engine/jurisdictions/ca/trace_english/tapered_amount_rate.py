"""English text for the trace line of `tax_engine.jurisdictions.ca.trace.tapered_amount_rate`."""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.tapered_amount_rate import TaperedAmountRateLine


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
