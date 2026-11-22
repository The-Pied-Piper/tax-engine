"""Unit tests for artifact kinds and artifacts (design.md §2).

An `ArtifactKind[V]` names a kind of artifact by a namespaced identifier and states the type of
its values; an `Artifact[V]` is one value of a kind in one computation. `ArtifactCatalog` only
records the kinds a package declares; `ArtifactRegistry.register_catalog` registers them. Names are
made up; the catalog tests use a fresh registry, so declaring can be seen to register nothing.
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
    HasFloor,
    Money,
    RecordField,
    YesNo,
)
from tax_engine.domain.errors import (
    DomainError,
    DuplicateRegistrationError,
    InvalidAmountError,
    InvalidRegistrationError,
    NegativeArtifactError,
    UnknownRegistrationError,
)
from tax_engine.domain.kinds import (
    AmountKind,
    CountKind,
    DigitsKind,
    RateKind,
    RecordListKind,
    TextKind,
)
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.registry import Namespace, Registry
from tests.kinds import OddKind, ca_on_kinds, non_negative

D = Decimal
BASE = AmountKind("ex/taxable_base")
TAX = AmountKind("ex/basic_tax")
NON_NEGATIVE = AmountKind("ex/credit_amount", non_negative=True)


@pytest.fixture
def fresh() -> ArtifactRegistry:
    """An empty registry, to see that declaring in a catalog registers nothing in it."""
    return ArtifactRegistry()


# --- ArtifactKind ---------------------------------------------------------------------------


def test_an_artifact_kind_has_an_identifier_and_a_value_type() -> None:
    assert BASE.identifier == "ex/taxable_base"
    assert BASE.value_type is Decimal


def test_the_value_type_is_known_statically() -> None:
    assert_type(BASE, AmountKind)
    assert_type(CountKind("ex/count"), CountKind)


def test_money_is_an_alias_for_decimal_artifact_kinds() -> None:
    money: Money = BASE

    assert_type(money, ArtifactKind[Decimal])


def test_artifact_kinds_are_equal_by_identifier_and_value_type() -> None:
    assert AmountKind("ex/taxable_base") == BASE
    assert BASE != TAX
    other_type: ArtifactKind[Any] = CountKind("ex/taxable_base")
    assert other_type != BASE
    assert len({BASE, AmountKind("ex/taxable_base")}) == 1


def test_artifact_kinds_are_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        BASE.identifier = "ex/other"  # type: ignore[misc]


def test_label_is_the_local_part_of_the_identifier() -> None:
    assert BASE.label == "taxable_base"
    assert AmountKind("ca-on/basic_tax").label == "basic_tax"
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
        AmountKind(identifier)


@pytest.mark.parametrize("identifier", ["ex/a", "ca-on/basic_tax", "x1/line_26000", "a-b-c/x2"])
def test_accepts_namespaced_snake_case_identifiers(identifier: str) -> None:
    assert AmountKind(identifier).identifier == identifier


def test_an_invalid_identifier_fails_like_an_invalid_catalog_declaration(
    fresh: ArtifactRegistry,
) -> None:
    with pytest.raises(InvalidRegistrationError) as direct:
        AmountKind("ex/Bad")
    with pytest.raises(InvalidRegistrationError) as declared:
        AmountKind.declare(ArtifactCatalog(Namespace("ex")), "Bad")

    assert type(direct.value) is type(declared.value)


def test_value_type_must_be_a_type() -> None:
    with pytest.raises(TypeError, match="value_type must be a type"):
        OddKind("ex/a", cast(Any, "Decimal"))


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
    assert non_negative(BASE) is False
    catalog = ArtifactCatalog(Namespace("ex"))
    assert non_negative(AmountKind.declare(catalog, "taxable_base")) is False
    assert non_negative(CountKind("ex/person_count")) is False
    assert non_negative(TextKind("ex/person_name")) is False
    assert non_negative(RateKind("ex/credit_rate")) is False
    assert non_negative(OddKind("ex/flag", bool)) is False


def test_a_kind_may_be_declared_non_negative() -> None:
    assert_type(non_negative(NON_NEGATIVE), bool)
    assert non_negative(NON_NEGATIVE) is True


def test_a_catalog_declares_a_non_negative_kind(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = AmountKind.declare(catalog, "credit_amount", non_negative=True)

    assert_type(kind, AmountKind)
    assert kind.identifier == "ex/credit_amount"
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
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
    kind = AmountKind.declare(ArtifactCatalog(Namespace("ex")), "credit_amount", non_negative=True)

    with pytest.raises(NegativeArtifactError, match="ex/credit_amount"):
        Artifact(kind, D("-1"))


@pytest.mark.parametrize("kind_class", [TextKind, RateKind])
def test_a_text_or_rate_kind_takes_no_non_negative_flag(kind_class: type[Any]) -> None:
    with pytest.raises(TypeError):
        kind_class("ex/person_name", non_negative=True)


def test_a_text_kind_declares_no_non_negative_flag(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(TypeError):
        TextKind.declare(catalog, "person_name", non_negative=True)  # type: ignore[call-arg]

    assert catalog.kinds == ()
    assert fresh.identifiers() == frozenset()


def test_a_count_kind_may_be_declared_unconstrained(fresh: ArtifactRegistry) -> None:
    kind = CountKind.declare(ArtifactCatalog(Namespace("ex")), "person_count", non_negative=False)

    assert non_negative(kind) is False
    assert Artifact(kind, -1).value == -1


# --- counts: non-negative int kinds -----------------------------------------------------------
#
# A count is an `int` artifact, the number of something a form asks for. The existing
# `non_negative` flag is allowed on an `int` kind as well as a `Decimal` one, and the same
# `Artifact` check refuses a flagged count below zero; an unflagged `int` kind accepts any value.


COUNT = CountKind("ex/person_count", non_negative=True)


def test_an_int_kind_may_be_declared_non_negative() -> None:
    count = COUNT

    assert_type(count, CountKind)
    assert count.value_type is int
    assert non_negative(count) is True


def test_a_catalog_declares_a_non_negative_int_kind(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = CountKind.declare(catalog, "person_count", non_negative=True)

    assert_type(kind, CountKind)
    assert kind.identifier == "ex/person_count"
    assert kind.value_type is int
    assert non_negative(kind) is True
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
    kind = CountKind.declare(ArtifactCatalog(Namespace("ex")), "person_count", non_negative=True)

    with pytest.raises(NegativeArtifactError, match="ex/person_count"):
        Artifact(kind, -1)


def test_an_unflagged_int_kind_accepts_a_negative_int() -> None:
    assert Artifact(CountKind("ex/person_count"), -3).value == -3


def test_a_count_still_rejects_a_value_of_another_type() -> None:
    with pytest.raises(TypeError, match="person_count must be a int, got Decimal"):
        Artifact(COUNT, cast(Any, D("1")))


# --- kinds the later sections use ----------------------------------------------------------

NUMBER = DigitsKind("ex/business_number", digits=9)
DEPENDANTS = RecordListKind("ex/dependants", fields=(BASE,))


# --- ArtifactRegistry and ArtifactCatalog ---------------------------------------------------


def test_artifact_registry_is_a_registry() -> None:
    assert issubclass(ArtifactRegistry, Registry)


def test_the_bundled_kinds_are_built_once_per_process() -> None:
    assert ca_on_kinds() is ca_on_kinds()
    assert isinstance(ca_on_kinds(), ArtifactRegistry)


def test_catalog_declares_the_namespaced_kind(fresh: ArtifactRegistry) -> None:
    kind = AmountKind.declare(ArtifactCatalog(Namespace("ex")), "taxable_base")

    assert_type(kind, AmountKind)
    assert kind == AmountKind("ex/taxable_base")


def test_declaring_registers_nothing(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    AmountKind.declare(catalog, "taxable_base")
    CountKind.declare(catalog, "person_count")

    assert fresh.identifiers() == frozenset()
    with pytest.raises(UnknownRegistrationError):
        fresh.get("ex/taxable_base")


def test_catalog_kinds_are_the_declared_kinds_in_declaration_order(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    base = AmountKind.declare(catalog, "taxable_base")
    count = CountKind.declare(catalog, "person_count")
    tax = AmountKind.declare(catalog, "basic_tax")

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
    first = AmountKind.declare(catalog, "taxable_base")

    with pytest.raises(DuplicateRegistrationError, match="'ex/taxable_base'"):
        CountKind.declare(catalog, "taxable_base")

    assert catalog.kinds == (first,)
    assert fresh.identifiers() == frozenset()


def test_separate_catalogs_may_declare_the_same_identifier_until_registered(
    fresh: ArtifactRegistry,
) -> None:
    first = AmountKind.declare(ArtifactCatalog(Namespace("ex")), "taxable_base")
    second = CountKind.declare(ArtifactCatalog(Namespace("ex")), "taxable_base")

    assert first.identifier == second.identifier == "ex/taxable_base"


@pytest.mark.parametrize("local_id", ["", "TaxableBase", "taxable-base", "ex/taxable_base"])
def test_catalog_rejects_a_local_id_that_is_not_snake_case(
    fresh: ArtifactRegistry, local_id: str
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match="invalid local id"):
        AmountKind.declare(catalog, local_id)

    assert catalog.kinds == ()
    assert fresh.identifiers() == frozenset()


# --- ArtifactRegistry.extended --------------------------------------------------------------


def test_extended_is_a_new_registry_of_the_kinds_and_the_added_ones() -> None:
    registry = ArtifactRegistry()
    registry.register(BASE.identifier, BASE)
    kind = AmountKind("ex/rental.net_income")

    extended = registry.extended([kind])

    assert extended is not registry
    assert extended.get("ex/rental.net_income") is kind
    assert extended.get("ex/taxable_base") is BASE
    assert registry.identifiers() == {"ex/taxable_base"}


def test_extended_skips_an_equal_kind_registered_already_and_keeps_the_first() -> None:
    registry = ArtifactRegistry()
    first = AmountKind("ex/rental.net_income")
    registry.register(first.identifier, first)

    extended = registry.extended([AmountKind("ex/rental.net_income")])

    assert extended.get("ex/rental.net_income") is first
    assert extended.identifiers() == {"ex/rental.net_income"}


def test_extended_refuses_another_kind_under_that_identifier() -> None:
    registry = ArtifactRegistry()
    first = AmountKind("ex/rental.net_income")
    registry.register(first.identifier, first)

    with pytest.raises(DuplicateRegistrationError, match=r"'ex/rental\.net_income'"):
        registry.extended([CountKind("ex/rental.net_income")])

    assert registry.get("ex/rental.net_income") is first


# --- ArtifactRegistry.register_catalog ------------------------------------------------------


def test_register_catalog_registers_every_declared_kind_under_its_identifier(
    fresh: ArtifactRegistry,
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    base = AmountKind.declare(catalog, "taxable_base")
    count = CountKind.declare(catalog, "person_count")
    registry = ArtifactRegistry()

    registry.register_catalog(catalog)

    assert registry.get("ex/taxable_base") is base
    assert registry.get("ex/person_count") is count


def test_identifiers_lists_every_registered_identifier(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    AmountKind.declare(catalog, "taxable_base")
    CountKind.declare(catalog, "person_count")
    registry = ArtifactRegistry()
    registry.register_catalog(catalog)

    identifiers = registry.identifiers()

    assert_type(identifiers, frozenset[str])
    assert identifiers == frozenset({"ex/taxable_base", "ex/person_count"})


def test_register_catalog_registers_into_that_registry_only(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    AmountKind.declare(catalog, "taxable_base")

    ArtifactRegistry().register_catalog(catalog)

    assert fresh.identifiers() == frozenset()


def test_registering_an_empty_catalog_registers_nothing(fresh: ArtifactRegistry) -> None:
    registry = ArtifactRegistry()

    registry.register_catalog(ArtifactCatalog(Namespace("ex")))

    assert registry.identifiers() == frozenset()


def test_registering_the_same_catalog_twice_is_idempotent(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    base = AmountKind.declare(catalog, "taxable_base")
    registry = ArtifactRegistry()
    registry.register_catalog(catalog)

    registry.register_catalog(catalog)

    assert registry.identifiers() == {"ex/taxable_base"}
    assert registry.get("ex/taxable_base") is base


def test_a_different_catalog_with_a_clashing_identifier_is_rejected(
    fresh: ArtifactRegistry,
) -> None:
    first = ArtifactCatalog(Namespace("ex"))
    base = AmountKind.declare(first, "taxable_base")
    second = ArtifactCatalog(Namespace("ex"))
    AmountKind.declare(second, "taxable_base")
    registry = ArtifactRegistry()
    registry.register_catalog(first)

    with pytest.raises(DuplicateRegistrationError, match="'ex/taxable_base'"):
        registry.register_catalog(second)

    assert registry.get("ex/taxable_base") is base


def test_a_catalog_clashing_with_a_directly_registered_kind_is_rejected(
    fresh: ArtifactRegistry,
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    AmountKind.declare(catalog, "taxable_base")
    registry = ArtifactRegistry()
    registry.register("ex/taxable_base", AmountKind("ex/taxable_base"))

    with pytest.raises(DuplicateRegistrationError, match="'ex/taxable_base'"):
        registry.register_catalog(catalog)


def test_the_same_local_id_may_appear_in_different_namespaces(fresh: ArtifactRegistry) -> None:
    first = ArtifactCatalog(Namespace("ex"))
    AmountKind.declare(first, "basic_tax")
    second = ArtifactCatalog(Namespace("ex-sub"))
    AmountKind.declare(second, "basic_tax")
    registry = ArtifactRegistry()

    registry.register_catalog(first)
    registry.register_catalog(second)

    assert registry.identifiers() == {"ex/basic_tax", "ex-sub/basic_tax"}


def test_a_directly_built_artifact_kind_is_not_registered(fresh: ArtifactRegistry) -> None:
    AmountKind("ex/taxable_base")

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
    kind = AmountKind(identifier)

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
        AmountKind(identifier)


def test_labels_are_distinct_sorted_quoted_and_comma_separated() -> None:
    other = AmountKind("ex/another")

    assert ArtifactKind.labels([BASE, other]) == "'another', 'taxable_base'"
    assert ArtifactKind.labels([]) == ""
    assert ArtifactKind.labels([BASE]) == "'taxable_base'"


def test_labels_collapse_kinds_sharing_a_label() -> None:
    same_label_as_int = CountKind("ex/taxable_base")
    other_namespace = AmountKind("ex2/taxable_base")

    assert ArtifactKind.labels([BASE, same_label_as_int, other_namespace]) == "'taxable_base'"


def test_labels_accept_any_iterable() -> None:
    assert ArtifactKind.labels(iter([BASE, BASE])) == "'taxable_base'"
    assert ArtifactKind.labels(frozenset({BASE})) == "'taxable_base'"


def test_the_label_of_a_dotted_identifier_is_its_whole_local_part() -> None:
    assert AmountKind("ex/rental.net_income").label == "rental.net_income"


def test_a_dotted_kind_is_registered_and_found_by_its_identifier(fresh: ArtifactRegistry) -> None:
    kind = AmountKind("ex/rental.net_income")

    fresh.register(kind.identifier, kind)

    assert fresh.kind("ex/rental.net_income") is kind


@pytest.mark.parametrize("local_id", ["rental.net_income", "a.b", "rental."])
def test_a_catalog_still_refuses_a_dot_in_a_local_id(local_id: str) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match="invalid local id"):
        AmountKind.declare(catalog, local_id)

    assert catalog.kinds == ()


def test_a_namespace_still_refuses_a_dot_in_a_local_id() -> None:
    with pytest.raises(InvalidRegistrationError, match="invalid local id"):
        Namespace("ex").identifier("rental.net_income")


def test_only_a_dotted_kind_is_a_form_export() -> None:
    assert AmountKind("ex/rental.net_income").is_form_export
    assert not AmountKind("ex/net_income").is_form_export


# --- the plain kinds ------------------------------------------------------------------------


def test_kinds_of_different_classes_are_never_equal() -> None:
    amount: ArtifactKind[Any] = AmountKind("ex/x")
    text: ArtifactKind[Any] = TextKind("ex/x")
    assert amount != CountKind("ex/x")
    assert text != OddKind("ex/x", str)


@pytest.mark.parametrize(
    ("kind_class", "value_type"),
    [(AmountKind, Decimal), (CountKind, int), (RateKind, Rate), (TextKind, str)],
)
def test_each_plain_kind_declares_itself_in_the_catalogs_namespace(
    kind_class: Any, value_type: type[Any]
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = kind_class.declare(catalog, "thing")

    assert type(kind) is kind_class
    assert kind.identifier == "ex/thing"
    assert kind.value_type is value_type
    assert catalog.kinds == (kind,)


def test_only_an_amount_a_count_or_a_record_list_is_a_record_field() -> None:
    assert isinstance(AmountKind("ex/a"), RecordField)
    assert isinstance(CountKind("ex/c"), RecordField)
    assert isinstance(DEPENDANTS, RecordField)
    assert not isinstance(TextKind("ex/t"), RecordField)
    assert not isinstance(NUMBER, RecordField)
    assert not isinstance(RateKind("ex/r"), RecordField)


def test_only_a_non_negative_count_is_yes_no() -> None:
    counts = CountKind("ex/c", non_negative=True)
    assert isinstance(counts, YesNo) and counts.is_yes_no
    unsigned = CountKind("ex/c")
    assert isinstance(unsigned, YesNo) and not unsigned.is_yes_no
    assert not isinstance(AmountKind("ex/a", non_negative=True), YesNo)
    assert not isinstance(TextKind("ex/t"), YesNo)


def test_is_below_floor_only_for_a_non_negative_kind_and_a_value_below_zero() -> None:
    assert NON_NEGATIVE.is_below_floor(D("-0.01"))
    assert not NON_NEGATIVE.is_below_floor(D(0))
    assert not BASE.is_below_floor(D(-1))
    assert COUNT.is_below_floor(-1)
    assert not COUNT.is_below_floor(0)
    assert not CountKind("ex/c").is_below_floor(-1)


@pytest.mark.parametrize(
    ("kind", "has_floor", "record_field", "yes_no"),
    [
        (AmountKind("ex/a"), True, True, False),
        (CountKind("ex/c"), True, True, True),
        (RateKind("ex/r"), False, False, False),
        (TextKind("ex/t"), False, False, False),
        (NUMBER, False, False, False),
        (DEPENDANTS, False, True, False),
        (OddKind("ex/flag", bool), False, False, False),
    ],
    ids=["amount", "count", "rate", "text", "digits", "record list", "odd"],
)
def test_each_kind_matches_only_the_protocols_it_has(
    kind: ArtifactKind[Any], has_floor: bool, record_field: bool, yes_no: bool
) -> None:
    assert isinstance(kind, HasFloor) is has_floor
    assert isinstance(kind, RecordField) is record_field
    assert isinstance(kind, YesNo) is yes_no


def test_a_kind_without_a_floor_holds_a_negative_value() -> None:
    assert Artifact(AmountKind("ex/a"), D(-1)).value == D(-1)
    assert Artifact(OddKind("ex/flag", int), -1).value == -1
