"""Divide: divides one money artifact by another, rounding the exact quotient once.

The output is `rounding.apply(dividend / divisor)`, the quotient formed once as an exact fraction;
with no rounding an inexact quotient raises `decimal.Inexact`. A zero divisor is not an error: the
output is 0, and the trace line still records the rounding rule.
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
from tax_engine.domain.trace import QuotientLine


@capability(identifier="divide")
class Divide(Capability):
    """Produces `output`: the consumed `dividend` / `divisor`, rounded once (0 if divisor is 0)."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"dividend": Decimal, "divisor": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        dividend: Money,
        divisor: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the kinds of the two parts, the output."""
        super().__init__(dividend=dividend, divisor=divisor, output=output)
        self._rounding = rounding
        self._dividend = dividend
        self._divisor = divisor
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        dividend = self._input(inputs, self._dividend).value
        divisor = self._input(inputs, self._divisor).value
        rounding = self._rounding.rounding
        result = (
            Decimal(0)
            if divisor == 0
            else rounding.apply(ExactFraction(dividend) / ExactFraction(divisor))
        )
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                QuotientLine(
                    self._output,
                    self._dividend,
                    dividend,
                    self._divisor,
                    divisor,
                    rounding,
                    result,
                ),
            ),
        )
