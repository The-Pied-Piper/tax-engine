from typing import Any

import pytest

from tax_engine import factory
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.errors import UnknownRegistrationError
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import UnitCatalog, UnitRegistry
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units


def test_the_artifact_kinds_hold_every_listed_catalog() -> None:
    expected = ArtifactRegistry()
    JURISDICTIONS.register(expected)

    assert artifact_kinds().identifiers() == expected.identifiers()


def test_each_call_to_the_artifact_kinds_builds_its_own_registry() -> None:
    assert artifact_kinds() is not artifact_kinds()


def test_the_units_are_those_of_every_listed_package_none_declaring_any_yet() -> None:
    assert units().identifiers() == frozenset()


def test_each_call_to_the_units_builds_its_own_registry() -> None:
    assert units() is not units()


def test_the_engine_reads_its_manifests_with_the_registered_units(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    given: dict[str, Any] = {}

    class Spy:
        def __init__(self, roots: Any, kinds: Any, units: Any = None) -> None:
            given["units"] = units

    registry = UnitRegistry()
    monkeypatch.setattr(factory, "YamlJurisdictionSource", Spy)
    monkeypatch.setattr(factory, "units", lambda: registry)

    factory.build_tax_computation()

    assert given["units"] is registry


def test_the_engine_builds_with_the_bundled_packages_having_text_for_every_unit() -> None:
    assert factory.build_tax_computation() is not None


def test_the_engine_refuses_to_build_when_a_registered_unit_has_no_english_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("furlongs")
    registry = UnitRegistry()
    registry.register_catalog(catalog)
    monkeypatch.setattr(factory, "units", lambda: registry)

    with pytest.raises(UnknownRegistrationError, match="ex/furlongs"):
        factory.build_tax_computation()
