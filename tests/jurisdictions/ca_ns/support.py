"""The Nova Scotia package list and the registries built over it.

Nova Scotia is listed in `tax_engine.registrations.JURISDICTIONS`, and a test of the registered
engine takes the registries of `tax_engine.registrations`. The tests written before the listing
build their own package list (core, federal, Nova Scotia) here and take their kinds and
capabilities from it. Each registry is built once per test process; never register into one.
"""

from functools import cache

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_ns
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.unit import UnitRegistry


@cache
def nova_scotia_packages() -> JurisdictionPackages:
    """The packages a Nova Scotia return needs: core, federal and ca-ns."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_ns,
        )
    )


@cache
def nova_scotia_kinds() -> ArtifactRegistry:
    """The artifact kinds of the Nova Scotia package list; never register into it."""
    kinds = ArtifactRegistry()
    nova_scotia_packages().register(kinds)
    return kinds


@cache
def nova_scotia_units() -> UnitRegistry:
    """The units of the Nova Scotia package list; never register into it."""
    registry = UnitRegistry()
    nova_scotia_packages().register_units(registry)
    return registry


@cache
def nova_scotia_capabilities() -> CapabilityRegistry:
    """The capabilities of the Nova Scotia package list; never register into it."""
    registry = CapabilityRegistry()
    nova_scotia_packages().register_capabilities(registry)
    return registry


@cache
def nova_scotia_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the Nova Scotia list; never register into it."""
    registry = ParameterParserRegistry()
    nova_scotia_packages().register_parameter_parsers(registry)
    return registry
