"""CountAtLeast: a count that may not fall below another, passed on unchanged.

For a form line that reads "the number ... cannot be less than": the manifest decides which
artifact is the count and which is its minimum. It is `core/at_most` for whole numbers, the other
way round: a count at or above the minimum is produced as is, and a count below it is not raised
to the minimum but is an input error, `InputBelowBoundError`. It records one `CountAtLeastLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InputBelowBoundError
from tax_calculator.domain.trace import CountAtLeastLine


@capability(identifier="count_at_least")
class CountAtLeast(Capability):
    """Produces `output`: the consumed `count`, unchanged, when it is at least the `minimum`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"count": int, "minimum": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(
        self,
        count: ArtifactKind[int],
        minimum: ArtifactKind[int],
        output: ArtifactKind[int],
    ) -> None:
        """Wire the capability: the count checked, the count it may not fall below, the count
        produced."""
        super().__init__(count=count, minimum=minimum, output=output)
        self._count = count
        self._minimum = minimum
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        count = self._input(inputs, self._count).value
        minimum = self._input(inputs, self._minimum).value
        if count < minimum:
            raise InputBelowBoundError(
                f"{self._count.identifier} {count} is below {self._minimum.identifier} {minimum}"
            )
        return CapabilityResult(
            outputs=(Artifact(self._output, count),),
            trace=(
                CountAtLeastLine(
                    output=self._output,
                    count_kind=self._count,
                    count=count,
                    minimum_kind=self._minimum,
                    minimum=minimum,
                ),
            ),
        )
