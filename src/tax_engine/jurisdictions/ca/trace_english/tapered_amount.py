"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.tapered_amount`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.tapered_amount import TaperedAmountLine


@english_renderer
class TaperedAmountRenderer:
    """English text for TaperedAmountLine."""

    line_class = TaperedAmountLine

    def render(self, line: TaperedAmountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        taper = line.taper
        # The amount taken off, in cents for reading; the exact fraction is on the line.
        reduction = (
            Decimal(line.reduction.numerator) / Decimal(line.reduction.denominator)
        ).quantize(Decimal("0.01"))
        return (
            f"{EnglishFigures.money(taper.base)} plus {EnglishFigures.money(taper.supplement)}, "
            f"less {EnglishFigures.money(reduction)} (the reduction for "
            f"{names.figure(line.base, line.base_amount)} over "
            f"{EnglishFigures.money(taper.threshold)}, "
            f"spread over a range of {EnglishFigures.money(taper.range)}), "
            f"not below {EnglishFigures.money(taper.base)}, "
            f"gives {EnglishFigures.money(line.result)} ({EnglishFigures.rounding(line.rounding)})"
        )
