"""MultiplyCounts: the product of a list of count artifacts.

The counts version of `core/multiply`, which multiplies two money amounts. The product of whole
numbers is exact, so nothing is rounded. A blank count takes a fallback or `pass_on`, one rule for
each kind.
"""

from __future__ import annotations

from collections.abc import Mapping
from math import prod
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.trace import MultiplyCountsLine


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
