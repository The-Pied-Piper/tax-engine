"""CountRefusedByConditions: an int code that names one option of a form, refused when it is none.

A statement's code picks one printed option (a line of the return, a designated province). A code
the form does not list names no option, so its amount would drop out of the return with no error.
The `conditions` dataset, the same kind `ca/count_by_conditions` reads, lists the conditions under
which the code is REFUSED, in the form's order and wording; a condition applies when every one of
its parts holds and a part holds when any of its tests holds, as for `ca/count_by_conditions`.
Only the consumed count (position 1) is read: a test of an amount, a comparison with another
figure or a second count position is refused when the capability is built. The dataset's
`count_when_any_applies` is a field of the shared kind and is not read here. When a condition
applies the count is an input error, `InputOutOfRangeError`, naming the kind, its value and the
text of the first condition that applies; otherwise the count is produced unchanged and one
`CountNotRefusedLine` is recorded.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InputOutOfRangeError, InvalidCapabilityError
from tax_calculator.domain.parameters.conditions import CONDITIONS, Condition, ConditionList
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import CountNotRefusedLine


@capability(identifier="count_refused_by_conditions")
class CountRefusedByConditions(Capability):
    """Produces `output`: the consumed `count`, unchanged, when no condition of the `conditions`
    dataset applies to it."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[ConditionList]]] = {"conditions": CONDITIONS}
    CONSUMES: ClassVar[Mapping[str, type]] = {"count": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(
        self,
        conditions: ParameterDataset[ConditionList],
        count: ArtifactKind[int],
        output: ArtifactKind[int],
    ) -> None:
        """Wire the capability: its conditions dataset, the count checked, the count produced."""
        super().__init__(count=count, output=output)
        values = conditions.values
        if values.amount_positions_read:
            raise InvalidCapabilityError(
                "CountRefusedByConditions: the conditions may not read an amount or compare "
                "with another amount"
            )
        highest = values.highest_count_position
        if highest > 1:
            raise InvalidCapabilityError(
                f"CountRefusedByConditions: the conditions read count position {highest}, "
                "but only position 1 is consumed"
            )
        self._conditions = conditions
        self._count = count
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        count = self._input(inputs, self._count).value
        for condition in self._conditions.values.conditions:
            if self._applies(condition, count):
                raise InputOutOfRangeError(
                    f"{self._count.identifier} {count} is refused: {condition.text}"
                )
        return CapabilityResult(
            outputs=(Artifact(self._output, count),),
            trace=(
                CountNotRefusedLine(
                    output=self._output,
                    count_kind=self._count,
                    count=count,
                ),
            ),
        )

    @staticmethod
    def _applies(condition: Condition, count: int) -> bool:
        """Whether every part of `condition` holds for `count` (a part holds when any test does)."""
        figure = Decimal(count)
        return all(
            any(test.than is not None and test.holds(figure, test.than) for test in part.tests)
            for part in condition.parts
        )
