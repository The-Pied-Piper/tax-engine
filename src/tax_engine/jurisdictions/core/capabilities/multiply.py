"""Multiply: multiplies one money artifact by another, rounding the exact product once.

The output is `rounding.apply(multiplicand * multiplier)`, the product formed once as an exact
fraction; the product of two finite decimals is always finite, so with no rounding it is exact.
Unlike `multiply_by_rate`, the multiplier is any figure, not a rate limited to 0 to 1, and no
figure is read as blank.
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
from tax_engine.domain.trace import ProductLine


@capability(identifier="multiply")
class Multiply(Capability):
    """Produces `output`: the consumed `multiplicand` x `multiplier`, rounded once."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"multiplicand": Decimal, "multiplier": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        multiplicand: Money,
        multiplier: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the kinds of the two factors, the output."""
        super().__init__(multiplicand=multiplicand, multiplier=multiplier, output=output)
        self._rounding = rounding
        self._multiplicand = multiplicand
        self._multiplier = multiplier
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        multiplicand = self._input(inputs, self._multiplicand).value
        multiplier = self._input(inputs, self._multiplier).value
        rounding = self._rounding.rounding
        result = rounding.apply(ExactFraction(multiplicand) * ExactFraction(multiplier))
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                ProductLine(
                    self._output,
                    self._multiplicand,
                    multiplicand,
                    self._multiplier,
                    multiplier,
                    rounding,
                    result,
                ),
            ),
        )
