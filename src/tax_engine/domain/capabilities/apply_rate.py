"""Apply rate: multiplies a money artifact by a rate from a `rate` dataset, exactly.

The product is rounded only with the `rate` dataset's rule, which defaults to no rounding.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.trace import RateAppliedLine


@capability(identifier="apply_rate")
class ApplyRate(Capability):
    """Produces `output`: the consumed `base` × the `rate` dataset's rate, rounded by its rule."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Rate]]] = {"rate": RATE}
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, rate: ParameterDataset[Rate], base: Money, output: Money) -> None:
        """Wire the capability: its rate dataset, the kind it multiplies, the kind it produces."""
        super().__init__(base=base, output=output)
        self._rate = rate
        self._base = base
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        rate, rounding = self._rate.values, self._rate.rounding
        result = rounding.apply(base * rate.value)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(RateAppliedLine(self._output, self._base, base, rate, rounding, result),),
        )
