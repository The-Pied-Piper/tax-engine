"""LesserOfCounts: the least of a list of count artifacts.

Schedule P Part D line 59 "Number from line 57 or line 58, whichever is less": no capability takes
the lesser of two counts (`core/lesser_of` takes money). Of equal counts the first listed is
produced. A `pass_on` blank blanks the output.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.jurisdictions.ca_qc.trace import LesserOfCountsLine


@capability(identifier="lesser_of_counts")
class LesserOfCounts(Capability):
    """Produces `output`: the least of the consumed `counts`, of which there is at least one."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"counts": list[int]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"counts"})

    def __init__(self, counts: tuple[ArtifactKind[int], ...], output: ArtifactKind[int]) -> None:
        """Wire the capability: the kinds it compares, in manifest order, and the kind it produces.

        Raises InvalidCapabilityError when `counts` is empty: there is no lesser of nothing.
        """
        super().__init__(counts=counts, output=output)
        if not counts:
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'counts' needs at least one kind, "
                "since there is no lesser of nothing"
            )
        self._counts = counts
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        parts = tuple((kind, self._input(inputs, kind).value) for kind in self._counts)
        # `min` keeps the first of equal values, so the first listed wins a tie.
        _kind, lesser = min(parts, key=lambda part: part[1])
        return CapabilityResult(
            outputs=(Artifact(self._output, lesser),),
            trace=(LesserOfCountsLine(self._output, parts, lesser),),
        )
