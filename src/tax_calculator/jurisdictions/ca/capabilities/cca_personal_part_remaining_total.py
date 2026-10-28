"""Form T776 Area A Note 9: the total of the remaining personal part entered in the rows."""

from __future__ import annotations

from typing import ClassVar

from tax_calculator.domain.artifact import Money
from tax_calculator.domain.capability import capability
from tax_calculator.jurisdictions.ca.capabilities.cca_entries_total import CcaEntriesTotal
from tax_calculator.jurisdictions.ca.catalog import CCA_PERSONAL_PART_REMAINING


@capability(identifier="cca_personal_part_remaining_total")
class CcaPersonalPartRemainingTotal(CcaEntriesTotal):
    """Produces `output`: the remaining personal part (Note 9) added over the rows of the CCA
    table."""

    FIELDS: ClassVar[tuple[Money, ...]] = (CCA_PERSONAL_PART_REMAINING,)
