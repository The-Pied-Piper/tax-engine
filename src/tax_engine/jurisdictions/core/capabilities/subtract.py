"""Subtract: takes one money artifact off another, exactly, and rounds the difference once.

One mechanism for every difference between two amounts on a return: the manifest decides which
artifact is the amount and which is taken off. The difference is formed exactly and rounded once by
the `rounding_only` dataset's rule: the manifest step names the dataset, and a
difference that needs no rounding names one that states none.

It has no floor: when `less` exceeds `amount` the result is negative, as is.

Either consumed slot may be blank. What a blank does there is the manifest step's `blank:` line:
pass it on (the difference is blank too), or take a fallback in its place.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import SubtractedLine


@capability(identifier="subtract")
class Subtract(Capability):
    """Produces `output`: the consumed `amount` less the consumed `less`, rounded by the dataset's
    rule, which may be negative."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "less": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"amount", "less"})

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        amount: Money,
        less: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the kind it starts from, the kind taken off,
        the kind produced."""
        super().__init__(amount=amount, less=less, output=output)
        self._rounding = rounding
        self._amount = amount
        self._less = less
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        less = self._input(inputs, self._less).value
        rounding = self._rounding.rounding
        # Decimal subtraction keeps the scale of the amounts (100.00 less 40 is 60.00 under no
        # rounding); the engine's context traps Inexact, so it is exact or it raises.
        result = rounding.apply(amount - less)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                SubtractedLine(
                    output=self._output,
                    minuend=self._amount,
                    minuend_amount=amount,
                    subtrahend=self._less,
                    subtrahend_amount=less,
                    rounding=rounding,
                    result=result,
                ),
            ),
        )
