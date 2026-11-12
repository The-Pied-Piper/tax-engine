"""Units: the words or symbol a figure is written with, such as `EX$` or `moons`.

A package declares its units on a `UnitCatalog`; a manifest names one with `unit:` by its full
identifier, `<namespace>/<snake_case>` like an artifact kind's, and `UnitRegistry.unit` finds it.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from tax_engine.domain.errors import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
)
from tax_engine.domain.registry import Namespace, Registry

__all__ = ["Placement", "Unit", "UnitCatalog", "UnitRegistry"]


class Placement(enum.Enum):
    """Where a unit's text goes: `BEFORE` the number ("EX$3500.00") or `AFTER` it ("12 moons")."""

    BEFORE = "before"
    AFTER = "after"


@dataclass(frozen=True)
class Unit:
    """A unit a manifest names `unit: <identifier>`, with the text it is written with.

    `singular` is the text beside a figure of exactly 1, `plural` the text beside any other; a
    symbol such as `EX$` is both. A unit is plain data; an adapter decides how to write it. The
    identifier, `<namespace>/<snake_case>`, is the language-neutral key; the text is wording in
    one language.
    """

    identifier: str
    singular: str
    plural: str
    placement: Placement

    def __post_init__(self) -> None:
        namespace, _, local_id = self.identifier.partition("/")
        try:
            Namespace(namespace).identifier(local_id)
        except InvalidRegistrationError:
            raise InvalidRegistrationError(
                f"invalid unit identifier {self.identifier!r}: expected "
                "<namespace>/<snake_case>, e.g. 'ex/moons'"
            ) from None
        for kind, text in (("singular", self.singular), ("plural", self.plural)):
            if not text.strip():
                raise InvalidRegistrationError(
                    f"unit {self.identifier!r}: {kind} must not be empty, got {text!r}"
                )


class UnitCatalog:
    """One package's units, built in the package's namespace.

    Each package that has units creates one, e.g. `UnitCatalog(Namespace("ex"))`. Declaring
    registers nothing; `UnitRegistry.register_catalog` does.
    """

    def __init__(self, namespace: Namespace) -> None:
        self._namespace = namespace
        self._units: dict[str, Unit] = {}

    @property
    def namespace(self) -> Namespace:
        """The namespace every unit of this catalog is declared in."""
        return self._namespace

    @property
    def units(self) -> tuple[Unit, ...]:
        """Every unit declared so far, in declaration order."""
        return tuple(self._units.values())

    def declare(self, local_id: str, singular: str, plural: str, placement: Placement) -> Unit:
        """Declare the unit `local_id` in this namespace; declaring one twice is an error."""
        unit = Unit(self._namespace.identifier(local_id), singular, plural, placement)
        if unit.identifier in self._units:
            raise DuplicateRegistrationError(
                f"unit {unit.identifier!r} is already declared in this catalog"
            )
        self._units[unit.identifier] = unit
        return unit


class UnitRegistry(Registry[Unit]):
    """The units the packages declare, keyed by full identifier (`ex/crowns`)."""

    def register_catalog(self, catalog: UnitCatalog) -> None:
        """Register every unit `catalog` declared; a clash registers nothing from the catalog.

        Registering the same catalog again changes nothing.
        """
        pending = [
            (unit.identifier, unit) for unit in catalog.units if self.identifier_of(unit) is None
        ]
        for key, _ in pending:
            if key in self.identifiers():
                raise DuplicateRegistrationError(f"unit {key!r} is already registered")
        for key, unit in pending:
            self.register(key, unit)

    def unit(self, identifier: str) -> Unit:
        """The unit registered as `identifier`, whatever its namespace.

        Raises UnknownRegistrationError for an unknown identifier, a bare name included.
        """
        return self.get(identifier)
