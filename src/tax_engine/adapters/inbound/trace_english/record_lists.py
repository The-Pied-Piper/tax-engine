"""English text for the trace lines of `tax_engine.domain.trace.record_lists`:
one renderer class
per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.domain.trace.record_lists import (
    FirstRecordCountLine,
    ItemLesserOfLine,
    ItemsTotalLine,
    ItemSumLine,
    RecordCountLine,
    RecordPositiveTotalLine,
    RecordTotalLine,
)


@english_renderer
class RecordTotalRenderer:
    """English text for RecordTotalLine."""

    line_class = RecordTotalLine

    def render(self, line: RecordTotalLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        field = line.field
        amounts = line.amounts
        total = line.total
        items = " + ".join(
            f"item {position} {field.label} {EnglishFigures.money(amount)}"
            for position, amount in enumerate(amounts, start=1)
        )
        return f"{output.label}: {items or 'no items'} = {EnglishFigures.money(total)}"


POSITIVE_RULE = "Only positive amounts are added; a zero or negative amount counts 0."


@english_renderer
class RecordPositiveTotalRenderer:
    """English text for RecordPositiveTotalLine."""

    line_class = RecordPositiveTotalLine

    def render(self, line: RecordPositiveTotalLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        field = line.field
        amounts = line.amounts
        total = line.total
        items = " + ".join(
            f"item {position} {field.label} {EnglishFigures.money(amount)}"
            + ("" if amount > 0 else " counts 0")
            for position, amount in enumerate(amounts, start=1)
        )
        sentence = f"{output.label}: {items or 'no items'} = {EnglishFigures.money(total)}."
        return f"{sentence} {POSITIVE_RULE}"


@english_renderer
class RecordCountRenderer:
    """English text for RecordCountLine."""

    line_class = RecordCountLine

    def render(self, line: RecordCountLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        records = line.records
        count = line.count
        noun = "item" if count == 1 else "items"
        counted = "no items" if count == 0 else f"{count} {noun}"
        return f"{output.label}: {counted} in {records.label} = {count}"


@english_renderer
class FirstRecordCountRenderer:
    """English text for FirstRecordCountLine."""

    line_class = FirstRecordCountLine

    def render(self, line: FirstRecordCountLine) -> str:
        """The English sentence for `line`."""
        return (
            f"{line.output.label}: item 1 {line.field.label} {line.value} "
            f"of {line.record_count} items"
        )


@english_renderer
class ItemsTotalRenderer:
    """English text for ItemsTotalLine."""

    line_class = ItemsTotalLine

    def render(self, line: ItemsTotalLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        items = line.items
        total = line.total
        terms = " + ".join(
            f"item {position} {EnglishFigures.money(amount)}" for position, amount in items
        )
        return f"{output.label}: {terms or 'no items'} = {EnglishFigures.money(total)}"


@english_renderer
class ItemSumRenderer:
    """English text for ItemSumLine."""

    line_class = ItemSumLine

    def render(self, line: ItemSumLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        parts = line.parts
        total = line.total
        terms = " + ".join(f"{kind.label} {EnglishFigures.money(amount)}" for kind, amount in parts)
        return f"{output.label}: item {position}: {terms} = {EnglishFigures.money(total)}"


@english_renderer
class ItemLesserOfRenderer:
    """English text for ItemLesserOfLine."""

    line_class = ItemLesserOfLine

    def render(self, line: ItemLesserOfLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        parts = line.parts
        result = line.result
        terms = " and ".join(
            f"{kind.label} {EnglishFigures.money(amount)}" for kind, amount in parts
        )
        return (
            f"{output.label}: item {position}: lesser of {terms} = {EnglishFigures.money(result)}"
        )
