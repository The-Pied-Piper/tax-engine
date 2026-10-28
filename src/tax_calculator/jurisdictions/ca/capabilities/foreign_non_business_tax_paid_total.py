"""Form T691 Part 4 line 7: the total of the non-business tax paid over the countries."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.capability import capability
from tax_calculator.jurisdictions.ca.capabilities.foreign_tax_countries_total import (
    ForeignTaxCountriesTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FOREIGN_NON_BUSINESS_TAX_PAID


@capability(identifier="foreign_non_business_tax_paid_total")
class ForeignNonBusinessTaxPaidTotal(ForeignTaxCountriesTotal):
    """Produces `output`: the sum of the non-business tax paid over the foreign tax countries."""

    FIELD: ClassVar[ArtifactKind[Any]] = FOREIGN_NON_BUSINESS_TAX_PAID
