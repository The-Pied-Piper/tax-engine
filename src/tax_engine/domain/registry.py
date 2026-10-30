"""Registries: where packages register the pieces they contribute (capabilities, parsers, ...).

The core never lists contributed pieces. `Registry` is a plain store keyed by strings; subclasses
add typed entry points under their own names. `Namespace` builds namespaced identifiers: a
package declares its namespace once, as `NAMESPACE = "..."` in its `__init__.py`, and each piece
is identified as `<namespace>/<local id>`. Nothing here discovers or imports anything.

Decorator registries (capabilities, parameter parsers) register when the decorated module is
imported, so the namespace is resolved then: resolving it while a package without `NAMESPACE`
is still being imported fails, so declare `NAMESPACE` at the top of its `__init__.py` (repeat the
parent's to inherit it), before importing any registering module. Artifact catalogs register
nothing on import: only `ArtifactRegistry.register_catalog`, called through
`JurisdictionPackages.register`, puts their kinds in a registry.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from typing import ClassVar, Self

from tax_engine.domain.errors import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)

_NAMESPACE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
_LOCAL_ID = re.compile(r"[a-z][a-z0-9]*(_[a-z0-9]+)*")


class Registry[T]:
    """A store of items of one kind under unique string keys.

    Construct one directly for a private registry, or use `shared()` for the application-wide one.
    """

    _shared: ClassVar[dict[type[object], object]] = {}

    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    @classmethod
    def shared(cls) -> Self:
        """The application-wide instance of this registry class, created on first use."""
        instance = Registry._shared.get(cls)
        if not isinstance(instance, cls):
            instance = cls()
            Registry._shared[cls] = instance
        return instance

    def register(self, key: str, item: T) -> None:
        """Store `item` under `key`; a key already taken is an error, never an override."""
        if key in self._items:
            raise DuplicateRegistrationError(f"{key!r} is already registered")
        self._items[key] = item

    def get(self, key: str) -> T:
        """The item registered under `key`."""
        try:
            return self._items[key]
        except KeyError:
            raise UnknownRegistrationError(f"nothing is registered as {key!r}") from None

    def identifiers(self) -> frozenset[str]:
        """Every key registered so far."""
        return frozenset(self._items)

    def identifier_of(self, item: T) -> str | None:
        """The key `item` itself is registered under (matched by identity), else `None`."""
        return next((key for key, found in self._items.items() if found is item), None)


@dataclass(frozen=True)
class Namespace:
    """A package's namespace, such as `core` or `ca-on`: lowercase letters, digits, single hyphens.

    It prefixes local ids to give full identifiers such as `core/progressive_tax`.
    """

    name: str

    def __post_init__(self) -> None:
        if not _NAMESPACE.fullmatch(self.name):
            raise InvalidRegistrationError(
                f"invalid namespace {self.name!r}: expected lowercase letters and digits with "
                "single hyphens, e.g. 'ca-on'"
            )

    def identifier(self, local_id: str) -> str:
        """The full identifier `<namespace>/<local_id>`; `local_id` must be snake_case."""
        if not _LOCAL_ID.fullmatch(local_id):
            raise InvalidRegistrationError(
                f"invalid local id {local_id!r}: expected snake_case, e.g. 'progressive_tax'"
            )
        return f"{self.name}/{local_id}"

    @classmethod
    def of(cls, item: object) -> Namespace:
        """The namespace declared by the nearest package above the module `item` comes from."""
        module = getattr(item, "__module__", None)
        if not isinstance(module, str):
            raise InvalidRegistrationError(f"cannot tell which module {item!r} comes from")
        parts = module.split(".")
        for end in range(len(parts), 0, -1):
            name = ".".join(parts[:end])
            package = sys.modules.get(name)
            if package is None or not hasattr(package, "__path__"):
                continue
            declared = getattr(package, "NAMESPACE", None)
            if declared is None:
                if cls._initializing(package):
                    raise InvalidRegistrationError(
                        f"package {name} is still being imported and has no NAMESPACE: declare "
                        "NAMESPACE at the top of its __init__.py (repeat the parent's to inherit "
                        "it), or do not import registering modules from that __init__.py"
                    )
                continue
            if not isinstance(declared, str):
                raise InvalidRegistrationError(
                    f"invalid NAMESPACE {declared!r} in {name}: expected a string"
                )
            try:
                return cls(declared)
            except InvalidRegistrationError as exc:
                raise InvalidRegistrationError(f"{name}: {exc}") from None
        raise InvalidRegistrationError(
            f"no package above {module} declares a NAMESPACE; "
            "declare one as NAMESPACE = '...' in the package's __init__.py"
        )

    @staticmethod
    def _initializing(package: object) -> bool:
        # `__spec__._initializing` is a private CPython attribute, set while a module's code
        # runs; where it is absent the check is skipped.
        return bool(getattr(getattr(package, "__spec__", None), "_initializing", False))
