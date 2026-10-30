"""English text for the trace lines of `tax_engine.domain.trace.choices`: one renderer class
per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
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

    def render(self, line: ChosenByCountLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        count_kind = line.count_kind
        count = line.count
        chosen_kind = line.chosen_kind
        chosen = line.chosen_value
        return (
            f"{output.label}: {chosen_kind.label} {EnglishFigures.money(chosen)}, "
            f"chosen as {count_kind.label} is {count}"
        )


@english_renderer
class ChosenBySignRenderer:
    """English text for ChosenBySignLine."""

    line_class = ChosenBySignLine

    def render(self, line: ChosenBySignLine) -> str:
        """The English sentence for `line`."""
        output = line.output
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
            return (
                f"{output.label}: 0, no amount when {sign_kind.label} "
                f"{EnglishFigures.money(sign)} is {word}"
            )
        return (
            f"{output.label}: {chosen_kind.label} {EnglishFigures.money(line.chosen_value)}, "
            f"chosen as {sign_kind.label} {EnglishFigures.money(sign)} is {word}"
        )


@english_renderer
class ChosenByRangeRenderer:
    """English text for ChosenByRangeLine."""

    line_class = ChosenByRangeLine

    def render(self, line: ChosenByRangeLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        tested_kind = line.tested_kind
        tested = line.tested_value
        chosen_kind = line.chosen_kind
        chosen = line.chosen_value
        return (
            f"{output.label}: {chosen_kind.label} {EnglishFigures.money(chosen)}, "
            f"chosen as {tested_kind.label} is {EnglishFigures.money(tested)}"
        )


@english_renderer
class ConditionRenderer:
    """English text for ConditionLine."""

    line_class = ConditionLine

    def render(self, line: ConditionLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        text = line.text
        reads = line.reads
        applies = line.applies
        figures = ", ".join(
            f"{kind.label} {value if isinstance(value, int) else EnglishFigures.money(value)}"
            for kind, value in reads
        )
        verdict = "applies" if applies else "does not apply"
        return f'{output.label}: condition {position} "{text}": {figures}, {verdict}'


@english_renderer
class ConditionsCountRenderer:
    """English text for ConditionsCountLine."""

    line_class = ConditionsCountLine

    def render(self, line: ConditionsCountLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        applied = line.applied
        count = line.count
        if not applied:
            which = "no condition applies"
        elif len(applied) == 1:
            which = f"condition {applied[0]} applies"
        else:
            which = f"conditions {', '.join(str(position) for position in applied)} apply"
        return f"{output.label}: {which}, so {count}"
