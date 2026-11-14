"""The British Columbia package list and the registries built over it, for the BC tests.

British Columbia is not in `tax_engine.registrations.JURISDICTIONS` until the end-to-end ticket
lists it, because a partial manifest would fail the startup check. Until then the British Columbia
tests build their own package list (core, federal, British Columbia) and take their kinds, units,
capabilities and parameter parsers from it, as `tests/kinds.py` and `tests/capabilities.py` do for
the bundled list. Each registry is built once per test process; never register into one.
"""

from __future__ import annotations

from functools import cache

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.unit import UnitRegistry


@cache
def british_columbia_packages() -> JurisdictionPackages:
    """The packages a British Columbia return needs: core, federal and British Columbia."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_bc,
        )
    )


@cache
def british_columbia_kinds() -> ArtifactRegistry:
    """The artifact kinds of the British Columbia package list; never register into it."""
    kinds = ArtifactRegistry()
    british_columbia_packages().register(kinds)
    return kinds


@cache
def british_columbia_units() -> UnitRegistry:
    """The units of the British Columbia package list; never register into it."""
    registry = UnitRegistry()
    british_columbia_packages().register_units(registry)
    return registry


@cache
def british_columbia_capabilities() -> CapabilityRegistry:
    """The capabilities of the British Columbia package list; never register into it."""
    registry = CapabilityRegistry()
    british_columbia_packages().register_capabilities(registry)
    return registry


@cache
def british_columbia_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the British Columbia package list; never register into it."""
    registry = ParameterParserRegistry()
    british_columbia_packages().register_parameter_parsers(registry)
    return registry
