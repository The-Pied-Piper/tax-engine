"""UnitText: the text one language writes a unit with, the same protocol for every language.

A `Unit` is only its identifier; each language supplies how a figure is written with it by
implementing `UnitText`. `trace_english.unit_text` holds the English implementation.
"""

from __future__ import annotations

import enum
from decimal import Decimal
from typing import Protocol

__all__ = ["Placement", "UnitText"]


class Placement(enum.Enum):
    """Where a unit's text goes: `BEFORE` the number ("EX$3500.00") or `AFTER` it ("12 moons")."""

    BEFORE = "before"
    AFTER = "after"


class UnitText(Protocol):
    """The text one language writes a unit with; every language implements it.

    A language defines, for its unit, the text beside a figure of exactly 1 (`singular`) and beside
    any other (`plural`), where the text goes (`placement`) and whether a space separates it from
    the figure (`spaced`), and writes a figure with them in `write`.
    """

    @property
    def identifier(self) -> str:
        """The identifier of the unit this is the text of."""
        ...

    @property
    def singular(self) -> str:
        """The text beside a figure of exactly 1."""
        ...

    @property
    def plural(self) -> str:
        """The text beside any other figure."""
        ...

    @property
    def placement(self) -> Placement:
        """Whether the text goes before or after the figure."""
        ...

    @property
    def spaced(self) -> bool:
        """Whether one space separates the text from the figure."""
        ...

    def write(self, shown: str, value: Decimal | int) -> str:
        """The figure `value`, which prints as `shown`, written with the unit."""
        ...
