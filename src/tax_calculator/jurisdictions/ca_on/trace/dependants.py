"""Trace line for dependants and caregivers: the allowable amounts worked out for one
dependant at a time.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.artifact import Money
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.trace.base import TraceLine

__all__ = ["CaregiverClaimLessClaimedLine"]


@dataclass(frozen=True)
class CaregiverClaimLessClaimedLine(TraceLine):
    """The allowable amount `result` for one dependant, by `position` (from 1), for `output`.

    It is `base` less the dependant's `net_income`, from 0 up to `maximum`, rounded with
    `rounding` to `allowable_before_claimed`, less the `claimed` amount, not below 0.

    Its own class, not a `CaregiverClaimLine`: it also carries the amount claimed for this
    dependant elsewhere, taken off the rounded amount.
    """

    output: Money
    position: int
    base: Amount
    net_income: Decimal
    maximum: Amount
    allowable_before_claimed: Decimal
    claimed: Decimal
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The dependant's allowable amount."""
        return self.result
