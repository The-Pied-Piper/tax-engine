"""Credits: an amount that, multiplied by a rate, reduces tax.

The amount is parameter data, resolved per (family, tax_year); the rate is its own parameter
(`rate` kind), so each fact has one home. The code holds no jurisdiction's figures.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidCreditError
from tax_calculator.domain.parameters.kind import ParameterKind


@dataclass(frozen=True)
class Credit:
    """A credit amount; a rate, given separately, turns it into tax relief."""

    amount: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError(f"credit amount must be a Decimal, got {type(self.amount).__name__}")
        if not self.amount.is_finite():
            raise InvalidCreditError(f"credit amount must be finite, got {self.amount}")
        if self.amount < 0:
            raise InvalidCreditError(f"credit amount must not be negative, got {self.amount}")


CREDIT: ParameterKind[Credit] = ParameterKind("credit", Credit)
