"""Finding capabilities by walking a package's modules: nothing lists them."""

from __future__ import annotations

from tax_engine.adapters.outbound.capability_modules import capabilities_in
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.domain.capability import CapabilityRegistry
from tests.jurisdictions.registration_fixtures import ex_cap, ex_on
from tests.jurisdictions.registration_fixtures.ex_cap import capabilities
from tests.jurisdictions.registration_fixtures.ex_cap.capabilities.levy import Levy, Undecorated
from tests.jurisdictions.registration_fixtures.ex_cap.capabilities.more.extra import Extra


def test_it_finds_every_decorated_class_in_every_module_below_the_package() -> None:
    assert capabilities_in(capabilities) == [Extra, Levy]


def test_a_class_imported_into_another_module_is_found_once_where_it_is_defined() -> None:
    assert capabilities_in(capabilities).count(Levy) == 1


def test_an_undecorated_subclass_of_a_decorated_class_is_left_out() -> None:
    assert Undecorated not in capabilities_in(capabilities)


def test_a_jurisdiction_package_registers_the_capabilities_it_walks() -> None:
    registry = CapabilityRegistry()

    JurisdictionPackages((ex_cap,)).register_capabilities(registry)

    assert registry.identifiers() == {"ex-cap/levy", "ex-cap/extra"}
    assert registry.get("ex-cap/levy") is Levy
    assert registry.get("ex-cap/extra") is Extra


def test_a_package_without_a_capabilities_package_contributes_none() -> None:
    registry = CapabilityRegistry()

    JurisdictionPackages((ex_on,)).register_capabilities(registry)

    assert registry.identifiers() == frozenset()
