"""Unit tests for units: `Unit`, `Placement`, `UnitCatalog` and `UnitRegistry`.

A unit has a full identifier `<namespace>/<snake_case>` (what a manifest writes after `unit:`, like
an artifact kind's), a singular and a plural word or symbol, and a placement before or after the
number; it is plain data, and the English adapter writes it (`EnglishFigures.with_unit`). A package
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
from tax_engine.domain.unit import Placement, Unit, UnitCatalog, UnitRegistry

CROWNS = Unit("ex/crowns", "EX$", "EX$", Placement.BEFORE, False)
MOONS = Unit("ex/moons", "moon", "moons", Placement.AFTER, True)


def test_a_unit_has_an_identifier_words_and_a_placement() -> None:
    assert (CROWNS.identifier, CROWNS.singular, CROWNS.plural, CROWNS.placement) == (
        "ex/crowns",
        "EX$",
        "EX$",
        Placement.BEFORE,
    )
    assert MOONS.placement is Placement.AFTER
    assert (CROWNS.spaced, MOONS.spaced) == (False, True)


def test_a_unit_is_a_value() -> None:
    assert Unit("ex/moons", "moon", "moons", Placement.AFTER, True) == MOONS
    assert hash(Unit("ex/moons", "moon", "moons", Placement.AFTER, True)) == hash(MOONS)
    assert CROWNS != MOONS


def test_a_unit_is_pure_data_it_writes_nothing() -> None:
    assert not hasattr(Unit, "format")


@pytest.mark.parametrize(
    "identifier",
    ["", "moons", "Moons", "ex/", "/moons", "ex/Moons", "ex/two words", "ex/9moons", "ex/a/b"],
)
def test_a_unit_identifier_is_a_namespace_and_a_snake_case_local_id(identifier: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="unit identifier"):
        Unit(identifier, "moon", "moons", Placement.AFTER, True)


def test_a_bare_unit_name_is_refused_naming_it() -> None:
    with pytest.raises(InvalidRegistrationError, match="'moons'"):
        Unit("moons", "moon", "moons", Placement.AFTER, True)


@pytest.mark.parametrize("singular", ["", "   "])
def test_a_unit_needs_a_singular_and_a_plural(singular: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="singular"):
        Unit("ex/moons", singular, "moons", Placement.AFTER, True)
    with pytest.raises(InvalidRegistrationError, match="plural"):
        Unit("ex/moons", "moon", singular, Placement.AFTER, True)


def test_a_package_declares_its_units_on_a_catalog() -> None:
    catalog = UnitCatalog(Namespace("ex"))

    crowns = catalog.declare("crowns", "EX$", "EX$", Placement.BEFORE, False)
    moons = catalog.declare("moons", "moon", "moons", Placement.AFTER, True)

    assert catalog.namespace == Namespace("ex")
    assert crowns == CROWNS
    assert crowns.identifier == "ex/crowns"
    assert catalog.units == (CROWNS, moons)


def test_a_catalog_refuses_a_local_id_it_already_declared() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("moons", "moon", "moons", Placement.AFTER, True)

    with pytest.raises(DuplicateRegistrationError, match="moons"):
        catalog.declare("moons", "mooon", "mooons", Placement.AFTER, True)


def test_a_registry_gets_a_unit_by_its_full_identifier() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("crowns", "EX$", "EX$", Placement.BEFORE, False)
    registry = UnitRegistry()
    registry.register_catalog(catalog)

    assert registry.get("ex/crowns") == CROWNS
    assert registry.unit("ex/crowns") == CROWNS
    assert registry.unit("ex/crowns") is registry.get("ex/crowns")


def test_registering_the_same_catalog_again_changes_nothing() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("crowns", "EX$", "EX$", Placement.BEFORE, False)
    registry = UnitRegistry()

    registry.register_catalog(catalog)
    registry.register_catalog(catalog)

    assert registry.unit("ex/crowns") == CROWNS


def test_a_second_catalog_of_one_namespace_may_not_redeclare_a_local_id() -> None:
    first = UnitCatalog(Namespace("ex"))
    first.declare("crowns", "EX$", "EX$", Placement.BEFORE, False)
    second = UnitCatalog(Namespace("ex"))
    second.declare("crowns", "X$", "X$", Placement.BEFORE, False)
    registry = UnitRegistry()
    registry.register_catalog(first)

    with pytest.raises(DuplicateRegistrationError, match="crowns"):
        registry.register_catalog(second)


def _registry() -> UnitRegistry:
    registry = UnitRegistry()
    for namespace, name, symbol in (
        ("core", "moons", "moon"),
        ("ex", "crowns", "EX$"),
        ("ex-on", "ducats", "ON$"),
    ):
        catalog = UnitCatalog(Namespace(namespace))
        catalog.declare(name, symbol, symbol, Placement.BEFORE, False)
        registry.register_catalog(catalog)
    return registry


def test_a_unit_of_any_namespace_is_found_by_its_full_identifier() -> None:
    registry = _registry()

    assert registry.unit("core/moons").singular == "moon"
    assert registry.unit("ex/crowns").singular == "EX$"
    assert registry.unit("ex-on/ducats").singular == "ON$"


def test_the_same_local_id_in_two_namespaces_is_two_units() -> None:
    registry = _registry()
    twin = UnitCatalog(Namespace("ex-on"))
    twin.declare("crowns", "ON$", "ON$", Placement.BEFORE, False)
    registry.register_catalog(twin)

    assert registry.unit("ex/crowns").singular == "EX$"
    assert registry.unit("ex-on/crowns").singular == "ON$"


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


def test_a_unit_is_a_frozen_public_value_with_five_readable_fields() -> None:
    assert [f.name for f in dataclasses.fields(Unit)] == [
        "identifier",
        "singular",
        "plural",
        "placement",
        "spaced",
    ]
    with pytest.raises(dataclasses.FrozenInstanceError):
        MOONS.identifier = "ex/suns"  # type: ignore[misc]
    assert {p.value for p in Placement} == {"before", "after"}


def test_spaced_is_part_of_a_units_equality_and_hash() -> None:
    tight = Unit("ex/crowns", "EX$", "EX$", Placement.BEFORE, False)
    spaced = Unit("ex/crowns", "EX$", "EX$", Placement.BEFORE, True)

    assert tight != spaced
    assert hash(tight) != hash(spaced)
    assert len({tight, spaced}) == 2
    assert tight == CROWNS


def test_a_unit_built_without_spaced_is_refused() -> None:
    with pytest.raises(TypeError, match="spaced"):
        Unit("ex/crowns", "EX$", "EX$", Placement.BEFORE)  # type: ignore[call-arg]


def test_declaring_a_unit_without_spaced_is_refused() -> None:
    catalog = UnitCatalog(Namespace("ex"))

    with pytest.raises(TypeError, match="spaced"):
        catalog.declare("crowns", "EX$", "EX$", Placement.BEFORE)  # type: ignore[call-arg]


def test_a_catalog_declares_spaced_by_position_or_keyword() -> None:
    catalog = UnitCatalog(Namespace("ex"))

    by_position = catalog.declare("moons", "moon", "moons", Placement.AFTER, True)
    by_keyword = catalog.declare("crowns", "EX$", "EX$", Placement.BEFORE, spaced=False)

    assert by_position.spaced is True
    assert by_keyword.spaced is False
