"""Trace lines for the provincial foreign tax credit: one sheet's lines 1 to 5 of Form T2036, or the
lines 1 to 5 of one Form T2036 worked on the totals of all the sheets."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction as ExactFraction

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.trace.base import TraceLine

__all__ = ["PooledProvincialForeignTaxCreditLine", "ProvincialForeignTaxCreditLine"]


@dataclass(frozen=True)
class ProvincialForeignTaxCreditLine(TraceLine):
    """The provincial foreign tax credit `result` of one sheet of Form T2209, by `position` (from
    1), for `output`.

    Line 3 is the sheet's `tax_paid` (line 1) less the `federal_credit` (line 2, the sheet's line 3
    of Form T2209). Line 4 is the sheet's `income` times `provincial_tax` divided by `net_income`,
    rounded once with `rounding` (0 when `net_income` is zero or less); the result is the lesser of
    `line_3` and `line_4`.

    When minimum tax is payable, `federal_credit` holds the line 2 used: `tax_paid` times
    `special_credit` (Form T691 Part 4 line 11) over `divisor`, rounded once with `rounding`;
    `separate_sheet` is whether the divisor is the one for a form for each country. Otherwise the
    three fields keep their defaults.
    """

    output: Money
    position: int
    tax_paid: Decimal
    federal_credit: Decimal
    line_3: Decimal
    income: Decimal
    net_income: Decimal
    provincial_tax: Decimal
    rounding: RoundingRule
    line_4: Decimal
    result: Decimal
    special_credit: Decimal | None = None
    divisor: ExactFraction | None = None
    separate_sheet: bool = False

    @property
    def amount(self) -> Decimal:
        """The sheet's credit."""
        return self.result


@dataclass(frozen=True)
class PooledProvincialForeignTaxCreditLine(TraceLine):
    """The provincial foreign tax credit `result` of all `sheets` of Form T2209 worked once on the
    totals, for `output`.

    Form T2036 is worked once when there is more than one sheet and the total non-business tax
    paid, `tax_paid`, is not more than `threshold`, with or without minimum tax. Without minimum
    tax, `federal_credit` is the total of the sheets' line 3 of Form T2209. When minimum tax is
    payable, `federal_credit` holds line 2 of the form: `tax_paid` times `special_credit` (Form
    T691 Part 4 line 11) over `divisor`, rounded once with `rounding`; the divisor is the total tax
    paid plus the business tax. Otherwise those two fields keep their defaults.

    Line 3 is `tax_paid` less the `federal_credit`. Line 4 is the total `income` (already capped at
    `net_income`) times `provincial_tax` divided by `net_income`, rounded once with `rounding` (0
    when `net_income` is zero or less); the result is the lesser of `line_3` and `line_4`.
    """

    output: Money
    sheets: int
    tax_paid: Decimal
    federal_credit: Decimal
    line_3: Decimal
    income: Decimal
    net_income: Decimal
    provincial_tax: Decimal
    threshold: Decimal
    rounding: RoundingRule
    line_4: Decimal
    result: Decimal
    special_credit: Decimal | None = None
    divisor: ExactFraction | None = None

    @property
    def amount(self) -> Decimal:
        """The pooled credit."""
        return self.result
