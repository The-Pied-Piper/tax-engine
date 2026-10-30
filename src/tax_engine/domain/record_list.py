"""Record lists: a variable number of same-shaped records held as one artifact value.

A `RecordList` is the value of a kind such as `ex/dependants`: its `fields`, the artifact kinds
every record has, and its `records` in the caller's order. A `Record` is a frozen mapping keyed by
field kind, read by kind and never by position. Every field is a `Decimal` or `int` kind or a
`RecordListKind`; a record holds each of them, an instance of its value type and, for a kind
declared non-negative, never below zero, and nothing else. A field of a record-list kind holds a
nested `RecordList` of exactly that kind's fields, which may be empty. A list may be empty.
Packages declare a record-list kind, a `RecordListKind`, on their own catalog with
`RecordListKind.declare`; an `Artifact` of one holds only a list built with that kind's fields.
A capability consuming one does the per-item work itself and names each item by its position
from 1 ("item 2").
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import ArtifactCatalog, ArtifactKind
from tax_engine.domain.errors import (
    InvalidRecordError,
    InvalidRegistrationError,
    NegativeArtifactError,
)


class Record(Mapping[ArtifactKind[Any], "Decimal | int | RecordList"]):
    """One record of a record list: a frozen mapping of its field kinds to their values.

    Built by `RecordList`, which checks it against the list's fields; equal to any mapping of the
    same items, and hashable.
    """

    __slots__ = ("_values",)

    def __init__(self, values: Mapping[ArtifactKind[Any], Decimal | int | RecordList]) -> None:
        self._values: dict[ArtifactKind[Any], object] = dict(values)

    def __getitem__[V](self, kind: ArtifactKind[V]) -> V:
        value = self._values[kind]
        # `RecordList` built the record with each value an instance of its kind's value type.
        if not isinstance(value, kind.value_type):
            raise TypeError(f"{kind.identifier} holds a {type(value).__name__}")
        return value

    def __iter__(self) -> Iterator[ArtifactKind[Any]]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __hash__(self) -> int:
        return hash(frozenset(self._values.items()))

    def __repr__(self) -> str:
        items = ", ".join(f"{kind.identifier}: {value!r}" for kind, value in self._values.items())
        return f"Record({{{items}}})"


@dataclass(frozen=True)
class RecordList:
    """Records of the same `fields`, in the caller's order, each checked when the list is built.

    The fields are `Decimal` or `int` artifact kinds or record-list kinds, none or more, no
    identifier twice, else an InvalidRecordError. With no fields every record is empty and the
    list only counts its records (a form's copies that carry no figures of their own). A record
    that is not a mapping, misses a field or has a key that is not one of the fields is an
    InvalidRecordError; a value that is not an instance of its field kind's value type is a
    TypeError (a `bool` is not a count); a value below zero for a field declared non-negative is a
    NegativeArtifactError. Each record error names the record by its position from 1 and the field
    by its identifier. A Decimal value that is NaN or infinite is an InvalidRecordError.
    """

    fields: tuple[ArtifactKind[Any], ...]
    records: tuple[Record, ...]

    def __init__(
        self,
        fields: Iterable[ArtifactKind[Any]],
        records: Iterable[Mapping[ArtifactKind[Any], object]],
    ) -> None:
        # Written by hand, so the dataclass keeps it: it takes any iterables, and
        # `__post_init__` normalises them.
        object.__setattr__(self, "fields", tuple(fields))
        object.__setattr__(self, "records", tuple(records))
        self.__post_init__()

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for kind in self.fields:
            if not isinstance(kind, ArtifactKind):
                raise InvalidRecordError(f"the field {kind!r} is not an artifact kind")
            if kind.identifier in seen:
                raise InvalidRecordError(f"the field {kind.identifier!r} is named more than once")
            seen.add(kind.identifier)
            # `bool` is a subclass of `int` but not a count, so the int check is exact.
            if not (
                issubclass(kind.value_type, Decimal)
                or kind.value_type is int
                or isinstance(kind, RecordListKind)
            ):
                raise InvalidRecordError(
                    f"the field {kind.identifier!r} holds a {kind.value_type.__name__}: "
                    f"a field must be a Decimal, int or record-list kind"
                )
        checked = tuple(
            self._checked(position, given) for position, given in enumerate(self.records, start=1)
        )
        object.__setattr__(self, "records", checked)

    def _checked(self, position: int, given: object) -> Record:
        item = f"item {position}"
        if not isinstance(given, Mapping):
            raise InvalidRecordError(
                f"{item}: a record must be a mapping of field kinds to values, "
                f"got {type(given).__name__}"
            )
        for kind in self.fields:
            if kind not in given:
                raise InvalidRecordError(f"{item}: missing field {kind.identifier}")
        for key in given:
            if key not in self.fields:
                name = key.identifier if isinstance(key, ArtifactKind) else repr(key)
                raise InvalidRecordError(f"{item}: unknown field {name}")
        values: dict[ArtifactKind[Any], Decimal | int | RecordList] = {}
        for kind in self.fields:
            value = given[kind]
            # `bool` is a subclass of `int` but not a count, so a count field refuses it.
            if not isinstance(value, kind.value_type) or isinstance(value, bool):
                raise TypeError(
                    f"{item}: {kind.identifier} must be a {kind.value_type.__name__}, "
                    f"got {type(value).__name__}"
                )
            if isinstance(kind, RecordListKind):
                try:
                    kind.check_value(value)
                except TypeError as exc:
                    raise TypeError(f"{item}: {exc}") from None
            if isinstance(value, Decimal) and not value.is_finite():
                raise InvalidRecordError(f"{item}: {kind.identifier} must be finite, got {value}")
            if kind.non_negative and value < 0:
                raise NegativeArtifactError(
                    f"{item}: {kind.identifier} cannot be negative, got {value}",
                    identifier=kind.identifier,
                    value=value,
                )
            values[kind] = value
        return Record(values)


@dataclass(frozen=True)
class RecordListKind(ArtifactKind[RecordList]):
    """A record-list kind: its values are `RecordList`s of exactly its `fields`, in that order.

    The fields are `Decimal`, `int` or record-list kinds, none or more, no identifier twice, else an
    InvalidRegistrationError naming the kind; they may come from any package's catalog. Two kinds
    of one identifier with other fields are not equal. Packages declare theirs with `declare`.
    """

    fields: tuple[ArtifactKind[Any], ...] = field(kw_only=True)

    def __init__(self, identifier: str, *, fields: Sequence[ArtifactKind[Any]]) -> None:
        # Written by hand, so the dataclass keeps it: the value type is always `RecordList`, never
        # non-negative, and the fields may be any sequence, which `__post_init__` normalises.
        object.__setattr__(self, "identifier", identifier)
        object.__setattr__(self, "value_type", RecordList)
        object.__setattr__(self, "non_negative", False)
        object.__setattr__(self, "fields", tuple(fields))
        self.__post_init__()

    def __post_init__(self) -> None:
        super().__post_init__()
        try:
            RecordList(self.fields, ())
        except InvalidRecordError as exc:
            raise InvalidRegistrationError(f"record list {self.identifier!r}: {exc}") from None

    @classmethod
    def declare(
        cls, catalog: ArtifactCatalog, local_id: str, fields: Sequence[ArtifactKind[Any]]
    ) -> RecordListKind:
        """Declare the record-list kind `<namespace>/<local_id>` of `fields` on `catalog`.

        The kind lands in the catalog's namespace, e.g. `ex/dependants`; its fields may come from
        any package's catalog. A local id the catalog already declared is an error.
        """
        kind = cls(catalog.namespace.identifier(local_id), fields=fields)
        catalog.add(kind)
        return kind

    def check_value(self, value: RecordList) -> None:
        """Refuse a record list built with other fields than this kind's, as a TypeError."""
        if value.fields != self.fields:
            raise TypeError(
                f"{self.identifier} must be a record list of fields "
                f"{[kind.identifier for kind in self.fields]}, "
                f"got fields {[kind.identifier for kind in value.fields]}"
            )
