"""The artifact kinds: amount, count, rate, text, digits and record list.

Each is an `ArtifactKind` of one value type that says for itself what it refuses and what a
package declares it with. Text is never read here: the adapters turn it into finished values
(adapters/text.py). A package declares one on its catalog with the class's own `declare`, e.g.
`AmountKind.declare(CATALOG, "taxable_income", non_negative=True)`.
An amount or a count may be non-negative; a count that is, is also how a yes/no is written, 1
for yes and 0 for no. A digits kind holds a fixed count of ASCII digits as text, a business
number say; a record-list kind holds a variable number of same-shaped records (the `RecordList`
value is in record_list.py). A new kind of value is a new subclass of `ArtifactKind`, not an edit
here.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import ArtifactCatalog, ArtifactKind
from tax_engine.domain.errors import (
    InvalidRecordError,
    InvalidRegistrationError,
    InvalidTextError,
)
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.record_list import RecordList

__all__ = ["AmountKind", "CountKind", "DigitsKind", "RateKind", "RecordListKind", "TextKind"]


@dataclass(frozen=True)
class AmountKind(ArtifactKind[Decimal]):
    """An amount: its values are exact `Decimal`s, never below zero if `non_negative`.

    `value_type` is `Decimal` unless a subclass of it is given.
    """

    non_negative: bool = field(default=False, kw_only=True)

    def __init__(
        self, identifier: str, value_type: type[Decimal] = Decimal, *, non_negative: bool = False
    ) -> None:
        # Written by hand, so the dataclass keeps it: the value type defaults to `Decimal`.
        object.__setattr__(self, "identifier", identifier)
        object.__setattr__(self, "value_type", value_type)
        object.__setattr__(self, "non_negative", non_negative)
        self.__post_init__()

    @classmethod
    def declare(
        cls, catalog: ArtifactCatalog, local_id: str, *, non_negative: bool = False
    ) -> AmountKind:
        """Declare the amount `<namespace>/<local_id>` on `catalog`, e.g. `ca/taxable_income`.

        A local id the catalog already declared is an error.
        """
        kind = cls(catalog.namespace.identifier(local_id), non_negative=non_negative)
        catalog.add(kind)
        return kind

    def is_below_floor(self, value: Decimal) -> bool:
        """Whether this kind is non-negative and `value` is below zero."""
        return self.non_negative and value < 0

    @property
    def is_record_field(self) -> bool:
        """An amount can be a field of a record."""
        return True


@dataclass(frozen=True)
class CountKind(ArtifactKind[int]):
    """A count: its values are whole numbers, never below zero if `non_negative`.

    A non-negative count is also how a yes/no is written, 1 for yes and 0 for no.
    """

    non_negative: bool = field(default=False, kw_only=True)

    def __init__(self, identifier: str, *, non_negative: bool = False) -> None:
        # Written by hand, so the dataclass keeps it: the value type is always `int`.
        object.__setattr__(self, "identifier", identifier)
        object.__setattr__(self, "value_type", int)
        object.__setattr__(self, "non_negative", non_negative)
        self.__post_init__()

    @classmethod
    def declare(
        cls, catalog: ArtifactCatalog, local_id: str, *, non_negative: bool = False
    ) -> CountKind:
        """Declare the count `<namespace>/<local_id>` on `catalog`, e.g. `ca/age_maximum`.

        A local id the catalog already declared is an error.
        """
        kind = cls(catalog.namespace.identifier(local_id), non_negative=non_negative)
        catalog.add(kind)
        return kind

    def is_below_floor(self, value: int) -> bool:
        """Whether this kind is non-negative and `value` is below zero."""
        return self.non_negative and value < 0

    @property
    def is_record_field(self) -> bool:
        """A count can be a field of a record."""
        return True

    @property
    def is_yes_no(self) -> bool:
        """A non-negative count is a yes/no."""
        return self.non_negative


@dataclass(frozen=True)
class RateKind(ArtifactKind[Rate]):
    """A rate: its values are `Rate`s, from 0 to 1. A manifest cannot give one as text."""

    def __init__(self, identifier: str) -> None:
        # Written by hand, so the dataclass keeps it: the value type is always `Rate`.
        object.__setattr__(self, "identifier", identifier)
        object.__setattr__(self, "value_type", Rate)
        self.__post_init__()

    @classmethod
    def declare(cls, catalog: ArtifactCatalog, local_id: str) -> RateKind:
        """Declare the rate `<namespace>/<local_id>` on `catalog`.

        A local id the catalog already declared is an error.
        """
        kind = cls(catalog.namespace.identifier(local_id))
        catalog.add(kind)
        return kind


@dataclass(frozen=True)
class TextKind(ArtifactKind[str]):
    """A kind of free text: its values are strings, read as written."""

    def __init__(self, identifier: str) -> None:
        # Written by hand, so the dataclass keeps it: the value type is always `str`.
        object.__setattr__(self, "identifier", identifier)
        object.__setattr__(self, "value_type", str)
        self.__post_init__()

    @classmethod
    def declare(cls, catalog: ArtifactCatalog, local_id: str) -> TextKind:
        """Declare the text `<namespace>/<local_id>` on `catalog`.

        A local id the catalog already declared is an error.
        """
        kind = cls(catalog.namespace.identifier(local_id))
        catalog.add(kind)
        return kind


@dataclass(frozen=True)
class DigitsKind(ArtifactKind[str]):
    """A digits kind: its values are texts of exactly its `digits` ASCII digits, or blank.

    `digits` is an `int` of at least 1 (a `bool` is not one), else an InvalidRegistrationError
    naming the kind. Two kinds of one identifier with another number of digits are not equal.
    Packages declare theirs with `declare`.
    """

    digits: int = field(kw_only=True)

    def __init__(self, identifier: str, *, digits: int) -> None:
        # Written by hand, so the dataclass keeps it: the value type is always `str` and never
        # non-negative.
        object.__setattr__(self, "identifier", identifier)
        object.__setattr__(self, "value_type", str)
        object.__setattr__(self, "digits", digits)
        self.__post_init__()

    def __post_init__(self) -> None:
        super().__post_init__()
        # `bool` is a subclass of `int` but not a number of digits, so the int check is exact.
        if type(self.digits) is not int or self.digits < 1:
            raise InvalidRegistrationError(
                f"digits kind {self.identifier!r}: the number of digits must be a whole number "
                f"of at least 1, got {self.digits!r}"
            )

    @classmethod
    def declare(cls, catalog: ArtifactCatalog, local_id: str, digits: int) -> DigitsKind:
        """Declare the digits kind `<namespace>/<local_id>` of `digits` digits on `catalog`.

        The kind lands in the catalog's namespace, e.g. `ex/business_number`. A local id the
        catalog already declared is an error.
        """
        kind = cls(catalog.namespace.identifier(local_id), digits=digits)
        catalog.add(kind)
        return kind

    def check_value(self, value: str) -> None:
        """Refuse a text that is neither blank nor exactly this kind's number of ASCII digits."""
        if value and not (len(value) == self.digits and value.isascii() and value.isdigit()):
            raise InvalidTextError(
                f"{self.identifier} must be {self.digits} digits, or blank, got {value!r}"
            )


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

    @property
    def is_record_field(self) -> bool:
        """A record-list kind can be a field of a record: a record may hold a list of records."""
        return True

    def check_value(self, value: RecordList) -> None:
        """Refuse a record list built with other fields than this kind's, as a TypeError."""
        if value.fields != self.fields:
            raise TypeError(
                f"{self.identifier} must be a record list of fields "
                f"{[kind.identifier for kind in self.fields]}, "
                f"got fields {[kind.identifier for kind in value.fields]}"
            )
