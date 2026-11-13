"""The packages the composition root wires together, listed explicitly.

Adding a jurisdiction is importing its package and listing it in `JURISDICTIONS`; see
docs/jurisdiction-packages.md.
"""

import tax_engine.adapters.inbound.trace_english
import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.ca_on
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.unit import UnitRegistry

CORE_PACKAGES = (tax_engine.adapters.inbound.trace_english,)

JURISDICTIONS = JurisdictionPackages(
    (
        tax_engine.jurisdictions.core,
        tax_engine.jurisdictions.ca,
        tax_engine.jurisdictions.ca_on,
        tax_engine.jurisdictions.ca_ab,
    )
)


def artifact_kinds() -> ArtifactRegistry:
    """A new registry of the artifact kinds of every package in `JURISDICTIONS`.

    Nothing is shared: each call builds its own, to be handed on by whoever wires the application.
    """
    kinds = ArtifactRegistry()
    JURISDICTIONS.register(kinds)
    return kinds


def units() -> UnitRegistry:
    """A new registry of the units of every package in `JURISDICTIONS`.

    Nothing is shared: each call builds its own, to be handed on by whoever wires the application.
    """
    registry = UnitRegistry()
    JURISDICTIONS.register_units(registry)
    return registry


def capabilities() -> CapabilityRegistry:
    """A new registry of the capabilities of every package in `JURISDICTIONS`, core included.

    Nothing is shared: each call builds its own, to be handed on by whoever wires the application.
    """
    registry = CapabilityRegistry()
    JURISDICTIONS.register_capabilities(registry)
    return registry


def parameter_parsers() -> ParameterParserRegistry:
    """A new registry of the parameter parsers of every package in `JURISDICTIONS`.

    Nothing is shared: each call builds its own, to be handed on by whoever wires the application.
    """
    registry = ParameterParserRegistry()
    JURISDICTIONS.register_parameter_parsers(registry)
    return registry
