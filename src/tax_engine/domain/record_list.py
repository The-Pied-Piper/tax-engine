"""Record lists: a variable number of same-shaped records held as one artifact value.

A `Record` is read by field kind, never by position; items are named by position from 1 ("item 2").
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import (
    ArtifactKind,
    HasFloor,
    RecordField,
)
from tax_engine.domain.blank import BLANK, Blank
from tax_engine.domain.errors import (
    BlankValueError,
    InvalidRecordError,
    NegativeArtifactError,
)


class Record(Mapping[ArtifactKind[Any], "Decimal | int | RecordList"]):
    """One record of a record list: a frozen mapping of its field kinds to their values.

    Built by `RecordList`, which checks it; equal to any mapping of the same items, and hashable. A
    field may be blank; reading its value is then a BlankValueError naming the field.
    """

    __slots__ = ("_values",)

    def __init__(
        self, values: Mapping[ArtifactKind[Any], Decimal | int | RecordList | Blank]
    ) -> None:
        self._values: dict[ArtifactKind[Any], object] = dict(values)

    def is_blank(self, kind: ArtifactKind[Any]) -> bool:
        """Whether the field `kind` of this record was left blank."""
        return self._values[kind] is BLANK

    def __getitem__[V](self, kind: ArtifactKind[V]) -> V:
        value = self._values[kind]
        if value is BLANK:
            raise BlankValueError(f"{kind.label} was left blank, so it has no value")
        # `RecordList` built the record with each value an instance of its kind's value type.
        if not isinstance(value, kind.value_type):
            raise TypeError(f"{kind.identifier} holds a {type(value).__name__}")
        return value

    def __iter__(self) -> Iterator[ArtifactKind[Any]]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Record):
            return self._values == other._values
        if isinstance(other, Mapping):
            return self._values == dict(other.items())
        return NotImplemented

    def __hash__(self) -> int:
        return hash(frozenset(self._values.items()))

    def __repr__(self) -> str:
        items = ", ".join(f"{kind.identifier}: {value!r}" for kind, value in self._values.items())
        return f"Record({{{items}}})"


@dataclass(frozen=True)
class RecordList:
    """Records of the same `fields`, in the caller's order, each checked when the list is built.

    With no fields every record is empty and the list only counts its records. Raises
    InvalidRecordError for invalid `fields`, a record that is not a mapping, misses a field or has
    an extra key, or a NaN or infinite `Decimal`; TypeError for a value not of its field's type (a
    `bool` is not a count); NegativeArtifactError for a negative value in a non-negative field.
    Errors name the record by position from 1 and the field by identifier.
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
            if not isinstance(kind, RecordField):
                raise InvalidRecordError(
                    f"the field {kind.identifier!r} holds a {kind.value_type.__name__}: "
                    f"a record cannot hold a field of this kind"
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
        values: dict[ArtifactKind[Any], Decimal | int | RecordList | Blank] = {}
        for kind in self.fields:
            value = given[kind]
            if value is BLANK:
                values[kind] = BLANK
                continue
            # `bool` is a subclass of `int` but not a count, so a count field refuses it.
            if not isinstance(value, kind.value_type) or isinstance(value, bool):
                raise TypeError(
                    f"{item}: {kind.identifier} must be a {kind.value_type.__name__}, "
                    f"got {type(value).__name__}"
                )
            try:
                kind.check_value(value)
            except TypeError as exc:
                raise TypeError(f"{item}: {exc}") from None
            if isinstance(value, Decimal) and not value.is_finite():
                raise InvalidRecordError(f"{item}: {kind.identifier} must be finite, got {value}")
            if isinstance(kind, HasFloor) and kind.is_below_floor(value):
                raise NegativeArtifactError(
                    f"{item}: {kind.identifier} cannot be negative, got {value}",
                    identifier=kind.identifier,
                    value=value,
                )
            values[kind] = value
        return Record(values)
