"""The plain artifact kinds: amount, count, rate and text.

Each is an `ArtifactKind` of one value type that says for itself how it reads text, what it
refuses and what a package declares it with. A package declares one on its catalog with the
class's own `declare`, e.g. `AmountKind.declare(CATALOG, "taxable_income", non_negative=True)`.
An amount or a count may be non-negative; a count that is, is also how a yes/no is written, 1
for yes and 0 for no. A new kind of value is a new subclass of `ArtifactKind`, not an edit here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from tax_engine.domain.artifact import Artifact, ArtifactCatalog, ArtifactKind
from tax_engine.domain.errors import InvalidTextError
from tax_engine.domain.parameters.rate import Rate

__all__ = ["AmountKind", "CountKind", "RateKind", "TextKind"]

# A number's spelling in text: an optional minus sign and digits, a decimal point and digits.
_DECIMAL_NUMBER = re.compile(r"-?[0-9]+(\.[0-9]+)?")
_WHOLE_NUMBER = re.compile(r"-?[0-9]+")


def _read_number(text: str, *, whole: bool, non_negative: bool) -> Decimal | int:
    """`text` as the plain decimal or whole number it spells, or an InvalidTextError."""
    pattern = _WHOLE_NUMBER if whole else _DECIMAL_NUMBER
    if not pattern.fullmatch(text):
        raise InvalidTextError(
            "must be a whole number" if whole else "must be a plain decimal number"
        )
    try:
        number = int(text) if whole else Decimal(text)
    except (InvalidOperation, ValueError):
        # Python refuses a whole number of more than 4300 digits.
        raise InvalidTextError("is too long to read as a number") from None
    if non_negative and number < 0:
        raise InvalidTextError("must not be below zero")
    return number


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

    def read(self, text: str) -> Artifact[Decimal]:
        """The amount `text` spells, a plain decimal number (not below zero if non-negative)."""
        number = _read_number(text, whole=False, non_negative=self.non_negative)
        return Artifact(self, self.value_type(number))

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

    def read(self, text: str) -> Artifact[int]:
        """The count `text` spells, a whole number (not below zero if non-negative)."""
        number = _read_number(text, whole=True, non_negative=self.non_negative)
        return Artifact(self, int(number))

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

    def read(self, text: str) -> Artifact[Rate]:
        """Refuse any text: a rate is computed, never entered."""
        raise InvalidTextError("has no spelling as text (Rate values)")


@dataclass(frozen=True)
class TextKind(ArtifactKind[str]):
    """A kind of free text: its values are strings, read as written."""

    default_spelling = "a string"

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

    def read(self, text: str) -> Artifact[str]:
        """The text itself."""
        return Artifact(self, text)
