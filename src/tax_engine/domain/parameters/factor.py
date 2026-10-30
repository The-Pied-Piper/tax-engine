"""Factors: a multiplier from data, the number a form multiplies an amount by.

Unlike a `Rate`, a factor has no upper bound of 1: a form's "multiplied by 2" is a factor. The
code holds no jurisdiction's factors.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.errors import InvalidFactorError
from tax_engine.domain.parameters.kind import ParameterKind


@dataclass(frozen=True)
class Factor:
    """A multiplier of zero or more, exact, with no upper bound; non-finite or negative refused."""

    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            raise TypeError(f"factor must be a Decimal, got {type(self.value).__name__}")
        if not self.value.is_finite():
            raise InvalidFactorError(f"factor must be finite, got {self.value}")
        if self.value < 0:
            raise InvalidFactorError(f"factor must not be negative, got {self.value}")


FACTOR: ParameterKind[Factor] = ParameterKind("factor", Factor)
"""Parses `factor` datasets: one quoted decimal `value` into a Factor, which checks it is not
negative."""
