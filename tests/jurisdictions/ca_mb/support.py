"""The Manitoba package list and the registries built over it.

Manitoba is not yet in `tax_engine.registrations.JURISDICTIONS`, so a test of the Manitoba package
builds its own package list (core, federal, Manitoba) here and takes its kinds and capabilities
from it. Each registry is built once per test process; never register into one.
"""

from functools import cache

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.unit import UnitRegistry


@cache
def manitoba_packages() -> JurisdictionPackages:
    """The packages a Manitoba return needs: core, federal and Manitoba."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_mb,
        )
    )


@cache
def manitoba_kinds() -> ArtifactRegistry:
    """The artifact kinds of the Manitoba package list; never register into it."""
    kinds = ArtifactRegistry()
    manitoba_packages().register(kinds)
    return kinds


@cache
def manitoba_capabilities() -> CapabilityRegistry:
    """The capabilities of the Manitoba package list; never register into it."""
    registry = CapabilityRegistry()
    manitoba_packages().register_capabilities(registry)
    return registry


def manitoba_units() -> UnitRegistry:
    """The units of the Manitoba package list; never register into it."""
    registry = UnitRegistry()
    manitoba_packages().register_units(registry)
    return registry
