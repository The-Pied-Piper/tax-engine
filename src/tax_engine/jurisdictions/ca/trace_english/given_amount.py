"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.given_amount`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.given_amount import GivenAmountLine


@english_renderer
class GivenAmountRenderer:
    """English text for GivenAmountLine."""

    line_class = GivenAmountLine

    def render(self, line: GivenAmountLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: {line.given.label} as given, "
            f"{EnglishFigures.money(line.given_amount)}"
        )
