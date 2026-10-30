"""ChartARowCTotal: Form T2222 Step 3, Chart A, row C for each individual, added.

"Row B: Enter the name of everyone (including yourself) who is claiming a deduction for trips
taken by the individual in row A and the total portion of the $1,200 standard amount allocated by
each claimant for all trips taken by that individual." and "Row C: Enter the total of all amounts
in row B. This total cannot be more than $1,200." For each individual in the consumed record list,
row C is the sum of the three row B amounts; a row C above the `maximum` dataset's amount is not
capped but an input error, `InputAboveBoundError`, naming the item by its position from 1. The
output is the sum of every individual's row C, exact: it never rounds, and the limit is each
individual's, not all of them together.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine, ItemSumLine
from tax_engine.jurisdictions.ca.catalog import (
    STANDARD_AMOUNT_ALLOCATED_1,
    STANDARD_AMOUNT_ALLOCATED_2,
    STANDARD_AMOUNT_ALLOCATED_3,
)

_ROW_B = (STANDARD_AMOUNT_ALLOCATED_1, STANDARD_AMOUNT_ALLOCATED_2, STANDARD_AMOUNT_ALLOCATED_3)


@capability(identifier="chart_a_row_c_total")
class ChartARowCTotal(Capability):
    """Produces `total`: the row C of each consumed individual, added, none above `maximum`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"maximum": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"individuals": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"total": Decimal}

    def __init__(
        self,
        maximum: ParameterDataset[Amount],
        individuals: ArtifactKind[RecordList],
        total: Money,
    ) -> None:
        """Wire the capability: the bound on row C, the record-list kind of individuals it reads
        and the kind it produces."""
        super().__init__(individuals=individuals, total=total)
        self._maximum = maximum
        self._individuals = individuals
        self._total = total

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        bound = self._maximum.values.value
        records = self._input(inputs, self._individuals).value.records
        lines: list[ItemSumLine] = []
        for position, record in enumerate(records, start=1):
            parts: list[tuple[ArtifactKind[Any], Decimal]] = []
            for kind in _ROW_B:
                amount = record[kind]
                if not isinstance(amount, Decimal):
                    raise TypeError(
                        f"{kind.identifier} must be a Decimal, got {type(amount).__name__}"
                    )
                parts.append((kind, amount))
            row_c = sum((amount for _kind, amount in parts), Decimal(0))
            if row_c > bound:
                raise InputAboveBoundError(
                    f"item {position}: This total cannot be more than ${bound:,}."
                )
            lines.append(ItemSumLine(self._total, position, tuple(parts), row_c))
        items = tuple((line.position, line.total) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._total, total),),
            trace=(*lines, ItemsTotalLine(self._total, items, total)),
        )
