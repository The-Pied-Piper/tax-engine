"""The Prince Edward Island package list and the registries built over it.

Prince Edward Island's line tests build their own package list (core, federal, Prince Edward
Island) here and take their kinds and capabilities from it; the full return is tested over the
registered list (`tax_engine.registrations.JURISDICTIONS`). Each registry is built once per test
process; never register into one.
"""

from functools import cache

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_pe
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.unit import UnitRegistry


@cache
def prince_edward_island_packages() -> JurisdictionPackages:
    """The packages a Prince Edward Island return needs: core, federal and Prince Edward Island."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_pe,
        )
    )


@cache
def prince_edward_island_kinds() -> ArtifactRegistry:
    """The artifact kinds of the Prince Edward Island package list; never register into it."""
    kinds = ArtifactRegistry()
    prince_edward_island_packages().register(kinds)
    return kinds


@cache
def prince_edward_island_units() -> UnitRegistry:
    """The units of the Prince Edward Island package list; never register into it."""
    registry = UnitRegistry()
    prince_edward_island_packages().register_units(registry)
    return registry


@cache
def prince_edward_island_capabilities() -> CapabilityRegistry:
    """The capabilities of the Prince Edward Island package list; never register into it."""
    registry = CapabilityRegistry()
    prince_edward_island_packages().register_capabilities(registry)
    return registry


@cache
def prince_edward_island_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the Prince Edward Island package list; never register into it."""
    registry = ParameterParserRegistry()
    prince_edward_island_packages().register_parameter_parsers(registry)
    return registry
