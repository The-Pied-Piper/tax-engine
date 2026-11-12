"""UnitText: the text a language writes a unit with, and the English one, by unit.

A `Unit` is only its identifier; each language supplies how a figure is written with it. English
text registers with `english_unit` in the `trace_english/units.py` of the package that declares the
unit, keyed by the unit's identifier, and `EnglishUnitTextRegistry.require` checks at startup that
every registered unit has some.
"""

from __future__ import annotations

import enum
from collections.abc import Iterable
from dataclasses import KW_ONLY, dataclass
from decimal import Decimal
from typing import Protocol

from tax_engine.domain.errors import DuplicateRegistrationError, UnknownRegistrationError
from tax_engine.domain.registry import SharedRegistry
from tax_engine.domain.unit import Unit

__all__ = [
    "EnglishUnitText",
    "EnglishUnitTextRegistry",
    "Placement",
    "UnitText",
    "english_unit",
]


class Placement(enum.Enum):
    """Where a unit's text goes: `BEFORE` the number ("EX$3500.00") or `AFTER` it ("12 moons")."""

    BEFORE = "before"
    AFTER = "after"


class UnitText(Protocol):
    """The text one language writes a unit with; every language implements it."""

    @property
    def identifier(self) -> str:
        """The identifier of the unit this is the text of."""
        ...

    def write(self, shown: str, value: Decimal | int) -> str:
        """The figure `value`, which prints as `shown`, written with the unit."""
        ...


@dataclass(frozen=True)
class EnglishUnitText:
    """The English text of the unit `identifier`.

    `singular` is the text beside a figure of exactly 1, `plural` the text beside any other; a
    symbol such as `EX$` is both. `spaced` says whether one space separates the text from the
    figure: `False` for a symbol written against its number ("EX$3500.00", "12%"), `True` for a
    word ("12 moons"). It is separate from `placement` because before and after units may go
    either way, and it is keyword-only with no default so a unit never prints with a spacing
    nobody chose.
    """

    identifier: str
    singular: str
    plural: str
    placement: Placement
    _: KW_ONLY
    spaced: bool

    def write(self, shown: str, value: Decimal | int) -> str:
        """The figure `value`, which prints as `shown`, written with the unit.

        A unit placed before the number goes before its digits, after any minus sign ("-EX$1.00");
        one placed after goes after the number ("12 moons"). One space separates the text from the
        figure when `spaced`. The singular is used for a value of exactly 1, the plural otherwise.
        """
        text = self.singular if value == 1 else self.plural
        gap = " " if self.spaced else ""
        if self.placement is Placement.AFTER:
            return f"{shown}{gap}{text}"
        sign, digits = ("-", shown[1:]) if shown.startswith("-") else ("", shown)
        return f"{sign}{text}{gap}{digits}"


class EnglishUnitTextRegistry(SharedRegistry[EnglishUnitText]):
    """Holds one English text per unit, by the unit's identifier.

    Register with `register_text` or `english_unit`.
    """

    def register_text(self, text: EnglishUnitText) -> None:
        """Register `text` for its unit; a second text for one unit is an error."""
        if text.identifier in self.identifiers():
            raise DuplicateRegistrationError(
                f"English text for unit {text.identifier!r} is already registered"
            )
        self.register(text.identifier, text)

    def for_unit(self, unit: Unit) -> EnglishUnitText:
        """The English text of `unit`; raises UnknownRegistrationError naming a unit with none."""
        try:
            return self.get(unit.identifier)
        except UnknownRegistrationError:
            raise UnknownRegistrationError(
                f"no English text is registered for unit {unit.identifier!r}"
            ) from None

    def require(self, units: Iterable[Unit]) -> None:
        """Raise one UnknownRegistrationError naming every unit of `units` with no English text."""
        missing = [unit.identifier for unit in units if unit.identifier not in self.identifiers()]
        if missing:
            raise UnknownRegistrationError(
                "no English text is registered for unit(s) " + ", ".join(repr(m) for m in missing)
            )


def english_unit(
    identifier: str,
    singular: str,
    plural: str,
    placement: Placement,
    *,
    spaced: bool,
) -> EnglishUnitText:
    """Register the English text of the unit `identifier` on the shared registry and return it."""
    text = EnglishUnitText(identifier, singular, plural, placement, spaced=spaced)
    EnglishUnitTextRegistry.shared().register_text(text)
    return text
