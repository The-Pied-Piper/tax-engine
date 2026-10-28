"""English text for the trace lines of `tax_calculator.jurisdictions.ca_on.trace.capped_records`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english.figures import EnglishFigures
from tax_calculator.adapters.inbound.trace_english.registry import english_renderer
from tax_calculator.jurisdictions.ca_on.trace.capped_records import CappedRecordLine


@english_renderer
class CappedRecordRenderer:
    """English text for CappedRecordLine."""

    line_class = CappedRecordLine

    def render(self, line: CappedRecordLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        expenditure = line.expenditure
        cap = line.cap
        rule = line.rounding
        result = line.result
        return (
            f"{output.label}: item {position}: {EnglishFigures.money(expenditure)}, at most "
            f"{EnglishFigures.money(cap.value)} = {EnglishFigures.money(result)} "
            f"({EnglishFigures.rounding(rule)})"
        )
