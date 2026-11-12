"""Unit tests for how JurisdictionPackages finds a package's units: an optional `units` module
holding `UNITS = UnitCatalog(...)`, registered by `register_units` into a `UnitRegistry`.

A package with no `units` module declares no units. Packages here are made-up module objects, put
in `sys.modules` (with their `units` modules) only for the duration of a test.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest
from tax_engine.domain.unit import Placement, Unit, UnitCatalog, UnitRegistry

from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.domain.errors import InvalidRegistrationError, UnknownRegistrationError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace

_NONE = object()
"""No `units` module at all."""

_UNSET = object()
"""A `units` module without `UNITS`."""

type MakePackage = Callable[..., ModuleType]


@pytest.fixture
def package(monkeypatch: pytest.MonkeyPatch) -> MakePackage:
    def make(directory: Path, name: str, namespace: str, units: object = _NONE) -> ModuleType:
        module = ModuleType(name)
        module.__file__ = str(directory / name / "__init__.py")
        module.__path__ = [str(directory / name)]
        module.NAMESPACE = namespace  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, name, module)
        if units is not _NONE:
            units_module = ModuleType(f"{name}.units")
            if units is not _UNSET:
                units_module.UNITS = units  # type: ignore[attr-defined]
            monkeypatch.setitem(sys.modules, units_module.__name__, units_module)
        return module

    return make


def catalog_of(namespace: str, name: str) -> UnitCatalog:
    catalog = UnitCatalog(Namespace(namespace))
    catalog.declare(name, "EX$", "EX$", Placement.BEFORE)
    return catalog


def test_the_units_of_each_packages_units_module_are_registered(
    tmp_path: Path, package: MakePackage
) -> None:
    packages = JurisdictionPackages(
        (
            package(tmp_path, "ex", "ex", catalog_of("ex", "crowns")),
            package(tmp_path, "ex_on", "ex-on", catalog_of("ex-on", "ducats")),
        )
    )
    registry = UnitRegistry()

    packages.register_units(registry)

    assert registry.resolve("crowns", JurisdictionCode("EX")) == Unit(
        "crowns", "EX$", "EX$", Placement.BEFORE
    )
    assert registry.resolve("ducats", JurisdictionCode("EX-ON")).name == "ducats"
    assert registry.resolve("crowns", JurisdictionCode("EX-ON")).name == "crowns"


def test_a_package_without_a_units_module_declares_no_units(
    tmp_path: Path, package: MakePackage
) -> None:
    packages = JurisdictionPackages((package(tmp_path, "ex", "ex"),))
    registry = UnitRegistry()

    packages.register_units(registry)

    with pytest.raises(UnknownRegistrationError, match="unit 'crowns'"):
        registry.resolve("crowns", JurisdictionCode("EX"))


def test_registering_units_again_is_idempotent(tmp_path: Path, package: MakePackage) -> None:
    packages = JurisdictionPackages((package(tmp_path, "ex", "ex", catalog_of("ex", "crowns")),))
    registry = UnitRegistry()

    packages.register_units(registry)
    packages.register_units(registry)

    assert registry.resolve("crowns", JurisdictionCode("EX")).name == "crowns"


@pytest.mark.parametrize("declared", [_UNSET, None, "crowns", UnitCatalog])
def test_a_units_module_must_declare_units_as_a_unit_catalog(
    tmp_path: Path, package: MakePackage, declared: object
) -> None:
    packages = JurisdictionPackages((package(tmp_path, "ex", "ex", declared),))

    with pytest.raises(InvalidRegistrationError, match=r"ex.*UNITS.*UnitCatalog"):
        packages.register_units(UnitRegistry())


def test_a_units_catalog_must_be_in_the_packages_namespace(
    tmp_path: Path, package: MakePackage
) -> None:
    packages = JurisdictionPackages((package(tmp_path, "ex", "ex", catalog_of("ex-on", "crowns")),))

    with pytest.raises(InvalidRegistrationError, match=r"NAMESPACE 'ex'.*'ex-on'"):
        packages.register_units(UnitRegistry())
