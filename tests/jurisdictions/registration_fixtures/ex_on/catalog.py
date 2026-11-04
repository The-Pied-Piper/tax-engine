"""The made-up package's artifact catalog. Importing it registers nothing: tests register it
explicitly, into a private registry, through `JurisdictionPackages.register`."""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.registration_fixtures.ex_on import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

LEVY_BASE = AmountKind.declare(CATALOG, "levy_base")
"""The amount the made-up levy applies to."""

LEVY = AmountKind.declare(CATALOG, "levy")
"""The made-up levy."""
