"""Units: what a figure is measured in, such as `ca/cad`, named by identifier only.

A package declares its units on a `UnitCatalog`; a manifest names one with `unit:` by its full
identifier, `<namespace>/<snake_case>` like an artifact kind's, and `UnitRegistry.unit` finds it.
"""

from __future__ import annotations

from dataclasses import dataclass

from tax_engine.domain.errors import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
)
from tax_engine.domain.registry import Namespace, Registry

__all__ = ["Unit", "UnitCatalog", "UnitRegistry"]


@dataclass(frozen=True)
class Unit:
    """A unit a manifest names `unit: <identifier>`: the identifier and nothing else.

    The identifier, `<namespace>/<snake_case>` (`ca/cad`), is language-neutral. The words, symbol,
    placement and spacing a figure is written with belong to each language's adapter, which finds
    them by the identifier.
    """

    identifier: str

    def __post_init__(self) -> None:
        namespace, _, local_id = self.identifier.partition("/")
        try:
            Namespace(namespace).identifier(local_id)
        except InvalidRegistrationError:
            raise InvalidRegistrationError(
                f"invalid unit identifier {self.identifier!r}: expected "
                "<namespace>/<snake_case>, e.g. 'ex/moons'"
            ) from None


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

    def declare(self, local_id: str) -> Unit:
        """Declare the unit `local_id` in this namespace; declaring one twice is an error."""
        unit = Unit(self._namespace.identifier(local_id))
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

    @property
    def units(self) -> tuple[Unit, ...]:
        """Every registered unit, in registration order."""
        return tuple(self._items.values())

    def unit(self, identifier: str) -> Unit:
        """The unit registered as `identifier`, whatever its namespace.

        Raises UnknownRegistrationError for an unknown identifier, a bare name included.
        """
        return self.get(identifier)
