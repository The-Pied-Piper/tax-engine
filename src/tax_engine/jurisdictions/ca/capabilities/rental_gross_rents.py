"""RentalGrossRents: the gross rents for all units of the T776 rental properties, added.

Form T776 Part 3 lists the rental properties with "Number of units", "Gross rents for short-term
rentals" and "Gross rents for all units", and line 8141 is the "Total of all your gross rents in the
year you receive them (add lines under "Gross rents for all units")". This capability reads the
record list of those properties and adds the "Gross rents for all units" field of every record,
exactly: it has no dataset, so it never rounds, and an empty list totals zero. Each item is named
by its position from 1 in the trace.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import RecordTotalLine
from tax_engine.jurisdictions.ca.catalog import RENTAL_PROPERTY_GROSS_RENTS


@capability(identifier="rental_gross_rents")
class RentalGrossRents(Capability):
    """Produces `output`: the gross rents for all units of every consumed `properties` record."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"properties": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, properties: ArtifactKind[RecordList], output: Money) -> None:
        """Wire the capability: the record-list kind it reads and the kind it produces."""
        super().__init__(properties=properties, output=output)
        self._properties = properties
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amounts: list[Decimal] = []
        for record in self._input(inputs, self._properties).value.records:
            amount = record[RENTAL_PROPERTY_GROSS_RENTS]
            if not isinstance(amount, Decimal):
                raise TypeError(
                    f"{RENTAL_PROPERTY_GROSS_RENTS.identifier} must be a Decimal, "
                    f"got {type(amount).__name__}"
                )
            amounts.append(amount)
        total = sum(amounts, Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(
                RecordTotalLine(
                    output=self._output,
                    field=RENTAL_PROPERTY_GROSS_RENTS,
                    amounts=tuple(amounts),
                    total=total,
                ),
            ),
        )
