"""Made-up capabilities, found by walking this package; nothing lists them."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import Capability, CapabilityResult, capability

NAMESPACE = "ex-cap"


@capability(identifier="in_init")
class InInit(Capability):
    """Defined in the package's own `__init__`, which the walk also reads."""

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return CapabilityResult(outputs=(), trace=())
