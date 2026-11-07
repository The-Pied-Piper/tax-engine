"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.tapered_amount`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.tapered_amount import TaperedAmountLine


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
        # The amount taken off, from the rounded result: line 1 plus line 2 less line 11.
        reduction = taper.base + taper.supplement - line.result
        return (
            f"{output.label}: {EnglishFigures.money(taper.base)} "
            f"plus {EnglishFigures.money(taper.supplement)} "
            f"less {EnglishFigures.money(reduction)} "
            f"for {base.label} {EnglishFigures.money(amount)} "
            f"over {EnglishFigures.money(taper.threshold)} (range "
            f"{EnglishFigures.money(taper.range)}), "
            f"not below {EnglishFigures.money(taper.base)} = {EnglishFigures.money(line.result)} "
            f"({EnglishFigures.rounding(rule)})"
        )
