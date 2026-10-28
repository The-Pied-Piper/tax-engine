"""EnglishFigures: how each type of field in a trace line reads in English.

Percentages, plain figures, exact fractions, rounding rules and the start of a CCA table line
read the same in every line, so every line's renderer formats them with EnglishFigures, as in
`EnglishFigures.money(amount)`; a package's renderer may too.
"""

from __future__ import annotations

import decimal
from decimal import Decimal
from fractions import Fraction as ExactFraction

from tax_calculator.domain.parameters.class_rates import ClassRate
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingRule, RoundTo


class EnglishFigures:
    """The English text of trace line fields by field type, shared by every line's renderer."""

    @classmethod
    def cca_class(cls, label: str, position: int, class_rate: ClassRate) -> str:
        """The start of a CCA table line: its output, its item and its class number."""
        return f"{label}: item {position} class {cls.money(class_rate.class_number)}"

    @staticmethod
    def percent(rate: Decimal) -> str:
        """`rate` as a plain percentage figure, e.g. 0.125 -> "12.5"."""
        return format((rate * 100).normalize(), "f")

    @staticmethod
    def money(amount: Decimal) -> str:
        """`amount` as a plain figure without trailing zeros, e.g. 115000.00 -> "115000"."""
        text = format(amount, "f")  # fixed-point, every digit; never an exponent
        return text.rstrip("0").rstrip(".") if "." in text else text

    @staticmethod
    def exact(amount: ExactFraction) -> str:
        """An exact fraction as a plain figure if it terminates, else "numerator/denominator"."""
        try:
            return EnglishFigures.money(NO_ROUNDING.apply(amount))
        except decimal.Inexact:
            return f"{amount.numerator}/{amount.denominator}"

    @staticmethod
    def rounding(rule: RoundingRule) -> str:
        """How `rule` rounds, e.g. "no rounding" or "half-up to 0.01"."""
        if rule == NO_ROUNDING:
            return "no rounding"
        if isinstance(rule, RoundTo):
            return f"{rule.mode.value.replace('_', '-')} to {rule.increment:f}"
        raise TypeError(f"no English rendering for rounding rule {type(rule).__name__}")
