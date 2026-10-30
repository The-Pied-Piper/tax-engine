"""Rate tables: a form's table of rates by bands of a figure, copied row for row.

Each row is printed as "more than X but not more than Y: rate" (the last row "more than X: rate",
with no upper bound); the table also holds `rate_at_zero`, the rate a form gives a figure of
exactly zero. The bounds are exact and kept as printed: an overlap between a row's upper bound and
the next row's lower bound, as a form's typo can print, is kept, while a gap is refused. A figure
above zero falls in the last row whose `more_than` it exceeds, so in an overlap the later row
applies. The code holds no jurisdiction's tables.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.errors import InvalidRateTableError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate


@dataclass(frozen=True)
class RateTableRow:
    """`rate` for a figure more than `more_than` and, when set, not more than `not_more_than`.

    The bounds are exact; a row without an upper bound is unbounded above.
    """

    more_than: Decimal
    not_more_than: Decimal | None
    rate: Rate

    def __post_init__(self) -> None:
        """Check: finite Decimal bounds, a `Rate`, and an upper bound above `more_than`."""
        if not isinstance(self.more_than, Decimal):
            raise TypeError(f"row more_than must be a Decimal, got {type(self.more_than).__name__}")
        if not self.more_than.is_finite():
            raise InvalidRateTableError(f"row more_than must be finite, got {self.more_than}")
        if self.not_more_than is not None:
            if not isinstance(self.not_more_than, Decimal):
                raise TypeError(
                    f"row not_more_than must be a Decimal, got {type(self.not_more_than).__name__}"
                )
            if not self.not_more_than.is_finite():
                raise InvalidRateTableError(
                    f"row not_more_than must be finite, got {self.not_more_than}"
                )
            if not self.not_more_than > self.more_than:
                raise InvalidRateTableError(
                    f"row not_more_than must be above its more_than, got {self.not_more_than} "
                    f"for more than {self.more_than}"
                )
        if not isinstance(self.rate, Rate):
            raise TypeError(f"row rate must be a Rate, got {type(self.rate).__name__}")


@dataclass(frozen=True)
class RateTable:
    """`rate_at_zero` and at least one row, the first more than 0, lower bounds strictly
    increasing, no gap between rows and an upper bound on every row but the last."""

    rate_at_zero: Rate
    rows: tuple[RateTableRow, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.rate_at_zero, Rate):
            raise TypeError(f"rate_at_zero must be a Rate, got {type(self.rate_at_zero).__name__}")
        if not isinstance(self.rows, tuple):
            raise TypeError(f"rows must be a tuple, got {type(self.rows).__name__}")
        for index, row in enumerate(self.rows):
            if not isinstance(row, RateTableRow):
                raise TypeError(f"rows[{index}] must be a RateTableRow, got {type(row).__name__}")
        if not self.rows:
            raise InvalidRateTableError("rate table needs at least one row")
        if self.rows[0].more_than != 0:
            raise InvalidRateTableError(
                f"the first row must be more than 0, got more than {self.rows[0].more_than}"
            )
        for index, (below, above) in enumerate(zip(self.rows, self.rows[1:], strict=False)):
            if above.more_than <= below.more_than:
                raise InvalidRateTableError(
                    f"rows[{index + 1}] more_than {above.more_than} does not exceed "
                    f"rows[{index}] more_than {below.more_than}; "
                    "more_than figures must be strictly increasing"
                )
            if below.not_more_than is None:
                raise InvalidRateTableError(
                    f"rows[{index}] has no not_more_than; "
                    "every row but the last must have a not_more_than"
                )
            if below.not_more_than < above.more_than:
                raise InvalidRateTableError(
                    f"rows[{index}] and rows[{index + 1}] leave a gap between "
                    f"{below.not_more_than} and {above.more_than}"
                )
        if self.rows[-1].not_more_than is not None:
            raise InvalidRateTableError(
                f"the last row must have no not_more_than, got {self.rows[-1].not_more_than}"
            )

    def row_for(self, figure: Decimal) -> RateTableRow | None:
        """The row a `figure` of zero or more falls in: `None` for exactly zero, which takes
        `rate_at_zero`, else the last row whose `more_than` it exceeds.

        The first row is more than 0, so a figure above zero always exceeds one; with no gaps,
        the figure is at most that row's `not_more_than` whenever it has one.
        """
        if figure == 0:
            return None
        return [row for row in self.rows if figure > row.more_than][-1]

    def rate_for(self, row: RateTableRow | None) -> Rate:
        """The rate `row` gives, or `rate_at_zero` for `None`."""
        return self.rate_at_zero if row is None else row.rate


RATE_TABLE: ParameterKind[RateTable] = ParameterKind("rate_table", RateTable)
