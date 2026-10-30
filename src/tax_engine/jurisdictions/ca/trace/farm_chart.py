"""Trace lines for Form T2043 Chart B: a percentage of one figure over another.

Chart B's rows 3 and 6 are percentages of the statement's figures over the totals of all
provinces; each records one `PercentageOfLine`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine

__all__ = [
    "PercentageOfLine",
]


@dataclass(frozen=True)
class PercentageOfLine(TraceLine):
    """The percentage `result` produced as `output`: `dividend` (worth `dividend_amount`) divided
    by `divisor` (worth `divisor_amount`), times 100, rounded once with `rounding`. A zero divisor
    gives 0.

    Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated province.
    Row 1 divided by row 2" and row 6 "Percentage (%) of salaries and wages allocated to the
    designated province. Row 4 divided by row 5": 60 means 60%.
    """

    output: Money
    dividend: Money
    dividend_amount: Decimal
    divisor: Money
    divisor_amount: Decimal
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The percentage."""
        return self.result
