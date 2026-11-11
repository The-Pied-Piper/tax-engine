"""English text for the trace lines of `tax_engine.domain.trace.record_lists`:
one renderer class
per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.names import EnglishNames
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

    def render(self, line: RecordTotalLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        field = line.field
        amounts = line.amounts
        total = line.total
        items = " plus ".join(
            f"{names.of(field)} of item {position} ({EnglishFigures.money(amount)})"
            for position, amount in enumerate(amounts, start=1)
        )
        return (
            f"{items} gives {EnglishFigures.money(total)}"
            if items
            else f"No items, so {EnglishFigures.money(total)}"
        )


POSITIVE_RULE = "Only positive amounts are added; a zero or negative amount counts 0."


@english_renderer
class RecordPositiveTotalRenderer:
    """English text for RecordPositiveTotalLine."""

    line_class = RecordPositiveTotalLine

    def render(self, line: RecordPositiveTotalLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        field = line.field
        amounts = line.amounts
        total = line.total
        items = " plus ".join(
            f"{names.of(field)} of item {position} ({EnglishFigures.money(amount)})"
            + ("" if amount > 0 else " counts 0")
            for position, amount in enumerate(amounts, start=1)
        )
        sentence = (
            f"{items} gives {EnglishFigures.money(total)}."
            if items
            else f"No items, so {EnglishFigures.money(total)}."
        )
        return f"{sentence} {POSITIVE_RULE}"


@english_renderer
class RecordCountRenderer:
    """English text for RecordCountLine."""

    line_class = RecordCountLine

    def render(self, line: RecordCountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        records = line.records
        count = line.count
        noun = "item" if count == 1 else "items"
        counted = "no items" if count == 0 else f"{count} {noun}"
        return f"{counted} in {names.of(records)}, so the count is {count}"


@english_renderer
class FirstRecordCountRenderer:
    """English text for FirstRecordCountLine."""

    line_class = FirstRecordCountLine

    def render(self, line: FirstRecordCountLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        noun = "item" if line.record_count == 1 else "items"
        return f"{names.of(line.field)} of item 1 ({line.value}), of {line.record_count} {noun}"


@english_renderer
class ItemsTotalRenderer:
    """English text for ItemsTotalLine."""

    line_class = ItemsTotalLine

    def render(self, line: ItemsTotalLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        items = line.items
        total = line.total
        terms = " plus ".join(
            f"item {position} ({EnglishFigures.money(amount)})" for position, amount in items
        )
        return (
            f"{terms} gives {EnglishFigures.money(total)}"
            if terms
            else f"No items, so {EnglishFigures.money(total)}"
        )


@english_renderer
class ItemSumRenderer:
    """English text for ItemSumLine."""

    line_class = ItemSumLine

    def render(self, line: ItemSumLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        position = line.position
        parts = line.parts
        total = line.total
        terms = " plus ".join(f"{names.figure(kind, amount)}" for kind, amount in parts)
        return f"Item {position}: {terms} gives {EnglishFigures.money(total)}"


@english_renderer
class ItemLesserOfRenderer:
    """English text for ItemLesserOfLine."""

    line_class = ItemLesserOfLine

    def render(self, line: ItemLesserOfLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        position = line.position
        parts = line.parts
        result = line.result
        terms = EnglishFigures.listing([names.figure(kind, amount) for kind, amount in parts])
        word = "lesser" if len(parts) == 2 else "least"
        return f"Item {position}: {word} of {terms} gives {EnglishFigures.money(result)}"
