"""ThresholdGate: an amount passed through only when a gate reaches a threshold, else 0.

For the return lines the form prints as "must be $X or more" (T1 line 45200, the refundable
medical expense supplement: working income of at least a threshold): a gate at or above the
`threshold` dataset's amount produces the consumed `amount` unchanged (keeping its scale), a
gate below it produces 0. The result, a gated-off 0 included, is rounded only with the
`threshold` dataset's rule, which defaults to no rounding. It records one `ThresholdGateLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import ThresholdGateLine


@capability(identifier="threshold_gate")
class ThresholdGate(Capability):
    """Produces `output`: the consumed `amount` when the consumed `gate` is at least the
    `threshold` dataset's amount, otherwise 0."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"threshold": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "gate": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self, threshold: ParameterDataset[Amount], amount: Money, gate: Money, output: Money
    ) -> None:
        """Wire the capability: its threshold dataset, the kind it passes, the kind it tests,
        the kind it produces."""
        super().__init__(amount=amount, gate=gate, output=output)
        self._threshold = threshold
        self._amount = amount
        self._gate = gate
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        gate = self._input(inputs, self._gate).value
        threshold, rounding = self._threshold.values, self._threshold.rounding
        # Inclusive: a gate equal to the threshold passes the amount through.
        passed = amount if gate >= threshold.value else Decimal(0)
        result = rounding.apply(passed)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                ThresholdGateLine(
                    self._output,
                    self._amount,
                    amount,
                    self._gate,
                    gate,
                    threshold,
                    rounding,
                    result,
                ),
            ),
        )
