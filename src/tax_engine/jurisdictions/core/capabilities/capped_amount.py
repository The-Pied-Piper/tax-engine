"""Capped amount: the lesser of a money artifact and an `amount` dataset's cap, exactly.

For the return lines the form prints as "whichever is less": a base at or below the cap is
produced unchanged (keeping its scale), a base above it produces the cap's value. The lesser is
rounded only with the `cap` dataset's rule, which defaults to no rounding.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import CappedAmountLine


@capability(identifier="capped_amount")
class CappedAmount(Capability):
    """Produces `output`: the lesser of the consumed `base` and the `cap` dataset's amount."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"cap": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, cap: ParameterDataset[Amount], base: Money, output: Money) -> None:
        """Wire the capability: its cap dataset, the kind it caps, the kind it produces."""
        super().__init__(base=base, output=output)
        self._cap = cap
        self._base = base
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        cap, rounding = self._cap.values, self._cap.rounding
        # At or below the cap the base itself is the lesser, so its scale is kept.
        lesser = cap.value if base > cap.value else base
        result = rounding.apply(lesser)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(CappedAmountLine(self._output, self._base, base, cap, rounding, result),),
        )
