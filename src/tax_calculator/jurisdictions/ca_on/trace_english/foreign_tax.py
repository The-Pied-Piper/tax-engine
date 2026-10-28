"""English text for the trace lines of `tax_calculator.jurisdictions.ca_on.trace.foreign_tax`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction as ExactFraction

from tax_calculator.adapters.inbound.trace_english.figures import EnglishFigures
from tax_calculator.adapters.inbound.trace_english.registry import english_renderer
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.jurisdictions.ca_on.trace.foreign_tax import (
    PooledProvincialForeignTaxCreditLine,
    ProvincialForeignTaxCreditLine,
)


def _line_2_wording(
    federal_credit: Decimal,
    tax_paid: Decimal,
    special_credit: Decimal | None,
    divisor: ExactFraction | None,
    basis: str,
    rounding: RoundingRule,
) -> str:
    """The wording of line 2: the federal credit, or the share of the special foreign tax credit
    when minimum tax is payable (`special_credit` and `divisor` set), described by `basis`."""
    money = EnglishFigures.money
    if special_credit is None or divisor is None:
        return f"federal credit {money(federal_credit)}"
    return (
        f"minimum tax line 2 {money(federal_credit)} ({money(tax_paid)} tax paid x "
        f"{money(special_credit)} special foreign tax credit / "
        f"{EnglishFigures.exact(divisor)} {basis}, "
        f"{EnglishFigures.rounding(rounding)})"
    )


@english_renderer
class PooledProvincialForeignTaxCreditRenderer:
    """English text for PooledProvincialForeignTaxCreditLine."""

    line_class = PooledProvincialForeignTaxCreditLine

    def render(self, line: PooledProvincialForeignTaxCreditLine) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        line_2 = _line_2_wording(
            line.federal_credit,
            line.tax_paid,
            line.special_credit,
            line.divisor,
            "total tax paid plus business tax",
            line.rounding,
        )
        return (
            f"{line.output.label}: all {line.sheets} sheets pooled, tax paid "
            f"{money(line.tax_paid)} is not more than {money(line.threshold)}: "
            f"tax paid {money(line.tax_paid)} less {line_2} = {money(line.line_3)}; "
            f"{money(line.income)} net foreign income x {money(line.provincial_tax)} provincial "
            f"tax / {money(line.net_income)} net income = {money(line.line_4)} "
            f"({EnglishFigures.rounding(line.rounding)}); credit {money(line.result)}"
        )


@english_renderer
class ProvincialForeignTaxCreditRenderer:
    """English text for ProvincialForeignTaxCreditLine."""

    line_class = ProvincialForeignTaxCreditLine

    def render(self, line: ProvincialForeignTaxCreditLine) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        line_2 = _line_2_wording(
            line.federal_credit,
            line.tax_paid,
            line.special_credit,
            line.divisor,
            "total foreign taxes paid, separate sheet"
            if line.separate_sheet
            else "total tax paid plus business tax",
            line.rounding,
        )
        return (
            f"{line.output.label}: sheet {line.position}: tax paid {money(line.tax_paid)} less "
            f"{line_2} = {money(line.line_3)}; "
            f"{money(line.income)} net foreign income x {money(line.provincial_tax)} provincial "
            f"tax / {money(line.net_income)} net income = {money(line.line_4)} "
            f"({EnglishFigures.rounding(line.rounding)}); credit {money(line.result)}"
        )
