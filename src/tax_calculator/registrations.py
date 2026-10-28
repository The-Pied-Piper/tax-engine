"""The packages the composition root wires together, listed explicitly.

`CORE_PACKAGES` names the core packages whose decorators fill the shared capability, parameter
parser and English trace renderer registries: each one's `__init__.py` imports its modules, so
importing this module runs them. `JURISDICTIONS` lists the jurisdiction packages; importing one
registers only its own capabilities and trace line renderers, through the `capabilities` and
`trace_english` packages its `__init__.py` imports, and `JURISDICTIONS.register()`, called by the
composition root at startup, registers their artifact catalogs. Adding a jurisdiction `<x>` is
importing `tax_calculator.jurisdictions.<x>` and adding it to `JURISDICTIONS`.
"""

import tax_calculator.adapters.inbound.trace_english
import tax_calculator.adapters.outbound.parameter_parsers
import tax_calculator.domain.capabilities
import tax_calculator.jurisdictions.ca
import tax_calculator.jurisdictions.ca_on
from tax_calculator.adapters.outbound.jurisdiction_packages import JurisdictionPackages

CORE_PACKAGES = (
    tax_calculator.domain.capabilities,
    tax_calculator.adapters.outbound.parameter_parsers,
    tax_calculator.adapters.inbound.trace_english,
)

JURISDICTIONS = JurisdictionPackages(
    (tax_calculator.jurisdictions.ca, tax_calculator.jurisdictions.ca_on)
)
