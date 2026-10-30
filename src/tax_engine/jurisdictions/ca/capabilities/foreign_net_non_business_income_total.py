"""Form T691 Part 4 line 2: the total of the net foreign non-business income over the countries."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.capability import capability
from tax_engine.jurisdictions.ca.capabilities.foreign_tax_countries_total import (
    ForeignTaxCountriesTotal,
)
from tax_engine.jurisdictions.ca.catalog import NET_FOREIGN_NON_BUSINESS_INCOME


@capability(identifier="foreign_net_non_business_income_total")
class ForeignNetNonBusinessIncomeTotal(ForeignTaxCountriesTotal):
    """Produces `output`: the sum of the net foreign non-business income over the countries."""

    FIELD: ClassVar[ArtifactKind[Any]] = NET_FOREIGN_NON_BUSINESS_INCOME
