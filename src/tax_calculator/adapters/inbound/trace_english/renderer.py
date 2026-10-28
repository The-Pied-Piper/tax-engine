"""EnglishTraceRenderer: renders a trace as English text, one sentence per trace line.

Each line is rendered by the renderer registered for its exact class in an
EnglishRendererRegistry, by default the shared one that the renderer modules fill on import.
"""

from __future__ import annotations

from collections.abc import Iterable

from tax_calculator.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_calculator.domain.errors import UnknownRegistrationError
from tax_calculator.domain.trace import TraceLine


class EnglishTraceRenderer:
    """Renders trace lines as English text."""

    def __init__(self, renderers: EnglishRendererRegistry | None = None) -> None:
        """Render with `renderers`, by default the shared registry."""
        self._renderers = EnglishRendererRegistry.shared() if renderers is None else renderers

    def render(self, line: TraceLine) -> str:
        """The English sentence for `line`; raises TypeError for a line class it does not know."""
        try:
            renderer = self._renderers.for_line_class(type(line))
        except UnknownRegistrationError:
            raise TypeError(f"no English rendering for trace line {type(line).__name__}") from None
        return renderer.render(line)

    def render_all(self, trace: Iterable[TraceLine]) -> tuple[str, ...]:
        """The English sentence for each line of `trace`, in order."""
        return tuple(self.render(line) for line in trace)
