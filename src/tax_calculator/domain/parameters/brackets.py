"""Progressive bracket schedules: the form's bracket columns over ascending thresholds.

Each bracket holds the threshold it starts from (`lower`) and its `rate`. The schedule computes
each bracket's `tax_at_start`, the tax at the bracket's start: the exact cumulative tax on the
brackets below (never a sum of rounded figures), rounded with the schedule's
`tax_at_start_rounding` rule; the first bracket's is 0, put through the same rule. By default the
rule is none, so the tax at each start is the exact sum. The tax on an amount is the form's two
lines for the bracket the amount falls in: the rate on the excess over the bracket's lower, plus
its tax at its start. An amount at a threshold falls in the lower bracket, as the columns read
"more than ... but not more than ...".

A schedule is parameter data, resolved per (family, tax_year); the code holds no jurisdiction's
thresholds, rates or rounding. Arithmetic is exact apart from the rule's rounding of each start:
rounding the column's tax is the capability's decision, made with its own rounding rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidBracketScheduleError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingRule


@dataclass(frozen=True)
class Bracket:
    """One column: `rate` on amounts above `lower`."""

    lower: Decimal
    rate: Decimal

    def __post_init__(self) -> None:
        """Check: finite Decimal figures, `lower` >= 0, `rate` in [0, 1]."""
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
    """Brackets from 0, strictly ascending; the tax at each start rounded by one rule."""

    brackets: tuple[Bracket, ...]
    tax_at_start_rounding: RoundingRule = NO_ROUNDING

    def __post_init__(self) -> None:
        """Check the rule is a RoundingRule, the first threshold 0 and each above the last."""
        if not isinstance(self.tax_at_start_rounding, RoundingRule):
            raise TypeError(
                "schedule tax_at_start_rounding must be a RoundingRule, "
                f"got {type(self.tax_at_start_rounding).__name__}"
            )
        if not self.brackets:
            raise InvalidBracketScheduleError("a schedule needs at least one bracket")
        first = self.brackets[0]
        if first.lower != 0:
            raise InvalidBracketScheduleError(
                f"the first bracket must start at 0, got {first.lower}"
            )
        for below, above in zip(self.brackets, self.brackets[1:], strict=False):
            if above.lower <= below.lower:
                raise InvalidBracketScheduleError(
                    f"bracket thresholds must be strictly ascending: {above.lower} "
                    f"follows {below.lower}"
                )

    def column_for(self, amount: Decimal) -> BracketColumn:
        """The column `amount` falls in, with the rate on its excess plus its tax at its start."""
        if not isinstance(amount, Decimal):
            raise TypeError(f"amount must be a Decimal, got {type(amount).__name__}")
        if amount < 0:
            raise ValueError(f"amount must not be negative, got {amount}")
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
        # The exact tax on the brackets below, summed unrounded, then rounded once by the rule;
        # the first bracket's 0 passes through the rule too, so every start has the rule's scale.
        below = self.brackets[: index + 1]
        exact = sum(
            (
                (above.lower - bracket.lower) * bracket.rate
                for bracket, above in zip(below, below[1:], strict=False)
            ),
            Decimal(0),
        )
        return self.tax_at_start_rounding.apply(exact)

    def tax_on(self, amount: Decimal) -> Decimal:
        """Exact tax on `amount`: the tax of the column it falls in."""
        return self.column_for(amount).tax


BRACKETS: ParameterKind[BracketSchedule] = ParameterKind("brackets", BracketSchedule)
