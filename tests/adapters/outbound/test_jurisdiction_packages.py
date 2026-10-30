"""Unit tests for JurisdictionPackages: jurisdiction packages -> namespace -> package directory.

A package's directory is `Path(package.__file__).parent` and its namespace is its `NAMESPACE`;
`register` imports each package's `catalog` module and pushes its `CATALOG` (an `ArtifactCatalog`)
into an artifact registry. Packages here are made-up module objects, put in `sys.modules` (with
their `catalog` modules) only for the duration of a test.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Iterator
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest

from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.domain.artifact import ArtifactCatalog, ArtifactRegistry
from tax_engine.domain.errors import DuplicateRegistrationError, InvalidRegistrationError
from tax_engine.domain.registry import Namespace

_MISSING = object()
"""No `catalog` module at all."""

_UNSET = object()
"""A `catalog` module without a `CATALOG`."""

type MakePackage = Callable[..., ModuleType]
type MakeOnDisk = Callable[[str, str, str], ModuleType]


@pytest.fixture
def package(monkeypatch: pytest.MonkeyPatch) -> MakePackage:
    """Builds a made-up package `name` and, unless `catalog` is missing, its `catalog` module
    holding `CATALOG = catalog`; both are in `sys.modules` until the test ends."""

    def make(
        directory: Path, name: str, namespace: object = None, catalog: object = _MISSING
    ) -> ModuleType:
        module = ModuleType(name)
        module.__file__ = str(directory / name / "__init__.py")
        module.__path__ = [str(directory / name)]
        if namespace is not None:
            module.NAMESPACE = namespace  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, name, module)
        if catalog is not _MISSING:
            catalog_module = ModuleType(f"{name}.catalog")
            if catalog is not _UNSET:
                catalog_module.CATALOG = catalog  # type: ignore[attr-defined]
            monkeypatch.setitem(sys.modules, catalog_module.__name__, catalog_module)
        return module

    return make


def catalog_of(namespace: str, *local_ids: str) -> ArtifactCatalog:
    catalog = ArtifactCatalog(Namespace(namespace))
    for local_id in local_ids:
        catalog.declare(local_id, Decimal)
    return catalog


@pytest.fixture(autouse=True)
def shared(monkeypatch: pytest.MonkeyPatch) -> ArtifactRegistry:
    """A fresh registry standing in for the shared one in every test, so it never sees these."""
    registry = ArtifactRegistry()
    monkeypatch.setattr(ArtifactRegistry, "shared", classmethod(lambda cls: registry))
    return registry


def test_maps_each_namespace_to_its_package_directory(tmp_path: Path, package: MakePackage) -> None:
    packages = JurisdictionPackages(
        (package(tmp_path, "ex", "ex"), package(tmp_path, "ex_on", "ex-on"))
    )

    assert packages.roots() == {
        Namespace("ex"): tmp_path / "ex",
        Namespace("ex-on"): tmp_path / "ex_on",
    }


def test_no_packages_give_no_roots() -> None:
    assert JurisdictionPackages(()).roots() == {}


def test_a_package_without_namespace_is_rejected(tmp_path: Path, package: MakePackage) -> None:
    with pytest.raises(InvalidRegistrationError, match="ex_on"):
        JurisdictionPackages((package(tmp_path, "ex_on"),))


def test_an_invalid_namespace_is_rejected(tmp_path: Path, package: MakePackage) -> None:
    with pytest.raises(InvalidRegistrationError, match="ex_on"):
        JurisdictionPackages((package(tmp_path, "ex_on", "Ex_On"),))


def test_two_packages_with_one_namespace_are_rejected(tmp_path: Path, package: MakePackage) -> None:
    with pytest.raises(DuplicateRegistrationError, match="'ex'"):
        JurisdictionPackages((package(tmp_path, "one", "ex"), package(tmp_path, "two", "ex")))


def test_a_package_without_a_file_is_rejected() -> None:
    module = ModuleType("ex_pkg")
    module.NAMESPACE = "ex"  # type: ignore[attr-defined]

    with pytest.raises(InvalidRegistrationError, match="ex_pkg"):
        JurisdictionPackages((module,))


# --- register ------------------------------------------------------------------------------


def test_registers_each_packages_catalog_into_the_given_registry(
    tmp_path: Path, shared: ArtifactRegistry, package: MakePackage
) -> None:
    ex = catalog_of("ex", "levy_base", "levy")
    ex_on = catalog_of("ex-on", "surtax")
    packages = JurisdictionPackages(
        (package(tmp_path, "ex", "ex", ex), package(tmp_path, "ex_on", "ex-on", ex_on))
    )
    registry = ArtifactRegistry()

    packages.register(registry)

    assert registry.identifiers() == {"ex/levy_base", "ex/levy", "ex-on/surtax"}
    for kind in (*ex.kinds, *ex_on.kinds):
        assert registry.get(kind.identifier) is kind
    assert shared.identifiers() == frozenset()


def test_registers_into_the_shared_registry_by_default(
    tmp_path: Path, shared: ArtifactRegistry, package: MakePackage
) -> None:
    ex = catalog_of("ex", "levy")
    packages = JurisdictionPackages((package(tmp_path, "ex", "ex", ex),))

    packages.register()

    assert shared.identifiers() == {"ex/levy"}
    assert shared.get("ex/levy") is ex.kinds[0]


def test_none_means_the_shared_registry(
    tmp_path: Path, shared: ArtifactRegistry, package: MakePackage
) -> None:
    packages = JurisdictionPackages((package(tmp_path, "ex", "ex", catalog_of("ex", "levy")),))

    packages.register(None)

    assert shared.identifiers() == {"ex/levy"}


def test_registering_twice_is_idempotent(tmp_path: Path, package: MakePackage) -> None:
    ex = catalog_of("ex", "levy")
    packages = JurisdictionPackages((package(tmp_path, "ex", "ex", ex),))
    registry = ArtifactRegistry()
    packages.register(registry)

    packages.register(registry)

    assert registry.identifiers() == {"ex/levy"}
    assert registry.get("ex/levy") is ex.kinds[0]


def test_no_packages_register_nothing() -> None:
    registry = ArtifactRegistry()

    JurisdictionPackages(()).register(registry)

    assert registry.identifiers() == frozenset()


def test_an_empty_catalog_registers_nothing(tmp_path: Path, package: MakePackage) -> None:
    registry = ArtifactRegistry()

    JurisdictionPackages((package(tmp_path, "ex", "ex", catalog_of("ex")),)).register(registry)

    assert registry.identifiers() == frozenset()


def test_a_package_without_a_catalog_is_rejected_by_name_and_nothing_is_registered(
    tmp_path: Path, package: MakePackage
) -> None:
    packages = JurisdictionPackages(
        (
            package(tmp_path, "ex", "ex", catalog_of("ex", "levy")),
            package(tmp_path, "ex_on", "ex-on"),
        )
    )
    registry = ArtifactRegistry()

    with pytest.raises(InvalidRegistrationError, match="ex_on"):
        packages.register(registry)

    assert registry.identifiers() == frozenset()


@pytest.mark.parametrize(
    "catalog", [None, "ex-on", object(), ArtifactRegistry(), ModuleType("ex_on.kinds")]
)
def test_a_catalog_that_is_not_an_artifact_catalog_is_rejected_by_name(
    tmp_path: Path, catalog: object, package: MakePackage
) -> None:
    packages = JurisdictionPackages(
        (
            package(tmp_path, "ex", "ex", catalog_of("ex", "levy")),
            package(tmp_path, "ex_on", "ex-on", catalog),
        )
    )
    registry = ArtifactRegistry()

    with pytest.raises(InvalidRegistrationError, match="ex_on"):
        packages.register(registry)

    assert registry.identifiers() == frozenset()


def test_a_catalog_module_without_catalog_is_rejected_by_name(
    tmp_path: Path, package: MakePackage
) -> None:
    packages = JurisdictionPackages(
        (
            package(tmp_path, "ex", "ex", catalog_of("ex", "levy")),
            package(tmp_path, "ex_on", "ex-on", _UNSET),
        )
    )
    registry = ArtifactRegistry()

    with pytest.raises(InvalidRegistrationError, match="ex_on"):
        packages.register(registry)

    assert registry.identifiers() == frozenset()


def test_a_rejected_package_does_not_fail_construction(
    tmp_path: Path, package: MakePackage
) -> None:
    packages = JurisdictionPackages((package(tmp_path, "ex_on", "ex-on"),))

    assert packages.roots() == {Namespace("ex-on"): tmp_path / "ex_on"}


def test_a_catalog_in_another_namespace_than_its_package_is_rejected(
    tmp_path: Path, package: MakePackage
) -> None:
    packages = JurisdictionPackages(
        (
            package(tmp_path, "one", "ex", catalog_of("ex", "levy")),
            package(tmp_path, "two", "ex-on", catalog_of("ex", "levy")),
        )
    )
    registry = ArtifactRegistry()

    with pytest.raises(InvalidRegistrationError, match=r"two.*'ex'.*'ex-on'|two.*'ex-on'.*'ex'"):
        packages.register(registry)

    assert registry.identifiers() == frozenset()


def test_a_catalog_clashing_with_one_already_registered_is_rejected(
    tmp_path: Path, package: MakePackage
) -> None:
    registry = ArtifactRegistry()
    registry.register_catalog(catalog_of("ex", "levy"))
    packages = JurisdictionPackages((package(tmp_path, "ex", "ex", catalog_of("ex", "levy")),))

    with pytest.raises(DuplicateRegistrationError, match="'ex/levy'"):
        packages.register(registry)


# --- import errors inside a real catalog module ----------------------------------------------


@pytest.fixture
def on_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[MakeOnDisk]:
    """Writes a real package `name` under a temporary import root, with `catalog.py` holding
    `catalog_source`; it and its modules leave `sys.modules` when the test ends."""
    monkeypatch.syspath_prepend(str(tmp_path))
    names: list[str] = []

    def make(name: str, namespace: str, catalog_source: str) -> ModuleType:
        directory = tmp_path / name
        directory.mkdir()
        (directory / "__init__.py").write_text(f"NAMESPACE = {namespace!r}\n")
        (directory / "catalog.py").write_text(catalog_source)
        names.append(name)
        return importlib.import_module(name)

    yield make
    for name in names:
        for loaded in [m for m in sys.modules if m == name or m.startswith(f"{name}.")]:
            del sys.modules[loaded]


def test_a_missing_dependency_of_a_catalog_module_is_not_hidden(on_disk: MakeOnDisk) -> None:
    packages = JurisdictionPackages(
        (on_disk("ex_on_missing_dep", "ex-on", "import made_up_missing_dep\n"),)
    )

    with pytest.raises(ModuleNotFoundError) as raised:
        packages.register(ArtifactRegistry())

    assert raised.value.name == "made_up_missing_dep"
    assert not isinstance(raised.value, InvalidRegistrationError)


def test_a_failing_import_in_a_catalog_module_is_not_hidden(on_disk: MakeOnDisk) -> None:
    packages = JurisdictionPackages(
        (on_disk("ex_on_bad_import", "ex-on", "from decimal import NoSuchThing\n"),)
    )

    with pytest.raises(ImportError, match="NoSuchThing"):
        packages.register(ArtifactRegistry())
