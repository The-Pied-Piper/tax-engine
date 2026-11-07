"""Unit tests for capability registration: `@capability` and the CapabilityRegistry.

`@capability` only gives a class its identifier; a registry is built and filled by whoever wires
the application. Made-up capabilities are subclasses made on the spot, so no class shared between
tests is ever stamped.
"""

from __future__ import annotations

from typing import assert_type

import pytest

from tax_engine.domain.capability import Capability, CapabilityRegistry, capability
from tax_engine.domain.errors import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)
from tax_engine.domain.registry import Registry
from tax_engine.jurisdictions.core.capabilities.apply_rate import ApplyRate
from tax_engine.jurisdictions.core.capabilities.bracket_column_figure import (
    BracketColumnLowerBound,
    BracketColumnRate,
    BracketColumnTaxAtStart,
)
from tax_engine.jurisdictions.core.capabilities.progressive_tax import ProgressiveTax
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tests.capabilities import bundled_capabilities
from tests.domain.registration_fixtures.with_namespace.gadgets import GadgetLevy


def undecorated() -> type[GadgetLevy]:
    """A new subclass of `GadgetLevy` that claims to come from the `ex` namespace's module."""

    class MadeUpLevy(GadgetLevy):
        pass

    MadeUpLevy.__module__ = GadgetLevy.__module__
    return MadeUpLevy


def made_up(local_id: str = "gadget_levy") -> type[GadgetLevy]:
    """A new subclass of `GadgetLevy` in the `ex` namespace, decorated as `local_id`."""
    return capability(identifier=local_id)(undecorated())


# --- the registry ---------------------------------------------------------------------------


def test_capability_registry_is_a_registry_of_capability_classes() -> None:
    assert issubclass(CapabilityRegistry, Registry)


def test_a_directly_constructed_registry_is_separate_and_empty() -> None:
    registry = CapabilityRegistry()

    assert registry is not CapabilityRegistry()
    with pytest.raises(UnknownRegistrationError):
        registry.get("core/progressive_tax")


def test_there_is_no_application_wide_registry() -> None:
    assert not hasattr(CapabilityRegistry, "shared")


def test_register_class_returns_the_class_unchanged() -> None:
    cls = made_up()
    registered = CapabilityRegistry().register_class(cls)

    assert_type(registered, type[GadgetLevy])

    assert registered is cls


def test_register_class_registers_under_the_identifier_the_class_carries() -> None:
    cls = made_up()
    registry = CapabilityRegistry()
    registry.register_class(cls)

    found = registry.get("ex/gadget_levy")

    assert_type(found, type[Capability])
    assert found is cls


def test_register_class_needs_the_full_identifier_to_look_up() -> None:
    registry = CapabilityRegistry()
    registry.register_class(made_up())

    with pytest.raises(UnknownRegistrationError, match="'gadget_levy'"):
        registry.get("gadget_levy")


def test_registering_the_same_class_again_changes_nothing() -> None:
    registry = CapabilityRegistry()
    cls = made_up()
    registry.register_class(cls)

    registry.register_class(cls)

    assert registry.identifiers() == {"ex/gadget_levy"}
    assert registry.get("ex/gadget_levy") is cls


def test_another_class_under_one_identifier_fails() -> None:
    registry = CapabilityRegistry()
    registry.register_class(made_up())

    with pytest.raises(DuplicateRegistrationError, match="'ex/gadget_levy'"):
        registry.register_class(made_up())


def test_register_class_refuses_a_class_without_an_identifier() -> None:
    with pytest.raises(InvalidRegistrationError, match="no identifier"):
        CapabilityRegistry().register_class(GadgetLevy)


# --- the decorator --------------------------------------------------------------------------


def test_decorator_gives_the_class_its_namespaced_identifier() -> None:
    cls = made_up()

    assert cls.IDENTIFIER == "ex/gadget_levy"
    assert cls.identifier() == "ex/gadget_levy"


def test_decorator_registers_nothing() -> None:
    made_up("never_registered")

    with pytest.raises(UnknownRegistrationError):
        bundled_capabilities().get("ex/never_registered")


def test_decorator_returns_the_class_unchanged() -> None:
    cls = undecorated()
    decorated = capability(identifier="gadget_levy")(cls)

    assert_type(decorated, type[GadgetLevy])

    assert decorated is cls


def test_decorator_rejects_a_local_id_that_is_not_snake_case() -> None:
    with pytest.raises(InvalidRegistrationError, match="snake_case"):
        made_up("GadgetLevy")


def test_a_subclass_of_a_decorated_class_carries_no_identifier_of_its_own() -> None:
    class Parent(GadgetLevy):
        pass

    Parent.__module__ = GadgetLevy.__module__
    capability(identifier="gadget_levy")(Parent)

    class Child(Parent):
        pass

    assert Child.IDENTIFIER == "ex/gadget_levy"
    assert Child.identifier() is None


# --- core capabilities ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("identifier", "cls"),
    [
        ("core/progressive_tax", ProgressiveTax),
        ("core/apply_rate", ApplyRate),
        ("core/subtract_not_below_zero", SubtractNotBelowZero),
        ("core/bracket_column_lower_bound", BracketColumnLowerBound),
        ("core/bracket_column_rate", BracketColumnRate),
        ("core/bracket_column_tax_at_start", BracketColumnTaxAtStart),
    ],
)
def test_core_capabilities_are_registered_by_the_bundled_packages(
    identifier: str, cls: type[Capability]
) -> None:
    assert bundled_capabilities().get(identifier) is cls


def test_core_capabilities_declare_the_core_namespace() -> None:
    import tax_engine.jurisdictions.core.capabilities as core

    assert core.NAMESPACE == "core"
