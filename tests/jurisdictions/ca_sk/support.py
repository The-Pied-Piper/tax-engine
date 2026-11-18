"""The Saskatchewan package list and the registries built over it.

Saskatchewan is not yet listed in `tax_engine.registrations.JURISDICTIONS`, so the tests build their
own package list (core, federal, Saskatchewan) here and take their kinds and capabilities from it.
Each registry is built once per test process; never register into one.
"""

from functools import cache

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_sk
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.unit import UnitRegistry


@cache
def saskatchewan_packages() -> JurisdictionPackages:
    """The packages a Saskatchewan return needs: core, federal and Saskatchewan."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_sk,
        )
    )


@cache
def saskatchewan_kinds() -> ArtifactRegistry:
    """The artifact kinds of the Saskatchewan package list; never register into it."""
    kinds = ArtifactRegistry()
    saskatchewan_packages().register(kinds)
    return kinds


@cache
def saskatchewan_units() -> UnitRegistry:
    """The units of the Saskatchewan package list; never register into it."""
    registry = UnitRegistry()
    saskatchewan_packages().register_units(registry)
    return registry


@cache
def saskatchewan_capabilities() -> CapabilityRegistry:
    """The capabilities of the Saskatchewan package list; never register into it."""
    registry = CapabilityRegistry()
    saskatchewan_packages().register_capabilities(registry)
    return registry


@cache
def saskatchewan_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the Saskatchewan package list; never register into it."""
    registry = ParameterParserRegistry()
    saskatchewan_packages().register_parameter_parsers(registry)
    return registry
