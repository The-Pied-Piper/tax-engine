"""Made-up things registered under the `ex` namespace of the enclosing package."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.capability import Capability, CapabilityResult


class Gadget:
    """A made-up thing to register."""


class Sprocket:
    """Another made-up thing to register."""


class GadgetLevy(Capability):
    """A made-up capability; deliberately not decorated, so importing it registers nothing."""

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return CapabilityResult(outputs=(), trace=())
