"""Apply ratio: multiplies a money artifact by a ratio of two other money artifacts.

For form lines such as "tax otherwise payable × foreign income / worldwide income", whose ratio is
computed by earlier lines, not stated by a dataset: the output is
`rounding.apply(amount × numerator / denominator)`, the product formed first and divided once, as an
exact fraction so nothing is rounded before the rule. It is rounded only with the `rounding_only`
dataset's rule; under no rounding a quotient with no finite decimal expansion raises
`decimal.Inexact`. A zero denominator is refused with a `ValidationError`. A ratio above 1 is not
capped here; where the law caps it, the manifest does with `lesser_of`. The arithmetic is the static
method `ApplyRatio.ratio_of`, which a capability that works a ratio per item calls instead of
copying it.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import ValidationError
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import RatioAppliedLine


@capability(identifier="apply_ratio")
class ApplyRatio(Capability):
    """Produces `output`: the consumed `amount` × `numerator` / `denominator`, rounded once."""

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
        """Wire the capability: its rounding dataset, the three kinds of the ratio, the output."""
        super().__init__(amount=amount, numerator=numerator, denominator=denominator, output=output)
        self._rounding = rounding
        self._amount = amount
        self._numerator = numerator
        self._denominator = denominator
        self._output = output

    @staticmethod
    def ratio_of(
        amount: Decimal, numerator: Decimal, denominator: Decimal, rounding: RoundingRule
    ) -> Decimal:
        """`rounding.apply(amount × numerator / denominator)`: the product formed first and
        divided once, as an exact fraction. A zero `denominator` is a `ValidationError`."""
        if denominator == 0:
            raise ValidationError("the denominator is zero, so the ratio is undefined")
        return rounding.apply(
            ExactFraction(amount) * ExactFraction(numerator) / ExactFraction(denominator)
        )

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        numerator = self._input(inputs, self._numerator).value
        denominator = self._input(inputs, self._denominator).value
        if denominator == 0:
            raise ValidationError(
                f"{self._denominator.identifier} is zero, so {self._amount.identifier} × "
                f"{self._numerator.identifier} / {self._denominator.identifier} is undefined"
            )
        rounding = self._rounding.rounding
        result = self.ratio_of(amount, numerator, denominator, rounding)
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
