"""Unit tests for the total of the additions over the rows of the CCA table, T776 Area A.

Identifier `ca/cca_additions_total`. The shared cases are in `CcaEntriesTotalCases`.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.cca_additions_total import CcaAdditionsTotal
from tests.jurisdictions.ca.capabilities.cca_entries_totals import (
    TOTAL,
    CcaEntriesTotalCases,
    classes,
    row,
    total,
    wired,
)

D = Decimal


class TestCcaAdditionsTotal(CcaEntriesTotalCases):
    CAPABILITY = CcaAdditionsTotal
    IDENTIFIER = "ca/cca_additions_total"
    MODULE = "cca_additions_total"
    COLUMNS_TOTALLED = ("additions", "diep", "aiip", "riip")

    def test_the_additions_are_columns_3_4_11_and_12_added_over_the_rows(self) -> None:
        rows = (row(additions="10"), row(diep="1"), row(aiip="0.10"), row(riip="0.01"))

        assert total(self.CAPABILITY, *rows) == D("11.11")

    def test_the_additions_record_an_items_total_line(self) -> None:
        result = wired(self.CAPABILITY).compute((classes(row(additions="2", diep="3"), row()),))

        assert result.trace == (ItemsTotalLine(TOTAL, ((1, D("5")), (2, D("0"))), D("5")),)
