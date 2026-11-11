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


def _figure(value: int | Decimal | Blank) -> str:
    """A figure a condition read: a count as it is, an amount as money, a blank as left blank."""
    if isinstance(value, Blank):
        return "left blank"
    return str(value) if isinstance(value, int) else EnglishFigures.money(value)


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
        return (
            f"{names.figure(chosen_kind, chosen)}, chosen because {names.figure(count_kind, count)}"
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

    def render(self, line: ConditionLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        position = line.position
        text = line.text
        reads = line.reads
        applies = line.applies
        figures = ", ".join(f"{names.of(kind)} ({_figure(value)})" for kind, value in reads)
        verdict = "applies" if applies else "does not apply"
        return f'Condition {position} "{text}" {verdict}: {figures}'


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
            which = f"conditions {', '.join(str(position) for position in applied)} apply"
        return f"{which}, so the count is {count}"
