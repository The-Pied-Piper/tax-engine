"""Trace lines for the foreign tax credit: one country's line 3, or all countries pooled, and the
lines 4 to 11 of the business part of one sheet."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine

__all__ = [
    "ForeignBusinessLine10",
    "ForeignBusinessLine11",
    "ForeignBusinessLine4",
    "ForeignBusinessLine5",
    "ForeignBusinessLine7",
    "ForeignBusinessLine8",
    "ForeignPropertyTaxLine",
    "ForeignTaxCreditLine",
    "PooledForeignTaxCreditLine",
]


@dataclass(frozen=True)
class ForeignPropertyTaxLine(TraceLine):
    """The foreign tax on income from property over the limit, `result`, of one country, by
    `position` (from 1), for `output`.

    The limit is `income` (the country's net income from property) times the limit rate, rounded
    with `rounding`; the result is the country's property `tax_paid` less the limit, not below
    zero.
    """

    output: Money
    position: int
    tax_paid: Decimal
    income: Decimal
    rate: Decimal
    rounding: RoundingRule
    limit: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The country's tax over the limit."""
        return self.result


@dataclass(frozen=True)
class ForeignTaxCreditLine(TraceLine):
    """The federal non-business foreign tax credit `result` of one country, by `position` (from
    1), for `output`.

    Line 2 is the country's `income` (already capped at `net_income`) times `basic_federal_tax`
    divided by `net_income`, rounded once with `rounding`; the result is the lesser of the
    country's `tax_paid` (line 1) and `line_2`. When `net_income` is zero or less there is no tax
    payable to credit against, so `income` and `line_2` are 0.
    """

    output: Money
    position: int
    tax_paid: Decimal
    income: Decimal
    net_income: Decimal
    basic_federal_tax: Decimal
    rounding: RoundingRule
    line_2: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The country's credit."""
        return self.result


@dataclass(frozen=True)
class PooledForeignTaxCreditLine(TraceLine):
    """The federal non-business foreign tax credit `result` of all `countries` worked as one, for
    `output`.

    The countries are pooled when there is one of them or when their `total_foreign_taxes`, the non-
    business `tax_paid` plus the business income tax paid for the year ("the total foreign taxes
    paid to all foreign countries"), is not more than `threshold`. Line 2 is the total `income`
    (already capped at `net_income`) times `basic_federal_tax` divided by `net_income`, rounded once
    with `rounding`; the result is the lesser of `tax_paid` and `line_2`. When `net_income` is zero
    or less, `income` and `line_2` are 0.
    """

    output: Money
    countries: int
    tax_paid: Decimal
    income: Decimal
    net_income: Decimal
    basic_federal_tax: Decimal
    total_foreign_taxes: Decimal
    threshold: Decimal
    rounding: RoundingRule
    line_2: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The pooled credit."""
        return self.result


@dataclass(frozen=True)
class ForeignBusinessLine4(TraceLine):
    """Form T2209 line 4 (43400) of the sheet at `position` (from 1), for `output`: the business
    income `tax_paid` for the year plus the `unused_credits` for that country, `result`."""

    output: Money
    position: int
    tax_paid: Decimal
    unused_credits: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The sheet's line 4."""
        return self.result


@dataclass(frozen=True)
class ForeignBusinessLine5(TraceLine):
    """Form T2209 line 5 of the sheet at `position` (from 1), for `output`: the net foreign
    business `income` (43900, already capped at `net_income`) times `basic_federal_tax` (note 8)
    divided by `net_income`, rounded once with `rounding`, `result`; 0 when `net_income` is zero or
    less."""

    output: Money
    position: int
    income: Decimal
    net_income: Decimal
    basic_federal_tax: Decimal
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The sheet's line 5."""
        return self.result


@dataclass(frozen=True)
class ForeignBusinessLine7(TraceLine):
    """Form T2209 line 7 "Add lines 5 and 6." of the sheet at `position` (from 1), for `output`:
    `line_5` plus `line_6`, `result`."""

    output: Money
    position: int
    line_5: Decimal
    line_6: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The sheet's line 7."""
        return self.result


@dataclass(frozen=True)
class ForeignBusinessLine8(TraceLine):
    """Form T2209 line 8 "Add basic federal tax (8) and the amount from line 6." of the sheet at
    `position` (from 1), for `output`: `basic_federal_tax` plus `line_6`, `result`."""

    output: Money
    position: int
    basic_federal_tax: Decimal
    line_6: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The sheet's line 8."""
        return self.result


@dataclass(frozen=True)
class ForeignBusinessLine10(TraceLine):
    """Form T2209 line 10 "Line 8 minus line 9" of the sheet at `position` (from 1), for
    `output`: `line_8` less `line_3` (line 9, "the amount from line 3"), `result`, which can be
    below zero."""

    output: Money
    position: int
    line_8: Decimal
    line_3: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The sheet's line 10."""
        return self.result


@dataclass(frozen=True)
class ForeignBusinessLine11(TraceLine):
    """Form T2209 line 11 "Enter whichever is less: the amount from line 4, 7 or 10." of the sheet
    at `position` (from 1), for `output`: the least of `line_4`, `line_7` and `line_10`,
    `result`."""

    output: Money
    position: int
    line_4: Decimal
    line_7: Decimal
    line_10: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The sheet's line 11."""
        return self.result
