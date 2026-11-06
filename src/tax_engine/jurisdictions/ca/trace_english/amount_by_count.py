"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.amount_by_count`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.amount_by_count import AmountByCountLine


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
