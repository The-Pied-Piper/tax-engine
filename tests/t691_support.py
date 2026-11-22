"""Test support: the Form T691 Part 7 amounts a caller gives.

Form T691 is a federal form that the provincial minimum tax lines read as one total (line 1 minus
line 2, or line 14). A caller types its lines 1 and 2 once, as the optional inputs
`ca/t691_minimum_amount` and `ca/t691_basic_federal_tax`, so a test that wants a T691 amount asks
for it here instead of declaring a provincial input of its own.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca.catalog import T691_BASIC_FEDERAL_TAX, T691_MINIMUM_AMOUNT


def minimum_amount(amount: str) -> Artifact[Decimal]:
    """The caller's T691 line 1 amount, as a starting artifact."""
    return Artifact(T691_MINIMUM_AMOUNT, Decimal(amount))


def basic_federal_tax(amount: str) -> Artifact[Decimal]:
    """The caller's T691 line 2 amount, as a starting artifact."""
    return Artifact(T691_BASIC_FEDERAL_TAX, Decimal(amount))


def line_1_minus_line_2(amount: str) -> list[Artifact[Decimal]]:
    """Starting artifacts that make T691 Part 7 line 1 minus line 2 equal to `amount`: line 1 when
    it is not negative, else line 2 with the absolute value (line 1 left blank)."""
    value = Decimal(amount)
    if value >= 0:
        return [minimum_amount(amount)]
    return [basic_federal_tax(str(-value))]


def line_14(amount: str) -> list[Artifact[Decimal]]:
    """Starting artifacts that make T691 line 14 equal to `amount`: line 1 given, line 13 blank."""
    return [minimum_amount(amount)]
