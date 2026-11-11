"""EnglishFigures: how each type of field in a trace line reads in English.

Percentages, plain figures, rounding rules
read the same in every line, so every line's renderer formats them with EnglishFigures, as in
`EnglishFigures.money(amount)`; a package's renderer may too.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingRule, RoundTo


class EnglishFigures:
    """The English text of trace line fields by field type, shared by every line's renderer."""

    @staticmethod
    def listing(items: Sequence[str]) -> str:
        """`items` as a list in words: "a", "a and b", "a, b and c"."""
        if len(items) <= 1:
            return "".join(items)
        return f"{', '.join(items[:-1])} and {items[-1]}"

    @staticmethod
    def percent(rate: Decimal) -> str:
        """`rate` as a plain percentage figure, e.g. 0.125 -> "12.5"."""
        return format((rate * 100).normalize(), "f")

    @staticmethod
    def money(amount: Decimal) -> str:
        """`amount` in cents or finer, e.g. 70000 -> "70000.00" and 0.125 -> "0.125"."""
        exponent = amount.as_tuple().exponent
        shown = (
            amount.quantize(Decimal("0.01"))
            if isinstance(exponent, int) and exponent > -2
            else amount
        )
        return format(shown, "f")  # fixed-point, every digit; never an exponent

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
