"""The packages the composition root wires together, listed explicitly.

`CORE_PACKAGES` names the core packages whose decorators fill the shared capability, parameter
parser and English trace renderer registries: each one's `__init__.py` imports its modules, so
importing this module runs them. `JURISDICTIONS` lists the jurisdiction packages; importing one
registers only its own capabilities and trace line renderers, through the `capabilities` and
`trace_english` packages its `__init__.py` imports. Their artifact kinds are not registered by
importing: `artifact_kinds()`, called once by the composition root, builds the registry of every
catalog's kinds and hands it to what reads text (the manifest source, a request adapter).
Adding a jurisdiction `<x>` is importing `tax_engine.jurisdictions.<x>` and adding it to
`JURISDICTIONS`.
"""

import tax_engine.adapters.inbound.trace_english
import tax_engine.adapters.outbound.parameter_parsers
import tax_engine.domain.capabilities
import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.domain.artifact import ArtifactRegistry

CORE_PACKAGES = (
    tax_engine.domain.capabilities,
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
