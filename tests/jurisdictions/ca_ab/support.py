"""The Alberta package list and the registries built over it, for the Alberta tests.

Alberta is not in `tax_engine.registrations.JURISDICTIONS` until the end-to-end ticket lists
it, because a partial Alberta manifest would fail the startup check. Until then the Alberta tests
build their own package list (core, federal, Alberta) and take their kinds, units, capabilities and
parameter parsers from it, as `tests/kinds.py` and `tests/capabilities.py` do for the bundled list.
Each registry is built once per test process; never register into one.
"""

from __future__ import annotations

from functools import cache

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.unit import UnitRegistry


@cache
def alberta_packages() -> JurisdictionPackages:
    """The packages an Alberta return needs: core, the federal package and Alberta."""
    return JurisdictionPackages(
        (
            tax_engine.jurisdictions.core,
            tax_engine.jurisdictions.ca,
            tax_engine.jurisdictions.ca_ab,
        )
    )


@cache
def alberta_kinds() -> ArtifactRegistry:
    """The artifact kinds of the Alberta package list; never register into it."""
    kinds = ArtifactRegistry()
    alberta_packages().register(kinds)
    return kinds


@cache
def alberta_units() -> UnitRegistry:
    """The units of the Alberta package list; never register into it."""
    registry = UnitRegistry()
    alberta_packages().register_units(registry)
    return registry


@cache
def alberta_capabilities() -> CapabilityRegistry:
    """The capabilities of the Alberta package list; never register into it."""
    registry = CapabilityRegistry()
    alberta_packages().register_capabilities(registry)
    return registry


@cache
def alberta_parameter_parsers() -> ParameterParserRegistry:
    """The parameter parsers of the Alberta package list; never register into it."""
    registry = ParameterParserRegistry()
    alberta_packages().register_parameter_parsers(registry)
    return registry
