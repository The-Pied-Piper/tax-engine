"""Unit tests for the total of the opening UCC over the rows of the CCA table, T776 Area A.

Identifier `ca/cca_opening_ucc_total`. The shared cases are in `CcaEntriesTotalCases`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.trace import RecordTotalLine
from tax_engine.jurisdictions.ca.capabilities.cca_opening_ucc_total import CcaOpeningUccTotal
from tax_engine.jurisdictions.ca.catalog import CCA_UCC_AT_START
from tests.jurisdictions.ca.capabilities.cca_entries_totals import (
    TOTAL,
    CcaEntriesTotalCases,
    classes,
    row,
    total,
    wired,
)

D = Decimal


class TestCcaOpeningUccTotal(CcaEntriesTotalCases):
    CAPABILITY = CcaOpeningUccTotal
    IDENTIFIER = "ca/cca_opening_ucc_total"
    MODULE = "cca_opening_ucc_total"
    COLUMNS_TOTALLED = ("ucc",)

    def test_the_opening_ucc_is_added_over_the_rows(self) -> None:
        assert total(self.CAPABILITY, row(ucc="100.25"), row(ucc="0.50")) == D("100.75")

    def test_the_opening_ucc_records_a_record_total_line(self) -> None:
        result = wired(self.CAPABILITY).compute((classes(row(ucc="1"), row(personal="4")),))

        assert result.trace == (RecordTotalLine(TOTAL, CCA_UCC_AT_START, (D("1"), D("0")), D("1")),)
