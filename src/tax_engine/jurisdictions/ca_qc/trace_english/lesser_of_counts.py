"""English text for the trace lines of `tax_engine.jurisdictions.ca_qc.trace.lesser_of_counts`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca_qc.trace.lesser_of_counts import LesserOfCountsLine


@english_renderer
class LesserOfCountsRenderer:
    """English text for LesserOfCountsLine."""

    line_class = LesserOfCountsLine

    def render(self, line: LesserOfCountsLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        terms = EnglishFigures.listing([names.figure(kind, count) for kind, count in line.parts])
        word = "Lesser" if len(line.parts) == 2 else "Least"
        if len(line.parts) == 1:
            return f"{terms} gives {names.shown(line.label, line.result)}"
        return f"{word} of {terms} gives {names.shown(line.label, line.result)}"
