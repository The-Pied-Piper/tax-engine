"""Multiple over: a `factor` dataset's multiple of one money artifact less another, floored at zero.

For the return lines the form prints as an amount "multiplied by" a factor, then "minus" another
line, "if negative, enter 0": the manifest decides which artifact is multiplied (`amount`) and
which is taken off (`less`). The output is `rounding.apply(max(factor × amount − less, 0))`,
rounded once after the floor with the `factor` dataset's rule, which defaults to no rounding; like
`core/subtract_not_below_zero`, a difference at or below zero is a plain `Decimal(0)`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.factor import FACTOR, Factor
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import MultipleOverLine


@capability(identifier="multiple_over")
class MultipleOver(Capability):
    """Produces `output`: `factor` times the consumed `amount` less the consumed `less`, not below
    zero, rounded."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Factor]]] = {"factor": FACTOR}
    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "less": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self, factor: ParameterDataset[Factor], amount: Money, less: Money, output: Money
    ) -> None:
        """Wire the capability: its factor dataset, the kind multiplied, the kind taken off, the
        kind produced."""
        super().__init__(amount=amount, less=less, output=output)
        self._factor = factor
        self._amount = amount
        self._less = less
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        less = self._input(inputs, self._less).value
        factor, rounding = self._factor.values, self._factor.rounding
        difference = factor.value * amount - less
        # A zero or negative difference is a plain zero: no scale, never a negative zero.
        result = rounding.apply(difference if difference > 0 else Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                MultipleOverLine(
                    output=self._output,
                    base=self._amount,
                    base_amount=amount,
                    factor=factor,
                    less=self._less,
                    less_amount=less,
                    rounding=rounding,
                    result=result,
                ),
            ),
        )
