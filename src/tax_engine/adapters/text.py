"""Reading the text of a manifest or a request as values: the one place the engine does it.

Text comes from outside the engine (a YAML manifest now, a request later), so turning it into a
`Decimal`, an `int` or a string is an adapter's job; the domain holds finished values only. The
YAML loader and the request adapter both call these functions, so there is one copy of the rules:
a number is an optional minus sign and digits, with a decimal point and digits if it is a
`Decimal`. What a value may be (not below zero, so many digits) is the kind's own check, made when
the finished `Artifact` is built.

Every refusal is an InvalidTextError saying what the text must be; a caller adds where the text
came from.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK
from tax_engine.domain.errors import InvalidTextError
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.record_list import RecordList

__all__ = ["read_artifact", "read_default", "read_number"]

# A number's spelling in text: an optional minus sign and digits, a decimal point and digits.
_DECIMAL_NUMBER = re.compile(r"-?[0-9]+(\.[0-9]+)?")
_WHOLE_NUMBER = re.compile(r"-?[0-9]+")


def read_number(value_type: type, text: str) -> Decimal | int:
    """`text` as the plain decimal or whole number it spells, as a `value_type` of `int` or
    `Decimal` (or a subclass of it).

    Any other `value_type` has no spelling as a number.
    """
    whole = value_type is int
    if not whole and not issubclass(value_type, Decimal):
        raise InvalidTextError(f"has no spelling as text ({value_type.__name__} values)")
    pattern = _WHOLE_NUMBER if whole else _DECIMAL_NUMBER
    if not pattern.fullmatch(text):
        raise InvalidTextError(
            "must be a whole number" if whole else "must be a plain decimal number"
        )
    try:
        # A Decimal subclass takes the exact decimal; a whole number is an `int`.
        return int(text) if whole else value_type(Decimal(text))
    except (InvalidOperation, ValueError):
        # Python refuses a whole number of more than 4300 digits.
        raise InvalidTextError("is too long to read as a number") from None


def read_artifact[V](kind: ArtifactKind[V], text: str) -> Artifact[V]:
    """The artifact of `kind` that `text` spells, as a manifest or a request writes it.

    The value is read by the kind's value type: a number for a `Decimal` or `int`, the text as
    written for a `str`; a record list or a rate has no spelling as text. The kind's own checks
    are made by the artifact, which refuses what the kind cannot hold (a negative amount of a
    non-negative kind, text that is not a digits kind's digits).
    """
    if kind.value_type is str:
        value: Any = text
    else:
        value = read_number(kind.value_type, text)
    return Artifact(kind, value)


def read_default[V](kind: ArtifactKind[V], declared: str | tuple[()] | None) -> Artifact[V]:
    """The artifact a manifest's declared default is read as: `None` is blank, a string is read
    as `read_artifact` reads it, and `()` (an empty list) is an empty record list for a
    record-list kind and refused for any other kind.
    """
    if declared is None:
        return Artifact(kind, BLANK)
    if isinstance(declared, str):
        return read_artifact(kind, declared)
    if isinstance(kind, RecordListKind):
        empty: Any = RecordList(kind.fields, ())
        return Artifact(kind, empty)
    raise InvalidTextError(f"must be {'a string' if kind.value_type is str else 'a quoted number'}")
