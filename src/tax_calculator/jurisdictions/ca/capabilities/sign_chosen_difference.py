"""SignChosenDifference: a difference picked by the sign of another figure.

For lines such as T691 Part 1 line 23: "If line 20 is positive, enter the amount from line 22. If
line 20 is negative, enter whichever is less: the amount from line 21 or line 22 (show in
brackets)." When the consumed `sign_amount` is zero or positive the output is the consumed
`difference` as it is. When it is negative the output is the lesser of the consumed `reference`
and the magnitude of `difference`, as a negative number, so the output is signed. It never
rounds: the output is one of the consumed figures, or its negative. It records one
`SignChosenDifferenceLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import SignChosenDifferenceLine


@capability(identifier="sign_chosen_difference")
class SignChosenDifference(Capability):
    """Produces `output`: `difference` when `sign_amount` is not negative, otherwise the lesser of
    `reference` and the magnitude of `difference`, as a negative number."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {}
    CONSUMES: ClassVar[Mapping[str, type]] = {
        "sign_amount": Decimal,
        "reference": Decimal,
        "difference": Decimal,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self, sign_amount: Money, reference: Money, difference: Money, output: Money
    ) -> None:
        """Wire the capability: the kind that gives the sign, the reference, the difference and
        the kind produced."""
        super().__init__(
            sign_amount=sign_amount, reference=reference, difference=difference, output=output
        )
        self._sign_amount = sign_amount
        self._reference = reference
        self._difference = difference
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        sign_amount = self._input(inputs, self._sign_amount).value
        reference = self._input(inputs, self._reference).value
        difference = self._input(inputs, self._difference).value
        if sign_amount < 0:
            result = Decimal(0) - min(reference, abs(difference))
        else:
            result = difference
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                SignChosenDifferenceLine(
                    self._output,
                    self._sign_amount,
                    sign_amount,
                    self._reference,
                    reference,
                    self._difference,
                    difference,
                    result,
                ),
            ),
        )
