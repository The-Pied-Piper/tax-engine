"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.apprenticeship`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.apprenticeship import ApprenticeWagesLine


@english_renderer
class ApprenticeWagesRenderer:
    """English text for ApprenticeWagesLine."""

    line_class = ApprenticeWagesLine

    def render(self, line: ApprenticeWagesLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        salary_and_wages = line.salary_and_wages
        maximum = line.maximum
        rule = line.rounding
        result = line.result
        return (
            f"{output.label}: apprentice {position}: the lesser of eligible salary and wages "
            f"{EnglishFigures.money(salary_and_wages)} and the maximum "
            f"{EnglishFigures.money(maximum.value)} is {EnglishFigures.money(result)} "
            f"({EnglishFigures.rounding(rule)})"
        )
