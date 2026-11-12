"""Unit tests for units: `Unit`, `Placement`, `UnitCatalog` and `UnitRegistry`.

A unit has a name (what a manifest writes after `unit:`), a singular and a plural word or symbol,
and a placement before or after the number. A package declares its units on a `UnitCatalog`, like
its kinds on an `ArtifactCatalog`; a `UnitRegistry` holds the catalogs and resolves a manifest's
unit name for one jurisdiction: core's units, the jurisdiction's own, and, for a province, those
of its federal package. Names, symbols and namespaces are made up.
"""

from __future__ import annotations

import dataclasses
from decimal import Decimal

import pytest

from tax_engine.domain.errors import (
    DomainError,
    DuplicateRegistrationError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import Placement, Unit, UnitCatalog, UnitRegistry

D = Decimal

CROWNS = Unit("crowns", "EX$", "EX$", Placement.BEFORE)
MOONS = Unit("moons", "moon", "moons", Placement.AFTER)


def test_a_unit_has_a_name_words_and_a_placement() -> None:
    assert (CROWNS.name, CROWNS.singular, CROWNS.plural, CROWNS.placement) == (
        "crowns",
        "EX$",
        "EX$",
        Placement.BEFORE,
    )
    assert MOONS.placement is Placement.AFTER


def test_a_unit_is_a_value() -> None:
    assert Unit("moons", "moon", "moons", Placement.AFTER) == MOONS
    assert hash(Unit("moons", "moon", "moons", Placement.AFTER)) == hash(MOONS)
    assert CROWNS != MOONS


def test_a_unit_before_the_number_is_written_against_it() -> None:
    assert CROWNS.format(D("3500.00"), "3500.00") == "EX$3500.00"
    assert CROWNS.format(D("0.00"), "0.00") == "EX$0.00"


def test_a_unit_after_the_number_is_written_after_a_space() -> None:
    assert MOONS.format(12, "12") == "12 moons"


def test_a_unit_after_the_number_is_singular_for_exactly_one() -> None:
    assert MOONS.format(1, "1") == "1 moon"
    assert MOONS.format(2, "2") == "2 moons"
    assert MOONS.format(0, "0") == "0 moons"


def test_a_unit_before_the_number_uses_its_singular_or_plural_the_same_way() -> None:
    marks = Unit("marks", "one mark ", "marks ", Placement.BEFORE)

    assert marks.format(1, "1") == "one mark 1"
    assert marks.format(3, "3") == "marks 3"


@pytest.mark.parametrize("name", ["", "Moons", "two words", "ex/moons", "9moons"])
def test_a_unit_name_is_a_snake_case_local_id(name: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="unit name"):
        Unit(name, "moon", "moons", Placement.AFTER)


@pytest.mark.parametrize("singular", ["", "   "])
def test_a_unit_needs_a_singular_and_a_plural(singular: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="singular"):
        Unit("moons", singular, "moons", Placement.AFTER)
    with pytest.raises(InvalidRegistrationError, match="plural"):
        Unit("moons", "moon", singular, Placement.AFTER)


def test_a_package_declares_its_units_on_a_catalog() -> None:
    catalog = UnitCatalog(Namespace("ex"))

    crowns = catalog.declare("crowns", "EX$", "EX$", Placement.BEFORE)
    moons = catalog.declare("moons", "moon", "moons", Placement.AFTER)

    assert catalog.namespace == Namespace("ex")
    assert crowns == CROWNS
    assert catalog.units == (CROWNS, moons)


def test_a_catalog_refuses_a_name_it_already_declared() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("moons", "moon", "moons", Placement.AFTER)

    with pytest.raises(DuplicateRegistrationError, match="moons"):
        catalog.declare("moons", "mooon", "mooons", Placement.AFTER)


def test_a_registry_resolves_the_units_of_the_catalogs_registered() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("crowns", "EX$", "EX$", Placement.BEFORE)
    registry = UnitRegistry()
    registry.register_catalog(catalog)

    assert registry.resolve("crowns", JurisdictionCode("EX")) == CROWNS


def test_registering_the_same_catalog_again_changes_nothing() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("crowns", "EX$", "EX$", Placement.BEFORE)
    registry = UnitRegistry()

    registry.register_catalog(catalog)
    registry.register_catalog(catalog)

    assert registry.resolve("crowns", JurisdictionCode("EX")) == CROWNS


def test_a_second_catalog_of_one_namespace_may_not_redeclare_a_name() -> None:
    first = UnitCatalog(Namespace("ex"))
    first.declare("crowns", "EX$", "EX$", Placement.BEFORE)
    second = UnitCatalog(Namespace("ex"))
    second.declare("crowns", "X$", "X$", Placement.BEFORE)
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
        ("ex-ab", "florins", "AB$"),
    ):
        catalog = UnitCatalog(Namespace(namespace))
        catalog.declare(name, symbol, symbol, Placement.BEFORE)
        registry.register_catalog(catalog)
    return registry


def test_every_jurisdiction_resolves_core_units() -> None:
    registry = _registry()

    for code in ("EX", "EX-ON", "EX-AB"):
        assert registry.resolve("moons", JurisdictionCode(code)).name == "moons"


def test_a_jurisdiction_resolves_its_own_units() -> None:
    assert _registry().resolve("ducats", JurisdictionCode("EX-ON")).singular == "ON$"
    assert _registry().resolve("crowns", JurisdictionCode("EX")).singular == "EX$"


def test_a_province_inherits_the_units_of_its_federal_package() -> None:
    assert _registry().resolve("crowns", JurisdictionCode("EX-ON")).singular == "EX$"
    assert _registry().resolve("crowns", JurisdictionCode("EX-AB")).singular == "EX$"


def test_a_unit_found_in_neither_core_nor_the_jurisdiction_is_unknown() -> None:
    registry = _registry()

    with pytest.raises(UnknownRegistrationError, match="unit 'furlongs'") as caught:
        registry.resolve("furlongs", JurisdictionCode("EX-ON"))
    assert isinstance(caught.value, DomainError)


def test_another_provinces_or_a_provinces_units_are_not_inherited_sideways_or_upwards() -> None:
    registry = _registry()

    with pytest.raises(UnknownRegistrationError, match="unit 'ducats'"):
        registry.resolve("ducats", JurisdictionCode("EX-AB"))
    with pytest.raises(UnknownRegistrationError, match="unit 'ducats'"):
        registry.resolve("ducats", JurisdictionCode("EX"))


def test_a_unit_is_a_frozen_public_value_with_four_readable_fields() -> None:
    assert [f.name for f in dataclasses.fields(Unit)] == [
        "name",
        "singular",
        "plural",
        "placement",
    ]
    with pytest.raises(dataclasses.FrozenInstanceError):
        MOONS.name = "suns"  # type: ignore[misc]
    assert {p.value for p in Placement} == {"before", "after"}
