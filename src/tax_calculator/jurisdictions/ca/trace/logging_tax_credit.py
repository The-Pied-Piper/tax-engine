"""Trace lines for the federal logging tax credit: the lesser amount worked out for one province
at a time.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.artifact import Money
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.trace.base import TraceLine

__all__ = ["LoggingTaxCreditLine"]


@dataclass(frozen=True)
class LoggingTaxCreditLine(TraceLine):
    """The lesser amount `result` for one province, by `position` (from 1), for `output`.

    Its tax side is `tax_rate` times the logging tax `tax_paid`, rounded with `tax_rounding` to
    `tax_share`; its income side is `income_rate` times the `net_logging_income`, rounded with
    `income_rounding` to `income_share`. `result` is the lesser of the two sides.

    Its own class, not a `CaregiverClaimLine`: it takes the lesser of two rated sides, not a base
    less a net income up to a maximum.
    """

    output: Money
    position: int
    tax_paid: Decimal
    tax_rate: Rate
    tax_share: Decimal
    net_logging_income: Decimal
    income_rate: Rate
    income_share: Decimal
    tax_rounding: RoundingRule
    income_rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The province's amount."""
        return self.result
