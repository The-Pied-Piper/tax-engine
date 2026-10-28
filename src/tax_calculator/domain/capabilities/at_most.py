"""AtMost: a money artifact that may not exceed another, passed on unchanged.

For a form line that reads "not more than": the manifest decides which artifact is the amount
(typically a filer's claim) and which is its bound. An amount at or below the bound is produced
as is, exactly and with its own scale; it has no dataset, so it never rounds, and no floor. An
amount above the bound is not capped: it is an input error, `InputAboveBoundError`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.trace import AtMostLine


@capability(identifier="at_most")
class AtMost(Capability):
    """Produces `output`: the consumed `amount`, unchanged, when it is at most the `bound`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "bound": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, amount: Money, bound: Money, output: Money) -> None:
        """Wire the capability: the kind checked, the kind it may not exceed, the kind produced."""
        super().__init__(amount=amount, bound=bound, output=output)
        self._amount = amount
        self._bound = bound
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        bound = self._input(inputs, self._bound).value
        if amount > bound:
            raise InputAboveBoundError(
                f"{self._amount.identifier} {amount} is above {self._bound.identifier} {bound}"
            )
        return CapabilityResult(
            outputs=(Artifact(self._output, amount),),
            trace=(
                AtMostLine(
                    output=self._output,
                    amount_kind=self._amount,
                    amount_value=amount,
                    bound=self._bound,
                    bound_value=bound,
                ),
            ),
        )
