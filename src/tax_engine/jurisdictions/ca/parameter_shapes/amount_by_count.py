"""Amounts by count: the figures a form prints against a count, such as a table by months.

A table holds rows in the order given, each a non-negative `int` count and the exact, finite,
non-negative amount printed against it. A count is listed once. The code holds no
jurisdiction's tables.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.errors import InvalidAmountByCountError
from tax_engine.domain.parameters.kind import ParameterKind


@dataclass(frozen=True)
class AmountByCount:
    """`rows`, each a `(count, amount)` pair; checked when built."""

    rows: tuple[tuple[int, Decimal], ...]

    def __post_init__(self) -> None:
        """Check: at least one row, int counts >= 0 listed once, finite Decimal amounts >= 0."""
        if not self.rows:
            raise InvalidAmountByCountError("amount by count must not be empty")
        seen: set[int] = set()
        for count, amount in self.rows:
            if not isinstance(count, int) or isinstance(count, bool):
                raise TypeError(
                    f"amount by count: count must be an int, got {type(count).__name__}"
                )
            if not isinstance(amount, Decimal):
                raise TypeError(
                    f"amount by count: amount must be a Decimal, got {type(amount).__name__}"
                )
            if count < 0:
                raise InvalidAmountByCountError(
                    f"amount by count: count must not be negative, got {count}"
                )
            if not amount.is_finite():
                raise InvalidAmountByCountError(
                    f"amount by count: amount must be finite, got {amount}"
                )
            if amount < 0:
                raise InvalidAmountByCountError(
                    f"amount by count: amount must not be negative, got {amount}"
                )
            if count in seen:
                raise InvalidAmountByCountError(f"amount by count: duplicate count {count}")
            seen.add(count)
        # A zero amount is a plain zero (its scale kept), never a negative zero.
        object.__setattr__(
            self,
            "rows",
            tuple(
                (count, amount.copy_abs() if not amount else amount) for count, amount in self.rows
            ),
        )


AMOUNT_BY_COUNT: ParameterKind[AmountByCount] = ParameterKind("amount_by_count", AmountByCount)
