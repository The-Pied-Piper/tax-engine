"""SubtractNotBelowZero: takes one money artifact off another, floored at zero.

The output is `rounding.apply(max(amount - less, 0))`; a floored zero is never negative zero. A
`pass_on` blank blanks it without the floor.
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
from tax_engine.domain.trace import SubtractedNotBelowZeroLine


@capability(identifier="subtract_not_below_zero")
class SubtractNotBelowZero(Capability):
    """Produces `output`: the consumed `amount` less the consumed `less`, never below zero,
    rounded by the dataset's rule."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "less": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"amount", "less"})

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        amount: Money,
        less: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the kind it starts from, the kind taken off,
        the kind produced."""
        super().__init__(amount=amount, less=less, output=output)
        self._rounding = rounding
        self._amount = amount
        self._less = less
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        less = self._input(inputs, self._less).value
        floored = max(ExactFraction(amount) - ExactFraction(less), ExactFraction(0))
        rounding = self._rounding.rounding
        result = rounding.apply(floored)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                SubtractedNotBelowZeroLine(
                    output=self._output,
                    minuend=self._amount,
                    minuend_amount=amount,
                    subtrahend=self._less,
                    subtrahend_amount=less,
                    rounding=rounding,
                    result=result,
                ),
            ),
        )
