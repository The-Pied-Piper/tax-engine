"""Fractions: a fraction of whole numbers, such as a form's "two-thirds" or a printed factor of 0.

Held as numerator (zero or more) and positive denominator, kept as given and never reduced, because
two-thirds is not a finite decimal; the capability that applies it does the one division.
"""

from __future__ import annotations

from dataclasses import dataclass

from tax_engine.domain.errors import InvalidFractionError
from tax_engine.domain.parameters.kind import ParameterKind


@dataclass(frozen=True)
class Fraction:
    """A fraction of a whole numerator of zero or more and a positive whole denominator, kept as
    given; others refused."""

    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        for part, value in (("numerator", self.numerator), ("denominator", self.denominator)):
            # bool is an int subclass; True must not become a part of 1.
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"fraction {part} must be an int, got {type(value).__name__}")
        if self.numerator < 0:
            raise InvalidFractionError(
                f"fraction numerator must not be negative, got {self.numerator}"
            )
        if self.denominator <= 0:
            raise InvalidFractionError(
                f"fraction denominator must be positive, got {self.denominator}"
            )


FRACTION: ParameterKind[Fraction] = ParameterKind("fraction", Fraction)
