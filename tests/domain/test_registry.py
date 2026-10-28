"""Unit tests for Registry (a plain string-keyed store) and Namespace (namespaced identifiers).

A package declares its namespace once, as `NAMESPACE` in its `__init__.py`; `Namespace.of` finds
the nearest package above an object's module that declares one, and `identifier` builds
`<namespace>/<local id>`. Names are made up; the made-up packages live in
`registration_fixtures`.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Iterator
from types import SimpleNamespace
from typing import assert_type

import pytest

from tax_calculator.domain.errors import (
    DomainError,
    DuplicateRegistrationError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)
from tax_calculator.domain.registry import Namespace, Registry
from tests.domain.registration_fixtures.bad_namespace.oddities import Oddity
from tests.domain.registration_fixtures.nonstring_namespace import oddities as nonstring
from tests.domain.registration_fixtures.with_namespace.gadgets import Gadget, Sprocket
from tests.domain.registration_fixtures.with_namespace.inner import gadgets as inner
from tests.domain.registration_fixtures.with_namespace.plain.widgets import Widget
from tests.domain.registration_fixtures.without_namespace.orphans import Orphan


def make_registry() -> Registry[type[object]]:
    return Registry[type[object]]()


# --- registering and looking up by plain string keys ---------------------------------------


def test_get_returns_the_exact_registered_object() -> None:
    registry = make_registry()
    registry.register("gadget", Gadget)
    registry.register("sprocket", Sprocket)

    found: type[object] = registry.get("gadget")

    assert found is Gadget
    assert registry.get("sprocket") is Sprocket


def test_keys_are_used_as_given() -> None:
    registry = make_registry()
    registry.register("ex/gadget", Gadget)

    assert registry.get("ex/gadget") is Gadget
    with pytest.raises(UnknownRegistrationError, match="'gadget'"):
        registry.get("gadget")


def test_get_of_an_unknown_key_fails() -> None:
    registry = make_registry()
    registry.register("gadget", Gadget)

    with pytest.raises(UnknownRegistrationError, match="'missing'"):
        registry.get("missing")


def test_registries_do_not_share_registrations() -> None:
    first = make_registry()
    first.register("gadget", Gadget)

    with pytest.raises(UnknownRegistrationError):
        make_registry().get("gadget")


# --- uniqueness ---------------------------------------------------------------------------


def test_registering_a_key_twice_fails() -> None:
    registry = make_registry()
    registry.register("gadget", Gadget)

    with pytest.raises(DuplicateRegistrationError, match="'gadget'"):
        registry.register("gadget", Sprocket)

    assert registry.get("gadget") is Gadget  # never silently overridden


def test_registering_the_same_object_twice_under_one_key_fails() -> None:
    registry = make_registry()
    registry.register("gadget", Gadget)

    with pytest.raises(DuplicateRegistrationError, match="'gadget'"):
        registry.register("gadget", Gadget)


def test_identifiers_lists_every_registered_key() -> None:
    registry = Registry[int]()
    assert registry.identifiers() == frozenset()

    registry.register("one", 1)
    registry.register("two", 2)

    identifiers = registry.identifiers()
    assert_type(identifiers, frozenset[str])
    assert isinstance(identifiers, frozenset)
    assert identifiers == frozenset({"one", "two"})


def test_identifier_of_is_the_key_an_item_is_registered_under() -> None:
    registry = make_registry()
    registry.register("gadget", Gadget)
    registry.register("sprocket", Sprocket)

    found = registry.identifier_of(Sprocket)

    assert_type(found, str | None)
    assert found == "sprocket"
    assert registry.identifier_of(Gadget) == "gadget"


def test_identifier_of_an_unregistered_item_is_none() -> None:
    registry = make_registry()
    registry.register("gadget", Gadget)

    assert registry.identifier_of(Sprocket) is None


def test_identifier_of_matches_by_identity_not_equality() -> None:
    registry = Registry[list[int]]()
    registered = [1]
    registry.register("one", registered)

    assert registry.identifier_of([1]) is None
    assert registry.identifier_of(registered) == "one"


# --- namespaces ---------------------------------------------------------------------------


def test_namespace_of_an_object_is_the_one_its_package_declares() -> None:
    assert Namespace.of(Gadget) == Namespace("ex")
    assert Namespace.of(Gadget).name == "ex"


def test_identifier_is_the_namespace_and_the_local_id() -> None:
    assert Namespace.of(Gadget).identifier("gadget") == "ex/gadget"


def test_namespace_is_inherited_from_an_enclosing_package() -> None:
    # `plain` declares no NAMESPACE; its parent package declares "ex".
    assert Namespace.of(Widget).identifier("widget") == "ex/widget"


def test_nearest_package_declaring_a_namespace_wins() -> None:
    # `inner` declares "ex-inner" below a package declaring "ex".
    assert Namespace.of(inner.Gadget).identifier("gadget") == "ex-inner/gadget"


def test_the_same_local_id_in_different_namespaces_gives_distinct_identifiers() -> None:
    registry = make_registry()
    registry.register(Namespace.of(Gadget).identifier("gadget"), Gadget)
    registry.register(Namespace.of(inner.Gadget).identifier("gadget"), inner.Gadget)

    assert registry.get("ex/gadget") is Gadget
    assert registry.get("ex-inner/gadget") is inner.Gadget


def test_an_object_from_a_module_without_a_namespace_fails_naming_the_module() -> None:
    module = "tests.domain.registration_fixtures.without_namespace.orphans"

    with pytest.raises(InvalidRegistrationError, match="NAMESPACE") as excinfo:
        Namespace.of(Orphan)

    assert module in str(excinfo.value)


FIXTURES = "tests.domain.registration_fixtures.with_namespace"
LATE = f"{FIXTURES}.late_namespace"
REEXPORTING = f"{FIXTURES}.reexporting"
STILL_IMPORTING = (
    r"is still being imported and has no NAMESPACE: declare NAMESPACE at the top of its "
    r"__init__\.py \(repeat the parent's to inherit it\), or do not import registering modules "
    r"from that __init__\.py"
)


@pytest.fixture
def forget_half_imported() -> Iterator[None]:
    """Drop the half-imported fixture modules afterwards, so the import fails again next time."""
    yield
    for package in (LATE, REEXPORTING):
        for name in [n for n in sys.modules if n == package or n.startswith(f"{package}.")]:
            del sys.modules[name]


@pytest.mark.usefixtures("forget_half_imported")
def test_registering_before_the_package_declares_its_namespace_fails() -> None:
    # The package imports a registering module above its NAMESPACE line; falling back to the
    # enclosing package's namespace would register the item under the wrong identifier.
    with pytest.raises(InvalidRegistrationError, match=STILL_IMPORTING) as excinfo:
        importlib.import_module(LATE)

    assert LATE in str(excinfo.value)


@pytest.mark.usefixtures("forget_half_imported")
def test_registering_from_the_init_of_a_package_inheriting_its_namespace_fails() -> None:
    # Strict on purpose: while the package initialises, a missing NAMESPACE cannot be told apart
    # from one not declared yet, so inheriting packages must not import registering modules.
    with pytest.raises(InvalidRegistrationError, match=STILL_IMPORTING) as excinfo:
        importlib.import_module(REEXPORTING)

    assert REEXPORTING in str(excinfo.value)


def test_a_malformed_declared_namespace_is_rejected() -> None:
    with pytest.raises(InvalidRegistrationError, match="'Ex_Bad'"):
        Namespace.of(Oddity)


def test_a_declared_namespace_that_is_not_a_string_is_rejected() -> None:
    with pytest.raises(InvalidRegistrationError, match="NAMESPACE 1"):
        Namespace.of(nonstring.Oddity)


def test_an_object_without_a_module_name_is_rejected() -> None:
    # An object whose `__module__` is not a string gives no package to walk up from.
    with pytest.raises(InvalidRegistrationError, match="which module"):
        Namespace.of(SimpleNamespace(__module__=1))


@pytest.mark.parametrize("name", ["", "Ex", "ex_bad", "ex--bad", "-ex", "ex-", "ex/bad", "e x"])
def test_a_malformed_namespace_name_is_rejected(name: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="lowercase"):
        Namespace(name)


@pytest.mark.parametrize("name", ["core", "ca", "ca-on", "ex2", "a-b-c"])
def test_well_formed_namespace_names_are_accepted(name: str) -> None:
    assert Namespace(name).identifier("gadget") == f"{name}/gadget"


@pytest.mark.parametrize(
    "local_id",
    [
        "",
        "Gadget",
        "gadget-x",
        "gadget x",
        "_gadget",
        "gadget_",
        "gadget__x",
        "1gadget",
        "ex/gadget",
    ],
)
def test_a_local_id_that_is_not_snake_case_is_rejected(local_id: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="snake_case"):
        Namespace("ex").identifier(local_id)


@pytest.mark.parametrize("local_id", ["gadget", "gadget_2", "big_gadget", "g"])
def test_snake_case_local_ids_are_accepted(local_id: str) -> None:
    assert Namespace("ex").identifier(local_id) == f"ex/{local_id}"


# --- one shared instance per registry subclass ---------------------------------------------


class ExampleRegistry(Registry[type[object]]):
    """A made-up registry subclass, so these tests never touch a real shared registry."""


class OtherExampleRegistry(Registry[type[object]]):
    """A second made-up registry subclass."""


def test_shared_returns_the_same_instance_every_time() -> None:
    shared = ExampleRegistry.shared()

    assert isinstance(shared, ExampleRegistry)
    assert ExampleRegistry.shared() is shared


def test_each_registry_subclass_has_its_own_shared_instance() -> None:
    assert id(OtherExampleRegistry.shared()) != id(ExampleRegistry.shared())
    assert isinstance(OtherExampleRegistry.shared(), OtherExampleRegistry)


def test_a_plain_registry_can_be_constructed_directly() -> None:
    assert isinstance(Registry[type[object]](), Registry)


def test_a_directly_constructed_registry_is_not_the_shared_one() -> None:
    assert ExampleRegistry() is not ExampleRegistry.shared()


def test_a_subclass_registers_and_gets_through_the_inherited_methods() -> None:
    registry = ExampleRegistry()
    registry.register("gadget", Gadget)

    assert registry.get("gadget") is Gadget


# --- errors -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "error", [DuplicateRegistrationError, UnknownRegistrationError, InvalidRegistrationError]
)
def test_registration_errors_are_domain_errors(error: type[Exception]) -> None:
    assert issubclass(error, DomainError)
