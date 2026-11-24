"""Rate figure: a rate of a `rate` dataset as a figure of its own, exactly.

The output is the dataset's rate with no rounding, for a step that multiplies it into another rate.
`core/apply_rate` rounds its product with the dataset's rule, which a credit rate printed to the
cent would apply to a rate that is not a money amount.
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
from tax_engine.domain.trace import RateFigureLine


@capability(identifier="rate_figure")
class RateFigure(Capability):
    """Produces `output`: the `rate` dataset's rate, exactly."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Rate]]] = {"rate": RATE}
    CONSUMES: ClassVar[Mapping[str, type]] = {}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, rate: ParameterDataset[Rate], output: Money) -> None:
        """Wire the capability: its rate dataset and the kind it produces."""
        super().__init__(output=output)
        self._rate = rate
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        rate = self._rate.values
        return CapabilityResult(
            outputs=(Artifact(self._output, rate.value),),
            trace=(RateFigureLine(self._output, rate),),
        )
