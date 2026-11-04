"""A made-up capability."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import Capability, CapabilityResult, capability


@capability(identifier="levy")
class Levy(Capability):
    """Decorated, so the walk finds it."""

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return CapabilityResult(outputs=(), trace=())


class Undecorated(Levy):
    """A subclass of a decorated class, not itself decorated: the walk leaves it out."""


LevyAlias = Levy
