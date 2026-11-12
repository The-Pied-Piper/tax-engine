"""The jurisdiction packages: where each keeps its data, and registering their catalogs.

A package declares `NAMESPACE` in its `__init__.py`; see docs/jurisdiction-packages.md for the
layout.
"""

from __future__ import annotations

import importlib
from collections.abc import Iterable, Mapping
from pathlib import Path
from types import MappingProxyType, ModuleType

from tax_engine.adapters.outbound.capability_modules import capabilities_in
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.parser_modules import parsers_in
from tax_engine.domain.artifact import ArtifactCatalog, ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import DuplicateRegistrationError, InvalidRegistrationError
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import UnitCatalog, UnitRegistry


class JurisdictionPackages:
    """The jurisdiction packages the application uses, keyed by the namespace each declares.

    A package without a valid `NAMESPACE`, or two packages declaring the same one, is rejected.
    """

    def __init__(self, packages: Iterable[ModuleType]) -> None:
        roots: dict[Namespace, Path] = {}
        owners: dict[Namespace, str] = {}
        names: dict[str, Namespace] = {}
        for package in packages:
            namespace = self._namespace(package)
            if namespace in owners:
                raise DuplicateRegistrationError(
                    f"namespace {namespace.name!r} is declared by both {owners[namespace]} "
                    f"and {package.__name__}"
                )
            owners[namespace] = package.__name__
            roots[namespace] = self._directory(package)
            names[package.__name__] = namespace
        self._roots: Mapping[Namespace, Path] = MappingProxyType(roots)
        self._namespaces: Mapping[str, Namespace] = MappingProxyType(names)

    def roots(self) -> Mapping[Namespace, Path]:
        """Each package's namespace mapped to its package directory."""
        return self._roots

    def register(self, registry: ArtifactRegistry) -> None:
        """Register every package's catalog, its `catalog` module's `CATALOG`, into `registry`.

        Registering again is idempotent. An identifier clashing with one already in `registry` is an
        error that can leave the catalogs registered before it in place.
        """
        catalogs = [self._catalog(name, namespace) for name, namespace in self._namespaces.items()]
        for catalog in catalogs:
            registry.register_catalog(catalog)

    def register_units(self, registry: UnitRegistry) -> None:
        """Register the units of every package that has a `units` module, its `UNITS` catalog.

        A package without a `units` module has no units. Registering again is idempotent; a unit
        identifier taken by another unit is an error.
        """
        catalogs = [self._units(name, namespace) for name, namespace in self._namespaces.items()]
        for catalog in catalogs:
            if catalog is not None:
                registry.register_catalog(catalog)

    def register_capabilities(self, registry: CapabilityRegistry) -> None:
        """Register the capabilities of every package, found by walking its `capabilities` package.

        Every package is walked first, so an import error registers nothing. Registering again is
        idempotent; an identifier taken by another class is an error that can leave earlier
        registrations in place.
        """
        found = [
            cls
            for module in (self._subpackage(name, "capabilities") for name in self._namespaces)
            if module is not None
            for cls in capabilities_in(module)
        ]
        for cls in found:
            registry.register_class(cls)

    def register_parameter_parsers(self, registry: ParameterParserRegistry) -> None:
        """Register the parsers of every package, found by walking its `parameter_parsers` package.

        Every package is walked first, so an import error registers nothing. Registering again is
        idempotent; a kind another class's parser holds is an error.
        """
        found = [
            cls
            for module in (self._subpackage(name, "parameter_parsers") for name in self._namespaces)
            if module is not None
            for cls in parsers_in(module)
        ]
        for cls in found:
            registry.register_class(cls)

    @staticmethod
    def _subpackage(package: str, name: str) -> ModuleType | None:
        module_name = f"{package}.{name}"
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name != module_name:
                raise
            return None

    @staticmethod
    def _catalog(package: str, namespace: Namespace) -> ArtifactCatalog:
        module_name = f"{package}.catalog"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name != module_name:
                raise
            raise InvalidRegistrationError(
                f"jurisdiction package {package} has no catalog module: declare its artifact "
                "kinds in catalog.py as CATALOG = ArtifactCatalog(...)"
            ) from None
        catalog = getattr(module, "CATALOG", None)
        if not isinstance(catalog, ArtifactCatalog):
            raise InvalidRegistrationError(
                f"jurisdiction package {package} must declare CATALOG as an ArtifactCatalog in "
                f"its catalog.py, got {catalog!r}"
            )
        if catalog.namespace != namespace:
            raise InvalidRegistrationError(
                f"jurisdiction package {package} declares NAMESPACE {namespace.name!r} but its "
                f"CATALOG is in namespace {catalog.namespace.name!r}"
            )
        return catalog

    @staticmethod
    def _units(package: str, namespace: Namespace) -> UnitCatalog | None:
        module = JurisdictionPackages._subpackage(package, "units")
        if module is None:
            return None
        catalog = getattr(module, "UNITS", None)
        if not isinstance(catalog, UnitCatalog):
            raise InvalidRegistrationError(
                f"jurisdiction package {package} must declare UNITS as a UnitCatalog in its "
                f"units.py, got {catalog!r}"
            )
        if catalog.namespace != namespace:
            raise InvalidRegistrationError(
                f"jurisdiction package {package} declares NAMESPACE {namespace.name!r} but its "
                f"UNITS is in namespace {catalog.namespace.name!r}"
            )
        return catalog

    @staticmethod
    def _namespace(package: ModuleType) -> Namespace:
        declared = getattr(package, "NAMESPACE", None)
        if not isinstance(declared, str):
            raise InvalidRegistrationError(
                f"jurisdiction package {package.__name__} must declare NAMESPACE = '...' as a "
                f"string in its __init__.py, got {declared!r}"
            )
        try:
            return Namespace(declared)
        except InvalidRegistrationError as exc:
            raise InvalidRegistrationError(f"{package.__name__}: {exc}") from None

    @staticmethod
    def _directory(package: ModuleType) -> Path:
        file = getattr(package, "__file__", None)
        if not isinstance(file, str):
            raise InvalidRegistrationError(
                f"jurisdiction package {package.__name__} has no __file__ to locate its data"
            )
        return Path(file).parent
