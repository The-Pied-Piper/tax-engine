"""Unit tests for record lists: a variable number of same-shaped records as one artifact.

A `RecordList` holds its `fields`, the artifact kinds every record has, and its `records` in the
caller's order. A record is a frozen mapping keyed by field kind, read by kind and never by
position. Each record is checked when the list is built: every field present, no other key, each
value an instance of its field kind's value type and, for a kind declared non-negative, not below
zero; an error names the record by its position from 1 ("item 2") and the field by its identifier.
A list may be empty. `RecordListKind.declare` declares a record-list kind on a catalog, a
`RecordListKind` whose value type is `RecordList` and which carries its fields; it refuses a
repeated field and a field kind that is not `Decimal` or `int`. A list without fields holds empty
records and only counts them. Names are made up; like the artifact tests, the catalog tests point
`ArtifactRegistry.shared` at a fresh registry.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactCatalog, ArtifactKind, ArtifactRegistry
from tax_engine.domain.errors import (
    DomainError,
    DuplicateRegistrationError,
    InvalidRecordError,
    InvalidRegistrationError,
    NegativeArtifactError,
)
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.registry import Namespace

D = Decimal
NET_INCOME = ArtifactKind("ex/dependant_net_income", Decimal, non_negative=True)
MONTHS = ArtifactKind("ex/months_resident", int, non_negative=True)
ADJUSTMENT = ArtifactKind("ex/adjustment", Decimal)
FIELDS = (NET_INCOME, MONTHS)


@pytest.fixture
def fresh(monkeypatch: pytest.MonkeyPatch) -> ArtifactRegistry:
    """A fresh registry that catalogs register into for the duration of one test."""
    registry = ArtifactRegistry()
    monkeypatch.setattr(ArtifactRegistry, "shared", classmethod(lambda cls: registry))
    return registry


def record(net_income: str, months: int) -> dict[ArtifactKind[Any], object]:
    return {NET_INCOME: D(net_income), MONTHS: months}


# --- RecordList -----------------------------------------------------------------------------


def test_a_record_list_has_its_fields_and_records_in_the_callers_order() -> None:
    records = RecordList(
        fields=FIELDS, records=[record("25000", 12), record("5000", 6), record("30000", 12)]
    )

    assert records.fields == (NET_INCOME, MONTHS)
    assert isinstance(records.records, tuple)
    assert [item[NET_INCOME] for item in records.records] == [D("25000"), D("5000"), D("30000")]
    assert [item[MONTHS] for item in records.records] == [12, 6, 12]


def test_a_record_is_a_mapping_read_by_field_kind() -> None:
    (only,) = RecordList(FIELDS, [record("5000", 6)]).records

    assert isinstance(only, Mapping)
    assert only[NET_INCOME] == D("5000")
    assert only[MONTHS] == 6
    assert type(only[MONTHS]) is int
    assert set(only) == {NET_INCOME, MONTHS}
    assert only == {NET_INCOME: D("5000"), MONTHS: 6}


def test_a_record_list_may_be_empty() -> None:
    records = RecordList(FIELDS, [])

    assert records.records == ()
    assert records.fields == FIELDS


def test_a_record_list_without_fields_holds_empty_records_and_counts_them() -> None:
    records = RecordList((), [{}, {}])

    assert records.fields == ()
    assert len(records.records) == 2
    assert all(len(each) == 0 for each in records.records)


def test_an_empty_record_of_a_list_without_fields_is_not_given_a_key() -> None:
    with pytest.raises(InvalidRecordError, match="item 1"):
        RecordList((), [{NET_INCOME: D(1)}])


def test_a_record_list_takes_any_iterable_of_records() -> None:
    from_tuple = RecordList(FIELDS, (record("1", 1), record("2", 2)))
    from_generator = RecordList(FIELDS, (record(str(n), n) for n in (1, 2)))

    assert from_tuple == from_generator


def test_a_record_is_frozen() -> None:
    (only,) = RecordList(FIELDS, [record("5000", 6)]).records

    with pytest.raises(TypeError):
        only[NET_INCOME] = D("1")  # type: ignore[index]


def test_a_record_list_is_frozen() -> None:
    records = RecordList(FIELDS, [record("5000", 6)])

    with pytest.raises(AttributeError):
        records.records = ()  # type: ignore[misc]
    with pytest.raises(AttributeError):
        records.fields = ()  # type: ignore[misc]


def test_changing_the_given_mapping_later_does_not_change_the_record() -> None:
    given = record("5000", 6)
    records = RecordList(FIELDS, [given])

    given[NET_INCOME] = D("99")

    assert records.records[0][NET_INCOME] == D("5000")


def test_record_lists_are_equal_by_fields_and_records_in_order() -> None:
    first, second = record("5000", 6), record("25000", 12)

    assert RecordList(FIELDS, [first, second]) == RecordList(FIELDS, [first, second])
    assert RecordList(FIELDS, [first, second]) != RecordList(FIELDS, [second, first])
    assert RecordList(FIELDS, []) != RecordList((NET_INCOME,), [])
    assert len({RecordList(FIELDS, [first]), RecordList(FIELDS, [first])}) == 1


def test_a_record_list_is_a_value_an_artifact_can_hold(fresh: ArtifactRegistry) -> None:
    kind = RecordListKind.declare(ArtifactCatalog(Namespace("ex")), "dependants", fields=FIELDS)
    records = RecordList(kind.fields, [record("5000", 6)])

    artifact = Artifact(kind, records)

    assert artifact.value is records
    assert Artifact(kind, records) == Artifact(kind, RecordList(FIELDS, [record("5000", 6)]))


def test_an_artifact_accepts_a_record_list_built_with_its_kinds_fields(
    fresh: ArtifactRegistry,
) -> None:
    kind = RecordListKind.declare(ArtifactCatalog(Namespace("ex")), "dependants", fields=FIELDS)
    records = RecordList((NET_INCOME, MONTHS), [record("5000", 6)])

    assert Artifact(kind, records).value is records
    assert Artifact(kind, RecordList(FIELDS, [])).value == RecordList(FIELDS, [])


@pytest.mark.parametrize(
    "fields",
    [
        (NET_INCOME,),  # fewer fields
        (NET_INCOME, MONTHS, ADJUSTMENT),  # more fields
        (NET_INCOME, ADJUSTMENT),  # other fields, same number
        (MONTHS, NET_INCOME),  # the same fields in another order
    ],
    ids=["fewer", "more", "other", "reordered"],
)
def test_an_artifact_refuses_a_record_list_with_other_fields_than_its_kind(
    fresh: ArtifactRegistry, fields: tuple[ArtifactKind[Any], ...]
) -> None:
    # The field list is structure: a record list built for other fields is not a value of the kind.
    kind = RecordListKind.declare(ArtifactCatalog(Namespace("ex")), "dependants", fields=FIELDS)

    with pytest.raises(TypeError, match=r"ex/dependants.*fields"):
        Artifact(kind, RecordList(fields, []))


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (5000, "item 2: ex/dependant_net_income must be a Decimal, got int"),
        (5000.0, "item 2: ex/dependant_net_income must be a Decimal, got float"),
        ("5000", "item 2: ex/dependant_net_income must be a Decimal, got str"),
    ],
)
def test_a_wrongly_typed_amount_is_refused_naming_the_item_and_field(
    value: object, message: str
) -> None:
    bad: dict[ArtifactKind[Any], object] = {NET_INCOME: value, MONTHS: 6}

    with pytest.raises(TypeError, match=message):
        RecordList(FIELDS, [record("1", 1), bad])


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (D("6"), "item 1: ex/months_resident must be a int, got Decimal"),
        (6.0, "item 1: ex/months_resident must be a int, got float"),
    ],
)
def test_a_wrongly_typed_count_is_refused_naming_the_item_and_field(
    value: object, message: str
) -> None:
    with pytest.raises(TypeError, match=message):
        RecordList(FIELDS, [{NET_INCOME: D("1"), MONTHS: value}])


def test_a_negative_amount_is_refused_naming_the_item_field_and_value() -> None:
    with pytest.raises(
        NegativeArtifactError, match=r"item 3: ex/dependant_net_income cannot be negative, got -1"
    ) as raised:
        RecordList(FIELDS, [record("1", 1), record("2", 2), record("-1", 3)])

    assert raised.value.identifier == "ex/dependant_net_income"
    assert raised.value.value == D("-1")


def test_a_negative_count_is_refused_naming_the_item_field_and_value() -> None:
    with pytest.raises(
        NegativeArtifactError, match=r"item 1: ex/months_resident cannot be negative, got -2"
    ) as raised:
        RecordList(FIELDS, [record("1", -2)])

    assert raised.value.identifier == "ex/months_resident"
    assert raised.value.value == -2


@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity"])
def test_a_non_finite_amount_is_refused_naming_the_item_and_field(value: str) -> None:
    with pytest.raises(
        InvalidRecordError, match=rf"item 2: ex/dependant_net_income must be finite, got {value}"
    ):
        RecordList(FIELDS, [record("1", 1), record(value, 2)])


@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity"])
def test_a_non_finite_amount_is_refused_in_a_field_not_declared_non_negative(value: str) -> None:
    with pytest.raises(InvalidRecordError, match=r"item 1: ex/adjustment must be finite"):
        RecordList((ADJUSTMENT,), [{ADJUSTMENT: D(value)}])


def test_a_non_finite_amount_in_a_nested_record_list_is_refused() -> None:
    inner = RecordListKind("ex/inner", fields=(ADJUSTMENT,))
    with pytest.raises(InvalidRecordError, match=r"item 1: ex/adjustment must be finite"):
        RecordList((inner,), [{inner: RecordList((ADJUSTMENT,), [{ADJUSTMENT: D("NaN")}])}])


@pytest.mark.parametrize("value", ["0", "-0", "0.00"])
def test_a_non_negative_field_accepts_zero_and_signed_zero(value: str) -> None:
    (only,) = RecordList(FIELDS, [record(value, 0)]).records

    assert only[NET_INCOME] == D(value)
    assert only[MONTHS] == 0


def test_a_field_not_declared_non_negative_accepts_a_negative_value() -> None:
    (only,) = RecordList((ADJUSTMENT,), [{ADJUSTMENT: D("-40")}]).records

    assert only[ADJUSTMENT] == D("-40")


def test_a_missing_field_is_refused_naming_the_item_and_field() -> None:
    with pytest.raises(InvalidRecordError, match=r"item 2: missing field ex/months_resident"):
        RecordList(FIELDS, [record("1", 1), {NET_INCOME: D("2")}])


def test_an_unknown_field_is_refused_naming_the_item_and_field() -> None:
    bad = {**record("2", 2), ADJUSTMENT: D("5")}

    with pytest.raises(InvalidRecordError, match=r"item 2: unknown field ex/adjustment"):
        RecordList(FIELDS, [record("1", 1), bad])


def test_a_field_of_the_same_identifier_but_another_value_type_is_unknown() -> None:
    # Fields are kinds: `ex/months_resident` as a Decimal is not the `int` field of that name.
    impostor = ArtifactKind("ex/months_resident", Decimal)
    bad = {NET_INCOME: D("1"), impostor: D("6")}

    with pytest.raises(InvalidRecordError, match=r"item 1: "):
        RecordList(FIELDS, [bad])


def test_a_record_that_is_not_a_mapping_is_refused_naming_the_item() -> None:
    with pytest.raises(InvalidRecordError, match=r"item 2: "):
        RecordList(FIELDS, [record("1", 1), cast(Any, [D("2"), 2])])


def test_an_invalid_record_is_a_domain_error() -> None:
    assert issubclass(InvalidRecordError, DomainError)


# --- RecordListKind.declare -------------------------------------------------------------------


def test_a_catalog_declares_a_record_list_kind_in_its_namespace(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = RecordListKind.declare(catalog, "dependants", fields=FIELDS)

    assert_type(kind, RecordListKind)
    assert isinstance(kind, ArtifactKind)
    assert kind.identifier == "ex/dependants"
    assert kind.label == "dependants"
    assert kind.value_type is RecordList
    assert kind.non_negative is False
    assert kind.fields == (NET_INCOME, MONTHS)
    assert catalog.kinds == (kind,)


def test_the_fields_may_be_given_by_position(fresh: ArtifactRegistry) -> None:
    kind = RecordListKind.declare(ArtifactCatalog(Namespace("ex")), "dependants", (NET_INCOME,))

    assert kind.fields == (NET_INCOME,)


def test_the_fields_keep_their_declared_order(fresh: ArtifactRegistry) -> None:
    kind = RecordListKind.declare(
        ArtifactCatalog(Namespace("ex")), "dependants", fields=(MONTHS, NET_INCOME)
    )

    assert kind.fields == (MONTHS, NET_INCOME)


def test_a_field_may_come_from_another_packages_catalog(fresh: ArtifactRegistry) -> None:
    parent = ArtifactCatalog(Namespace("ex"))
    net_income = parent.declare("dependant_net_income", Decimal, non_negative=True)
    child = ArtifactCatalog(Namespace("ex-on"))

    kind = RecordListKind.declare(child, "dependants", fields=(net_income,))

    assert kind.identifier == "ex-on/dependants"
    assert kind.fields == (net_income,)
    assert child.kinds == (kind,)
    assert parent.kinds == (net_income,)


def test_record_list_kinds_are_told_apart_by_their_fields(fresh: ArtifactRegistry) -> None:
    # The field list is structure: the same identifier with other fields is another kind.
    one = RecordListKind.declare(
        ArtifactCatalog(Namespace("ex")), "dependants", fields=(NET_INCOME,)
    )
    two = RecordListKind.declare(ArtifactCatalog(Namespace("ex")), "dependants", fields=FIELDS)
    again = RecordListKind.declare(ArtifactCatalog(Namespace("ex")), "dependants", fields=FIELDS)

    assert one != two
    assert two == again
    assert len({two, again}) == 1


def test_declaring_a_record_list_registers_nothing(fresh: ArtifactRegistry) -> None:
    RecordListKind.declare(ArtifactCatalog(Namespace("ex")), "dependants", fields=FIELDS)

    assert fresh.identifiers() == frozenset()


def test_a_declared_record_list_kind_registers_with_its_catalog(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    count = catalog.declare("person_count", int)
    kind = RecordListKind.declare(catalog, "dependants", fields=FIELDS)
    registry = ArtifactRegistry()

    registry.register_catalog(catalog)

    assert registry.kind("ex/dependants") is kind
    assert registry.kind("ex/person_count") is count


def test_declare_accepts_an_empty_field_list(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = RecordListKind.declare(catalog, "copies", fields=())

    assert kind.fields == ()
    assert catalog.kinds == (kind,)


def test_declare_refuses_a_repeated_field(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(
        InvalidRegistrationError, match=r"ex/dependants.*ex/dependant_net_income.*more than once"
    ):
        RecordListKind.declare(catalog, "dependants", fields=(NET_INCOME, MONTHS, NET_INCOME))

    assert catalog.kinds == ()


@pytest.mark.parametrize(
    ("value_type", "name"),
    [(float, "float"), (str, "str"), (bool, "bool"), (RecordList, "RecordList")],
)
def test_declare_refuses_a_field_that_is_not_decimal_or_int(
    fresh: ArtifactRegistry, value_type: type[Any], name: str
) -> None:
    # `bool` is a subclass of `int` but not a count, as for a non-negative kind.
    catalog = ArtifactCatalog(Namespace("ex"))
    field = ArtifactKind("ex/odd_field", value_type)

    with pytest.raises(InvalidRegistrationError, match=rf"ex/dependants.*ex/odd_field.*{name}"):
        RecordListKind.declare(catalog, "dependants", fields=(NET_INCOME, field))

    assert catalog.kinds == ()


def test_declare_refuses_a_local_id_already_declared(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    first = catalog.declare("dependants", int)

    with pytest.raises(DuplicateRegistrationError, match="'ex/dependants'"):
        RecordListKind.declare(catalog, "dependants", fields=FIELDS)

    assert catalog.kinds == (first,)


def test_declare_refuses_a_local_id_already_declared_as_a_record_list(
    fresh: ArtifactRegistry,
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    first = RecordListKind.declare(catalog, "dependants", fields=FIELDS)

    with pytest.raises(DuplicateRegistrationError, match="'ex/dependants'"):
        catalog.declare("dependants", int)

    assert catalog.kinds == (first,)


@pytest.mark.parametrize("local_id", ["", "Dependants", "dependant-list", "ex/dependants"])
def test_declare_refuses_a_local_id_that_is_not_snake_case(
    fresh: ArtifactRegistry, local_id: str
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match="invalid local id"):
        RecordListKind.declare(catalog, local_id, fields=FIELDS)

    assert catalog.kinds == ()


def test_a_catalog_adds_a_kind_built_elsewhere_in_its_namespace(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    kind = RecordListKind("ex/dependants", fields=FIELDS)

    catalog.add(kind)

    assert catalog.kinds == (kind,)
    assert fresh.identifiers() == frozenset()


def test_a_catalog_refuses_to_add_a_kind_of_another_namespace(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match=r"ex-on/dependants.*'ex'"):
        catalog.add(RecordListKind("ex-on/dependants", fields=FIELDS))

    assert catalog.kinds == ()


def test_a_record_list_kind_given_a_list_of_fields_holds_them_as_a_tuple() -> None:
    kind = RecordListKind("ex/dependants", fields=[NET_INCOME, MONTHS])

    assert kind.fields == (NET_INCOME, MONTHS)
    assert isinstance(kind.fields, tuple)
    assert kind == RecordListKind("ex/dependants", fields=FIELDS)
    assert len({kind, RecordListKind("ex/dependants", fields=FIELDS)}) == 1


def test_declare_given_a_list_of_fields_holds_them_as_a_tuple(
    fresh: ArtifactRegistry,
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = RecordListKind.declare(catalog, "dependants", fields=[NET_INCOME, MONTHS])

    assert kind.fields == (NET_INCOME, MONTHS)
    assert isinstance(kind.fields, tuple)
    assert catalog.kinds == (kind,)


@pytest.mark.parametrize(
    "field", ["ex/months_resident", None, Decimal, 3], ids=["identifier", "none", "type", "int"]
)
def test_a_record_list_kind_refuses_a_field_that_is_not_an_artifact_kind(field: object) -> None:
    with pytest.raises(InvalidRegistrationError, match=r"ex/dependants"):
        RecordListKind("ex/dependants", fields=cast(Any, (NET_INCOME, field)))


def test_declare_refuses_a_field_that_is_not_an_artifact_kind(
    fresh: ArtifactRegistry,
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match=r"ex/dependants"):
        RecordListKind.declare(
            catalog, "dependants", fields=cast(Any, (NET_INCOME, "ex/months_resident"))
        )

    assert catalog.kinds == ()


# --- a field that is itself a record list ---------------------------------------------------

RENT = ArtifactKind("ex/unit_rent", Decimal, non_negative=True)
UNIT_FIELDS = (RENT,)
UNITS = RecordListKind("ex/units", fields=UNIT_FIELDS)
FLOOR = ArtifactKind("ex/floor", int)
PROPERTY_FIELDS = (FLOOR, UNITS)


def units(*rents: str) -> RecordList:
    return RecordList(UNIT_FIELDS, [{RENT: D(rent)} for rent in rents])


def test_a_field_may_be_a_record_list_kind() -> None:
    properties = RecordList(
        PROPERTY_FIELDS,
        [{FLOOR: 1, UNITS: units("100", "250.50")}, {FLOOR: 2, UNITS: units()}],
    )

    assert properties.fields == PROPERTY_FIELDS
    assert properties.records[0][UNITS] == units("100", "250.50")
    assert properties.records[0][UNITS].records[1][RENT] == D("250.50")
    assert properties.records[1][UNITS].records == ()


def test_a_nested_list_may_be_empty() -> None:
    properties = RecordList(PROPERTY_FIELDS, [{FLOOR: 1, UNITS: RecordList(UNIT_FIELDS, [])}])

    assert properties.records[0][UNITS].records == ()


def test_a_record_holding_a_nested_list_is_hashable_and_equal_by_value() -> None:
    first = RecordList(PROPERTY_FIELDS, [{FLOOR: 1, UNITS: units("100")}])
    second = RecordList(PROPERTY_FIELDS, [{FLOOR: 1, UNITS: units("100")}])
    other = RecordList(PROPERTY_FIELDS, [{FLOOR: 1, UNITS: units("101")}])

    assert first == second
    assert first != other
    assert hash(first.records[0]) == hash(second.records[0])


def test_a_record_list_kind_accepts_a_record_list_field() -> None:
    kind = RecordListKind("ex/properties", fields=PROPERTY_FIELDS)

    assert kind.fields == PROPERTY_FIELDS


def test_declare_accepts_a_record_list_field(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = RecordListKind.declare(catalog, "properties", fields=PROPERTY_FIELDS)

    assert kind.fields == PROPERTY_FIELDS


def test_a_nested_list_of_other_fields_is_refused_naming_the_item_and_field() -> None:
    other = RecordList((NET_INCOME,), [{NET_INCOME: D("1")}])

    with pytest.raises(TypeError, match=r"item 2: ex/units"):
        RecordList(PROPERTY_FIELDS, [{FLOOR: 1, UNITS: units("1")}, {FLOOR: 2, UNITS: other}])


@pytest.mark.parametrize(
    ("value", "got"), [(D("5"), "Decimal"), ([], "list"), (None, "NoneType"), ("x", "str")]
)
def test_a_nested_field_that_is_not_a_record_list_is_refused_naming_the_item_and_field(
    value: object, got: str
) -> None:
    bad: dict[ArtifactKind[Any], object] = {FLOOR: 1, UNITS: value}

    with pytest.raises(TypeError, match=rf"item 2: ex/units must be a RecordList, got {got}"):
        RecordList(PROPERTY_FIELDS, [{FLOOR: 1, UNITS: units()}, bad])


def test_a_missing_nested_field_is_refused_naming_the_item_and_field() -> None:
    with pytest.raises(InvalidRecordError, match=r"item 1: missing field ex/units"):
        RecordList(PROPERTY_FIELDS, [{FLOOR: 1}])


def test_an_artifact_holds_a_record_list_with_a_nested_list(fresh: ArtifactRegistry) -> None:
    kind = RecordListKind("ex/properties", fields=PROPERTY_FIELDS)
    value = RecordList(PROPERTY_FIELDS, [{FLOOR: 1, UNITS: units("100")}])

    assert Artifact(kind, value).value == value


def test_a_record_list_kind_may_carry_the_dotted_identifier_of_a_form_export() -> None:
    # The engine derives `<form>.<export>` kinds as record-list kinds of the export's one field.
    amount = ArtifactKind("ex/net_income", Decimal)

    kind = RecordListKind("ex/rental.net_income", fields=(amount,))
    value = RecordList(kind.fields, [{amount: Decimal("10000")}, {amount: Decimal("4000")}])

    assert kind.identifier == "ex/rental.net_income"
    assert Artifact(kind, value).value.records[1][amount] == Decimal("4000")
    assert kind == RecordListKind("ex/rental.net_income", fields=(amount,))


def test_a_catalog_cannot_declare_a_dotted_record_list_kind() -> None:
    amount = ArtifactKind("ex/net_income", Decimal)

    with pytest.raises(InvalidRegistrationError, match="invalid local id"):
        RecordListKind.declare(ArtifactCatalog(Namespace("ex")), "rental.net_income", (amount,))
