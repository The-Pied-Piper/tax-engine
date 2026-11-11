"""SumNotBelowZero: adds the values of a list of money artifacts, floored at zero, then rounded.

The output is `rounding.apply(max(sum, 0))`; a floored zero is never negative zero and takes the
rule's scale (0.00 under the cent rule). Blank parts follow `blank:` as for `Sum`, and a passed-on
blank is not floored.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import SumNotBelowZeroLine


@capability(identifier="sum_not_below_zero")
class SumNotBelowZero(Capability):
    """Produces `output`: the sum of the consumed `parts`, never below zero, rounded by the
    dataset's rule; zero if none."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"parts": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"parts"})
    BLANK_PER_ITEM: ClassVar[frozenset[str]] = frozenset({"parts"})

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        parts: tuple[Money, ...],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the kinds it adds, in manifest order, and the
        kind it produces."""
        super().__init__(parts=parts, output=output)
        self._rounding = rounding
        self._parts = parts
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        parts = tuple((kind, self._input(inputs, kind).value) for kind in self._parts)
        exact_sum = sum((ExactFraction(value) for _kind, value in parts), ExactFraction(0))
        floored = max(exact_sum, ExactFraction(0))
        rounding = self._rounding.rounding
        total = rounding.apply(floored)
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(SumNotBelowZeroLine(self._output, parts, rounding, total),),
        )
