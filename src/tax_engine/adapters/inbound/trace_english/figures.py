"""EnglishFigures: how each type of field in a trace line reads in English.

Percentages, plain figures and rounding rules read the same in every line, so renderers format them
here, as in `EnglishFigures.money(amount)`.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingRule, RoundTo
from tax_engine.domain.unit import Placement, Unit


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
        text = format(amount, "f")  # fixed-point, every digit; never an exponent
        whole, _, cents = text.partition(".")
        shown = f"{whole}.{cents.ljust(2, '0')}"
        return "0.00" if shown == "-0.00" else shown

    @staticmethod
    def with_unit(shown: str, value: Decimal | int, unit: Unit | None) -> str:
        """The figure `value`, which prints as `shown`, written with `unit`.

        A unit placed before the number goes before its digits, after any minus sign ("-EX$1.00");
        one placed after goes after the number ("12 moons"). One space separates the unit from the
        figure when the unit is `spaced` ("EX$ 1.00", "12%" when not). The unit's singular text is
        used for a value of exactly 1 and its plural for any other. With no unit, `shown` as it is.
        """
        if unit is None:
            return shown
        text = unit.singular if value == 1 else unit.plural
        gap = " " if unit.spaced else ""
        if unit.placement is Placement.AFTER:
            return f"{shown}{gap}{text}"
        sign, digits = ("-", shown[1:]) if shown.startswith("-") else ("", shown)
        return f"{sign}{text}{gap}{digits}"

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
