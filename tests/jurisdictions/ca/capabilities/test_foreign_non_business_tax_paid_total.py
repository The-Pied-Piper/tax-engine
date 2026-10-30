"""Unit tests for the total of non-business tax paid to foreign countries, Form T691 Part 4 line 7.

Identifier `ca/foreign_non_business_tax_paid_total`. The shared cases are in
`ForeignTaxCountriesTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_engine.jurisdictions.ca.capabilities.foreign_non_business_tax_paid_total import (
    ForeignNonBusinessTaxPaidTotal,
)
from tax_engine.jurisdictions.ca.catalog import FOREIGN_NON_BUSINESS_TAX_PAID
from tests.jurisdictions.ca.capabilities.foreign_tax_countries_totals import (
    ForeignTaxCountriesTotalCases,
)


class TestForeignNonBusinessTaxPaidTotal(ForeignTaxCountriesTotalCases):
    CAPABILITY: Any = ForeignNonBusinessTaxPaidTotal
    IDENTIFIER = "ca/foreign_non_business_tax_paid_total"
    MODULE = "foreign_non_business_tax_paid_total"
    FIELD = FOREIGN_NON_BUSINESS_TAX_PAID
