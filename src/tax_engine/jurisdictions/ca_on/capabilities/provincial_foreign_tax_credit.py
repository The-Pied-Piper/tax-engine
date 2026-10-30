"""ProvincialForeignTaxCredit: the Ontario non-business foreign tax credit, T2036 lines 1 to 5.

Form T2036, "Provincial or Territorial Foreign Tax Credit": line 1 "Enter the amount from line 1 of
Form T2209."; line 2 "Enter the amount from line 3 of Form T2209, unless you have to pay minimum
tax.(1)"; line 3 "Line 1 minus line 2"; line 4 "Net foreign non-business income (2)" "×
Provincial or territorial tax otherwise payable (4)" over "Net income (3)"; line 5 "Enter
whichever amount is less: line 3 or line 4." "Provincial or territorial foreign tax credit".
"Enter the total from line 5 (for each country if applicable) on the line for the provincial or
territorial foreign tax credit of Form 428." Notes (2) and (3) take the net foreign non-business
income and the net income from line 2 of Form T2209.

Each sheet of Form T2209 is a record of the consumed `sheets` list, holding its line 1 (tax paid),
the income used on its line 2 and its line 3; `net_income` and `provincial_tax` are the
return-wide figures of notes (3) and (4). For each sheet, line 3 is line 1 less the sheet's line 3
of Form T2209, line 4 is the sheet's income times `provincial_tax` over `net_income`, worked by
`ApplyRatio.ratio_of` and rounded once with the `rounding` dataset's rule, line 5 is the lesser of
line 3 and line 4, and the output is the sum of the sheets' line 5, 0 when there are no sheets (net
income is then not read). A net income of zero or less makes line 4 0 without a division, so line 5
and the total are 0, and each sheet's income is 0: no tax is payable, so no credit (Income Tax Act
s.126(1)). It records one
`ProvincialForeignTaxCreditLine` for each sheet, by position from 1, then an `ItemsTotalLine`.

With more than one sheet and the total of the sheets' line 1 at or under the `threshold` dataset
(the $200), with or without minimum tax, Form T2036 is one form on the totals, as the form asks when
the total non-business income taxes paid to all foreign countries are $200 or less, even where Form
T2209 is per country because business tax takes its total foreign taxes over $200. Line 1 is the
total tax paid, line 2 the total of the sheets' line 3 of Form T2209 (without minimum tax) or, with
minimum tax, the one line 2 described below, line 3 line 1 less line 2, line 4 the total income
(capped at net income, 0 when net income is zero or less) times `provincial_tax` over
`net_income`, and the output is the lesser of lines 3 and 4. It records one
`PooledProvincialForeignTaxCreditLine` alone, with no `ItemsTotalLine`.

Line 2 note (1), when "you have to pay minimum tax" (the consumed `minimum_tax_applies` count, Form
T691 Part 5 line 11 above 0, is 1): for a resident of Ontario at the end of the year, "If the total
non-business income taxes you paid to all foreign countries is $200 or less", line 1 of this form
divided by "the sum of line 1 of this form and the amount on line 8 of Part 4 of Form T691", times
"the special foreign tax credit on line 11 of Part 4 of Form T691"; "If the total non-business
income taxes you paid to all foreign countries is more than $200", for each country line 1 of that
country divided by "the total foreign taxes paid for 2025 (to get this total, add the amount on
line 7 of Part 4 of Form T691, Alternative Minimum Tax, divided by 66.6666% and the amount on line
8 of Part 4 of Form T691)", times the same line 11. The total of the sheets' line 1 is tested
against the `threshold` dataset (the $200); line 7 is the consumed `non_business_tax_paid`, line 8
`business_tax_paid`, line 11 `special_foreign_tax_credit`, and the 66.6666% the `rate` dataset. At
or under the threshold line 2 is one figure on the totals: the total of line 1 times line 11 over
the total of line 1 plus line 8, rounded once. Over it each sheet is its line 1 times line 11 over
line 7 divided by the rate plus line 8, each rounded on its own. Line 2 is worked as an exact
fraction and rounded once with the `rounding` dataset's rule. The figures of Form T691 are in
cents, so line 2 may top line 1 by a cent: it is then held at line 1 (line 3 is 0), on the totals as
on each sheet, and refused beyond a cent; the form prints no tolerance, so this one-cent
allowance is the one this capability takes. A zero divisor is refused with a ValidationError.
With the count 0 line 2 is the sheet's line 3 of Form T2209, and the totals' line 2 the total of
those.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capabilities.apply_ratio import ApplyRatio
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import ValidationError
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.record_list import Record, RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.catalog import (
    FOREIGN_NON_BUSINESS_TAX_PAID,
    FOREIGN_TAX_CREDIT_SHEET_LINE_3,
    NET_FOREIGN_NON_BUSINESS_INCOME,
)
from tax_engine.jurisdictions.ca_on.trace import (
    PooledProvincialForeignTaxCreditLine,
    ProvincialForeignTaxCreditLine,
)

ONE_CENT = Decimal("0.01")
"""How far line 2 may top line 1 before the inputs are refused (T691 figures are in cents)."""


@capability(identifier="provincial_foreign_tax_credit")
class ProvincialForeignTaxCredit(Capability):
    """Produces `total`: for each consumed sheet of Form T2209, the lesser of its tax paid less
    its line 2 (its federal credit, or its share of the special foreign tax credit when minimum
    tax is payable) and its share of `provincial_tax`, added; or, with several sheets whose total
    tax paid is at or under the threshold, with or without minimum tax, the lesser of the totals'
    tax paid less the line 2 on the totals and the total income's share of `provincial_tax`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "rounding": ROUNDING_ONLY,
        "threshold": AMOUNT,
        "rate": RATE,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {
        "minimum_tax_applies": int,
        "sheets": RecordList,
        "net_income": Decimal,
        "provincial_tax": Decimal,
        "non_business_tax_paid": Decimal,
        "business_tax_paid": Decimal,
        "special_foreign_tax_credit": Decimal,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"total": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        threshold: ParameterDataset[Amount],
        rate: ParameterDataset[Rate],
        minimum_tax_applies: ArtifactKind[int],
        sheets: ArtifactKind[RecordList],
        net_income: Money,
        provincial_tax: Money,
        non_business_tax_paid: Money,
        business_tax_paid: Money,
        special_foreign_tax_credit: Money,
        total: Money,
    ) -> None:
        """Wire the capability: its rounding, threshold and rate datasets, the minimum tax count,
        the sheets and the return-wide figures it reads, the kind produced."""
        super().__init__(
            minimum_tax_applies=minimum_tax_applies,
            sheets=sheets,
            net_income=net_income,
            provincial_tax=provincial_tax,
            non_business_tax_paid=non_business_tax_paid,
            business_tax_paid=business_tax_paid,
            special_foreign_tax_credit=special_foreign_tax_credit,
            total=total,
        )
        self._rounding = rounding
        self._threshold = threshold
        self._rate = rate
        self._minimum_tax_applies = minimum_tax_applies
        self._non_business_tax_paid = non_business_tax_paid
        self._business_tax_paid = business_tax_paid
        self._special_foreign_tax_credit = special_foreign_tax_credit
        self._sheets = sheets
        self._net_income = net_income
        self._provincial_tax = provincial_tax
        self._total = total

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._sheets).value.records
        if not records:
            return CapabilityResult(
                outputs=(Artifact(self._total, Decimal(0)),),
                trace=(ItemsTotalLine(self._total, (), Decimal(0)),),
            )
        net_income = self._input(inputs, self._net_income).value
        provincial_tax = self._input(inputs, self._provincial_tax).value
        rule = self._rounding.rounding
        minimum_tax = self._input(inputs, self._minimum_tax_applies).value == 1
        business_tax = self._input(inputs, self._business_tax_paid).value
        line_11 = self._input(inputs, self._special_foreign_tax_credit).value
        if len(records) > 1:
            total_tax_paid = sum(
                (Decimal(record[FOREIGN_NON_BUSINESS_TAX_PAID]) for record in records), Decimal(0)
            )
            if total_tax_paid <= self._threshold.values.value:
                return self._pooled(
                    records,
                    total_tax_paid,
                    net_income,
                    provincial_tax,
                    rule,
                    minimum_tax,
                    business_tax,
                    line_11,
                )
        line_7 = self._input(inputs, self._non_business_tax_paid).value
        divisor: ExactFraction | None = None
        separate_sheet = False
        special_credit: Decimal | None = None
        if minimum_tax:
            special_credit = line_11
            total_tax_paid = sum(
                (Decimal(record[FOREIGN_NON_BUSINESS_TAX_PAID]) for record in records), Decimal(0)
            )
            separate_sheet = total_tax_paid > self._threshold.values.value
            if separate_sheet:
                divisor = ExactFraction(line_7) / ExactFraction(
                    self._rate.values.value
                ) + ExactFraction(business_tax)
            else:
                divisor = ExactFraction(total_tax_paid) + ExactFraction(business_tax)
            if divisor == 0:
                raise ValidationError(
                    "the total of tax paid plus the business tax is zero, so line 2 of Form "
                    "T2036, which divides by it, is undefined"
                )
        lines: list[ProvincialForeignTaxCreditLine] = []
        for position, record in enumerate(records, start=1):
            tax_paid = Decimal(record[FOREIGN_NON_BUSINESS_TAX_PAID])
            income = (
                Decimal(0) if net_income <= 0 else Decimal(record[NET_FOREIGN_NON_BUSINESS_INCOME])
            )
            if divisor is not None and special_credit is not None:
                federal_credit = _line_2_within_line_1(
                    rule.apply(ExactFraction(tax_paid) * ExactFraction(special_credit) / divisor),
                    tax_paid,
                )
            else:
                federal_credit = Decimal(record[FOREIGN_TAX_CREDIT_SHEET_LINE_3])
            line_3 = tax_paid - federal_credit
            line_4 = (
                Decimal(0)
                if net_income <= 0
                else ApplyRatio.ratio_of(income, provincial_tax, net_income, rule)
            )
            lines.append(
                ProvincialForeignTaxCreditLine(
                    self._total,
                    position,
                    tax_paid,
                    federal_credit,
                    line_3,
                    income,
                    net_income,
                    provincial_tax,
                    rule,
                    line_4,
                    min(line_3, line_4),
                    special_credit,
                    divisor,
                    separate_sheet,
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._total, total),),
            trace=(*lines, ItemsTotalLine(self._total, items, total)),
        )

    def _pooled(
        self,
        records: tuple[Record, ...],
        tax_paid: Decimal,
        net_income: Decimal,
        provincial_tax: Decimal,
        rule: RoundingRule,
        minimum_tax: bool,
        business_tax: Decimal,
        line_11: Decimal,
    ) -> CapabilityResult:
        """Form T2036 worked once on the totals of the sheets: line 3 is the total tax paid less
        line 2, line 4 the total income, capped at net income, times `provincial_tax` over
        `net_income` (0 when net income is zero or less). Line 2 is the total of the sheets' line 3
        of Form T2209, or with `minimum_tax` the total
        tax paid times line 11 over the total plus the business tax, rounded once."""
        special_credit: Decimal | None = None
        divisor: ExactFraction | None = None
        if not minimum_tax:
            federal_credit = sum(
                (Decimal(record[FOREIGN_TAX_CREDIT_SHEET_LINE_3]) for record in records),
                Decimal(0),
            )
        else:
            special_credit = line_11
            divisor = ExactFraction(tax_paid) + ExactFraction(business_tax)
            if divisor == 0:
                raise ValidationError(
                    "the total of tax paid plus the business tax is zero, so line 2 of Form "
                    "T2036, which divides by it, is undefined"
                )
            federal_credit = _line_2_within_line_1(
                rule.apply(ExactFraction(tax_paid) * ExactFraction(special_credit) / divisor),
                tax_paid,
            )
        line_3 = tax_paid - federal_credit
        income = Decimal(0)
        line_4 = Decimal(0)
        if net_income > 0:
            income = min(
                sum(
                    (Decimal(record[NET_FOREIGN_NON_BUSINESS_INCOME]) for record in records),
                    Decimal(0),
                ),
                net_income,
            )
            line_4 = ApplyRatio.ratio_of(income, provincial_tax, net_income, rule)
        line = PooledProvincialForeignTaxCreditLine(
            self._total,
            len(records),
            tax_paid,
            federal_credit,
            line_3,
            income,
            net_income,
            provincial_tax,
            self._threshold.values.value,
            rule,
            line_4,
            min(line_3, line_4),
            special_credit,
            divisor,
        )
        return CapabilityResult(
            outputs=(Artifact(self._total, line.result),),
            trace=(line,),
        )


def _line_2_within_line_1(federal_credit: Decimal, tax_paid: Decimal) -> Decimal:
    """Line 2 held at line 1 when it tops it by no more than a cent, refused beyond that. The
    figures of Form T691 are in cents, and dividing line 7 back by 66.6666% can leave the divisor a
    little under the tax paid and line 2 a cent over line 1; line 3 is then 0."""
    if federal_credit > tax_paid + ONE_CENT:
        raise ValidationError(
            f"line 2 of Form T2036, {federal_credit}, is more than the {tax_paid} of its "
            "line 1, so line 3 would be negative; the amounts on lines 7, 8 and 11 of "
            "Part 4 of Form T691 do not fit the tax paid on the sheets"
        )
    return min(federal_credit, tax_paid)
