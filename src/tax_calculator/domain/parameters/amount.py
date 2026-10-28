"""Amounts: a plain money value from data, such as a cap a form states, with no further meaning.

Unlike a `Credit`, nothing multiplies an amount by a rate. The code holds no jurisdiction's
amounts.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidAmountError
from tax_calculator.domain.parameters.kind import ParameterKind


@dataclass(frozen=True)
class Amount:
    """A money amount of zero or more, exact; a non-finite or negative value is refused."""

    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            raise TypeError(f"amount must be a Decimal, got {type(self.value).__name__}")
        if not self.value.is_finite():
            raise InvalidAmountError(f"amount must be finite, got {self.value}")
        if self.value < 0:
            raise InvalidAmountError(f"amount must not be negative, got {self.value}")


AMOUNT: ParameterKind[Amount] = ParameterKind("amount", Amount)
