"""The Newfoundland and Labrador package list and the registries built over it.

Newfoundland and Labrador is not in `tax_engine.registrations.JURISDICTIONS` yet, so the tests
build their own package list (core, federal, Newfoundland and Labrador) here and take their kinds
and capabilities from it. Each registry is built once per test process; never register into one.
"""

from functools import cache

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.unit import UnitRegistry


@cache
def newfoundland_packages() -> JurisdictionPackages:
    """The packages a return needs: core, federal and Newfoundland and Labrador."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_nl,
        )
    )


@cache
def newfoundland_kinds() -> ArtifactRegistry:
    """The artifact kinds of the Newfoundland and Labrador package list; never register into it."""
    kinds = ArtifactRegistry()
    newfoundland_packages().register(kinds)
    return kinds


@cache
def newfoundland_units() -> UnitRegistry:
    """The units of the Newfoundland and Labrador package list; never register into it."""
    registry = UnitRegistry()
    newfoundland_packages().register_units(registry)
    return registry


@cache
def newfoundland_capabilities() -> CapabilityRegistry:
    """The capabilities of the Newfoundland and Labrador package list; never register into it."""
    registry = CapabilityRegistry()
    newfoundland_packages().register_capabilities(registry)
    return registry


@cache
def newfoundland_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the package list; never register into it."""
    registry = ParameterParserRegistry()
    newfoundland_packages().register_parameter_parsers(registry)
    return registry
