"""SubtractNotBelowZero: takes one money artifact off another, floored at zero, exactly.

For the return lines the form prints with "if negative, enter 0": the manifest decides which
artifact is the amount and which is taken off. Like `Subtract` it has no dataset, so it never
rounds; unlike it, a difference below zero becomes a plain `Decimal(0)`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.trace import SubtractedNotBelowZeroLine


@capability(identifier="subtract_not_below_zero")
class SubtractNotBelowZero(Capability):
    """Produces `output`: the consumed `amount` less the consumed `less`, never below zero."""

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
        difference = amount - less
        # A zero or negative difference is a plain zero: no scale, never a negative zero.
        result = difference if difference > 0 else Decimal(0)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                SubtractedNotBelowZeroLine(
                    output=self._output,
                    minuend=self._amount,
                    minuend_amount=amount,
                    subtrahend=self._less,
                    subtrahend_amount=less,
                    result=result,
                ),
            ),
        )
