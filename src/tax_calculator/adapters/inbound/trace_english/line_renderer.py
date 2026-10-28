"""The LineRenderer protocol: how one trace line class reads as English text."""

from __future__ import annotations

from typing import Protocol

from tax_calculator.domain.trace import TraceLine


class LineRenderer[L: TraceLine](Protocol):
    """Renders the lines of one trace line class as English text.

    EnglishTraceRenderer looks the renderer up by the exact class of each line, in an
    EnglishRendererRegistry. Declare `line_class` as a plain class attribute, not a property, so
    `@english_renderer` can type-check it against `render`.
    """

    @property
    def line_class(self) -> type[L]:
        """The exact trace line class this renderer renders."""
        ...

    def render(self, line: L) -> str:
        """The English sentence for `line`."""
        ...
