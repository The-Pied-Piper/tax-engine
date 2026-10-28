"""ApplyChosenRate: multiplies a money artifact by a rate artifact, exactly, rounded once.

Schedule ON479-A, line 8: "Line 6 multiplied by the percentage from line 7". Unlike
`core/apply_rate`, whose rate is a `rate` dataset's, the rate here is an artifact chosen by an
earlier line. The output is `rounding.apply(base × rate)`, the product computed as an exact
fraction so nothing is rounded before the `rounding_only` dataset's rule.
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
from tax_calculator.domain.trace import ChosenRateAppliedLine


@capability(identifier="apply_chosen_rate")
class ApplyChosenRate(Capability):
    """Produces `output`: the consumed `base` × the consumed `rate`, rounded by `rounding`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal, "rate": Rate}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        base: Money,
        rate: ArtifactKind[Rate],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the kind multiplied, the rate, the output."""
        super().__init__(base=base, rate=rate, output=output)
        self._rounding = rounding
        self._base = base
        self._rate = rate
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        rate = self._input(inputs, self._rate).value
        rounding = self._rounding.rounding
        result = rounding.apply(ExactFraction(base) * ExactFraction(rate.value))
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                ChosenRateAppliedLine(
                    self._output, self._base, base, self._rate, rate, rounding, result
                ),
            ),
        )
