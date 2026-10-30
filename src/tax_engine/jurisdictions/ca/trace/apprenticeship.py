"""Trace lines for the apprenticeship job creation tax credit: the eligible salary and wages
counted for each apprentice, one at a time.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.amount import Amount
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine

__all__ = ["ApprenticeWagesLine"]


@dataclass(frozen=True)
class ApprenticeWagesLine(TraceLine):
    """The amount `result` for one apprentice, by `position` (from 1), for `output`.

    It is the lesser of the apprentice's `salary_and_wages` and the `maximum`, rounded with
    `rounding`.

    Its own class, not a `CappedAmountLine`: the amount is worked on for one apprentice, named by
    position, not for an artifact of its own.
    """

    output: Money
    position: int
    salary_and_wages: Decimal
    maximum: Amount
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The apprentice's amount."""
        return self.result
