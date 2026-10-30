"""The jurisdiction packages: where each keeps its data, and registering their catalogs.

A jurisdiction package declares only `NAMESPACE = "..."` in its `__init__.py`; its directory is
the one holding that file, with `catalog.py`, `manifests/` and `parameters/` inside. The YAML
sources read under these directories; `register` imports each `catalog` module and registers its
`CATALOG` into an artifact registry, when the composition root asks.
"""

from __future__ import annotations

import importlib
from collections.abc import Iterable, Mapping
from pathlib import Path
from types import MappingProxyType, ModuleType

from tax_engine.domain.artifact import ArtifactCatalog, ArtifactRegistry
from tax_engine.domain.errors import DuplicateRegistrationError, InvalidRegistrationError
from tax_engine.domain.registry import Namespace


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

    def register(self, registry: ArtifactRegistry | None = None) -> None:
        """Register every package's catalog, its `catalog` module's `CATALOG`, into `registry`.

        `None` means the shared ArtifactRegistry. Registering again is idempotent. Every catalog
        is looked up first, so a package without a catalog in its own namespace registers
        nothing; an identifier clashing with one already in `registry` is an error, which can
        leave the catalogs registered before it in place.
        """
        target = ArtifactRegistry.shared() if registry is None else registry
        catalogs = [self._catalog(name, namespace) for name, namespace in self._namespaces.items()]
        for catalog in catalogs:
            target.register_catalog(catalog)

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
