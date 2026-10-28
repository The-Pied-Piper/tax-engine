"""Credit amount: a `credit` dataset's amount as an artifact, so it can be one part of a sum.

The amount is rounded only with the `credit` dataset's rule, which defaults to no rounding. The
capability consumes nothing: in a composition it has no incoming edges.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import CreditAmountLine


@capability(identifier="credit_amount")
class CreditAmount(Capability):
    """Produces `output`: the `amount` dataset's credit amount, rounded by that dataset's rule."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Credit]]] = {"amount": CREDIT}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, amount: ParameterDataset[Credit], output: Money) -> None:
        """Wire the capability: its credit dataset and the kind it produces."""
        super().__init__(output=output)
        self._amount = amount
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        basis, rounding = self._amount.values, self._amount.rounding
        value = rounding.apply(basis.amount)
        return CapabilityResult(
            outputs=(Artifact(self._output, value),),
            trace=(CreditAmountLine(self._output, basis, rounding, value),),
        )
