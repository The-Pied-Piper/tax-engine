"""Form T776 Area A column 2: the total of the opening UCC entered in the rows of the CCA table."""

from __future__ import annotations

from typing import ClassVar

from tax_engine.domain.artifact import Money
from tax_engine.domain.capability import capability
from tax_engine.jurisdictions.ca.capabilities.cca_entries_total import CcaEntriesTotal
from tax_engine.jurisdictions.ca.catalog import CCA_UCC_AT_START


@capability(identifier="cca_opening_ucc_total")
class CcaOpeningUccTotal(CcaEntriesTotal):
    """Produces `output`: the opening UCC (column 2) added over the rows of the CCA table."""

    FIELDS: ClassVar[tuple[Money, ...]] = (CCA_UCC_AT_START,)
