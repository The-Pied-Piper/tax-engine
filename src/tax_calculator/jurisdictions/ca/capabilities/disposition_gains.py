"""DispositionGains: the gain or loss of one property type, rows added, losses offsetting gains.

For Schedule 3 (form 5000-S3) Part 3: "For each Gain or loss enter as many lines as necessary."
Each row's "(Column 5): Gain or loss (column 2 minus columns 3 and 4)" is its proceeds less its
adjusted cost base and its outlays, signed, and the line is "Total gain or loss (add all the
amounts under column 5)": the rows added, so a loss offsets the gains of the other rows. One
wiring serves each property type, a record list of the rows in and the line out. See
`DispositionRows` for the slots and the trace.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.capability import capability
from tax_calculator.domain.trace import TraceLine
from tax_calculator.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_calculator.jurisdictions.ca.trace import DispositionGainLine


@capability(identifier="disposition_gains")
class DispositionGains(DispositionRows):
    """Produces `output`: the total of the consumed `dispositions`' column 5, losses included."""

    def _row(
        self, position: int, proceeds: Decimal, cost_base: Decimal, outlays: Decimal
    ) -> tuple[TraceLine, Decimal]:
        gain = proceeds - cost_base - outlays
        return DispositionGainLine(self._output, position, proceeds, cost_base, outlays, gain), gain
