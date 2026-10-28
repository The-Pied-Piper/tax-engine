"""AmountWhenMore: an amount passed through only when one figure is more than another, else 0.

For a line that reads "if the amount on line A is more than the amount on line B, complete this
line": the manifest decides which artifact is the amount, which is tested (`more`) and which it
is tested against (`than`). A `more` above `than` produces the consumed `amount` unchanged
(keeping its scale), otherwise a plain `Decimal(0)`. Unlike `threshold_gate`, the figure it is
compared with is an artifact, and the comparison is strict. It has no dataset, so it never
rounds. It records one `AmountWhenMoreLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.trace import AmountWhenMoreLine


@capability(identifier="amount_when_more")
class AmountWhenMore(Capability):
    """Produces `output`: the consumed `amount` when the consumed `more` is above the consumed
    `than`, otherwise 0."""

    CONSUMES: ClassVar[Mapping[str, type]] = {
        "amount": Decimal,
        "more": Decimal,
        "than": Decimal,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, amount: Money, more: Money, than: Money, output: Money) -> None:
        """Wire the capability: the kind it passes, the kind it tests, the kind it tests against,
        the kind it produces."""
        super().__init__(amount=amount, more=more, than=than, output=output)
        self._amount = amount
        self._more = more
        self._than = than
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        more = self._input(inputs, self._more).value
        than = self._input(inputs, self._than).value
        result = amount if more > than else Decimal(0)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                AmountWhenMoreLine(
                    output=self._output,
                    amount_kind=self._amount,
                    amount_value=amount,
                    more_kind=self._more,
                    more_value=more,
                    than_kind=self._than,
                    than_value=than,
                    result=result,
                ),
            ),
        )
