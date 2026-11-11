"""EnglishTraceRenderer: renders a trace as English text, one sentence per trace line.

Each line is rendered by the renderer registered for its exact class in an
EnglishRendererRegistry, by default the shared one that the renderer modules fill on import.
"""

from __future__ import annotations

from collections.abc import Iterable

from tax_engine.adapters.inbound.trace_english.names import EnglishNames, FigureNames
from tax_engine.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_engine.domain.errors import UnknownRegistrationError
from tax_engine.domain.trace import TraceLine


class EnglishTraceRenderer:
    """Renders trace lines as English text."""

    def __init__(self, renderers: EnglishRendererRegistry | None = None) -> None:
        """Render with `renderers`, by default the shared registry."""
        self._renderers = EnglishRendererRegistry.shared() if renderers is None else renderers

    def render(self, line: TraceLine, printed: FigureNames | None = None) -> str:
        """The English sentence for `line`; raises TypeError for a line class it does not know.

        Figures are named as `printed` (a worksheet) prints them; with none, by label.
        """
        try:
            renderer = self._renderers.for_line_class(type(line))
        except UnknownRegistrationError:
            raise TypeError(f"no English rendering for trace line {type(line).__name__}") from None
        return _sentence(renderer.render(line, EnglishNames(printed)))

    def render_all(
        self, trace: Iterable[TraceLine], printed: FigureNames | None = None
    ) -> tuple[str, ...]:
        """The English sentence for each line of `trace`, in order, named as `printed` names."""
        return tuple(self.render(line, printed) for line in trace)


def _sentence(text: str) -> str:
    """`text` as a sentence: its first word capitalised and a full stop at the end."""
    capitalised = text[:1].upper() + text[1:]
    return capitalised if capitalised.endswith(".") else f"{capitalised}."
