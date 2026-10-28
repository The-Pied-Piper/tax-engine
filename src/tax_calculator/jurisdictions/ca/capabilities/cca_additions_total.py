"""Form T776 Area A columns 3, 4, 11 and 12: the total of the additions entered in the rows."""

from __future__ import annotations

from decimal import Decimal
from typing import ClassVar

from tax_calculator.domain.artifact import Money
from tax_calculator.domain.capability import capability
from tax_calculator.domain.trace import ItemsTotalLine, TraceLine
from tax_calculator.jurisdictions.ca.capabilities.cca_entries_total import CcaEntriesTotal
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_DIEP_ADDITIONS,
    CCA_RIIP_ADDITIONS,
)


@capability(identifier="cca_additions_total")
class CcaAdditionsTotal(CcaEntriesTotal):
    """Produces `output`: the additions of each row of the CCA table (column 3 and its parts in
    columns 4, 11 and 12, added), added over the rows.

    The trace is one `ItemsTotalLine`: each row's additions by its position from 1, then the total.
    """

    FIELDS: ClassVar[tuple[Money, ...]] = (
        CCA_ADDITIONS,
        CCA_DIEP_ADDITIONS,
        CCA_AIIP_ADDITIONS,
        CCA_RIIP_ADDITIONS,
    )

    def _line(self, amounts: tuple[Decimal, ...], total: Decimal) -> TraceLine:
        return ItemsTotalLine(self._output, tuple(enumerate(amounts, start=1)), total)
