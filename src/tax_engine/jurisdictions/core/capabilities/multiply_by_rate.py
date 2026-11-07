"""Multiply by rate: multiplies a money artifact by a rate artifact, a fraction from 0 to 1.

For form lines such as "Line 4 multiplied by the percentage from line 5", whose rate is computed
by an earlier line, not stated by a dataset: the output is `rounding.apply(base × rate)`, the
product formed exactly, as a fraction, and rounded only with the `rounding_only` dataset's rule,
which defaults to no rounding. The rate is a fraction (0.0915 is 9.15%), so nothing divides it by
100. A rate outside 0 to 1 is refused with `InvalidRateError`, as a rate dataset would refuse it;
the base is not capped.
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
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import MultipliedByRateLine


@capability(identifier="multiply_by_rate")
class MultiplyByRate(Capability):
    """Produces `output`: the consumed `base` × the consumed `rate`, rounded by the dataset's
    rule."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal, "rate": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        base: Money,
        rate: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the kind it multiplies, the rate kind, the
        kind it produces."""
        super().__init__(base=base, rate=rate, output=output)
        self._rounding = rounding
        self._base = base
        self._rate = rate
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        rate_value = self._input(inputs, self._rate).value
        rate = Rate(rate_value)
        rounding = self._rounding.rounding
        result = rounding.apply(ExactFraction(base) * ExactFraction(rate.value))
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                MultipliedByRateLine(
                    self._output,
                    self._base,
                    base,
                    self._rate,
                    rate.value,
                    rounding,
                    result,
                ),
            ),
        )
