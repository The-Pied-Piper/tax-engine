"""Unit tests for artifact kinds and artifacts (design.md §2).

An `ArtifactKind[V]` names a kind of artifact by a namespaced identifier and states the type of
its values; an `Artifact[V]` is one value of a kind in one computation. `ArtifactCatalog` only
records the kinds a package declares; `ArtifactRegistry.register_catalog` registers them. Names are
made up; the catalog tests point `ArtifactRegistry.shared` at a fresh registry with monkeypatch,
so the shared registry stays clean and declaring can be seen to register nothing.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Decimal
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import (
    Artifact,
    ArtifactCatalog,
    ArtifactKind,
    ArtifactRegistry,
    Money,
)
from tax_engine.domain.errors import (
    DomainError,
    DuplicateRegistrationError,
    InvalidAmountError,
    InvalidRegistrationError,
    NegativeArtifactError,
    UnknownRegistrationError,
)
from tax_engine.domain.registry import Namespace, Registry

D = Decimal
BASE = ArtifactKind("ex/taxable_base", Decimal)
TAX = ArtifactKind("ex/basic_tax", Decimal)
NON_NEGATIVE = ArtifactKind("ex/credit_amount", Decimal, non_negative=True)


@pytest.fixture
def fresh(monkeypatch: pytest.MonkeyPatch) -> ArtifactRegistry:
    """A fresh registry that catalogs register into for the duration of one test."""
    registry = ArtifactRegistry()
    monkeypatch.setattr(ArtifactRegistry, "shared", classmethod(lambda cls: registry))
    return registry


# --- ArtifactKind ---------------------------------------------------------------------------


def test_an_artifact_kind_has_an_identifier_and_a_value_type() -> None:
    assert BASE.identifier == "ex/taxable_base"
    assert BASE.value_type is Decimal


def test_the_value_type_is_known_statically() -> None:
    assert_type(BASE, ArtifactKind[Decimal])
    assert_type(ArtifactKind("ex/count", int), ArtifactKind[int])


def test_money_is_an_alias_for_decimal_artifact_kinds() -> None:
    money: Money = BASE

    assert_type(money, ArtifactKind[Decimal])


def test_artifact_kinds_are_equal_by_identifier_and_value_type() -> None:
    assert ArtifactKind("ex/taxable_base", Decimal) == BASE
    assert BASE != TAX
    other_type: ArtifactKind[Any] = ArtifactKind("ex/taxable_base", int)
    assert other_type != BASE
    assert len({BASE, ArtifactKind("ex/taxable_base", Decimal)}) == 1


def test_artifact_kinds_are_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        BASE.identifier = "ex/other"  # type: ignore[misc]


def test_label_is_the_local_part_of_the_identifier() -> None:
    assert BASE.label == "taxable_base"
    assert ArtifactKind("ca-on/basic_tax", Decimal).label == "basic_tax"
    assert_type(BASE.label, str)


@pytest.mark.parametrize(
    "identifier",
    [
        "",
        "taxable_base",  # no namespace
        "/taxable_base",
        "ex/",
        "Ex/taxable_base",
        "ex-/taxable_base",
        "e--x/taxable_base",
        "e_x/taxable_base",
        "ex/TaxableBase",
        "ex/taxable-base",
        "ex/_taxable",
        "ex/2x",
        "ex/a/b",
        " ex/a",
    ],
)
def test_rejects_an_identifier_not_namespace_slash_snake_case(identifier: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="invalid artifact kind identifier"):
        ArtifactKind(identifier, Decimal)


@pytest.mark.parametrize("identifier", ["ex/a", "ca-on/basic_tax", "x1/line_26000", "a-b-c/x2"])
def test_accepts_namespaced_snake_case_identifiers(identifier: str) -> None:
    assert ArtifactKind(identifier, Decimal).identifier == identifier


def test_an_invalid_identifier_fails_like_an_invalid_catalog_declaration(
    fresh: ArtifactRegistry,
) -> None:
    with pytest.raises(InvalidRegistrationError) as direct:
        ArtifactKind("ex/Bad", Decimal)
    with pytest.raises(InvalidRegistrationError) as declared:
        ArtifactCatalog(Namespace("ex")).declare("Bad", Decimal)

    assert type(direct.value) is type(declared.value)


def test_value_type_must_be_a_type() -> None:
    with pytest.raises(TypeError, match="value_type must be a type"):
        ArtifactKind("ex/a", cast(Any, "Decimal"))


def test_an_artifact_kind_is_invariant_in_its_value_type() -> None:
    # Covariance would let mypy accept an ArtifactKind[int] wired where an
    # ArtifactKind[Decimal] is expected.
    (value_type,) = vars(ArtifactKind)["__parameters__"]
    assert not (
        value_type.__covariant__
        or value_type.__contravariant__
        or getattr(value_type, "__infer_variance__", False)
    )


# --- Artifact -------------------------------------------------------------------------------


def test_an_artifact_carries_its_kind_and_value() -> None:
    artifact = Artifact(kind=BASE, value=D("2.5"))

    assert artifact.kind == BASE
    assert artifact.value == D("2.5")
    assert_type(artifact, Artifact[Decimal])


def test_an_artifact_value_must_be_of_its_kinds_value_type() -> None:
    with pytest.raises(TypeError, match="taxable_base must be a Decimal, got float"):
        Artifact(BASE, cast(Any, 2.5))


def test_artifacts_are_equal_by_kind_and_value() -> None:
    assert Artifact(BASE, D(1)) == Artifact(BASE, D(1))
    assert Artifact(BASE, D(1)) != Artifact(BASE, D(2))
    assert Artifact(BASE, D(1)) != Artifact(TAX, D(1))
    assert len({Artifact(BASE, D(1)), Artifact(BASE, D(1))}) == 1


def test_artifacts_are_immutable() -> None:
    artifact = Artifact(BASE, D(1))

    with pytest.raises(FrozenInstanceError):
        artifact.value = D(2)  # type: ignore[misc]


# --- non-negative kinds --------------------------------------------------------------------


def test_a_kind_is_unconstrained_by_default() -> None:
    assert BASE.non_negative is False
    assert ArtifactCatalog(Namespace("ex")).declare("taxable_base", Decimal).non_negative is False


def test_a_kind_may_be_declared_non_negative() -> None:
    assert_type(NON_NEGATIVE.non_negative, bool)
    assert NON_NEGATIVE.non_negative is True


def test_a_catalog_declares_a_non_negative_kind(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = catalog.declare("credit_amount", Decimal, non_negative=True)

    assert_type(kind, ArtifactKind[Decimal])
    assert kind.identifier == "ex/credit_amount"
    assert kind.value_type is Decimal
    assert kind.non_negative is True
    assert catalog.kinds == (kind,)


def test_a_non_negative_kind_rejects_a_negative_value_naming_the_kind_and_value() -> None:
    with pytest.raises(NegativeArtifactError, match=r"ex/credit_amount.*-1"):
        Artifact(NON_NEGATIVE, D("-1"))


@pytest.mark.parametrize("value", ["-0.0001", "-1", "-40000", "-1E+10"])
def test_a_non_negative_kind_rejects_any_value_below_zero(value: str) -> None:
    with pytest.raises(NegativeArtifactError, match="ex/credit_amount"):
        Artifact(NON_NEGATIVE, D(value))


@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity"])
def test_a_non_finite_decimal_is_refused_naming_the_kind_and_value(value: str) -> None:
    with pytest.raises(InvalidAmountError, match=rf"ex/credit_amount must be finite, got {value}"):
        Artifact(NON_NEGATIVE, D(value))


@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity"])
def test_a_non_finite_decimal_is_refused_for_a_kind_not_declared_non_negative(value: str) -> None:
    with pytest.raises(InvalidAmountError, match="ex/.* must be finite"):
        Artifact(BASE, D(value))


def test_a_negative_artifact_is_a_domain_error() -> None:
    assert issubclass(NegativeArtifactError, DomainError)


@pytest.mark.parametrize("value", ["0", "-0", "0.00", "-0.00", "0.0001", "16129"])
def test_a_non_negative_kind_accepts_zero_signed_zero_and_positive_values(value: str) -> None:
    artifact = Artifact(NON_NEGATIVE, D(value))

    assert artifact.value == D(value)


def test_an_unconstrained_kind_accepts_a_negative_value() -> None:
    assert Artifact(BASE, D("-1")).value == D("-1")


def test_a_kind_declared_in_a_catalog_as_non_negative_rejects_a_negative_value(
    fresh: ArtifactRegistry,
) -> None:
    kind = ArtifactCatalog(Namespace("ex")).declare("credit_amount", Decimal, non_negative=True)

    with pytest.raises(NegativeArtifactError, match="ex/credit_amount"):
        Artifact(kind, D("-1"))


def test_only_a_decimal_or_int_kind_may_be_non_negative_at_declaration(
    fresh: ArtifactRegistry,
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match="ex/person_name"):
        catalog.declare("person_name", str, non_negative=True)

    assert catalog.kinds == ()
    assert fresh.identifiers() == frozenset()


@pytest.mark.parametrize("value_type", [float, str, bool])
def test_only_a_decimal_or_int_kind_may_be_non_negative(value_type: type[Any]) -> None:
    # `bool` is a subclass of `int` but not a count: the flag is still refused on it.
    with pytest.raises(InvalidRegistrationError, match="ex/person_count"):
        ArtifactKind("ex/person_count", value_type, non_negative=True)


def test_a_non_decimal_kind_may_be_declared_unconstrained(fresh: ArtifactRegistry) -> None:
    kind = ArtifactCatalog(Namespace("ex")).declare("person_count", int, non_negative=False)

    assert kind.non_negative is False
    assert Artifact(kind, -1).value == -1


# --- counts: non-negative int kinds -----------------------------------------------------------
#
# A count is an `int` artifact, the number of something a form asks for. The existing
# `non_negative` flag is allowed on an `int` kind as well as a `Decimal` one, and the same
# `Artifact` check refuses a flagged count below zero; an unflagged `int` kind accepts any value.


COUNT = ArtifactKind("ex/person_count", int, non_negative=True)


def test_an_int_kind_may_be_declared_non_negative() -> None:
    count = COUNT

    assert_type(count, ArtifactKind[int])
    assert count.value_type is int
    assert count.non_negative is True


def test_a_catalog_declares_a_non_negative_int_kind(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = catalog.declare("person_count", int, non_negative=True)

    assert_type(kind, ArtifactKind[int])
    assert kind.identifier == "ex/person_count"
    assert kind.value_type is int
    assert kind.non_negative is True
    assert catalog.kinds == (kind,)


@pytest.mark.parametrize("value", [0, 1, 2, 40])
def test_a_non_negative_count_accepts_zero_and_positive_ints(value: int) -> None:
    artifact = Artifact(COUNT, value)

    assert artifact.value == value
    assert type(artifact.value) is int


def test_a_non_negative_count_rejects_a_negative_int_naming_the_kind_and_value() -> None:
    with pytest.raises(NegativeArtifactError, match=r"ex/person_count.*-1"):
        Artifact(COUNT, -1)


@pytest.mark.parametrize("value", [-1, -2, -1000])
def test_a_non_negative_count_rejects_any_int_below_zero(value: int) -> None:
    with pytest.raises(NegativeArtifactError, match="ex/person_count"):
        Artifact(COUNT, value)


def test_a_count_declared_in_a_catalog_as_non_negative_rejects_a_negative_int(
    fresh: ArtifactRegistry,
) -> None:
    kind = ArtifactCatalog(Namespace("ex")).declare("person_count", int, non_negative=True)

    with pytest.raises(NegativeArtifactError, match="ex/person_count"):
        Artifact(kind, -1)


def test_an_unflagged_int_kind_accepts_a_negative_int() -> None:
    assert Artifact(ArtifactKind("ex/person_count", int), -3).value == -3


def test_a_count_still_rejects_a_value_of_another_type() -> None:
    with pytest.raises(TypeError, match="person_count must be a int, got Decimal"):
        Artifact(COUNT, cast(Any, D("1")))


# --- ArtifactRegistry and ArtifactCatalog ---------------------------------------------------


def test_artifact_registry_is_a_registry() -> None:
    assert issubclass(ArtifactRegistry, Registry)


def test_shared_returns_the_same_instance_every_time() -> None:
    assert ArtifactRegistry.shared() is ArtifactRegistry.shared()
    assert isinstance(ArtifactRegistry.shared(), ArtifactRegistry)


def test_catalog_declares_the_namespaced_kind(fresh: ArtifactRegistry) -> None:
    kind = ArtifactCatalog(Namespace("ex")).declare("taxable_base", Decimal)

    assert_type(kind, ArtifactKind[Decimal])
    assert kind == ArtifactKind("ex/taxable_base", Decimal)


def test_declaring_registers_nothing(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    catalog.declare("taxable_base", Decimal)
    catalog.declare("person_count", int)

    assert fresh.identifiers() == frozenset()
    with pytest.raises(UnknownRegistrationError):
        fresh.get("ex/taxable_base")


def test_catalog_kinds_are_the_declared_kinds_in_declaration_order(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    base = catalog.declare("taxable_base", Decimal)
    count = catalog.declare("person_count", int)
    tax = catalog.declare("basic_tax", Decimal)

    kinds = catalog.kinds

    assert_type(kinds, tuple[ArtifactKind[Any], ...])
    assert isinstance(kinds, tuple)
    assert len(kinds) == 3
    assert kinds[0] is base
    assert kinds[1] is count
    assert kinds[2] is tax


def test_a_catalog_has_its_namespace() -> None:
    assert ArtifactCatalog(Namespace("ex-on")).namespace == Namespace("ex-on")


def test_a_new_catalog_has_no_kinds(fresh: ArtifactRegistry) -> None:
    assert ArtifactCatalog(Namespace("ex")).kinds == ()


def test_catalog_rejects_a_duplicate_local_id_at_declare(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    first = catalog.declare("taxable_base", Decimal)

    with pytest.raises(DuplicateRegistrationError, match="'ex/taxable_base'"):
        catalog.declare("taxable_base", int)

    assert catalog.kinds == (first,)
    assert fresh.identifiers() == frozenset()


def test_separate_catalogs_may_declare_the_same_identifier_until_registered(
    fresh: ArtifactRegistry,
) -> None:
    first = ArtifactCatalog(Namespace("ex")).declare("taxable_base", Decimal)
    second = ArtifactCatalog(Namespace("ex")).declare("taxable_base", int)

    assert first.identifier == second.identifier == "ex/taxable_base"


@pytest.mark.parametrize("local_id", ["", "TaxableBase", "taxable-base", "ex/taxable_base"])
def test_catalog_rejects_a_local_id_that_is_not_snake_case(
    fresh: ArtifactRegistry, local_id: str
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match="invalid local id"):
        catalog.declare(local_id, Decimal)

    assert catalog.kinds == ()
    assert fresh.identifiers() == frozenset()


# --- ArtifactRegistry.register_kind ---------------------------------------------------------


def test_register_kind_registers_a_new_kind_under_its_own_identifier() -> None:
    registry = ArtifactRegistry()
    kind = ArtifactKind("ex/rental.net_income", Decimal)

    registry.register_kind(kind)

    assert registry.get("ex/rental.net_income") is kind


def test_register_kind_skips_an_equal_kind_registered_already_and_keeps_the_first() -> None:
    registry = ArtifactRegistry()
    first = ArtifactKind("ex/rental.net_income", Decimal)
    registry.register_kind(first)

    registry.register_kind(ArtifactKind("ex/rental.net_income", Decimal))

    assert registry.get("ex/rental.net_income") is first
    assert registry.identifiers() == {"ex/rental.net_income"}


def test_register_kind_refuses_another_kind_under_that_identifier() -> None:
    registry = ArtifactRegistry()
    first = ArtifactKind("ex/rental.net_income", Decimal)
    registry.register_kind(first)

    with pytest.raises(DuplicateRegistrationError, match=r"'ex/rental\.net_income'"):
        registry.register_kind(ArtifactKind("ex/rental.net_income", int))

    assert registry.get("ex/rental.net_income") is first


# --- ArtifactRegistry.register_catalog ------------------------------------------------------


def test_register_catalog_registers_every_declared_kind_under_its_identifier(
    fresh: ArtifactRegistry,
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    base = catalog.declare("taxable_base", Decimal)
    count = catalog.declare("person_count", int)
    registry = ArtifactRegistry()

    registry.register_catalog(catalog)

    assert registry.get("ex/taxable_base") is base
    assert registry.get("ex/person_count") is count


def test_identifiers_lists_every_registered_identifier(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    catalog.declare("taxable_base", Decimal)
    catalog.declare("person_count", int)
    registry = ArtifactRegistry()
    registry.register_catalog(catalog)

    identifiers = registry.identifiers()

    assert_type(identifiers, frozenset[str])
    assert identifiers == frozenset({"ex/taxable_base", "ex/person_count"})


def test_register_catalog_registers_into_that_registry_only(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    catalog.declare("taxable_base", Decimal)

    ArtifactRegistry().register_catalog(catalog)

    assert fresh.identifiers() == frozenset()


def test_registering_an_empty_catalog_registers_nothing(fresh: ArtifactRegistry) -> None:
    registry = ArtifactRegistry()

    registry.register_catalog(ArtifactCatalog(Namespace("ex")))

    assert registry.identifiers() == frozenset()


def test_registering_the_same_catalog_twice_is_idempotent(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    base = catalog.declare("taxable_base", Decimal)
    registry = ArtifactRegistry()
    registry.register_catalog(catalog)

    registry.register_catalog(catalog)

    assert registry.identifiers() == {"ex/taxable_base"}
    assert registry.get("ex/taxable_base") is base


def test_a_different_catalog_with_a_clashing_identifier_is_rejected(
    fresh: ArtifactRegistry,
) -> None:
    first = ArtifactCatalog(Namespace("ex"))
    base = first.declare("taxable_base", Decimal)
    second = ArtifactCatalog(Namespace("ex"))
    second.declare("taxable_base", Decimal)
    registry = ArtifactRegistry()
    registry.register_catalog(first)

    with pytest.raises(DuplicateRegistrationError, match="'ex/taxable_base'"):
        registry.register_catalog(second)

    assert registry.get("ex/taxable_base") is base


def test_a_catalog_clashing_with_a_directly_registered_kind_is_rejected(
    fresh: ArtifactRegistry,
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    catalog.declare("taxable_base", Decimal)
    registry = ArtifactRegistry()
    registry.register("ex/taxable_base", ArtifactKind("ex/taxable_base", Decimal))

    with pytest.raises(DuplicateRegistrationError, match="'ex/taxable_base'"):
        registry.register_catalog(catalog)


def test_the_same_local_id_may_appear_in_different_namespaces(fresh: ArtifactRegistry) -> None:
    first = ArtifactCatalog(Namespace("ex"))
    first.declare("basic_tax", Decimal)
    second = ArtifactCatalog(Namespace("ex-sub"))
    second.declare("basic_tax", Decimal)
    registry = ArtifactRegistry()

    registry.register_catalog(first)
    registry.register_catalog(second)

    assert registry.identifiers() == {"ex/basic_tax", "ex-sub/basic_tax"}


def test_a_directly_built_artifact_kind_is_not_registered(fresh: ArtifactRegistry) -> None:
    ArtifactKind("ex/taxable_base", Decimal)

    with pytest.raises(UnknownRegistrationError):
        fresh.get("ex/taxable_base")
    assert fresh.identifiers() == frozenset()


# --- the dotted identifier of a form export ------------------------------------------------------
#
# An export `X` of a form `B` is an artifact `B.X`, named `<namespace>/<form local id>.<export
# local id>`. The grammar allows ONE dot in the local part, each side snake_case. Only the engine
# builds such an identifier: a catalog's `declare` and `Namespace.identifier` still refuse a dot.


@pytest.mark.parametrize(
    "identifier",
    ["ex/rental.net_income", "ca-on/t2125.business_income", "x1/a1.b2", "ex/a.b", "ex/a_b.c_d"],
)
def test_accepts_one_dot_between_two_snake_case_ids(identifier: str) -> None:
    kind = ArtifactKind(identifier, Decimal)

    assert kind.identifier == identifier


@pytest.mark.parametrize(
    "identifier",
    [
        "ex/rental.",
        "ex/.net_income",
        "ex/.",
        "ex/a.b.c",
        "ex/a..b",
        "ex/Rental.net_income",
        "ex/rental.Net_income",
        "ex/rental.net-income",
        "ex/rental._net",
        "ex/rental.2net",
        "ex/1rental.net",
        "ex/rental.net_",
        "ex/rental .net",
        "ex.rental/net_income",
        "ex/a/b.c",
        "ex/a.b/c",
    ],
)
def test_rejects_a_dot_that_is_not_between_two_snake_case_ids(identifier: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="invalid artifact kind identifier"):
        ArtifactKind(identifier, Decimal)


def test_labels_are_distinct_sorted_quoted_and_comma_separated() -> None:
    other = ArtifactKind("ex/another", Decimal)

    assert ArtifactKind.labels([BASE, other]) == "'another', 'taxable_base'"
    assert ArtifactKind.labels([]) == ""
    assert ArtifactKind.labels([BASE]) == "'taxable_base'"


def test_labels_collapse_kinds_sharing_a_label() -> None:
    same_label_as_int = ArtifactKind("ex/taxable_base", int)
    other_namespace = ArtifactKind("ex2/taxable_base", Decimal)

    assert ArtifactKind.labels([BASE, same_label_as_int, other_namespace]) == "'taxable_base'"


def test_labels_accept_any_iterable() -> None:
    assert ArtifactKind.labels(iter([BASE, BASE])) == "'taxable_base'"
    assert ArtifactKind.labels(frozenset({BASE})) == "'taxable_base'"


def test_the_label_of_a_dotted_identifier_is_its_whole_local_part() -> None:
    assert ArtifactKind("ex/rental.net_income", Decimal).label == "rental.net_income"


def test_a_dotted_kind_is_registered_and_found_by_its_identifier(fresh: ArtifactRegistry) -> None:
    kind = ArtifactKind("ex/rental.net_income", Decimal)

    fresh.register(kind.identifier, kind)

    assert fresh.kind("ex/rental.net_income") is kind


@pytest.mark.parametrize("local_id", ["rental.net_income", "a.b", "rental."])
def test_a_catalog_still_refuses_a_dot_in_a_local_id(local_id: str) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match="invalid local id"):
        catalog.declare(local_id, Decimal)

    assert catalog.kinds == ()


def test_a_namespace_still_refuses_a_dot_in_a_local_id() -> None:
    with pytest.raises(InvalidRegistrationError, match="invalid local id"):
        Namespace("ex").identifier("rental.net_income")


def test_only_a_dotted_kind_is_a_form_export() -> None:
    assert ArtifactKind("ex/rental.net_income", Decimal).is_form_export
    assert not ArtifactKind("ex/net_income", Decimal).is_form_export
