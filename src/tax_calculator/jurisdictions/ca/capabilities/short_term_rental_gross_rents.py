"""ShortTermRentalGrossRents: the gross rents for short-term rentals of the T776 properties, added.

Form T776 Part 3 lists the rental properties with "Number of units", "Gross rents for short-term
rentals" and "Gross rents for all units", and line 8140 is the "Total of your gross rents for
short-term rentals in the year you receive them (add amounts under "Gross rents for short-term
rentals")". This capability reads the record list of those properties and adds the "Gross rents
for short-term rentals" field of every record, exactly: it has no dataset, so it never rounds, and
an empty list totals zero. Each item is named by its position from 1 in the trace. The short-term
rents of a row are part of its "Gross rents for all units", so a row whose short-term rents are
above its gross rents is refused (`InputAboveBoundError`, naming the item and both fields), not
capped; equal is valid, and a row with no rents is valid.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import RecordTotalLine
from tax_calculator.jurisdictions.ca.catalog import (
    RENTAL_PROPERTY_GROSS_RENTS,
    RENTAL_PROPERTY_SHORT_TERM_RENTS,
)


@capability(identifier="short_term_rental_gross_rents")
class ShortTermRentalGrossRents(Capability):
    """Produces `output`: the short-term rents of every record of the consumed `properties`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"properties": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, properties: ArtifactKind[RecordList], output: Money) -> None:
        """Wire the capability: the record-list kind it reads and the kind it produces."""
        super().__init__(properties=properties, output=output)
        self._properties = properties
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amounts: list[Decimal] = []
        for position, record in enumerate(self._input(inputs, self._properties).value.records, 1):
            amount = record[RENTAL_PROPERTY_SHORT_TERM_RENTS]
            if not isinstance(amount, Decimal):
                raise TypeError(
                    f"{RENTAL_PROPERTY_SHORT_TERM_RENTS.identifier} must be a Decimal, "
                    f"got {type(amount).__name__}"
                )
            gross = record[RENTAL_PROPERTY_GROSS_RENTS]
            if not isinstance(gross, Decimal):
                raise TypeError(
                    f"{RENTAL_PROPERTY_GROSS_RENTS.identifier} must be a Decimal, "
                    f"got {type(gross).__name__}"
                )
            if amount > gross:
                raise InputAboveBoundError(
                    f"item {position}: {RENTAL_PROPERTY_SHORT_TERM_RENTS.identifier} {amount} "
                    f"is above {RENTAL_PROPERTY_GROSS_RENTS.identifier} {gross}"
                )
            amounts.append(amount)
        total = sum(amounts, Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(
                RecordTotalLine(
                    output=self._output,
                    field=RENTAL_PROPERTY_SHORT_TERM_RENTS,
                    amounts=tuple(amounts),
                    total=total,
                ),
            ),
        )
