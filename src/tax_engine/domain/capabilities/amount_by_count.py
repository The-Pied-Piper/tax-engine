"""Amount by count: the figure a form prints against a count, read from a table.

For lines that look an amount up in a printed table keyed by a count (the months a plan applied,
say): the output is `rounding.apply(row)`, the figure of the `table` dataset's row for the
consumed count, rounded once with that dataset's rule, which defaults to no rounding. A count
with no row is not guessed at, floored or carried over from the nearest row: it raises
`NoAmountForCountError`.

The class is `AmountForCount` so that it does not share a name with the `AmountByCount` value
object it reads.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import NoAmountForCountError
from tax_engine.domain.parameters.amount_by_count import AMOUNT_BY_COUNT, AmountByCount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import AmountByCountLine


@capability(identifier="amount_by_count")
class AmountForCount(Capability):
    """Produces `output`: the `table`'s row for the consumed `count`, rounded by its rule."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[AmountByCount]]] = {"table": AMOUNT_BY_COUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"count": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self, table: ParameterDataset[AmountByCount], count: ArtifactKind[int], output: Money
    ) -> None:
        """Wire the capability: its table dataset, the count it reads, the kind it produces."""
        super().__init__(count=count, output=output)
        self._table = table
        self._count = count
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        count = self._input(inputs, self._count).value
        rounding = self._table.rounding
        rows = dict(self._table.values.rows)
        if count not in rows:
            raise NoAmountForCountError(
                f"{self._table.family} has no amount for count {count} of {self._count.identifier}:"
                " the count was supplied by the caller and the printed table has no row for it,"
                " so the request is refused as invalid rather than answered with a guessed row"
            )
        row = rows[count]
        result = rounding.apply(row)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(AmountByCountLine(self._output, self._count, count, row, rounding, result),),
        )
