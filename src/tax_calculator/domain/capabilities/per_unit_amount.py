"""Per-unit amount: an `amount` dataset's amount for each unit of a count artifact.

For the return lines the form prints as "number of ... multiplied by" an amount: the output is
`rounding.apply(amount × count)`, the product of the per-unit amount and the `int` count, rounded
once with the `amount` dataset's rule, which defaults to no rounding, like `core/credit_amount`;
the per-unit amount itself is never rounded first.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import PerUnitAmountLine


@capability(identifier="per_unit_amount")
class PerUnitAmount(Capability):
    """Produces `output`: the `amount` dataset's amount times the consumed `count`, rounded."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"amount": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"count": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self, amount: ParameterDataset[Amount], count: ArtifactKind[int], output: Money
    ) -> None:
        """Wire the capability: its per-unit dataset, the count it reads, the kind it produces."""
        super().__init__(count=count, output=output)
        self._amount = amount
        self._count = count
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        count = self._input(inputs, self._count).value
        per_unit, rounding = self._amount.values, self._amount.rounding
        product = per_unit.value * count
        if not product:
            product = product.copy_abs()  # a zero product is a plain 0, never a signed one
        result = rounding.apply(product)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                PerUnitAmountLine(self._output, self._count, count, per_unit, rounding, result),
            ),
        )
