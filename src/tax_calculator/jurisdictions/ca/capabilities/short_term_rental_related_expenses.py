"""ShortTermRentalRelatedExpenses: the related expenses of the short-term rentals, added.

Form T776 Chart A, "Enter each short-term rental or mixed rental property on a separate row", has
the column
"Column 3: Related portion of the total from line 9365 of Part 4", the part of the short-term
rental portion of the expenses that each row carries. This capability reads the record
list of those rows and adds the column 3 field of every record, exactly: it has no dataset, so it
never rounds, and an empty list totals zero. Each item is named by its position from 1 in the
trace. The total is checked at most line 9365 by the form's steps, not here.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import RecordTotalLine
from tax_calculator.jurisdictions.ca.catalog import SHORT_TERM_RENTAL_RELATED_EXPENSES


@capability(identifier="short_term_rental_related_expenses")
class ShortTermRentalRelatedExpenses(Capability):
    """Produces `output`: the related expenses of every record of the consumed `units`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"units": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, units: ArtifactKind[RecordList], output: Money) -> None:
        """Wire the capability: the record-list kind it reads and the kind it produces."""
        super().__init__(units=units, output=output)
        self._units = units
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amounts: list[Decimal] = []
        for record in self._input(inputs, self._units).value.records:
            amount = record[SHORT_TERM_RENTAL_RELATED_EXPENSES]
            if not isinstance(amount, Decimal):
                raise TypeError(
                    f"{SHORT_TERM_RENTAL_RELATED_EXPENSES.identifier} must be a Decimal, "
                    f"got {type(amount).__name__}"
                )
            amounts.append(amount)
        total = sum(amounts, Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(
                RecordTotalLine(
                    output=self._output,
                    field=SHORT_TERM_RENTAL_RELATED_EXPENSES,
                    amounts=tuple(amounts),
                    total=total,
                ),
            ),
        )
