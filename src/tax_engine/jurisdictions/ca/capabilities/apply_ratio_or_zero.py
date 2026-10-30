"""ApplyRatioOrZero: an amount times a ratio, zero when the denominator is zero.

For form lines such as Form T2048 line 41 ("Line 39 multiplied by line 40"), whose ratio is
computed by earlier lines, and where the form says to enter "0" when the ratio's denominator is 0
(line 36: "if the result is "0", enter "0" on lines 41 and 42"). The output is
`rounding.apply(amount × numerator / denominator)`, the product formed first and divided once, as an
exact fraction so nothing is rounded before the rule. It is rounded only with the `rounding_only`
dataset's rule; under no rounding a quotient with no finite decimal expansion raises
`decimal.Inexact`. A zero denominator gives an output of 0, rounded by the same rule, with no error
raised. The trace holds one `RatioAppliedLine` naming the amount, numerator, denominator, rounding
and result. A ratio above 1 is not capped here; where the law caps it, the manifest does with
`lesser_of`.
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
from tax_engine.domain.trace import RatioAppliedLine


@capability(identifier="apply_ratio_or_zero")
class ApplyRatioOrZero(Capability):
    """Produces `output`: `amount` × `numerator` / `denominator`, rounded once; 0 if zero."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {
        "amount": Decimal,
        "numerator": Decimal,
        "denominator": Decimal,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        amount: Money,
        numerator: Money,
        denominator: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the amount, the numerator, the denominator,
        the output."""
        super().__init__(amount=amount, numerator=numerator, denominator=denominator, output=output)
        self._rounding = rounding
        self._amount = amount
        self._numerator = numerator
        self._denominator = denominator
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        numerator = self._input(inputs, self._numerator).value
        denominator = self._input(inputs, self._denominator).value
        rounding = self._rounding.rounding
        if denominator == 0:
            result = rounding.apply(ExactFraction(0))
        else:
            result = rounding.apply(
                ExactFraction(amount) * ExactFraction(numerator) / ExactFraction(denominator)
            )
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                RatioAppliedLine(
                    self._output,
                    self._amount,
                    amount,
                    self._numerator,
                    numerator,
                    self._denominator,
                    denominator,
                    rounding,
                    result,
                ),
            ),
        )
