"""Subtract: takes one money artifact off another, exactly.

One mechanism for every difference between two amounts on a return: the manifest decides which
artifact is the amount and which is taken off. A subtraction has no dataset, so it never rounds,
and it has no floor: when `less` exceeds `amount` the result is negative, as is.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.trace import SubtractedLine


@capability(identifier="subtract")
class Subtract(Capability):
    """Produces `output`: the consumed `amount` less the consumed `less`, which may be negative."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "less": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, amount: Money, less: Money, output: Money) -> None:
        """Wire the capability: the kind it starts from, the kind taken off, the kind produced."""
        super().__init__(amount=amount, less=less, output=output)
        self._amount = amount
        self._less = less
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        less = self._input(inputs, self._less).value
        result = amount - less
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                SubtractedLine(
                    output=self._output,
                    minuend=self._amount,
                    minuend_amount=amount,
                    subtrahend=self._less,
                    subtrahend_amount=less,
                    result=result,
                ),
            ),
        )
