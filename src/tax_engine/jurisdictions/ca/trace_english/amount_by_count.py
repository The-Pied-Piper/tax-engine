"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.amount_by_count`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.amount_by_count import AmountByCountLine


@english_renderer
class AmountByCountRenderer:
    """English text for AmountByCountLine."""

    line_class = AmountByCountLine

    def render(self, line: AmountByCountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return (
            f"Looking up {names.figure(line.count_kind, line.count)} in the table gives "
            f"{names.shown(line.label, line.row)} for {names.of(line.output)} "
            f"({EnglishFigures.rounding(line.rounding)})"
        )
