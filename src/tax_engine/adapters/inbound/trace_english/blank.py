"""English text for the trace lines of `tax_engine.domain.trace.blank`: one renderer class per
line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.domain.trace.blank import (
    BlankFallbackLine,
    BlankField,
    BlankFieldFallbackLine,
    BlankPassedOnLine,
    DefaultedInputLine,
    LeftBlankLine,
)


@english_renderer
class LeftBlankRenderer:
    """English text for LeftBlankLine."""

    line_class = LeftBlankLine

    def render(self, line: LeftBlankLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return "left blank"


@english_renderer
class DefaultedInputRenderer:
    """English text for DefaultedInputLine."""

    line_class = DefaultedInputLine

    def render(self, line: DefaultedInputLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return f"not given, so the form's default gives {_figure(line.value)}"


@english_renderer
class BlankFallbackRenderer:
    """English text for BlankFallbackLine."""

    line_class = BlankFallbackLine

    def render(self, line: BlankFallbackLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return f"left blank, taken as {_figure(line.fallback)}"


def _figure(fallback: Decimal | int) -> str:
    """The fallback as money for an amount, else as a plain whole number."""
    return EnglishFigures.money(fallback) if isinstance(fallback, Decimal) else str(fallback)


def _where(field: BlankField, names: EnglishNames) -> str:
    """The field, the record's position and the list, as the trace names a blank record field."""
    return f"{names.of(field.kind)} (item {field.position} of {names.of(field.records)})"


@english_renderer
class BlankFieldFallbackRenderer:
    """English text for BlankFieldFallbackLine."""

    line_class = BlankFieldFallbackLine

    def render(self, line: BlankFieldFallbackLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        return f"{_where(line.field, names)}: left blank, taken as {_figure(line.fallback)}"


@english_renderer
class BlankPassedOnRenderer:
    """English text for BlankPassedOnLine."""

    line_class = BlankPassedOnLine

    def render(self, line: BlankPassedOnLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        named = [names.of(kind) for kind in line.because] + [
            _where(f, names) for f in line.because_fields
        ]
        causes = EnglishFigures.listing(named)
        verb = "was" if len(named) == 1 else "were"
        return f"blank because {causes} {verb} blank"
