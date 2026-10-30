"""Trace lines for Schedule 12, the multigenerational home renovation tax credit: lines 3, 6 and 7
of each qualifying renovation, by position."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.amount import Amount
from tax_engine.domain.trace.base import TraceLine

__all__ = [
    "RenovationLine3",
    "RenovationLine6",
    "RenovationLine7",
]


@dataclass(frozen=True)
class RenovationLine3(TraceLine):
    """Schedule 12 line 3 of the qualifying renovation at `position` (from 1), for `output`: its
    `expenditures` (line 1) less its `reimbursed` amount (line 2), at most the `maximum` (line 4),
    `result`."""

    output: Money
    position: int
    expenditures: Decimal
    reimbursed: Decimal
    maximum: Amount
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The renovation's line 3."""
        return self.result


@dataclass(frozen=True)
class RenovationLine6(TraceLine):
    """Schedule 12 line 6 "Line 4 minus line 5" of the qualifying renovation at `position` (from 1),
    for `output`: the `maximum` (line 4) less the `claimed_by_others` amount (line 5), `result`."""

    output: Money
    position: int
    maximum: Amount
    claimed_by_others: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The renovation's line 6."""
        return self.result


@dataclass(frozen=True)
class RenovationLine7(TraceLine):
    """Schedule 12 line 7 "Enter whichever is less: amount from line 3 or line 6" of the qualifying
    renovation at `position` (from 1), for `output`: the lesser of `line_3` and `line_6`,
    `result`."""

    output: Money
    position: int
    line_3: Decimal
    line_6: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The renovation's line 7."""
        return self.result
