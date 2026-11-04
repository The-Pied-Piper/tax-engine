"""The packages the composition root wires together, listed explicitly.

`CORE_PACKAGES` names the core packages whose decorators fill the shared parameter parser and
English trace renderer registries: each one's `__init__.py` imports its modules, so importing this
module runs them. `JURISDICTIONS` lists the jurisdiction packages; importing one registers only its
own trace line renderers, through the `trace_english` package its `__init__.py` imports. Their
artifact kinds and capabilities are not registered by importing: `artifact_kinds()` and
`capabilities()`, called once each by the composition root, build the registries of every catalog's
kinds and of every `capabilities` package's classes (found by walking its modules) and hand them
on. Adding a jurisdiction `<x>` is importing `tax_engine.jurisdictions.<x>` and adding it to
`JURISDICTIONS`.
"""

import tax_engine.adapters.inbound.trace_english
import tax_engine.adapters.outbound.parameter_parsers
import tax_engine.domain.capabilities
import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.capability_modules import capabilities_in
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.capability import CapabilityRegistry

CORE_PACKAGES = (
    tax_engine.adapters.outbound.parameter_parsers,
    tax_engine.adapters.inbound.trace_english,
)

JURISDICTIONS = JurisdictionPackages((tax_engine.jurisdictions.ca, tax_engine.jurisdictions.ca_on))


def artifact_kinds() -> ArtifactRegistry:
    """A new registry of the artifact kinds of every package in `JURISDICTIONS`.

    Nothing is shared: each call builds its own, to be handed on by whoever wires the application.
    """
    kinds = ArtifactRegistry()
    JURISDICTIONS.register(kinds)
    return kinds


def capabilities() -> CapabilityRegistry:
    """A new registry of the capabilities of the core package and of every package in
    `JURISDICTIONS`.

    Nothing is shared: each call builds its own, to be handed on by whoever wires the application.
    """
    registry = CapabilityRegistry()
    for cls in capabilities_in(tax_engine.domain.capabilities):
        registry.register_class(cls)
    JURISDICTIONS.register_capabilities(registry)
    return registry
