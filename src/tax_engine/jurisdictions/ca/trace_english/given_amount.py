"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.given_amount`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.given_amount import GivenAmountLine


@english_renderer
class GivenAmountRenderer:
    """English text for GivenAmountLine."""

    line_class = GivenAmountLine

    def render(self, line: GivenAmountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return f"{names.figure(line.given, line.given_amount)}, as given"
