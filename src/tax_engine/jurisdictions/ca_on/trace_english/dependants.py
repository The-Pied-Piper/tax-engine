"""English text for the trace lines of `tax_engine.jurisdictions.ca_on.trace.dependants`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.figures import EnglishFigures
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca_on.trace.dependants import CaregiverClaimLessClaimedLine


@english_renderer
class CaregiverClaimLessClaimedRenderer:
    """English text for CaregiverClaimLessClaimedLine."""

    line_class = CaregiverClaimLessClaimedLine

    def render(self, line: CaregiverClaimLessClaimedLine) -> str:
        """The English sentence for `line`."""
        output = line.output
        position = line.position
        base = line.base
        net_income = line.net_income
        maximum = line.maximum
        allowable = line.allowable_before_claimed
        claimed = line.claimed
        rule = line.rounding
        result = line.result
        return (
            f"{output.label}: dependant {position}: {EnglishFigures.money(base.value)} less net "
            f"income {EnglishFigures.money(net_income)}, at most "
            f"{EnglishFigures.money(maximum.value)} = "
            f"{EnglishFigures.money(allowable)}, less claimed {EnglishFigures.money(claimed)} = "
            f"{EnglishFigures.money(result)} ({EnglishFigures.rounding(rule)})"
        )
