"""Quotient: one money artifact divided by another, exactly.

Worksheet ON479 line 8 is "Line 6 divided by line 7 =". The manifest decides which artifact is
the dividend and which the divisor. It has no dataset, so it never rounds: the division is done
as an exact fraction and written out with `NO_ROUNDING`, which raises `decimal.Inexact` for a
quotient with no finite decimal expansion. A zero divisor is refused.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import ValidationError
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.domain.trace import QuotientLine


@capability(identifier="quotient")
class Quotient(Capability):
    """Produces `output`: the consumed `dividend` divided by the consumed `divisor`, exactly."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"dividend": Decimal, "divisor": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, dividend: Money, divisor: Money, output: Money) -> None:
        """Wire the capability: the kind divided, the kind it is divided by, the kind produced."""
        super().__init__(dividend=dividend, divisor=divisor, output=output)
        self._dividend = dividend
        self._divisor = divisor
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        dividend = self._input(inputs, self._dividend).value
        divisor = self._input(inputs, self._divisor).value
        if divisor == 0:
            raise ValidationError(
                f"cannot divide {self._dividend.label} by {self._divisor.label}: it is 0"
            )
        result = NO_ROUNDING.apply(ExactFraction(dividend) / ExactFraction(divisor))
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                QuotientLine(
                    output=self._output,
                    dividend=self._dividend,
                    dividend_amount=dividend,
                    divisor=self._divisor,
                    divisor_amount=divisor,
                    result=result,
                ),
            ),
        )
