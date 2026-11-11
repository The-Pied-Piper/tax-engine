"""TimesCount: a money artifact's amount for each unit of a count artifact.

The output is `rounding.apply(amount × count)`; a blank count is not a count of 0.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import TimesCountLine


@capability(identifier="times_count")
class TimesCount(Capability):
    """Produces `output`: the consumed `amount` times the consumed `count`, rounded by the
    dataset's rule."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "count": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"amount", "count"})

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        amount: Money,
        count: ArtifactKind[int],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the amount for each unit, the count it reads,
        the kind produced."""
        super().__init__(amount=amount, count=count, output=output)
        self._rounding = rounding
        self._amount = amount
        self._count = count
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        count = self._input(inputs, self._count).value
        rounding = self._rounding.rounding
        result = rounding.apply(ExactFraction(amount) * count)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                TimesCountLine(
                    output=self._output,
                    amount_kind=self._amount,
                    amount_value=amount,
                    count_kind=self._count,
                    count=count,
                    rounding=rounding,
                    result=result,
                ),
            ),
        )
