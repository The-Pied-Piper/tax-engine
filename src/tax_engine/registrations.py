"""The packages the composition root wires together, listed explicitly.

`CORE_PACKAGES` names the core packages whose decorators fill the shared capability, parameter
parser and English trace renderer registries: each one's `__init__.py` imports its modules, so
importing this module runs them. `JURISDICTIONS` lists the jurisdiction packages; importing one
registers only its own capabilities and trace line renderers, through the `capabilities` and
`trace_english` packages its `__init__.py` imports, and `JURISDICTIONS.register()`, called by the
composition root at startup, registers their artifact catalogs. Adding a jurisdiction `<x>` is
importing `tax_engine.jurisdictions.<x>` and adding it to `JURISDICTIONS`.
"""

import tax_engine.adapters.inbound.trace_english
import tax_engine.adapters.outbound.parameter_parsers
import tax_engine.domain.capabilities
import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages

CORE_PACKAGES = (
    tax_engine.domain.capabilities,
    tax_engine.adapters.outbound.parameter_parsers,
    tax_engine.adapters.inbound.trace_english,
)

JURISDICTIONS = JurisdictionPackages((tax_engine.jurisdictions.ca, tax_engine.jurisdictions.ca_on))
