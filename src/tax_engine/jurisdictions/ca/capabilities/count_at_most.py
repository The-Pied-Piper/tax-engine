"""CountAtMost: a count that may not rise above another, passed on unchanged.

For a form line that reads "the number ... cannot be more than": the manifest decides which
artifact is the count and which is its maximum. It is `ca/count_at_least` the other way round: a
count at or below the maximum is produced as is, and a count above it is not lowered to the
maximum but is an input error, `InputAboveBoundError`. It records one `CountAtMostLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.trace import CountAtMostLine


@capability(identifier="count_at_most")
class CountAtMost(Capability):
    """Produces `output`: the consumed `count`, unchanged, when it is at most the `maximum`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"count": int, "maximum": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(
        self,
        count: ArtifactKind[int],
        maximum: ArtifactKind[int],
        output: ArtifactKind[int],
    ) -> None:
        """Wire the capability: the count checked, the count it may not rise above, the count
        produced."""
        super().__init__(count=count, maximum=maximum, output=output)
        self._count = count
        self._maximum = maximum
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        count = self._input(inputs, self._count).value
        maximum = self._input(inputs, self._maximum).value
        if count > maximum:
            raise InputAboveBoundError(
                f"{self._count.identifier} {count} is above {self._maximum.identifier} {maximum}"
            )
        return CapabilityResult(
            outputs=(Artifact(self._output, count),),
            trace=(
                CountAtMostLine(
                    output=self._output,
                    count_kind=self._count,
                    count=count,
                    maximum_kind=self._maximum,
                    maximum=maximum,
                ),
            ),
        )
