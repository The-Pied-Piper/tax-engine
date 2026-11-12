"""Unit tests for units: `Unit`, `Placement`, `UnitCatalog` and `UnitRegistry`.

A unit is its full identifier `<namespace>/<snake_case>` (what a manifest writes after `unit:`, like
an artifact kind's) and nothing else: it is language-neutral, and each language's adapter supplies
the text (English: `EnglishUnitText`). A package
declares its units on a `UnitCatalog`, like its kinds on an `ArtifactCatalog`; a `UnitRegistry`
holds the catalogs' units and looks one up by its full identifier, whatever the jurisdiction.
Names, symbols and namespaces are made up.
"""

from __future__ import annotations

import dataclasses

import pytest

from tax_engine.domain.errors import (
    DomainError,
    DuplicateRegistrationError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import Unit, UnitCatalog, UnitRegistry

CROWNS = Unit("ex/crowns")
MOONS = Unit("ex/moons")


def test_a_unit_has_an_identifier_and_nothing_else() -> None:
    assert CROWNS.identifier == "ex/crowns"
    assert MOONS.identifier == "ex/moons"
    for text in ("singular", "plural", "placement", "spaced"):
        assert not hasattr(CROWNS, text)


def test_a_unit_is_a_value() -> None:
    assert Unit("ex/moons") == MOONS
    assert hash(Unit("ex/moons")) == hash(MOONS)
    assert CROWNS != MOONS


def test_a_unit_is_pure_data_it_writes_nothing() -> None:
    assert not hasattr(Unit, "format")


@pytest.mark.parametrize(
    "identifier",
    ["", "moons", "Moons", "ex/", "/moons", "ex/Moons", "ex/two words", "ex/9moons", "ex/a/b"],
)
def test_a_unit_identifier_is_a_namespace_and_a_snake_case_local_id(identifier: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="unit identifier"):
        Unit(identifier)


def test_a_bare_unit_name_is_refused_naming_it() -> None:
    with pytest.raises(InvalidRegistrationError, match="'moons'"):
        Unit("moons")


def test_a_package_declares_its_units_on_a_catalog() -> None:
    catalog = UnitCatalog(Namespace("ex"))

    crowns = catalog.declare("crowns")
    moons = catalog.declare("moons")

    assert catalog.namespace == Namespace("ex")
    assert crowns == CROWNS
    assert crowns.identifier == "ex/crowns"
    assert catalog.units == (CROWNS, moons)


def test_a_catalog_refuses_a_local_id_it_already_declared() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("moons")

    with pytest.raises(DuplicateRegistrationError, match="moons"):
        catalog.declare("moons")


def test_a_registry_gets_a_unit_by_its_full_identifier() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("crowns")
    registry = UnitRegistry()
    registry.register_catalog(catalog)

    assert registry.get("ex/crowns") == CROWNS
    assert registry.unit("ex/crowns") == CROWNS
    assert registry.unit("ex/crowns") is registry.get("ex/crowns")


def test_registering_the_same_catalog_again_changes_nothing() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("crowns")
    registry = UnitRegistry()

    registry.register_catalog(catalog)
    registry.register_catalog(catalog)

    assert registry.unit("ex/crowns") == CROWNS


def test_a_second_catalog_of_one_namespace_may_not_redeclare_a_local_id() -> None:
    first = UnitCatalog(Namespace("ex"))
    first.declare("crowns")
    second = UnitCatalog(Namespace("ex"))
    second.declare("crowns")
    registry = UnitRegistry()
    registry.register_catalog(first)

    with pytest.raises(DuplicateRegistrationError, match="crowns"):
        registry.register_catalog(second)


def _registry() -> UnitRegistry:
    registry = UnitRegistry()
    for namespace, name in (("core", "moons"), ("ex", "crowns"), ("ex-on", "ducats")):
        catalog = UnitCatalog(Namespace(namespace))
        catalog.declare(name)
        registry.register_catalog(catalog)
    return registry


def test_a_unit_of_any_namespace_is_found_by_its_full_identifier() -> None:
    registry = _registry()

    assert registry.unit("core/moons").identifier == "core/moons"
    assert registry.unit("ex/crowns").identifier == "ex/crowns"
    assert registry.unit("ex-on/ducats").identifier == "ex-on/ducats"


def test_the_same_local_id_in_two_namespaces_is_two_units() -> None:
    registry = _registry()
    twin = UnitCatalog(Namespace("ex-on"))
    twin.declare("crowns")
    registry.register_catalog(twin)

    assert registry.unit("ex/crowns") != registry.unit("ex-on/crowns")
    assert registry.unit("ex-on/crowns").identifier == "ex-on/crowns"


def test_an_unknown_identifier_is_unknown() -> None:
    registry = _registry()

    with pytest.raises(UnknownRegistrationError, match="ex/furlongs") as caught:
        registry.unit("ex/furlongs")
    assert isinstance(caught.value, DomainError)
    with pytest.raises(UnknownRegistrationError, match="ex/furlongs"):
        registry.get("ex/furlongs")


def test_a_bare_name_is_not_searched_for_in_any_namespace() -> None:
    registry = _registry()

    with pytest.raises(UnknownRegistrationError, match="crowns"):
        registry.get("crowns")


def test_a_unit_is_a_frozen_public_value_with_one_readable_field() -> None:
    assert [f.name for f in dataclasses.fields(Unit)] == ["identifier"]
    with pytest.raises(dataclasses.FrozenInstanceError):
        MOONS.identifier = "ex/suns"  # type: ignore[misc]


def test_a_unit_built_with_text_is_refused() -> None:
    with pytest.raises(TypeError):
        Unit("ex/crowns", "EX$", "EX$")  # type: ignore[call-arg]


def test_declaring_a_unit_takes_a_local_id_only() -> None:
    catalog = UnitCatalog(Namespace("ex"))

    with pytest.raises(TypeError):
        catalog.declare("crowns", "EX$", "EX$")  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        catalog.declare("crowns", spaced=False)  # type: ignore[call-arg]


def test_the_domain_no_longer_has_a_placement() -> None:
    import tax_engine.domain.unit as unit_module

    assert not hasattr(unit_module, "Placement")


def test_a_registry_lists_its_units_in_registration_order() -> None:
    registry = _registry()

    assert [unit.identifier for unit in registry.units] == [
        "core/moons",
        "ex/crowns",
        "ex-on/ducats",
    ]
    assert isinstance(registry.units, tuple)
    assert UnitRegistry().units == ()


def test_a_registrys_units_follow_each_registration_after_the_first() -> None:
    registry = _registry()
    later = UnitCatalog(Namespace("ex"))
    later.declare("furlongs")
    registry.register_catalog(later)

    assert [unit.identifier for unit in registry.units][-1] == "ex/furlongs"
    assert registry.units[-1] is registry.unit("ex/furlongs")
