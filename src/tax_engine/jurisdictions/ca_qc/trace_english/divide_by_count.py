"""English text for the trace lines of `tax_engine.jurisdictions.ca_qc.trace.divide_by_count`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca_qc.trace.divide_by_count import DivideByCountLine


@english_renderer
class DivideByCountRenderer:
    """English text for DivideByCountLine."""

    line_class = DivideByCountLine

    def render(self, line: DivideByCountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        amount = names.figure(line.amount_kind, line.amount_value)
        count = names.figure(line.count_kind, line.count)
        result = names.shown(line.label, line.result)
        if line.count == 0:
            return f"{amount} shared among {count}, which is zero, gives {result}"
        return (
            f"{amount} shared among {count} gives {result} "
            f"({EnglishFigures.rounding(line.rounding)})"
        )
