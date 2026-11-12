"""Progressive bracket schedules: the form's bracket columns over ascending thresholds.

See docs/parameter-data.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.errors import AmountOutsideBracketRangeError, InvalidBracketScheduleError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingRule


@dataclass(frozen=True)
class Bracket:
    """One column: `rate` on amounts above `lower`, and the printed tax at its start if the form
    prints one (None if the schedule computes it)."""

    lower: Decimal
    rate: Decimal
    tax_at_start: Decimal | None = None

    def __post_init__(self) -> None:
        """Check: finite Decimal figures, `lower` >= 0, `rate` in [0, 1], and a printed
        `tax_at_start`, when given, finite and >= 0."""
        for name, value in (("lower", self.lower), ("rate", self.rate)):
            if not isinstance(value, Decimal):
                raise TypeError(f"bracket {name} must be a Decimal, got {type(value).__name__}")
            if not value.is_finite():
                raise InvalidBracketScheduleError(f"bracket {name} must be finite, got {value}")
        if self.lower < 0:
            raise InvalidBracketScheduleError(
                f"bracket lower must not be negative, got {self.lower}"
            )
        if not 0 <= self.rate <= 1:
            raise InvalidBracketScheduleError(
                f"bracket rate must be between 0 and 1, got {self.rate}"
            )
        if self.tax_at_start is not None:
            if not isinstance(self.tax_at_start, Decimal):
                raise TypeError(
                    "bracket tax_at_start must be a Decimal, "
                    f"got {type(self.tax_at_start).__name__}"
                )
            if not self.tax_at_start.is_finite():
                raise InvalidBracketScheduleError(
                    f"bracket tax_at_start must be finite, got {self.tax_at_start}"
                )
            if self.tax_at_start < 0:
                raise InvalidBracketScheduleError(
                    f"bracket tax_at_start must not be negative, got {self.tax_at_start}"
                )


@dataclass(frozen=True)
class BracketColumn:
    """The column an amount falls in: `rate` on the `excess` over `lower`, plus `tax_at_start`."""

    lower: Decimal
    rate: Decimal
    excess: Decimal
    tax_at_start: Decimal
    tax: Decimal


@dataclass(frozen=True)
class BracketSchedule:
    """Brackets over one range of amounts, strictly ascending; the tax at each start rounded by
    one rule.

    The range starts at the first bracket's threshold ("more than": 0 itself is covered only when
    that threshold is 0) and ends at `up_to` ("not more than"), or has no upper end if `up_to` is
    None. A first bracket above 0 must print its tax at start, since the schedule cannot compute
    the tax below its range.
    """

    brackets: tuple[Bracket, ...]
    tax_at_start_rounding: RoundingRule = NO_ROUNDING
    up_to: Decimal | None = None

    def __post_init__(self) -> None:
        """Check the rule is a RoundingRule, the thresholds ascend, a first bracket above 0 prints
        its tax at start, and `up_to`, if given, is a finite Decimal above the last threshold."""
        if not isinstance(self.tax_at_start_rounding, RoundingRule):
            raise TypeError(
                "schedule tax_at_start_rounding must be a RoundingRule, "
                f"got {type(self.tax_at_start_rounding).__name__}"
            )
        if not self.brackets:
            raise InvalidBracketScheduleError("a schedule needs at least one bracket")
        first = self.brackets[0]
        if first.lower != 0 and first.tax_at_start is None:
            raise InvalidBracketScheduleError(
                "the first bracket must start at 0 unless it gives its tax_at_start, "
                f"got {first.lower}"
            )
        for below, above in zip(self.brackets, self.brackets[1:], strict=False):
            if above.lower <= below.lower:
                raise InvalidBracketScheduleError(
                    f"bracket thresholds must be strictly ascending: {above.lower} "
                    f"follows {below.lower}"
                )
        if self.up_to is not None:
            if not isinstance(self.up_to, Decimal):
                raise TypeError(
                    f"schedule up_to must be a Decimal, got {type(self.up_to).__name__}"
                )
            if not self.up_to.is_finite():
                raise InvalidBracketScheduleError(
                    f"schedule up_to must be finite, got {self.up_to}"
                )
            if self.up_to <= self.brackets[-1].lower:
                raise InvalidBracketScheduleError(
                    f"schedule up_to must be above the last bracket's start "
                    f"{self.brackets[-1].lower}, got {self.up_to}"
                )

    @property
    def has_range(self) -> bool:
        """Whether the schedule states a range: an `up_to`, or a first bracket above 0."""
        return self.up_to is not None or self.brackets[0].lower != 0

    def covers(self, amount: Decimal) -> bool:
        """Whether `amount` is in the schedule's range: more than the first threshold (or 0 or
        more, if that is 0) and not more than `up_to`."""
        if not isinstance(amount, Decimal):
            raise TypeError(f"amount must be a Decimal, got {type(amount).__name__}")
        first = self.brackets[0].lower
        if amount < first or (first != 0 and amount == first):
            return False
        return self.up_to is None or amount <= self.up_to

    def column_for(self, amount: Decimal) -> BracketColumn:
        """The column `amount` falls in, with the rate on its excess plus its tax at its start.

        Raises AmountOutsideBracketRangeError if the range does not cover `amount`, and ValueError
        for a negative amount on a schedule from 0 with no upper end.
        """
        if not isinstance(amount, Decimal):
            raise TypeError(f"amount must be a Decimal, got {type(amount).__name__}")
        if self.brackets[0].lower == 0 and self.up_to is None and amount < 0:
            raise ValueError(f"amount must not be negative, got {amount}")
        if not self.covers(amount):
            raise AmountOutsideBracketRangeError(
                f"amount {amount} is outside the range of the bracket schedule"
            )
        index = 0
        for candidate in range(1, len(self.brackets)):
            if amount <= self.brackets[candidate].lower:
                break
            index = candidate
        bracket, tax_at_start = self.brackets[index], self._tax_at_start(index)
        excess = amount - bracket.lower
        return BracketColumn(
            bracket.lower, bracket.rate, excess, tax_at_start, excess * bracket.rate + tax_at_start
        )

    def _tax_at_start(self, index: int) -> Decimal:
        # A printed figure is the form's own constant: used as given, never computed or rounded.
        printed = self.brackets[index].tax_at_start
        if printed is not None:
            return printed
        # The exact tax on the brackets below, summed unrounded, then rounded once by the rule;
        # the first bracket's 0 passes through the rule too, so every start has the rule's scale.
        # A first bracket above 0 adds its printed start, the tax below the range.
        below = self.brackets[: index + 1]
        first_start = self.brackets[0].tax_at_start
        exact = (
            Decimal(0) if self.brackets[0].lower == 0 or first_start is None else first_start
        ) + sum(
            (
                (above.lower - bracket.lower) * bracket.rate
                for bracket, above in zip(below, below[1:], strict=False)
            ),
            Decimal(0),
        )
        return self.tax_at_start_rounding.apply(exact)

    def tax_on(self, amount: Decimal) -> Decimal:
        """Exact tax on `amount`: the tax of the column it falls in.

        Raises AmountOutsideBracketRangeError if the range does not cover `amount`.
        """
        return self.column_for(amount).tax


BRACKETS: ParameterKind[BracketSchedule] = ParameterKind("brackets", BracketSchedule)
