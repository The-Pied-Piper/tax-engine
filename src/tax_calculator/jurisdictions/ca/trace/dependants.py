"""Trace lines for dependants and caregivers: the allowable amounts worked out for one
dependant at a time.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.artifact import Money
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.parameters.claim_reduction import ClaimReduction
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.trace.base import TraceLine

__all__ = ["CaregiverClaimLine", "OtherDependantMedicalLine", "DisabilityTransferLine"]


@dataclass(frozen=True)
class CaregiverClaimLine(TraceLine):
    """The allowable amount `result` for one dependant, by `position` (from 1), for `output`.

    It is `base` less the dependant's `net_income`, from 0 up to `maximum`, rounded with
    `rounding`.

    Its own class, not a `CappedAmountLine`: the amount is worked on for one dependant, named by
    position, not for an artifact of its own.
    """

    output: Money
    position: int
    base: Amount
    net_income: Decimal
    maximum: Amount
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The dependant's allowable amount."""
        return self.result


@dataclass(frozen=True)
class OtherDependantMedicalLine(TraceLine):
    """The allowable amount `result` of medical expenses for one dependant, by `position` (from
    1), for `output`.

    It is the dependant's `expenses` less the `reduction`'s lesser of its ceiling and its rate
    times their `net_income`, from 0 up to the reduction's maximum when it has one, rounded with
    `rounding`.

    Its own class, not a `CaregiverClaimLine`: it is worked on from expenses and a reduction, not
    from a base amount and a maximum.
    """

    output: Money
    position: int
    expenses: Decimal
    net_income: Decimal
    reduction: ClaimReduction
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The dependant's allowable amount."""
        return self.result


@dataclass(frozen=True)
class DisabilityTransferLine(TraceLine):
    """The allowable amount `result` for one dependant, by `position` (from 1), for `output`.

    It follows the worksheet for the disability amount transferred from a dependant: `base`
    (line 1), `supplement` (line 2) and `threshold` (line 4) with `maximum` (the cap on line 8);
    the dependant's `under_18` (1 if under 18 on December 31, else 0) and `care_expenses` (line 3);
    `line_5` the expenses over the threshold and `line_6` the supplement less that, each from 0;
    `line_7` the supplement left, or 0 for a dependant 18 or older; `line_8` the base plus line 7,
    at most `maximum`; `credit_amounts` (line 9) and `line_10` their sum with line 8;
    `taxable_income` (line 11) and `line_12` line 10 less it, from 0; and `result` (line 13) the
    lesser of lines 8 and 12, rounded with `rounding`. Lines 5 to 12 are exact.

    Its own class, not a `CappedAmountLine`: the amount is worked on for one dependant, named by
    position, in many steps that the English rendering shows one by one.
    """

    output: Money
    position: int
    base: Amount
    supplement: Amount
    threshold: Amount
    maximum: Amount
    under_18: int
    care_expenses: Decimal
    line_5: Decimal
    line_6: Decimal
    line_7: Decimal
    line_8: Decimal
    credit_amounts: Decimal
    line_10: Decimal
    taxable_income: Decimal
    line_12: Decimal
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The dependant's allowable amount."""
        return self.result
