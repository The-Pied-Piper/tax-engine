"""Rates: a validated rate from 0 to 1, such as a credit rate, like `Credit` for amounts.

A rate has its own kind and datasets so that one rate is stated once, whichever capabilities use
it. The code holds no jurisdiction's rates.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidRateError
from tax_calculator.domain.parameters.kind import ParameterKind


@dataclass(frozen=True)
class Rate:
    """A rate from 0 to 1 inclusive, exact; anything else is refused when it is built."""

    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            raise TypeError(f"rate must be a Decimal, got {type(self.value).__name__}")
        if not self.value.is_finite():
            raise InvalidRateError(f"rate must be finite, got {self.value}")
        if not 0 <= self.value <= 1:
            raise InvalidRateError(f"rate must be between 0 and 1, got {self.value}")


RATE: ParameterKind[Rate] = ParameterKind("rate", Rate)
