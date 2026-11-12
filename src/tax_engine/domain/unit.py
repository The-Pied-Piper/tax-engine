"""Units: the words or symbol a figure is written with, such as `CA$` or `months`.

A package declares its units on a `UnitCatalog`; a manifest names one with `unit:` and
`UnitRegistry.resolve` finds it.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.errors import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace, Registry

__all__ = ["Placement", "Unit", "UnitCatalog", "UnitRegistry"]

# The namespace whose units every jurisdiction may use.
_CORE = "core"


class Placement(enum.Enum):
    """Where a unit's text goes: `BEFORE` the number ("CA$3500.00") or `AFTER` it ("12 months")."""

    BEFORE = "before"
    AFTER = "after"


@dataclass(frozen=True)
class Unit:
    """A unit a manifest names `unit: <name>`, with the text it is written with.

    `singular` is the text beside a figure of exactly 1, `plural` the text beside any other; a
    symbol such as `CA$` is both. A unit placed `BEFORE` is written against its number, one placed
    `AFTER` after a space. The name is a snake_case local id.
    """

    name: str
    singular: str
    plural: str
    placement: Placement

    def __post_init__(self) -> None:
        try:
            Namespace(_CORE).identifier(self.name)
        except InvalidRegistrationError:
            raise InvalidRegistrationError(
                f"invalid unit name {self.name!r}: expected snake_case, e.g. 'months'"
            ) from None
        for kind, text in (("singular", self.singular), ("plural", self.plural)):
            if not text.strip():
                raise InvalidRegistrationError(
                    f"unit {self.name!r}: {kind} must not be empty, got {text!r}"
                )

    def format(self, value: Decimal | int, shown: str) -> str:
        """The figure `value`, which prints as `shown`, with this unit: `EX$3500.00`, `12 moons`."""
        text = self.singular if value == 1 else self.plural
        return f"{text}{shown}" if self.placement is Placement.BEFORE else f"{shown} {text}"


class UnitCatalog:
    """One package's units, built in the package's namespace.

    Each package that has units creates one, e.g. `UnitCatalog(Namespace("ca"))`. Declaring
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

    def declare(self, name: str, singular: str, plural: str, placement: Placement) -> Unit:
        """Declare the unit `name`; a name declared twice is an error."""
        unit = Unit(name, singular, plural, placement)
        if name in self._units:
            raise DuplicateRegistrationError(f"unit {name!r} is already declared in this catalog")
        self._units[name] = unit
        return unit


class UnitRegistry(Registry[Unit]):
    """The units the packages declare, keyed `<namespace>/<name>` (`ca/cad`)."""

    def register_catalog(self, catalog: UnitCatalog) -> None:
        """Register every unit `catalog` declared; a clash registers nothing from the catalog.

        Registering the same catalog again changes nothing.
        """
        pending = [
            (catalog.namespace.identifier(unit.name), unit)
            for unit in catalog.units
            if self.identifier_of(unit) is None
        ]
        for key, _ in pending:
            if key in self.identifiers():
                raise DuplicateRegistrationError(f"unit {key!r} is already registered")
        for key, unit in pending:
            self.register(key, unit)

    def resolve(self, name: str, jurisdiction: JurisdictionCode) -> Unit:
        """The unit a manifest of `jurisdiction` names `name`.

        It is looked for in core and in the jurisdiction's namespaces, a province's and its
        country's. Raises UnknownRegistrationError if none has it, and InvalidRegistrationError if
        more than one does, naming each.
        """
        spaces = (*jurisdiction.namespaces, _CORE)
        keys = [f"{space}/{name}" for space in spaces if f"{space}/{name}" in self.identifiers()]
        if not keys:
            raise UnknownRegistrationError(f"unit {name!r} is not declared in {', '.join(spaces)}")
        if len(keys) > 1:
            raise InvalidRegistrationError(
                f"unit {name!r} is ambiguous: declared in " + " and ".join(repr(k) for k in keys)
            )
        return self.get(keys[0])
