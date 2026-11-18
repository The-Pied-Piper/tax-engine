"""The Newfoundland and Labrador artifact catalog: its own kinds, named from its forms.

Federal kinds come from `tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_nl import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))
