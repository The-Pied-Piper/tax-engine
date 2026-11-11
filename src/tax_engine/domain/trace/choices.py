"""Trace lines for choices: a figure chosen by a count, by a sign or by a range, and the conditions
tested and counted to make a choice.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import ArtifactKind, Money
from tax_engine.domain.blank import Blank
from tax_engine.domain.trace.base import TraceLine

__all__ = [
    "ChosenByCountLine",
    "ChosenByRangeLine",
    "ChosenBySignLine",
    "ConditionLine",
    "ConditionsCountLine",
]


@dataclass(frozen=True)
class ChosenByCountLine(TraceLine):
    """`chosen_kind` (worth `chosen_value`) produced as `output`, chosen as `count_kind` is `count`:
    the first candidate for a count of 0, the second for any other count.

    The line names the candidate chosen; the other is not recorded.
    """

    output: Money
    count_kind: ArtifactKind[int]
    count: int
    chosen_kind: Money
    chosen_value: Decimal

    @property
    def amount(self) -> Decimal:
        """The chosen value, unchanged."""
        return self.chosen_value

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


@dataclass(frozen=True)
class ChosenByRangeLine(TraceLine):
    """`chosen_kind` (worth `chosen_value`) produced as `output`, chosen as `tested_kind` is
    `tested_value`: the first, second or third candidate by the range the tested amount is in.

    The line names the candidate chosen; the others and the limits are not recorded.
    """

    output: Money
    tested_kind: Money
    tested_value: Decimal
    chosen_kind: Money
    chosen_value: Decimal

    @property
    def amount(self) -> Decimal:
        """The chosen value, unchanged."""
        return self.chosen_value

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


@dataclass(frozen=True)
class ChosenBySignLine(TraceLine):
    """`chosen_kind` (worth `chosen_value`) produced as `output`, chosen as `sign_kind` is `sign`:
    the candidate of the branch the sign falls in (positive, zero or negative).

    `chosen_kind` is None when no candidate covers the branch, and the value is then 0.
    """

    output: Money
    sign_kind: Money
    sign: Decimal
    chosen_kind: Money | None
    chosen_value: Decimal

    @property
    def amount(self) -> Decimal:
        """The chosen value, unchanged."""
        return self.chosen_value

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


@dataclass(frozen=True)
class ConditionLine(TraceLine):
    """One condition of a list, the `position` (from 1) of the printed `text`, for `output`.

    `reads` holds each figure the condition's tests read, in order: the kind and its value (a count
    as an int, an amount as a Decimal), or `BLANK` for a blank figure, on which a test does not
    hold. `applies` is whether the condition holds.
    """

    output: ArtifactKind[int]
    position: int
    text: str
    reads: tuple[tuple[ArtifactKind[int] | Money, int | Decimal | Blank], ...]
    applies: bool

    @property
    def amount(self) -> Decimal:
        """1 when the condition applies, 0 when it does not."""
        return Decimal(1 if self.applies else 0)

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label


@dataclass(frozen=True)
class ConditionsCountLine(TraceLine):
    """The `count` produced as `output` from a list of conditions: `applied` holds the positions
    (from 1) of the conditions that applied, in order, none when no condition applied.
    """

    output: ArtifactKind[int]
    applied: tuple[int, ...]
    count: int

    @property
    def amount(self) -> Decimal:
        """The count."""
        return Decimal(self.count)

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
