"""Unit tests for the total of business tax paid to foreign countries, Form T691 Part 4 line 8.

Identifier `ca/foreign_business_tax_paid_total`. The shared cases are in
`ForeignTaxCountriesTotalCases`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_paid_total import (
    ForeignBusinessTaxPaidTotal,
)
from tax_engine.jurisdictions.ca.catalog import (
    FOREIGN_BUSINESS_TAX_PAID,
    FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
)
from tests.jurisdictions.ca.capabilities.foreign_tax_countries_totals import (
    ForeignTaxCountriesTotalCases,
    country,
    total,
)

D = Decimal


class TestForeignBusinessTaxPaidTotal(ForeignTaxCountriesTotalCases):
    CAPABILITY: Any = ForeignBusinessTaxPaidTotal
    IDENTIFIER = "ca/foreign_business_tax_paid_total"
    MODULE = "foreign_business_tax_paid_total"
    FIELD = FOREIGN_BUSINESS_TAX_PAID

    def test_totals_the_year_tax_and_not_the_unused_credits(self) -> None:
        # Note (5) is the business tax for the year; the unused credits of note (6) are a
        # separate figure of the record and are not part of Form T691 line 8.
        row = {
            **self.own("3600"),
            FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: D("5000"),
        }

        assert total(self.CAPABILITY, row) == D("3600")

    def test_the_unused_credits_alone_total_zero(self) -> None:
        assert total(self.CAPABILITY, country(FOREIGN_BUSINESS_UNUSED_TAX_CREDITS, "5000")) == D(
            "0"
        )
