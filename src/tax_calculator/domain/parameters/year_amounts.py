"""Year amounts: the named figures a form prints for each year it changed them.

A table of rows, newest first. A row's `from_year` N means "year N or later"; only the last row may
leave it out, meaning "any earlier year". `row_for(year)` gives the first row that applies, or None
when the form prints nothing for that year. Like `Rate`, the value objects check themselves. The
code holds no jurisdiction's figures.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidYearAmountsError
from tax_calculator.domain.parameters.kind import ParameterKind


@dataclass(frozen=True)
class YearAmountsRow:
    """The named `amounts` from `from_year` on (None: any earlier year), exact.

    No amounts, an empty amount name, and a non-finite or negative amount are refused when it is
    built.
    """

    from_year: int | None
    amounts: Mapping[str, Decimal]

    def __post_init__(self) -> None:
        if self.from_year is not None and (
            not isinstance(self.from_year, int) or isinstance(self.from_year, bool)
        ):
            raise TypeError(
                f"from_year must be an int or None, got {type(self.from_year).__name__}"
            )
        if not self.amounts:
            raise InvalidYearAmountsError("a row must have at least one amount")
        for name, value in self.amounts.items():
            if not name:
                raise InvalidYearAmountsError("an amount name must not be empty")
            if not isinstance(value, Decimal):
                raise TypeError(f"{name} must be a Decimal, got {type(value).__name__}")
            if not value.is_finite():
                raise InvalidYearAmountsError(f"{name} must be finite, got {value}")
            if value < 0:
                raise InvalidYearAmountsError(f"{name} must not be negative, got {value}")

    def amount(self, name: str) -> Decimal:
        """The amount called `name`; an unknown name is refused."""
        if name not in self.amounts:
            raise InvalidYearAmountsError(f"no amount named {name!r}")
        return self.amounts[name]


@dataclass(frozen=True)
class YearAmounts:
    """At least one row, newest first: years strictly descending, the open-ended row only last,
    and every row with the same amount names."""

    rows: tuple[YearAmountsRow, ...]

    def __post_init__(self) -> None:
        if not self.rows:
            raise InvalidYearAmountsError("a table must have at least one row")
        for row in self.rows:
            if not isinstance(row, YearAmountsRow):
                raise TypeError(f"each row must be a YearAmountsRow, got {type(row).__name__}")
        names = set(self.rows[0].amounts)
        previous: int | None = None
        for position, row in enumerate(self.rows):
            if set(row.amounts) != names:
                raise InvalidYearAmountsError("every row must have the same amount names")
            if row.from_year is None:
                if position != len(self.rows) - 1:
                    raise InvalidYearAmountsError("only the last row may leave out from_year")
            else:
                if previous is not None and row.from_year >= previous:
                    raise InvalidYearAmountsError("from_year must be strictly descending")
                previous = row.from_year

    def row_for(self, year: int) -> YearAmountsRow | None:
        """The first row whose `from_year` is open-ended or at most `year`, or None."""
        if not isinstance(year, int) or isinstance(year, bool):
            raise TypeError(f"year must be an int, got {type(year).__name__}")
        for row in self.rows:
            if row.from_year is None or row.from_year <= year:
                return row
        return None


YEAR_AMOUNTS: ParameterKind[YearAmounts] = ParameterKind("year_amounts", YearAmounts)
