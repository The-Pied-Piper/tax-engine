"""English text for the trace lines of `tax_calculator.jurisdictions.ca.trace.farm_chart`: one renderer class
per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english.figures import EnglishFigures
from tax_calculator.adapters.inbound.trace_english.registry import english_renderer
from tax_calculator.jurisdictions.ca.trace.farm_chart import PercentageOfLine


@english_renderer
class PercentageOfRenderer:
    """English text for PercentageOfLine."""

    line_class = PercentageOfLine

    def render(self, line: PercentageOfLine) -> str:
        """The English sentence for `line`."""
        zero = " (zero divisor, so 0)" if line.divisor_amount == 0 else ""
        return (
            f"{line.output.label}: {line.dividend.label} "
            f"{EnglishFigures.money(line.dividend_amount)} divided by {line.divisor.label} "
            f"{EnglishFigures.money(line.divisor_amount)}, times 100 "
            f"({EnglishFigures.rounding(line.rounding)}){zero} = "
            f"{EnglishFigures.money(line.result)}%"
        )
