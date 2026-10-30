"""SumNotBelowZero: adds the values of a list of money artifacts, floored at zero, exactly.

For the return lines the form prints with "if negative, enter 0" after adding: the manifest
decides which parts are added, and in which order they are listed in the trace. Like `Sum` it
has no dataset, so it never rounds; unlike it, a total below zero becomes a plain `Decimal(0)`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.trace import SumNotBelowZeroLine


@capability(identifier="sum_not_below_zero")
class SumNotBelowZero(Capability):
    """Produces `output`: the sum of the consumed `parts`, never below zero; zero if none."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"parts": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, parts: tuple[Money, ...], output: Money) -> None:
        """Wire the capability: the kinds it adds, in manifest order, and the kind it produces."""
        super().__init__(parts=parts, output=output)
        self._parts = parts
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        parts = tuple((kind, self._input(inputs, kind).value) for kind in self._parts)
        sum_of_parts = sum((value for _kind, value in parts), Decimal(0))
        # A zero or negative total is a plain zero: no scale, never a negative zero.
        total = sum_of_parts if sum_of_parts > 0 else Decimal(0)
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(SumNotBelowZeroLine(self._output, parts, total),),
        )
