"""English text for the trace lines of `tax_calculator.jurisdictions.ca.trace.foreign_tax`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english.figures import EnglishFigures
from tax_calculator.adapters.inbound.trace_english.registry import english_renderer
from tax_calculator.jurisdictions.ca.trace.foreign_tax import (
    ForeignBusinessLine4,
    ForeignBusinessLine5,
    ForeignBusinessLine7,
    ForeignBusinessLine8,
    ForeignBusinessLine10,
    ForeignBusinessLine11,
    ForeignPropertyTaxLine,
    ForeignTaxCreditLine,
    PooledForeignTaxCreditLine,
)


@english_renderer
class ForeignPropertyTaxRenderer:
    """English text for ForeignPropertyTaxLine."""

    line_class = ForeignPropertyTaxLine

    def render(self, line: ForeignPropertyTaxLine) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: country {line.position}: tax paid on property income "
            f"{money(line.tax_paid)}, limit {EnglishFigures.percent(line.rate)}% of "
            f"{money(line.income)} = {money(line.limit)} "
            f"({EnglishFigures.rounding(line.rounding)}); over the limit {money(line.result)}"
        )


@english_renderer
class ForeignTaxCreditRenderer:
    """English text for ForeignTaxCreditLine."""

    line_class = ForeignTaxCreditLine

    def render(self, line: ForeignTaxCreditLine) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: country {line.position}: tax paid {money(line.tax_paid)}, "
            f"{money(line.income)} net foreign income x {money(line.basic_federal_tax)} basic "
            f"federal tax / {money(line.net_income)} net income = {money(line.line_2)} "
            f"({EnglishFigures.rounding(line.rounding)}); credit {money(line.result)}"
        )


@english_renderer
class PooledForeignTaxCreditRenderer:
    """English text for PooledForeignTaxCreditLine."""

    line_class = PooledForeignTaxCreditLine

    def render(self, line: PooledForeignTaxCreditLine) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        if line.countries == 1:
            start = f"one country: tax paid {money(line.tax_paid)},"
        else:
            start = (
                f"all {line.countries} countries pooled, total foreign taxes "
                f"{money(line.total_foreign_taxes)} is not more than {money(line.threshold)}: "
                f"tax paid {money(line.tax_paid)},"
            )
        return (
            f"{line.output.label}: {start} {money(line.income)} net foreign income x "
            f"{money(line.basic_federal_tax)} basic federal tax / {money(line.net_income)} net "
            f"income = {money(line.line_2)} ({EnglishFigures.rounding(line.rounding)}); "
            f"credit {money(line.result)}"
        )


@english_renderer
class ForeignBusinessLine4Renderer:
    """English text for ForeignBusinessLine4."""

    line_class = ForeignBusinessLine4

    def render(self, line: ForeignBusinessLine4) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: sheet {line.position}: line 4 = business income tax paid "
            f"{money(line.tax_paid)} + unused foreign tax credits {money(line.unused_credits)} "
            f"= {money(line.result)}"
        )


@english_renderer
class ForeignBusinessLine5Renderer:
    """English text for ForeignBusinessLine5."""

    line_class = ForeignBusinessLine5

    def render(self, line: ForeignBusinessLine5) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: sheet {line.position}: line 5 = {money(line.income)} net "
            f"foreign business income x {money(line.basic_federal_tax)} basic federal tax / "
            f"{money(line.net_income)} net income = {money(line.result)} "
            f"({EnglishFigures.rounding(line.rounding)})"
        )


@english_renderer
class ForeignBusinessLine7Renderer:
    """English text for ForeignBusinessLine7."""

    line_class = ForeignBusinessLine7

    def render(self, line: ForeignBusinessLine7) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: sheet {line.position}: line 7 = line 5 {money(line.line_5)} "
            f"+ line 6 {money(line.line_6)} = {money(line.result)}"
        )


@english_renderer
class ForeignBusinessLine8Renderer:
    """English text for ForeignBusinessLine8."""

    line_class = ForeignBusinessLine8

    def render(self, line: ForeignBusinessLine8) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: sheet {line.position}: line 8 = basic federal tax "
            f"{money(line.basic_federal_tax)} + line 6 {money(line.line_6)} = {money(line.result)}"
        )


@english_renderer
class ForeignBusinessLine10Renderer:
    """English text for ForeignBusinessLine10."""

    line_class = ForeignBusinessLine10

    def render(self, line: ForeignBusinessLine10) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: sheet {line.position}: line 10 = line 8 {money(line.line_8)} "
            f"- line 3 {money(line.line_3)} = {money(line.result)}"
        )


@english_renderer
class ForeignBusinessLine11Renderer:
    """English text for ForeignBusinessLine11."""

    line_class = ForeignBusinessLine11

    def render(self, line: ForeignBusinessLine11) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: sheet {line.position}: line 11 = least of line 4 "
            f"{money(line.line_4)}, line 7 {money(line.line_7)}, line 10 {money(line.line_10)} "
            f"= {money(line.result)}"
        )
