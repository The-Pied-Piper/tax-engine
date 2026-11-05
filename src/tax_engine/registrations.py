"""The packages the composition root wires together, listed explicitly.

`JURISDICTIONS` lists the packages: core and each jurisdiction. Nothing in them registers by being
imported: `artifact_kinds()`, `capabilities()` and `parameter_parsers()`, called once each by the
composition root, build the registries of every catalog's kinds, of every `capabilities` package's
classes and of every `parameter_parsers` package's classes (found by walking their modules) and
hand them on. Adding a jurisdiction `<x>` is importing `tax_engine.jurisdictions.<x>` and adding it
to `JURISDICTIONS`. `CORE_PACKAGES` names the one core package whose decorators still fill a shared
registry: the English trace renderers, until they follow the same shape.
"""

import tax_engine.adapters.inbound.trace_english
import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_on
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.parameter_parser import ParameterParserRegistry
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry

CORE_PACKAGES = (tax_engine.adapters.inbound.trace_english,)

JURISDICTIONS = JurisdictionPackages(
    (
        tax_engine.jurisdictions.core,
        tax_engine.jurisdictions.ca,
        tax_engine.jurisdictions.ca_on,
    )
)


def artifact_kinds() -> ArtifactRegistry:
    """A new registry of the artifact kinds of every package in `JURISDICTIONS`.

    Nothing is shared: each call builds its own, to be handed on by whoever wires the application.
    """
    kinds = ArtifactRegistry()
    JURISDICTIONS.register(kinds)
    return kinds


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
