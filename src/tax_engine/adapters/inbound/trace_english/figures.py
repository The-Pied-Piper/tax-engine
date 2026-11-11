"""EnglishFigures: how each type of field in a trace line reads in English.

Percentages, plain figures, rounding rules and the start of a CCA table line
read the same in every line, so every line's renderer formats them with EnglishFigures, as in
`EnglishFigures.money(amount)`; a package's renderer may too.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.parameters.class_rates import ClassRate
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingRule, RoundTo


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
        """`amount` at the precision it is stored, e.g. 115000.00 -> "115000.00"."""
        return format(amount, "f")  # fixed-point, every digit; never an exponent

    @staticmethod
    def rounding(rule: RoundingRule) -> str:
        """How `rule` rounds, e.g. "not rounded" or "rounded to the nearest cent"."""
        if rule == NO_ROUNDING:
            return "not rounded"
        if isinstance(rule, RoundTo):
            if rule.mode.value == "half_up" and rule.increment == Decimal("0.01"):
                return "rounded to the nearest cent"
            return f"rounded {rule.mode.value.replace('_', '-')} to {rule.increment:f}"
        raise TypeError(f"no English rendering for rounding rule {type(rule).__name__}")
