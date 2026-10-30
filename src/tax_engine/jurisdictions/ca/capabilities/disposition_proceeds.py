"""DispositionProceeds: the proceeds of disposition of one property type, rows added.

For Schedule 3 (form 5000-S3) Part 3: each row's "(Column 2): Proceeds of disposition" and the
line "Total proceeds of disposition (add all the amounts under column 2)": the rows' proceeds
added. One wiring serves each property type, a record list of the rows in and the line out. The
proceeds are never negative, so the line is too. See `DispositionRows` for the slots and the
trace.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.capability import capability
from tax_engine.domain.trace import TraceLine
from tax_engine.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_engine.jurisdictions.ca.trace import DispositionProceedsLine


@capability(identifier="disposition_proceeds")
class DispositionProceeds(DispositionRows):
    """Produces `output`: the total of the consumed `dispositions`' column 2."""

    def _row(
        self, position: int, proceeds: Decimal, cost_base: Decimal, outlays: Decimal
    ) -> tuple[TraceLine, Decimal]:
        return DispositionProceedsLine(self._output, position, proceeds), proceeds
