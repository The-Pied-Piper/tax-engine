"""English text for the trace lines of `tax_calculator.jurisdictions.ca_on.trace.placement_credit`:
one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english.figures import EnglishFigures
from tax_calculator.adapters.inbound.trace_english.registry import english_renderer
from tax_calculator.jurisdictions.ca_on.trace.placement_credit import PlacementCreditLine


@english_renderer
class PlacementCreditRenderer:
    """English text for PlacementCreditLine."""

    line_class = PlacementCreditLine

    def render(self, line: PlacementCreditLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        field = line.field
        expenditure = line.expenditure
        line_1 = line.line_1
        line_3 = line.line_3
        line_12 = line.line_12
        line_13 = line.line_13
        rule = line.rounding
        return (
            f"{output.label}: item {position} {field.label} {EnglishFigures.money(expenditure)}: "
            f"line 1 {EnglishFigures.money(line_1)}, line 3 {EnglishFigures.money(line_3)}, "
            f"line 12 {EnglishFigures.money(line_12)}, line 13 {EnglishFigures.money(line_13)} "
            f"({EnglishFigures.rounding(rule)})"
        )
