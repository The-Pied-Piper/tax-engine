"""Core's artifact catalog: empty, because core declares no artifact kinds of its own."""

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.registry import Namespace

CATALOG = ArtifactCatalog(Namespace("core"))
