"""ApplyPercentage: an amount times a percentage, rounded once.

For form lines such as Form T2048 line 3 ("Line 1 multiplied by the percentage from line 2"),
where the percentage is entered as the form prints it: 50 means 50%. The output is
`rounding.apply(amount × percentage / 100)`, the product formed first as an exact fraction and
rounded once, with only the `rounding_only` dataset's rule. There is no denominator, so no
zero-denominator case arises. The trace holds one `PercentageAppliedLine` naming the amount,
percentage, rounding and result. A percentage is not capped here; where the law caps it, the
manifest does with `lesser_of`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.trace import PercentageAppliedLine


@capability(identifier="apply_percentage")
class ApplyPercentage(Capability):
    """Produces `output`: the consumed `amount` × `percentage` / 100, rounded once."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "percentage": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        amount: Money,
        percentage: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the amount, the percentage, the output."""
        super().__init__(amount=amount, percentage=percentage, output=output)
        self._rounding = rounding
        self._amount = amount
        self._percentage = percentage
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        percentage = self._input(inputs, self._percentage).value
        rounding = self._rounding.rounding
        result = rounding.apply(ExactFraction(amount) * ExactFraction(percentage) / 100)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                PercentageAppliedLine(
                    self._output,
                    self._amount,
                    amount,
                    self._percentage,
                    percentage,
                    rounding,
                    result,
                ),
            ),
        )
