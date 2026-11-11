"""Reading the text of a manifest or a request as values: the one place the engine does it.

The domain holds finished values only. A refusal is an InvalidTextError, to which the caller adds
where the text came from.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import cast

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
    written for a `str`; a record list or a rate has no spelling as text. The artifact refuses what
    the kind cannot hold.
    """
    # `kind.value_type` says which `V` it is (checked by `Artifact`), which the type cannot show.
    if kind.value_type is str:
        return Artifact(kind, cast(V, text))
    return Artifact(kind, cast(V, read_number(kind.value_type, text)))


def read_default[V](kind: ArtifactKind[V], declared: str | tuple[()] | None) -> Artifact[V]:
    """The artifact a manifest's declared default is read as.

    `None` is blank, a string is read as `read_artifact` reads it, and `()` is an empty record list
    for a record-list kind and refused for any other kind.
    """
    if declared is None:
        return Artifact(kind, BLANK)
    if isinstance(declared, str):
        return read_artifact(kind, declared)
    if isinstance(kind, RecordListKind):
        return cast(Artifact[V], Artifact(kind, RecordList(kind.fields, ())))
    raise InvalidTextError(f"must be {'a string' if kind.value_type is str else 'a quoted number'}")
