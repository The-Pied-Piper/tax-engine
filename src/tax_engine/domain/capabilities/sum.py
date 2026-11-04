"""Sum: adds the values of a list of money artifacts, exactly.

One mechanism for every total on a return: the manifest decides which parts are added, and in
which order they are listed in the trace. A sum has no dataset, so it never rounds; a form that
rounds a total does so in a later capability with a rounding rule of its own.

Any part may be blank (`BLANK_ALLOWED`). What a blank does is the manifest step's `blank:` line,
for the whole list or for one part by its identifier (`BLANK_PER_ITEM`): so a total can pass a
blank part on while another part, a line that may be left out, counts as zero.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.trace import SumLine


@capability(identifier="sum")
class Sum(Capability):
    """Produces `output`: the sum of the consumed `parts`, which is zero when there are none."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"parts": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"parts"})
    BLANK_PER_ITEM: ClassVar[frozenset[str]] = frozenset({"parts"})

    def __init__(self, parts: tuple[Money, ...], output: Money) -> None:
        """Wire the capability: the kinds it adds, in manifest order, and the kind it produces."""
        super().__init__(parts=parts, output=output)
        self._parts = parts
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        parts = tuple((kind, self._input(inputs, kind).value) for kind in self._parts)
        total = sum((value for _kind, value in parts), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(SumLine(self._output, parts, total),),
        )
