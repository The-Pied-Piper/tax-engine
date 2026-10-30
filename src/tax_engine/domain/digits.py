"""Digits kinds: a number the form asks for as a fixed count of digits, held as text.

A `DigitsKind` is the kind of an entry such as a nine-digit business number: its value type is
`str` and it carries `digits`, the number of digits the form asks for. An `Artifact` of one holds
exactly that many ASCII digits, kept as entered, a leading zero included, or the empty text for a
box left blank; any other text is an InvalidTextError naming the kind. Nothing is stripped or
reformatted: spaces and hyphens are refused. Packages declare a digits kind on their own catalog
with `DigitsKind.declare`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tax_engine.domain.artifact import ArtifactCatalog, ArtifactKind
from tax_engine.domain.errors import InvalidRegistrationError, InvalidTextError


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
        object.__setattr__(self, "non_negative", False)
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
