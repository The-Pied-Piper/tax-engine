"""Unit tests for the total of net foreign non-business income, Form T691 Part 4 line 2.

Identifier `ca/foreign_net_non_business_income_total`. The shared cases are in
`ForeignTaxCountriesTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.jurisdictions.ca.capabilities.foreign_net_non_business_income_total import (
    ForeignNetNonBusinessIncomeTotal,
)
from tax_calculator.jurisdictions.ca.catalog import NET_FOREIGN_NON_BUSINESS_INCOME
from tests.jurisdictions.ca.capabilities.foreign_tax_countries_totals import (
    ForeignTaxCountriesTotalCases,
)


class TestForeignNetNonBusinessIncomeTotal(ForeignTaxCountriesTotalCases):
    CAPABILITY: Any = ForeignNetNonBusinessIncomeTotal
    IDENTIFIER = "ca/foreign_net_non_business_income_total"
    MODULE = "foreign_net_non_business_income_total"
    FIELD = NET_FOREIGN_NON_BUSINESS_INCOME
