"""RatioTruncated: a ratio of two money figures, rounded once by a `rounding_only` dataset.

For lines such as RC381 line 6, "Line 4 divided by line 5 (calculated to the fifth decimal place
without rounding)": the dataset's rule is the form's (an increment of 0.00001 and mode down), so
the quotient, an exact fraction, is truncated by the rule and nothing else rounds it. A zero
divisor gives a plain `Decimal(0)`, never an error. `RatioTruncatedAtMostOne` shares the
implementation for a ratio that "cannot be more than 1": a dividend above the divisor gives
exactly 1, checked before the zero-divisor rule. Each records one `RatioTruncatedLine`.

The output is a `Rate` artifact (0 to 1), so a later line can multiply an amount by it. The plain
`RatioTruncated` is for a dividend not above the divisor: a ratio above 1 (or a negative one, from
a negative figure) is refused by `Rate` itself with `InvalidRateError`. `RatioTruncatedAtMostOne`
gives exactly 1 above the divisor; a negative dividend is refused the same way.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.trace import RatioTruncatedLine


@capability(identifier="ratio_truncated")
class RatioTruncated(Capability):
    """Produces the rate `output`: the consumed `dividend` ÷ the consumed `divisor`, rounded by the
    `rounding` dataset's rule, and 0 for a zero divisor."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"dividend": Decimal, "divisor": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Rate}

    _CAP_AT_ONE: ClassVar[bool] = False

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        dividend: Money,
        divisor: Money,
        output: ArtifactKind[Rate],
    ) -> None:
        """Wire the capability: its rounding dataset, the kind divided, the kind it is divided
        by, the rate kind produced."""
        super().__init__(dividend=dividend, divisor=divisor, output=output)
        self._rounding = rounding
        self._dividend = dividend
        self._divisor = divisor
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        dividend = self._input(inputs, self._dividend).value
        divisor = self._input(inputs, self._divisor).value
        rounding = self._rounding.rounding
        if self._CAP_AT_ONE and dividend > divisor:
            result = Decimal(1)
        elif divisor == 0:
            result = Decimal(0)
        else:
            result = rounding.apply(ExactFraction(dividend) / ExactFraction(divisor))
        rate = Rate(result)
        return CapabilityResult(
            outputs=(Artifact(self._output, rate),),
            trace=(
                RatioTruncatedLine(
                    output=self._output,
                    dividend=self._dividend,
                    dividend_amount=dividend,
                    divisor=self._divisor,
                    divisor_amount=divisor,
                    rounding=rounding,
                    cap_at_one=self._CAP_AT_ONE,
                    result=result,
                ),
            ),
        )


@capability(identifier="ratio_truncated_at_most_one")
class RatioTruncatedAtMostOne(RatioTruncated):
    """Produces `output`: the ratio as `RatioTruncated` does, but exactly 1 when the consumed
    `dividend` is above the `divisor`."""

    _CAP_AT_ONE: ClassVar[bool] = True
