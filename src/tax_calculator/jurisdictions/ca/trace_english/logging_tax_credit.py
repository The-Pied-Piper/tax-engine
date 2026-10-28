"""English text for the trace lines of `tax_calculator.jurisdictions.ca.trace.logging_tax_credit`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english.figures import EnglishFigures
from tax_calculator.adapters.inbound.trace_english.registry import english_renderer
from tax_calculator.jurisdictions.ca.trace.logging_tax_credit import LoggingTaxCreditLine


@english_renderer
class LoggingTaxCreditRenderer:
    """English text for LoggingTaxCreditLine."""

    line_class = LoggingTaxCreditLine

    def render(self, line: LoggingTaxCreditLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        tax_paid = line.tax_paid
        tax_rate = line.tax_rate
        tax_share = line.tax_share
        net_income = line.net_logging_income
        income_rate = line.income_rate
        income_share = line.income_share
        result = line.result
        return (
            f"{output.label}: province {position}: "
            f"{EnglishFigures.percent(tax_rate.value)}% of logging tax paid "
            f"{EnglishFigures.money(tax_paid)} = {EnglishFigures.money(tax_share)} "
            f"({EnglishFigures.rounding(line.tax_rounding)}); "
            f"{EnglishFigures.percent(income_rate.value)}% of net logging income "
            f"{EnglishFigures.money(net_income)} = {EnglishFigures.money(income_share)} "
            f"({EnglishFigures.rounding(line.income_rounding)}); "
            f"lesser {EnglishFigures.money(result)}"
        )
