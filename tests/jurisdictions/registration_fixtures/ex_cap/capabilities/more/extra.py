"""A made-up capability one package down, which also imports `Levy` from its sibling module."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tests.jurisdictions.registration_fixtures.ex_cap.capabilities.levy import Levy

__all__ = ["Extra", "Levy"]


@capability(identifier="extra")
class Extra(Capability):
    """Decorated, so the walk finds it."""

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return CapabilityResult(outputs=(), trace=())
