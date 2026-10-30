"""Unit tests for capability registration: `@capability` and the shared CapabilityRegistry.

Made-up capabilities are never registered in the shared registry. The `@capability` tests
point `CapabilityRegistry.shared` at a fresh registry with monkeypatch: the decorator keeps
its one public form, `@capability(identifier=...)`, and the shared registry stays clean.
"""

from __future__ import annotations

from typing import assert_type

import pytest

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.progressive_tax import ProgressiveTax
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capability import Capability, CapabilityRegistry, capability
from tax_engine.domain.errors import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)
from tax_engine.domain.registry import Namespace, Registry
from tests.domain.registration_fixtures.with_namespace.gadgets import GadgetLevy


@pytest.fixture
def fresh(monkeypatch: pytest.MonkeyPatch) -> CapabilityRegistry:
    """A fresh registry that `@capability` registers into for the duration of one test."""
    registry = CapabilityRegistry()
    monkeypatch.setattr(CapabilityRegistry, "shared", classmethod(lambda cls: registry))
    return registry


# --- the registry ---------------------------------------------------------------------------


def test_capability_registry_is_a_registry_of_capability_classes() -> None:
    assert issubclass(CapabilityRegistry, Registry)


def test_shared_returns_the_same_instance_every_time() -> None:
    assert CapabilityRegistry.shared() is CapabilityRegistry.shared()
    assert isinstance(CapabilityRegistry.shared(), CapabilityRegistry)


def test_a_directly_constructed_registry_is_separate_and_empty() -> None:
    registry = CapabilityRegistry()

    assert registry is not CapabilityRegistry.shared()
    with pytest.raises(UnknownRegistrationError):
        registry.get("core/progressive_tax")


def test_register_class_returns_the_class_unchanged() -> None:
    registered = CapabilityRegistry().register_class("gadget_levy", GadgetLevy)

    assert_type(registered, type[GadgetLevy])

    assert registered is GadgetLevy


def test_register_class_registers_under_the_namespaced_identifier() -> None:
    registry = CapabilityRegistry()
    registry.register_class("gadget_levy", GadgetLevy)

    found = registry.get("ex/gadget_levy")

    assert_type(found, type[Capability])
    assert found is GadgetLevy
    assert Namespace.of(GadgetLevy).identifier("gadget_levy") == "ex/gadget_levy"


def test_register_class_needs_the_full_identifier_to_look_up() -> None:
    registry = CapabilityRegistry()
    registry.register_class("gadget_levy", GadgetLevy)

    with pytest.raises(UnknownRegistrationError, match="'gadget_levy'"):
        registry.get("gadget_levy")


def test_register_class_twice_under_one_identifier_fails() -> None:
    registry = CapabilityRegistry()
    registry.register_class("gadget_levy", GadgetLevy)

    with pytest.raises(DuplicateRegistrationError, match="'ex/gadget_levy'"):
        registry.register_class("gadget_levy", GadgetLevy)


def test_register_class_rejects_a_local_id_that_is_not_snake_case() -> None:
    with pytest.raises(InvalidRegistrationError, match="snake_case"):
        CapabilityRegistry().register_class("GadgetLevy", GadgetLevy)


# --- the decorator --------------------------------------------------------------------------


def test_decorator_registers_the_class_under_its_namespaced_identifier(
    fresh: CapabilityRegistry,
) -> None:
    capability(identifier="gadget_levy")(GadgetLevy)

    found = fresh.get("ex/gadget_levy")

    assert_type(found, type[Capability])
    assert found is GadgetLevy


def test_decorator_returns_the_class_unchanged(fresh: CapabilityRegistry) -> None:
    decorated = capability(identifier="gadget_levy")(GadgetLevy)

    assert_type(decorated, type[GadgetLevy])

    assert decorated is GadgetLevy


def test_decorating_two_classes_with_one_identifier_fails(fresh: CapabilityRegistry) -> None:
    capability(identifier="gadget_levy")(GadgetLevy)

    with pytest.raises(DuplicateRegistrationError, match="'ex/gadget_levy'"):
        capability(identifier="gadget_levy")(GadgetLevy)


# --- core capabilities ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("identifier", "cls"),
    [
        ("core/progressive_tax", ProgressiveTax),
        ("core/apply_rate", ApplyRate),
        ("core/subtract_not_below_zero", SubtractNotBelowZero),
    ],
)
def test_core_capabilities_are_registered_in_the_shared_registry(
    identifier: str, cls: type[Capability]
) -> None:
    assert CapabilityRegistry.shared().get(identifier) is cls


def test_core_capabilities_declare_the_core_namespace() -> None:
    import tax_engine.domain.capabilities as core

    assert core.NAMESPACE == "core"
