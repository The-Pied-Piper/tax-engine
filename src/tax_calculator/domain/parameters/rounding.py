"""Rounding rules (design.md §3, Rounding).

Rounding is a parameter, never a jurisdiction constant in code. A capability
decides *where* it rounds, as does a parameter value that computes a figure of its
own (a bracket schedule's tax at each bracket's start); the `RoundingRule` each is
given decides *how*. The default is `NO_ROUNDING`, which leaves amounts exact, so
every rounding point calls `apply` and an unconfigured rule changes nothing.

Only exact amounts are accepted: a `Decimal`, or the exact `Fraction` a capability gets by
dividing. Rounding works on exact fractions, so any positive increment (0.01, 1, 0.05, ...)
rounds without an inexact division. `apply` is the one place allowed to be inexact: the engine
runs capabilities under a `decimal` context that traps `Inexact`, and rounding is the only
arithmetic a dataset asks for. `NO_ROUNDING` still never rounds: a quotient with no finite
decimal expansion raises `decimal.Inexact`.
"""

from __future__ import annotations

import decimal
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from fractions import Fraction

from tax_calculator.domain.errors import InvalidRoundingRuleError

_HALF = Fraction(1, 2)


class RoundingMode(Enum):
    """How an amount between two increments is resolved.

    Values are stable identifiers, used when rules are read from parameter data.
    """

    HALF_UP = "half_up"  # nearest; ties away from zero
    HALF_EVEN = "half_even"  # nearest; ties to the even neighbour
    DOWN = "down"  # toward zero
    UP = "up"  # away from zero
    FLOOR = "floor"  # toward negative infinity
    CEILING = "ceiling"  # toward positive infinity

    def to_integer(self, value: Fraction) -> int:
        """Resolve an exact value to a whole number according to this mode."""
        lower, upper = math.floor(value), math.ceil(value)
        if lower == upper:
            return lower
        toward_zero, away_from_zero = (lower, upper) if value > 0 else (upper, lower)
        match self:
            case RoundingMode.DOWN:
                return toward_zero
            case RoundingMode.UP:
                return away_from_zero
            case RoundingMode.FLOOR:
                return lower
            case RoundingMode.CEILING:
                return upper
        distance = value - lower
        if distance != _HALF:
            return lower if distance < _HALF else upper
        if self is RoundingMode.HALF_UP:
            return away_from_zero
        return lower if lower % 2 == 0 else upper


class RoundingRule(ABC):
    """How a capability rounds an amount. Capabilities depend on this type."""

    @abstractmethod
    def apply(self, amount: Decimal | Fraction) -> Decimal:
        """Return `amount`, a `Decimal` or an exact `Fraction`, rounded by this rule."""

    @staticmethod
    def _exact(amount: Decimal | Fraction) -> Fraction:
        """`amount` as an exact fraction; refuses anything but a finite Decimal or Fraction."""
        if isinstance(amount, Fraction):
            return amount
        if not isinstance(amount, Decimal):
            raise TypeError(f"amount must be a Decimal or a Fraction, got {type(amount).__name__}")
        if not amount.is_finite():
            raise ValueError(f"amount must be finite, got {amount}")
        return Fraction(amount)


@dataclass(frozen=True)
class _NoRounding(RoundingRule):
    """The default rule: amounts stay exact. Use `NO_ROUNDING`, never this class.

    A dataclass for value equality: a copy of `NO_ROUNDING` (e.g. after
    serialisation) is still equal to it.
    """

    def apply(self, amount: Decimal | Fraction) -> Decimal:
        if isinstance(amount, Decimal):
            self._exact(amount)  # refuses a non-finite Decimal
            return amount
        return self._terminating(self._exact(amount))

    @staticmethod
    def _terminating(exact: Fraction) -> Decimal:
        """`exact` as the shortest Decimal; raises `decimal.Inexact` if it has no finite expansion.

        Built from its digits, so the context's precision never rounds it.
        """
        denominator = exact.denominator
        twos = fives = 0
        while denominator % 2 == 0:
            denominator //= 2
            twos += 1
        while denominator % 5 == 0:
            denominator //= 5
            fives += 1
        if denominator != 1:
            raise decimal.Inexact(f"{exact} has no finite decimal expansion")
        places = max(twos, fives)
        digits = abs(exact.numerator) * 10**places // exact.denominator
        return Decimal((int(exact < 0), tuple(int(d) for d in str(digits)), -places))

    def __str__(self) -> str:
        """A developer repr; trace text is rendered by adapters, not by this method."""
        return "no rounding"


NO_ROUNDING: RoundingRule = _NoRounding()


@dataclass(frozen=True)
class RoundTo(RoundingRule):
    """Round to a multiple of `increment` using `mode`.

    The result carries the increment's scale: 7 rounded to 0.01 is 7.00.
    """

    increment: Decimal
    mode: RoundingMode

    def __post_init__(self) -> None:
        if not isinstance(self.increment, Decimal):
            raise TypeError(f"increment must be a Decimal, got {type(self.increment).__name__}")
        if not isinstance(self.mode, RoundingMode):
            raise TypeError(f"mode must be a RoundingMode, got {type(self.mode).__name__}")
        if not self.increment.is_finite() or self.increment <= 0:
            raise InvalidRoundingRuleError(
                f"increment must be a positive finite decimal, got {self.increment}"
            )

    def apply(self, amount: Decimal | Fraction) -> Decimal:
        steps = self.mode.to_integer(self._exact(amount) / Fraction(self.increment))
        # Exact whatever the caller's context: enough digits for the product, no Inexact trap.
        with decimal.localcontext() as context:
            context.traps[decimal.Inexact] = False
            context.prec = len(str(abs(steps))) + len(self.increment.as_tuple().digits) + 2
            return steps * self.increment

    def __str__(self) -> str:
        """A developer repr; trace text is rendered by adapters, not by this method."""
        return f"{self.mode.value.replace('_', '-')} to {self.increment}"
