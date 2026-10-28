"""RestrictedFarmLossApplied: the restricted farm loss applied on one list of farmland dispositions.

For Schedule 3 Part 3 and Guide T4037 p.34: each row of the consumed record list carries the
Guide's line C, the property taxes of the restricted farm loss added to the adjusted cost base, and
line D, the interest added to it. The output is the sum of both over every row, in the record
list's order: the amount the filer has applied, which reduces the restricted farm loss balance
("Also, you have to reduce your RFL balance by these amounts."). The part of the loss typed on a
row is not summed here; the total is checked against the unapplied balance by `core/at_most`. An
empty list totals 0. The sum is exact and never rounds, as there is no dataset. The trace is one
`FarmLossAppliedLine` per row, by position from 1, then one ItemsTotalLine.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.capability import capability
from tax_calculator.domain.record_list import Record
from tax_calculator.domain.trace import TraceLine
from tax_calculator.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_calculator.jurisdictions.ca.catalog import (
    DISPOSITION_FARM_LOSS_INTEREST,
    DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
)
from tax_calculator.jurisdictions.ca.trace import FarmLossAppliedLine


@capability(identifier="restricted_farm_loss_applied")
class RestrictedFarmLossApplied(DispositionRows):
    """Produces `output`: the sum of lines C and D of the restricted farm loss over the rows.

    The record list, the slots and the wiring are `DispositionRows`'; the columns 2 to 5 of a row
    are not read. Each row records its own `FarmLossAppliedLine`.
    """

    def _record_row(self, position: int, record: Record) -> tuple[TraceLine, Decimal]:
        property_taxes = Decimal(record[DISPOSITION_FARM_LOSS_PROPERTY_TAXES])
        interest = Decimal(record[DISPOSITION_FARM_LOSS_INTEREST])
        applied = property_taxes + interest
        line = FarmLossAppliedLine(self._output, position, property_taxes, interest, applied)
        return line, applied
