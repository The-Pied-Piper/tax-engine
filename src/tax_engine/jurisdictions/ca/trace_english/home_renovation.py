"""English text for the trace lines of `tax_engine.jurisdictions.ca.trace.home_renovation`:
one renderer
class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca.trace.home_renovation import (
    RenovationLine3,
    RenovationLine6,
    RenovationLine7,
)


@english_renderer
class RenovationLine3Renderer:
    """English text for RenovationLine3."""

    line_class = RenovationLine3

    def render(self, line: RenovationLine3) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: renovation {line.position}: expenditures "
            f"{money(line.expenditures)} less reimbursed {money(line.reimbursed)}, at most "
            f"{money(line.maximum.value)} = {money(line.result)}"
        )


@english_renderer
class RenovationLine6Renderer:
    """English text for RenovationLine6."""

    line_class = RenovationLine6

    def render(self, line: RenovationLine6) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: renovation {line.position}: maximum "
            f"{money(line.maximum.value)} less claimed by others "
            f"{money(line.claimed_by_others)} = {money(line.result)}"
        )


@english_renderer
class RenovationLine7Renderer:
    """English text for RenovationLine7."""

    line_class = RenovationLine7

    def render(self, line: RenovationLine7) -> str:
        """The English sentence for `line`."""
        money = EnglishFigures.money
        return (
            f"{line.output.label}: renovation {line.position}: lesser of line 3 "
            f"{money(line.line_3)} and line 6 {money(line.line_6)} = {money(line.result)}"
        )
