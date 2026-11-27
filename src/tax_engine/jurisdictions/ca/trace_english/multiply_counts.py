"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.multiply_counts`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.multiply_counts import MultiplyCountsLine


@english_renderer
class MultiplyCountsRenderer:
    """English text for MultiplyCountsLine."""

    line_class = MultiplyCountsLine

    def render(self, line: MultiplyCountsLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        terms = EnglishFigures.listing([names.figure(kind, count) for kind, count in line.parts])
        return f"{terms} multiplied give {names.shown(line.label, line.result)}"
