"""Unit tests for the total of the remaining personal part over the CCA table rows, T776 Area A.

Identifier `ca/cca_personal_part_remaining_total`. The shared cases are in `CcaEntriesTotalCases`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.trace import RecordTotalLine
from tax_calculator.jurisdictions.ca.capabilities.cca_personal_part_remaining_total import (
    CcaPersonalPartRemainingTotal,
)
from tax_calculator.jurisdictions.ca.catalog import CCA_PERSONAL_PART_REMAINING
from tests.jurisdictions.ca.capabilities.cca_entries_totals import (
    TOTAL,
    CcaEntriesTotalCases,
    classes,
    row,
    total,
    wired,
)

D = Decimal


class TestCcaPersonalPartRemainingTotal(CcaEntriesTotalCases):
    CAPABILITY = CcaPersonalPartRemainingTotal
    IDENTIFIER = "ca/cca_personal_part_remaining_total"
    MODULE = "cca_personal_part_remaining_total"
    COLUMNS_TOTALLED = ("personal",)

    def test_the_remaining_personal_part_is_added_over_the_rows(self) -> None:
        assert total(self.CAPABILITY, row(personal="3"), row(personal="4")) == D("7")

    def test_the_remaining_personal_part_records_a_record_total_line(self) -> None:
        result = wired(self.CAPABILITY).compute((classes(row(ucc="1"), row(personal="4")),))

        assert result.trace == (
            RecordTotalLine(TOTAL, CCA_PERSONAL_PART_REMAINING, (D("0"), D("4")), D("4")),
        )
