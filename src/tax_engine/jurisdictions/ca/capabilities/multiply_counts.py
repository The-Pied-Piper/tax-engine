"""MultiplyCounts: the product of a list of count artifacts.

Schedule 8 Part 2 line A, "Enter "12" on line A below unless any of the following conditions apply":
the months a filer typed in (or the printed 12) are kept for a filer whose age conditions are all
1, and are 0 when one of them is 0 (born in 1954 or earlier, so 70 or older for all of 2025, or in
2008 or later, so not yet 18 in 2025). No capability multiplies counts (`core/times_count` takes an
amount and a count). A blank count takes a fallback or `pass_on`, one rule for each kind.
"""

from __future__ import annotations

from collections.abc import Mapping
from math import prod
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.jurisdictions.ca.trace import MultiplyCountsLine


@capability(identifier="multiply_counts")
class MultiplyCounts(Capability):
    """Produces `output`: the product of the consumed `counts`, of which there is at least one."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"counts": list[int]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"counts"})
    BLANK_PER_ITEM: ClassVar[frozenset[str]] = frozenset({"counts"})

    def __init__(self, counts: tuple[ArtifactKind[int], ...], output: ArtifactKind[int]) -> None:
        """Wire the capability: the kinds it multiplies, in manifest order, and the kind produced.

        Raises InvalidCapabilityError when `counts` is empty: there is no product of nothing.
        """
        super().__init__(counts=counts, output=output)
        if not counts:
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'counts' needs at least one kind, "
                "since there is no product of nothing"
            )
        self._counts = counts
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        parts = tuple((kind, self._input(inputs, kind).value) for kind in self._counts)
        result = prod(count for _kind, count in parts)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(MultiplyCountsLine(self._output, parts, result),),
        )
