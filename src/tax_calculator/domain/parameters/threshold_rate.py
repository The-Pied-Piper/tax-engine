"""Threshold rates: the figures of a line that passes an amount through or divides by a rate.

A `rate` and a `threshold`: a form line passes an amount through when it is at or below the
threshold, and otherwise divides another figure by the rate. Like `Rate`, the value object checks
itself. The code holds no jurisdiction's figures.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidThresholdRateError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import Rate


@dataclass(frozen=True)
class ThresholdRate:
    """A `rate` above zero and a `threshold` of zero or more, exact.

    A non-finite or negative threshold, and a rate of 0 (it is a divisor), are refused when it is
    built.
    """

    rate: Rate
    threshold: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.rate, Rate):
            raise TypeError(f"rate must be a Rate, got {type(self.rate).__name__}")
        self._check("threshold", self.threshold)
        if self.rate.value == 0:
            raise InvalidThresholdRateError("rate must not be zero")

    @staticmethod
    def _check(name: str, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError(f"{name} must be a Decimal, got {type(value).__name__}")
        if not value.is_finite():
            raise InvalidThresholdRateError(f"{name} must be finite, got {value}")
        if value < 0:
            raise InvalidThresholdRateError(f"{name} must not be negative, got {value}")


THRESHOLD_RATE: ParameterKind[ThresholdRate] = ParameterKind("threshold_rate", ThresholdRate)
