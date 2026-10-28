"""The made-up package's artifact catalog. Importing it registers nothing: tests register it
explicitly, into a private registry, through `JurisdictionPackages.register`."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.artifact import ArtifactCatalog
from tax_calculator.domain.registry import Namespace
from tests.jurisdictions.registration_fixtures.ex_on import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

LEVY_BASE = CATALOG.declare("levy_base", Decimal)
"""The amount the made-up levy applies to."""

LEVY = CATALOG.declare("levy", Decimal)
"""The made-up levy."""
