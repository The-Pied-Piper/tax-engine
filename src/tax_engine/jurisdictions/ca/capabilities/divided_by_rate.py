"""DividedByRate: a figure divided by a rate from a `rate` dataset, rounded once.

For lines such as T1206 line 8A, "Amount from line 8 ÷ 14.5%", and line 33C, "Amount from line
33A divided by the tax rate you entered on line 33B". It mirrors `apply_rate`, dividing instead of
multiplying: the output is the consumed `dividend` divided by the dataset's rate. The division is
an exact fraction, so 5.05% divides as 2,000/101, and the dataset's rounding rule rounds the
quotient once; under `rounding: none` an inexact division raises `decimal.Inexact`. It records one
`DividedByRateLine`.
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
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.trace import DividedByRateLine


@capability(identifier="divided_by_rate")
class DividedByRate(Capability):
    """Produces `output`: the consumed `dividend` ÷ the `rate` dataset's rate, rounded by its
    rule."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Rate]]] = {"rate": RATE}
    CONSUMES: ClassVar[Mapping[str, type]] = {"dividend": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, rate: ParameterDataset[Rate], dividend: Money, output: Money) -> None:
        """Wire the capability: its rate dataset, the kind it divides, the kind it produces."""
        super().__init__(dividend=dividend, output=output)
        self._rate = rate
        self._dividend = dividend
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        dividend = self._input(inputs, self._dividend).value
        rate, rounding = self._rate.values, self._rate.rounding
        result = rounding.apply(ExactFraction(dividend) / ExactFraction(rate.value))
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                DividedByRateLine(self._output, self._dividend, dividend, rate, rounding, result),
            ),
        )
