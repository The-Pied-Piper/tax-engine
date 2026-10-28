"""Trace line for a placement credit: the credit of one item of a record list."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.artifact import Money
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.trace.base import TraceLine

__all__ = ["PlacementCreditLine"]


@dataclass(frozen=True)
class PlacementCreditLine(TraceLine):
    """The credit of one item of a record list, produced as part of `output`: the item at
    `position` (from 1) has `field` (the eligible expenditures) worth `expenditure`; its line 1 is
    that at `expenditure_rate`, its line 3 is that at `supplement_rate`, its line 12 is line 3
    multiplied by `remaining_share` (worth `remaining_share_amount`), and its line 13 is the
    lesser of line 1 plus line 12 and `maximum`, rounded with `rounding`.

    `line_1`, `line_3` and `line_12` are exact; `line_13` is rounded. Its own class, not a
    `RecordTotalLine`: each item carries several lines of its own. The total of the items is an
    `ItemsTotalLine`.
    """

    output: Money
    position: int
    field: Money
    expenditure: Decimal
    line_1: Decimal
    line_3: Decimal
    line_12: Decimal
    line_13: Decimal
    remaining_share: Money
    remaining_share_amount: Decimal
    expenditure_rate: Rate
    supplement_rate: Rate
    maximum: Amount
    rounding: RoundingRule

    @property
    def amount(self) -> Decimal:
        """The item's last line, line 13."""
        return self.line_13
