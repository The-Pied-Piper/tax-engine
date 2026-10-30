"""CountByConditions: 1 or 0 from a form's list of conditions, so a line can be switched on or off.

Form ON428 line 80: "Enter "0" on line 80 if any of the following applies to you:" followed by the
printed conditions; and the rule that "only the individual with the higher net income can claim the
amounts on lines 75 and 76". The `conditions` dataset copies the form's conditions in the form's
order and wording, and says which count a list gives when any condition applies; when none does the
count is the other one of 0 and 1. Each test of a condition names the figure it reads by its
position (from 1) in the consumed list of `counts` (the yes/no counts a caller gives, 1 = the
condition applies) or of `amounts`, and a comparison with another amount names that amount's
position too, so a kind is listed once however many tests read it. Every test is evaluated, so the
trace records every figure read: one `ConditionLine` for each condition, then a
`ConditionsCountLine`. The output is a count, so nothing is rounded.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.parameters.conditions import CONDITIONS, Condition, ConditionList
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import ConditionLine, ConditionsCountLine


@capability(identifier="count_by_conditions")
class CountByConditions(Capability):
    """Produces `output`: the `conditions` dataset's count when any condition applies to the
    consumed `counts` and `amounts`, else the other one of 0 and 1."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[ConditionList]]] = {"conditions": CONDITIONS}
    CONSUMES: ClassVar[Mapping[str, type]] = {"counts": list[int], "amounts": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(
        self,
        conditions: ParameterDataset[ConditionList],
        counts: tuple[ArtifactKind[int], ...],
        amounts: tuple[Money, ...],
        output: ArtifactKind[int],
    ) -> None:
        """Wire the capability: its conditions dataset, the counts and amounts it reads (each
        position the dataset reads must be listed, and each listed kind must be read), the kind
        produced."""
        super().__init__(counts=counts, amounts=amounts, output=output)
        self._check_listed("counts", counts, conditions.values.count_positions_read)
        self._check_listed("amounts", amounts, conditions.values.amount_positions_read)
        self._conditions = conditions
        self._counts = counts
        self._amounts = amounts
        self._output = output

    @staticmethod
    def _check_listed(
        slot: str, kinds: tuple[ArtifactKind[Any], ...], read: frozenset[int]
    ) -> None:
        """Refuse a position read beyond the `kinds` listed and a listed kind no test reads."""
        highest = max(read, default=0)
        if highest > len(kinds):
            raise InvalidCapabilityError(
                f"CountByConditions: {slot!r} lists {len(kinds)} kinds but the conditions "
                f"read position {highest}"
            )
        for position, kind in enumerate(kinds, start=1):
            if position not in read:
                raise InvalidCapabilityError(
                    f"CountByConditions: {slot!r} lists {kind.identifier!r} at position "
                    f"{position}, which no condition reads"
                )

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        counts = tuple(self._input(inputs, kind).value for kind in self._counts)
        amounts = tuple(self._input(inputs, kind).value for kind in self._amounts)
        values = self._conditions.values
        lines = tuple(
            self._line(position, condition, counts, amounts)
            for position, condition in enumerate(values.conditions, start=1)
        )
        applied = tuple(line.position for line in lines if line.applies)
        count = values.count_when_any_applies if applied else values.count_when_none_applies
        return CapabilityResult(
            outputs=(Artifact(self._output, count),),
            trace=(*lines, ConditionsCountLine(self._output, applied, count)),
        )

    def _line(
        self,
        position: int,
        condition: Condition,
        counts: tuple[int, ...],
        amounts: tuple[Decimal, ...],
    ) -> ConditionLine:
        """Evaluate every test of `condition`, never stopping early, and record what was read."""
        reads: list[tuple[ArtifactKind[int] | Money, int | Decimal]] = []
        held: list[list[bool]] = []
        for part in condition.parts:
            results: list[bool] = []
            for test in part.tests:
                if test.reads == "count":
                    count = counts[test.position - 1]
                    reads.append((self._counts[test.position - 1], count))
                    figure = Decimal(count)
                else:
                    figure = amounts[test.position - 1]
                    reads.append((self._amounts[test.position - 1], figure))
                # A test has exactly one of `than` and `against`.
                if test.against is not None:
                    counterpart = amounts[test.against - 1]
                    reads.append((self._amounts[test.against - 1], counterpart))
                    results.append(test.holds(figure, counterpart))
                elif test.than is not None:
                    results.append(test.holds(figure, test.than))
            held.append(results)
        applies = all(any(results) for results in held)
        return ConditionLine(self._output, position, condition.text, tuple(reads), applies)
