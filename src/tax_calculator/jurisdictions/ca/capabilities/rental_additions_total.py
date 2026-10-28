"""RentalAdditionsTotal: Form T776 Area B (line 9925) or Area C (line 9927), the total of column 5.

Form T776 Area B "Equipment additions in the year" and Area C "Building additions in the year":
"Column 5: Rental portion (column 3 minus column 4)" for each addition of the consumed record list,
and "Line 9925: Total equipment additions in the year: Total of column 5" or "Line 9927: Total
building additions in the year: Total of column 5". Column 3 is the total cost and column 4 the
personal portion; a personal portion above the total cost is not capped but an input error,
`InputAboveBoundError`, naming the item by its position from 1. The output is the sum of every
addition's column 5, exact: it never rounds. With no additions it is 0. It records one
`RentalAdditionLine` for each addition, then one `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    RENTAL_ADDITION_PERSONAL_PORTION,
    RENTAL_ADDITION_TOTAL_COST,
)
from tax_calculator.jurisdictions.ca.trace import RentalAdditionLine


@capability(identifier="rental_additions_total")
class RentalAdditionsTotal(Capability):
    """Produces `total`: the rental portion (total cost less personal portion) of each consumed
    addition, added, no personal portion above its total cost."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"additions": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"total": Decimal}

    def __init__(self, additions: ArtifactKind[RecordList], total: Money) -> None:
        """Wire the capability: the record-list kind of additions it reads and the kind it
        produces."""
        super().__init__(additions=additions, total=total)
        self._additions = additions
        self._total = total

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._additions).value.records
        lines: list[RentalAdditionLine] = []
        for position, record in enumerate(records, start=1):
            class_number, total_cost, personal_portion = (
                record[CCA_CLASS_NUMBER],
                record[RENTAL_ADDITION_TOTAL_COST],
                record[RENTAL_ADDITION_PERSONAL_PORTION],
            )
            for value in (class_number, total_cost, personal_portion):
                if not isinstance(value, Decimal):
                    raise TypeError(
                        f"item {position}: expected a Decimal, got {type(value).__name__}"
                    )
            if personal_portion > total_cost:
                raise InputAboveBoundError(
                    f"item {position}: the personal portion ({personal_portion}) is above the "
                    f"total cost ({total_cost})"
                )
            lines.append(
                RentalAdditionLine(
                    self._total,
                    position,
                    class_number,
                    total_cost,
                    personal_portion,
                    total_cost - personal_portion,
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._total, total),),
            trace=(*lines, ItemsTotalLine(self._total, items, total)),
        )
