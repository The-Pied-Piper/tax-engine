"""ForeignNonBusinessTaxCredit: the federal non-business foreign tax credit, T2209 lines 1 to 3.

Form T2209, "Federal non-business foreign tax credit": line 1 "Non-business income tax paid to a
foreign country (1) 43100"; line 2 "Net foreign non-business income (2) 43300" "× Basic federal tax
(4) = 2" over "Net income (3)"; line 3 "Enter whichever is less: the amount from line 1 or line 2."
Note (2): "If your net foreign non-business income is more than your net income, use your net income
in the calculation." "If you paid tax to more than one foreign country, and the total foreign taxes
paid to all foreign countries was more than $200, do the applicable calculation shown on this form
... to each country on a separate sheet in Canadian dollars. Enter the total amount on this form."

Each country is a record of the consumed `countries` list, holding lines 1 and the income of line
2 and the business figures of lines 4 to 6 (see below); `net_income` and `basic_federal_tax` are the
return-wide figures of notes (3) and (4). The page 1 note, "your non-business foreign tax credit for
that income cannot be more than 15% of your net income from that property. However, you may be able
to deduct the part of the foreign taxes you paid over 15% on line 23200 of your return", is taken
by leaving that part of a country's tax paid out of line 1: the country's tax paid less its excess
over the `limit_rate` dataset's 15% (`ForeignPropertyTaxOverLimit.excess`, the amount of line 23200
that `ca/foreign_property_tax_over_limit` totals) is the line 1 used, in the sheet and in the
trace; the pooling threshold is still compared with the tax actually paid, before that excess.
With more than one country and the total foreign taxes, the non-business tax paid plus the
business income tax paid for the year (line 4's first part, not its unused credits), above the
`pooling_threshold` dataset's amount (the printed $200), each
country is worked on its own: its income is capped at net income, line 2 is the income times basic
federal tax over net income, worked by `ApplyRatio.ratio_of` and rounded once with the `rounding`
dataset's rule, line 3 is the lesser of line 1 and line 2, and the output is the sum of the
countries' line 3, 0 when there are no countries. Otherwise one pooled calculation is worked on the
totals (tax paid summed, income summed then capped at net income). A net income of zero or less
makes line 2 0 without a division, and each income 0 (the cap floored at 0), so line 3 and the total
are 0: no tax is payable, so no credit (Income Tax Act s.126(1)). The net income in the trace is
the figure given. It records one `ForeignTaxCreditLine` for each country, by position from 1, then
an `ItemsTotalLine`; the pooled case records one `PooledForeignTaxCreditLine` alone, naming the
total foreign taxes compared with the threshold.

The second output, `sheets`, lists the T2209 sheets behind the total, in order: one record for each
country when each is worked on its own, one pooled record otherwise (also for a single country),
none without countries. A sheet holds line 1 (tax paid), the income used on line 2 (after the cap at
net income) and line 3, the same figure that enters the total, then the business figures for the
lines 4 to 6 of the business part: the business income tax paid for the year and the unused
business foreign tax credits (line 4), the net foreign business income (line 5, capped at net
income as note (7) says: "If your net foreign business income is more than your net income, use
your net income in the calculation.") and the federal surtax of line 6. A country on its own sheet
copies its figures; the pooled sheet adds them (the business income added, then capped). The
business lines are worked from the sheets by the capabilities of lines 4 to 11, not here.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capabilities.apply_ratio import ApplyRatio
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.foreign_property_tax_over_limit import (
    ForeignPropertyTaxOverLimit,
)
from tax_calculator.jurisdictions.ca.catalog import (
    FOREIGN_BUSINESS_TAX_PAID,
    FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
    FOREIGN_NON_BUSINESS_TAX_PAID,
    FOREIGN_SURTAX_OUTSIDE_CANADA,
    FOREIGN_TAX_CREDIT_SHEET_LINE_3,
    NET_FOREIGN_BUSINESS_INCOME,
    NET_FOREIGN_NON_BUSINESS_INCOME,
)
from tax_calculator.jurisdictions.ca.trace import ForeignTaxCreditLine, PooledForeignTaxCreditLine


@dataclass(frozen=True)
class ForeignTaxSheet:
    """One T2209 sheet: line 1 `tax_paid`, the `income` used on line 2, line 3 `result`, and the
    business figures `business_tax_paid` and `unused_credits` (line 4), `business_income` (line 5,
    already capped at net income) and `surtax` (line 6)."""

    tax_paid: Decimal
    income: Decimal
    result: Decimal
    business_tax_paid: Decimal
    unused_credits: Decimal
    business_income: Decimal
    surtax: Decimal


@capability(identifier="foreign_non_business_tax_credit")
class ForeignNonBusinessTaxCredit(Capability):
    """Produces `total`: the lesser of tax paid and its share of basic federal tax, for each
    consumed country (or all of them pooled), added; and `sheets`, the record of each T2209 sheet
    worked, with the business figures of its lines 4 to 6."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "rounding": ROUNDING_ONLY,
        "pooling_threshold": AMOUNT,
        "limit_rate": RATE,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {
        "countries": RecordList,
        "net_income": Decimal,
        "basic_federal_tax": Decimal,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"total": Decimal, "sheets": RecordList}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        pooling_threshold: ParameterDataset[Amount],
        limit_rate: ParameterDataset[Rate],
        countries: ArtifactKind[RecordList],
        net_income: Money,
        basic_federal_tax: Money,
        total: Money,
        sheets: RecordListKind,
    ) -> None:
        """Wire the capability: its rounding, pooling threshold and property limit rate datasets,
        the record list of countries and the two return-wide figures it reads, the kinds
        produced."""
        super().__init__(
            countries=countries,
            net_income=net_income,
            basic_federal_tax=basic_federal_tax,
            total=total,
            sheets=sheets,
        )
        self._rounding = rounding
        self._pooling_threshold = pooling_threshold
        self._limit_rate = limit_rate
        self._countries = countries
        self._net_income = net_income
        self._basic_federal_tax = basic_federal_tax
        self._total = total
        self._sheets = sheets

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._countries).value.records
        if not records:
            return CapabilityResult(
                outputs=(
                    Artifact(self._total, Decimal(0)),
                    Artifact(self._sheets, RecordList(self._sheets.fields, ())),
                ),
                trace=(ItemsTotalLine(self._total, (), Decimal(0)),),
            )
        net_income = self._input(inputs, self._net_income).value
        basic_federal_tax = self._input(inputs, self._basic_federal_tax).value
        rule = self._rounding.rounding
        threshold = self._pooling_threshold.values.value
        paid = [Decimal(record[FOREIGN_NON_BUSINESS_TAX_PAID]) for record in records]
        taxes = [
            tax - ForeignPropertyTaxOverLimit.excess(record, self._limit_rate)
            for tax, record in zip(paid, records, strict=True)
        ]
        incomes = [Decimal(record[NET_FOREIGN_NON_BUSINESS_INCOME]) for record in records]
        business_taxes = [Decimal(record[FOREIGN_BUSINESS_TAX_PAID]) for record in records]
        unused = [Decimal(record[FOREIGN_BUSINESS_UNUSED_TAX_CREDITS]) for record in records]
        business_incomes = [Decimal(record[NET_FOREIGN_BUSINESS_INCOME]) for record in records]
        surtaxes = [Decimal(record[FOREIGN_SURTAX_OUTSIDE_CANADA]) for record in records]
        total_foreign_taxes = sum(paid, Decimal(0)) + sum(business_taxes, Decimal(0))
        if len(records) == 1 or total_foreign_taxes <= threshold:
            tax_paid = sum(taxes, Decimal(0))
            income = self._capped(sum(incomes, Decimal(0)), net_income)
            line_2 = self._line_2(income, basic_federal_tax, net_income, rule)
            result = min(tax_paid, line_2)
            sheet = ForeignTaxSheet(
                tax_paid,
                income,
                result,
                sum(business_taxes, Decimal(0)),
                sum(unused, Decimal(0)),
                self._capped(sum(business_incomes, Decimal(0)), net_income),
                sum(surtaxes, Decimal(0)),
            )
            return CapabilityResult(
                outputs=(Artifact(self._total, result), self._sheet_list([sheet])),
                trace=(
                    PooledForeignTaxCreditLine(
                        self._total,
                        len(records),
                        tax_paid,
                        income,
                        net_income,
                        basic_federal_tax,
                        total_foreign_taxes,
                        threshold,
                        rule,
                        line_2,
                        result,
                    ),
                ),
            )
        lines: list[ForeignTaxCreditLine] = []
        sheets: list[ForeignTaxSheet] = []
        for position, (tax_paid, country_income) in enumerate(
            zip(taxes, incomes, strict=True), start=1
        ):
            income = self._capped(country_income, net_income)
            line_2 = self._line_2(income, basic_federal_tax, net_income, rule)
            sheets.append(
                ForeignTaxSheet(
                    tax_paid,
                    income,
                    min(tax_paid, line_2),
                    business_taxes[position - 1],
                    unused[position - 1],
                    self._capped(business_incomes[position - 1], net_income),
                    surtaxes[position - 1],
                )
            )
            lines.append(
                ForeignTaxCreditLine(
                    self._total,
                    position,
                    tax_paid,
                    income,
                    net_income,
                    basic_federal_tax,
                    rule,
                    line_2,
                    min(tax_paid, line_2),
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._total, total), self._sheet_list(sheets)),
            trace=(*lines, ItemsTotalLine(self._total, items, total)),
        )

    @staticmethod
    def _capped(income: Decimal, net_income: Decimal) -> Decimal:
        """An income capped at net income (note 2, note 7); with a net income of zero or less it
        is 0, the cap floored at 0."""
        if net_income <= 0:
            return Decimal(0)
        return min(income, net_income)

    @staticmethod
    def _line_2(
        income: Decimal, basic_federal_tax: Decimal, net_income: Decimal, rule: RoundingRule
    ) -> Decimal:
        """Line 2 of a sheet: income times basic federal tax over net income, rounded once; with a
        net income of zero or less it is 0 and nothing is divided."""
        if net_income <= 0:
            return Decimal(0)
        return ApplyRatio.ratio_of(income, basic_federal_tax, net_income, rule)

    def _sheet_list(self, rows: list[ForeignTaxSheet]) -> Artifact[RecordList]:
        """The `sheets` output: one record for each sheet."""
        return Artifact(
            self._sheets,
            RecordList(
                self._sheets.fields,
                [
                    {
                        FOREIGN_NON_BUSINESS_TAX_PAID: sheet.tax_paid,
                        NET_FOREIGN_NON_BUSINESS_INCOME: sheet.income,
                        FOREIGN_TAX_CREDIT_SHEET_LINE_3: sheet.result,
                        FOREIGN_BUSINESS_TAX_PAID: sheet.business_tax_paid,
                        FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: sheet.unused_credits,
                        NET_FOREIGN_BUSINESS_INCOME: sheet.business_income,
                        FOREIGN_SURTAX_OUTSIDE_CANADA: sheet.surtax,
                    }
                    for sheet in rows
                ],
            ),
        )
