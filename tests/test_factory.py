from typing import Any

import pytest

from tax_engine import factory
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.unit import UnitRegistry
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
