"""The one federal artifact catalog, which every family module declares its kinds on.

It lives in its own module so that a family module can import it without importing the package
(whose `__init__` imports the family modules).
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))
