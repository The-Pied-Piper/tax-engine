"""English text for the trace lines of `tax_engine.domain.trace.choices`: one renderer class
per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.domain.blank import Blank
from tax_engine.domain.trace.choices import (
    ChosenByCountLine,
    ChosenByRangeLine,
    ChosenBySignLine,
    ConditionLine,
    ConditionsCountLine,
)


@english_renderer
class ChosenByCountRenderer:
    """English text for ChosenByCountLine."""

    line_class = ChosenByCountLine

    def render(self, line: ChosenByCountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        count_kind = line.count_kind
        count = line.count
        chosen_kind = line.chosen_kind
        chosen = line.chosen_value
        verdict = "is 0" if count == 0 else "is not 0"
        return (
            f"{names.figure(chosen_kind, chosen)}, chosen because "
            f"{names.figure(count_kind, count)} {verdict}"
        )


@english_renderer
class ChosenBySignRenderer:
    """English text for ChosenBySignLine."""

    line_class = ChosenBySignLine

    def render(self, line: ChosenBySignLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        sign_kind = line.sign_kind
        sign = line.sign
        chosen_kind = line.chosen_kind
        if sign > 0:
            word = "positive"
        elif sign < 0:
            word = "negative"
        else:
            word = "zero"
        if chosen_kind is None:
            return f"0, no amount when {names.figure(sign_kind, sign)} is {word}"
        return (
            f"{names.figure(chosen_kind, line.chosen_value)}, "
            f"chosen because {names.figure(sign_kind, sign)} is {word}"
        )


@english_renderer
class ChosenByRangeRenderer:
    """English text for ChosenByRangeLine."""

    line_class = ChosenByRangeLine

    def render(self, line: ChosenByRangeLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        tested_kind = line.tested_kind
        tested = line.tested_value
        chosen_kind = line.chosen_kind
        chosen = line.chosen_value
        return (
            f"{names.figure(chosen_kind, chosen)}, "
            f"chosen because {names.figure(tested_kind, tested)} fits its range"
        )


@english_renderer
class ConditionRenderer:
    """English text for ConditionLine."""

    line_class = ConditionLine

    @staticmethod
    def _read(label: str, value: int | Decimal | Blank, names: EnglishNames) -> str:
        """A figure a condition read, with its unit; a blank as left blank."""
        return "left blank" if isinstance(value, Blank) else names.shown(label, value)

    def render(self, line: ConditionLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        position = line.position
        text = line.text
        reads = line.reads
        applies = line.applies
        figures = ", ".join(
            f"{names.of(kind)} ({self._read(kind.label, value, names)})" for kind, value in reads
        )
        verdict = "applies" if applies else "does not apply"
        read = f" (read {figures})" if figures else ""
        return f'Condition {position} "{text}"{read} {verdict}'


@english_renderer
class ConditionsCountRenderer:
    """English text for ConditionsCountLine."""

    line_class = ConditionsCountLine

    def render(self, line: ConditionsCountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        applied = line.applied
        count = line.count
        if not applied:
            which = "no condition applies"
        elif len(applied) == 1:
            which = f"condition {applied[0]} applies"
        else:
            which = f"conditions {EnglishFigures.listing([str(p) for p in applied])} apply"
        return f"{which}, so the count is {count}"
