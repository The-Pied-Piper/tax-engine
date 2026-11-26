"""The Nova Scotia artifact catalog: Nova Scotia's own kinds, named
from the Nova Scotia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ns import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))
