"""The New Brunswick package list and the registries built over it.

New Brunswick is listed in `tax_engine.registrations.JURISDICTIONS`, and a test of the registered
engine takes the `take_home_service` fixture of `conftest.py` or the registries of
`tax_engine.registrations`. The tests written before the listing build their own package list
(core, federal, New Brunswick) here and take their kinds and capabilities from it. Each registry is
built once per test process; never register into one.
"""

from functools import cache

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nb
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.unit import UnitRegistry


@cache
def new_brunswick_packages() -> JurisdictionPackages:
    """The packages a New Brunswick return needs: core, federal and New Brunswick."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_nb,
        )
    )


@cache
def new_brunswick_kinds() -> ArtifactRegistry:
    """The artifact kinds of the New Brunswick package list; never register into it."""
    kinds = ArtifactRegistry()
    new_brunswick_packages().register(kinds)
    return kinds


@cache
def new_brunswick_units() -> UnitRegistry:
    """The units of the New Brunswick package list; never register into it."""
    registry = UnitRegistry()
    new_brunswick_packages().register_units(registry)
    return registry


@cache
def new_brunswick_capabilities() -> CapabilityRegistry:
    """The capabilities of the New Brunswick package list; never register into it."""
    registry = CapabilityRegistry()
    new_brunswick_packages().register_capabilities(registry)
    return registry


@cache
def new_brunswick_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the New Brunswick package list; never register into it."""
    registry = ParameterParserRegistry()
    new_brunswick_packages().register_parameter_parsers(registry)
    return registry
