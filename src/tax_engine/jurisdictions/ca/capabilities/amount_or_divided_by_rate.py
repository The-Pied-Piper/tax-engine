"""AmountOrDividedByRate: an amount, or another figure divided by a rate, chosen by a threshold.

For lines such as Schedule 11 line 11: "Enter the amount from line 26000 of your return on line 11
if it is $57,375 or less. If it is more than $57,375, enter the result of the following
calculation: Amount from line 76 of your return divided by 14.5% =". At or below the `limit`
dataset's threshold ("or less") the output is the consumed `amount`; over it, the consumed
`dividend` divided by the dataset's rate. The division is an exact fraction, so 5.05% divides as
2,000/101, and the dataset's rounding rule rounds the chosen figure once; under `rounding: none`
an inexact division raises `decimal.Inexact`. Both figures are always required. It records one
`AmountOrDividedByRateLine`.
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
from tax_engine.domain.parameters.threshold_rate import THRESHOLD_RATE, ThresholdRate
from tax_engine.domain.trace import AmountOrDividedByRateLine


@capability(identifier="amount_or_divided_by_rate")
class AmountOrDividedByRate(Capability):
    """Produces `output`: the consumed `amount` when it is at or below the `limit` dataset's
    threshold, otherwise the consumed `dividend` divided by the dataset's rate."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[ThresholdRate]]] = {"limit": THRESHOLD_RATE}
    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "dividend": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        limit: ParameterDataset[ThresholdRate],
        amount: Money,
        dividend: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its dataset, the kind tested, the kind divided, the kind
        produced."""
        super().__init__(amount=amount, dividend=dividend, output=output)
        self._limit = limit
        self._amount = amount
        self._dividend = dividend
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        dividend = self._input(inputs, self._dividend).value
        limit, rounding = self._limit.values, self._limit.rounding
        # Inclusive: an amount equal to the threshold passes through.
        chosen = (
            amount
            if amount <= limit.threshold
            else ExactFraction(dividend) / ExactFraction(limit.rate.value)
        )
        result = rounding.apply(chosen)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                AmountOrDividedByRateLine(
                    self._output,
                    self._amount,
                    amount,
                    self._dividend,
                    dividend,
                    limit,
                    rounding,
                    result,
                ),
            ),
        )
