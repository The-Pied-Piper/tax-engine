"""TimesCount: a money artifact's amount for each unit of a count artifact.

For an amount computed once and claimed for each of a counted number of persons, where the
amount is itself an artifact (a dataset's per-unit amount is `core/per_unit_amount`): the output
is `amount × count`, exact and with the amount's scale kept (a product that needs more digits
than the Decimal context holds raises); it has no dataset, so it never rounds, and no floor. A
count of 0 gives a plain zero, without the amount's scale; a zero product is never a signed zero.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.trace import TimesCountLine


@capability(identifier="times_count")
class TimesCount(Capability):
    """Produces `output`: the consumed `amount` times the consumed `count`, exactly."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "count": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, amount: Money, count: ArtifactKind[int], output: Money) -> None:
        """Wire the capability: the amount for each unit, the count it reads, the kind produced."""
        super().__init__(amount=amount, count=count, output=output)
        self._amount = amount
        self._count = count
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        count = self._input(inputs, self._count).value
        if count == 0:
            result = Decimal(0)  # a plain 0, not the amount's scale
        else:
            result = amount * count
            if not result:
                result = result.copy_abs()  # a zero product is never a signed zero
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                TimesCountLine(
                    output=self._output,
                    amount_kind=self._amount,
                    amount_value=amount,
                    count_kind=self._count,
                    count=count,
                    result=result,
                ),
            ),
        )
