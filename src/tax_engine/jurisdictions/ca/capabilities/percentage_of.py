"""PercentageOf: one money figure as a percentage of another, rounded once by a `rounding_only`
dataset.

For Form T2043 Chart B rows 3 and 6, "Percentage (%) of gross income allocated to the designated
province. Row 1 divided by row 2", and "Percentage (%) of salaries and wages allocated to the
designated province. Row 4 divided by row 5": the consumed `dividend` over the consumed `divisor`,
times 100, so 60 means 60%. The output is `rounding.apply(100 x dividend / divisor)`, the quotient
an exact fraction, rounded by the dataset's rule and by nothing else. A zero divisor gives a plain
`Decimal(0)`, never an error, as `ca/ratio_truncated` does. It records one `PercentageOfLine`.
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
from tax_engine.jurisdictions.ca.trace import PercentageOfLine


@capability(identifier="percentage_of")
class PercentageOf(Capability):
    """Produces `output`: the consumed `dividend` ÷ the consumed `divisor` × 100, rounded once by
    the `rounding` dataset's rule, and 0 for a zero divisor."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"dividend": Decimal, "divisor": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        dividend: Money,
        divisor: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the kind divided, the kind it is divided
        by, the kind of the percentage produced."""
        super().__init__(dividend=dividend, divisor=divisor, output=output)
        self._rounding = rounding
        self._dividend = dividend
        self._divisor = divisor
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        dividend = self._input(inputs, self._dividend).value
        divisor = self._input(inputs, self._divisor).value
        rounding = self._rounding.rounding
        if divisor == 0:
            result = Decimal(0)
        else:
            result = rounding.apply(100 * ExactFraction(dividend) / ExactFraction(divisor))
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                PercentageOfLine(
                    output=self._output,
                    dividend=self._dividend,
                    dividend_amount=dividend,
                    divisor=self._divisor,
                    divisor_amount=divisor,
                    rounding=rounding,
                    result=result,
                ),
            ),
        )
