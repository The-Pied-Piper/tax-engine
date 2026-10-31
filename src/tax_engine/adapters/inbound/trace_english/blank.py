"""English text for the trace lines of `tax_engine.domain.trace.blank`: one renderer class per
line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.domain.trace.blank import BlankFallbackLine, BlankPassedOnLine, LeftBlankLine


@english_renderer
class LeftBlankRenderer:
    """English text for LeftBlankLine."""

    line_class = LeftBlankLine

    def render(self, line: LeftBlankLine) -> str:
        """The English sentence for `line`."""
        return f"{line.kind.label}: left blank"


@english_renderer
class BlankFallbackRenderer:
    """English text for BlankFallbackLine."""

    line_class = BlankFallbackLine

    def render(self, line: BlankFallbackLine) -> str:
        """The English sentence for `line`."""
        fallback = line.fallback
        figure = EnglishFigures.money(fallback) if isinstance(fallback, Decimal) else str(fallback)
        return f"{line.kind.label}: left blank, taken as {figure}"


@english_renderer
class BlankPassedOnRenderer:
    """English text for BlankPassedOnLine."""

    line_class = BlankPassedOnLine

    def render(self, line: BlankPassedOnLine) -> str:
        """The English sentence for `line`."""
        causes = ", ".join(kind.label for kind in line.because)
        verb = "was" if len(line.because) == 1 else "were"
        return f"{line.output.label}: blank because {causes} {verb} blank"
