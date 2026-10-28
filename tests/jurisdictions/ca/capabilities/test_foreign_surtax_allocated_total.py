"""Unit tests for the total of the surtax allocated to the foreign countries, Form T2209 line 6.

Identifier `ca/foreign_surtax_allocated_total`. The shared cases are in
`ForeignTaxCountriesTotalCases`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_calculator.jurisdictions.ca.capabilities.foreign_surtax_allocated_total import (
    ForeignSurtaxAllocatedTotal,
)
from tax_calculator.jurisdictions.ca.catalog import (
    FOREIGN_BUSINESS_TAX_PAID,
    FOREIGN_SURTAX_OUTSIDE_CANADA,
)
from tests.jurisdictions.ca.capabilities.foreign_tax_countries_totals import (
    ForeignTaxCountriesTotalCases,
    country,
    total,
)

D = Decimal


class TestForeignSurtaxAllocatedTotal(ForeignTaxCountriesTotalCases):
    CAPABILITY: Any = ForeignSurtaxAllocatedTotal
    IDENTIFIER = "ca/foreign_surtax_allocated_total"
    MODULE = "foreign_surtax_allocated_total"
    FIELD = FOREIGN_SURTAX_OUTSIDE_CANADA

    def test_totals_the_surtax_and_not_the_business_tax(self) -> None:
        row = {**self.own("415.35"), FOREIGN_BUSINESS_TAX_PAID: D("3600")}

        assert total(self.CAPABILITY, row) == D("415.35")

    def test_the_parts_of_two_countries_are_added(self) -> None:
        rows = (self.own("300.10"), self.own("99.90"))

        assert total(self.CAPABILITY, *rows) == D("400.00")

    def test_the_business_tax_alone_totals_zero(self) -> None:
        assert total(self.CAPABILITY, country(FOREIGN_BUSINESS_TAX_PAID, "3600")) == D("0")
