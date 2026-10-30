"""DispositionGainsOnly: the gain of one property type, rows added, a row's loss counting 0.

For Schedule 3 (form 5000-S3) Part 3, Personal-use property: "Line 9 and line 15800: Total gain
only (add all the amounts under column 5)". Each row's column 5 is its proceeds less its adjusted
cost base and its outlays; a row with a loss counts 0, so it does not decrease the gains of the
other rows (Guide T4037: "you cannot use the loss to decrease capital gains on other personal-use
property"). See `DispositionRows` for the slots and the trace.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.capability import capability
from tax_engine.domain.trace import TraceLine
from tax_engine.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_engine.jurisdictions.ca.trace import DispositionGainOnlyLine


@capability(identifier="disposition_gains_only")
class DispositionGainsOnly(DispositionRows):
    """Produces `output`: the total of the consumed `dispositions`' gains, a loss counting 0."""

    def _row(
        self, position: int, proceeds: Decimal, cost_base: Decimal, outlays: Decimal
    ) -> tuple[TraceLine, Decimal]:
        gain = proceeds - cost_base - outlays
        counted = max(Decimal(0), gain)
        line = DispositionGainOnlyLine(
            self._output, position, proceeds, cost_base, outlays, gain, counted
        )
        return line, counted
