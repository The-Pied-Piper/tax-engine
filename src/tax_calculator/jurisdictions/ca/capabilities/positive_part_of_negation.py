"""PositivePartOfNegation: the negation of an amount that may be negative, not below zero.

For a line that reads "enter ... as a positive amount" of an earlier line that may be negative:
a negative amount is produced as a positive one, exactly and with its scale kept, and anything
else is a plain `Decimal(0)`, never a signed zero. It has no dataset, so it never rounds. It
records one `PositivePartOfNegationLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.trace import PositivePartOfNegationLine


@capability(identifier="positive_part_of_negation")
class PositivePartOfNegation(Capability):
    """Produces `output`: the negation of the consumed `amount` when it is below zero, else 0."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, amount: Money, output: Money) -> None:
        """Wire the capability: the kind it negates, the kind it produces."""
        super().__init__(amount=amount, output=output)
        self._amount = amount
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        # `copy_negate` is exact; unary minus would round to the context's precision.
        result = amount.copy_negate() if amount < 0 else Decimal(0)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(PositivePartOfNegationLine(self._output, self._amount, amount, result),),
        )
