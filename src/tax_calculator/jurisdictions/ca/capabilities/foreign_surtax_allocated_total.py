"""Form T2209 line 6: the total of the surtax allocated to the countries, over the countries."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.capability import capability
from tax_calculator.jurisdictions.ca.capabilities.foreign_tax_countries_total import (
    ForeignTaxCountriesTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FOREIGN_SURTAX_OUTSIDE_CANADA


@capability(identifier="foreign_surtax_allocated_total")
class ForeignSurtaxAllocatedTotal(ForeignTaxCountriesTotal):
    """Produces `output`: the sum of the surtax allocated to each foreign tax country.

    Form T2209 line 6 is one surtax, T1 line 127, "Enter the amount that applies to the country or
    countries you identified at the top of this page": the parts are the filer's, and their total
    is checked against line 127 by the step that reads this output.
    """

    FIELD: ClassVar[ArtifactKind[Any]] = FOREIGN_SURTAX_OUTSIDE_CANADA
