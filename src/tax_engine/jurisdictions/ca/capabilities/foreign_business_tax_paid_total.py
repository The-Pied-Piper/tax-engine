"""Form T691 Part 4 line 8: the total of the business tax paid for the year over the countries."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.capability import capability
from tax_engine.jurisdictions.ca.capabilities.foreign_tax_countries_total import (
    ForeignTaxCountriesTotal,
)
from tax_engine.jurisdictions.ca.catalog import FOREIGN_BUSINESS_TAX_PAID


@capability(identifier="foreign_business_tax_paid_total")
class ForeignBusinessTaxPaidTotal(ForeignTaxCountriesTotal):
    """Produces `output`: the sum of the business tax paid for the year over the foreign countries.

    The unused foreign tax credits of Form T2209 line 4 are another figure of each record and are
    not summed.
    """

    FIELD: ClassVar[ArtifactKind[Any]] = FOREIGN_BUSINESS_TAX_PAID
