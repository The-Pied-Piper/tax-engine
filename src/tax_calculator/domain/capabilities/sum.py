"""Sum: adds the values of a list of money artifacts, exactly.

One mechanism for every total on a return: the manifest decides which parts are added, and in
which order they are listed in the trace. A sum has no dataset, so it never rounds; a form that
rounds a total does so in a later capability with a rounding rule of its own.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.trace import SumLine


@capability(identifier="sum")
class Sum(Capability):
    """Produces `output`: the sum of the consumed `parts`, which is zero when there are none."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"parts": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

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
