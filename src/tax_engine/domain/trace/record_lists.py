"""Trace lines for record lists: a field's total, the total of its positive amounts and the
records' count over a list, the first record's value, the items' total, and one item's sum or lesser
of.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import ArtifactKind, Money
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace.base import TraceLine

__all__ = [
    "RecordTotalLine",
    "RecordPositiveTotalLine",
    "RecordCountLine",
    "FirstRecordCountLine",
    "ItemsTotalLine",
    "ItemSumLine",
    "ItemLesserOfLine",
]


@dataclass(frozen=True)
class RecordTotalLine(TraceLine):
    """The `total` produced as `output`: `field` added over the items of a record list, in the
    list's order, each item's `amounts` entry its value of `field`, exactly.

    Its own class, not a `SumLine`: the parts are the items of one list, named by position, not
    artifacts of their own.
    """

    output: Money
    field: Money
    amounts: tuple[Decimal, ...]
    total: Decimal

    @property
    def amount(self) -> Decimal:
        """The exact total."""
        return self.total


@dataclass(frozen=True)
class RecordPositiveTotalLine(TraceLine):
    """The `total` produced as `output`: the positive `amounts` of `field` added over the items of
    a record list, in the list's order, each amount exactly as read; a zero or negative amount
    counts 0.

    Its own class, not a `SumLine`: the parts are the items of one list, named by position, not
    artifacts of their own.
    """

    output: Money
    field: Money
    amounts: tuple[Decimal, ...]
    total: Decimal

    @property
    def amount(self) -> Decimal:
        """The exact total."""
        return self.total


@dataclass(frozen=True)
class RecordCountLine(TraceLine):
    """The `count` of the records of the list `records`, produced as `output`."""

    output: ArtifactKind[int]
    records: ArtifactKind[RecordList]
    count: int

    @property
    def amount(self) -> Decimal:
        """The count, as an amount."""
        return Decimal(self.count)


@dataclass(frozen=True)
class FirstRecordCountLine(TraceLine):
    """The `value` of the count `field` in the first item of a record list, produced as `output`,
    the list having `record_count` items.
    """

    output: ArtifactKind[int]
    field: ArtifactKind[int]
    value: int
    record_count: int

    @property
    def amount(self) -> Decimal:
        """The count, as an amount."""
        return Decimal(self.value)


@dataclass(frozen=True)
class ItemsTotalLine(TraceLine):
    """The `total` produced as `output` by adding `items`, each the position (from 1) of an item
    of a record list and its amount, in order. No items is a total of 0.

    Its own class, not a `SumLine`: the parts are items of one list, named by position, not
    artifacts of their own.
    """

    output: Money
    items: tuple[tuple[int, Decimal], ...]
    total: Decimal

    @property
    def amount(self) -> Decimal:
        """The exact total."""
        return self.total


@dataclass(frozen=True)
class ItemSumLine(TraceLine):
    """The `total` produced as `output` for the item at `position` (from 1) of a record list, by
    adding `parts`, each a field kind and its value in that item, in order.

    Its own class, not a `SumLine`: the parts are fields of one item, named by its position.
    """

    output: Money
    position: int
    parts: tuple[tuple[Money, Decimal], ...]
    total: Decimal

    @property
    def amount(self) -> Decimal:
        """The total of the item's parts."""
        return self.total


@dataclass(frozen=True)
class ItemLesserOfLine(TraceLine):
    """The `result` for the item at `position` (from 1) of a record list, produced as `output`:
    the least of `parts`, each a field kind and its value in that item, in order.

    Its own class, not a `LesserOfLine`: the parts are fields of one item, named by its position.
    """

    output: Money
    position: int
    parts: tuple[tuple[Money, Decimal], ...]
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The least of the item's parts."""
        return self.result
