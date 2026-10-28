"""ChartBZoneTotal: the base of the two Chart B zone totals of Form T2222, not registered itself.

For Step 3, Chart B: "Enter the lowest amount from column 3, 4, or 5 in the column for the
prescribed zone(s) you resided in at the time of the trip.", one record for each trip in the
consumed record list. A trip in the zone of the subclass counts the lowest of its three columns;
a trip in the other zone counts nothing. The output is the total of those amounts, exact: there
is no dataset, so it never rounds. A subclass is one capability for each zone's total, named by
its `ZONE`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemLesserOfLine, ItemsTotalLine
from tax_calculator.jurisdictions.ca.catalog import (
    TRIP_BENEFIT_OR_STANDARD_AMOUNT,
    TRIP_LOWEST_RETURN_AIRFARE,
    TRIP_TRAVEL_EXPENSES,
    TRIP_ZONE,
)

ZONE_A = 1
ZONE_B = 2


class ChartBZoneTotal(Capability):
    """Produces `total`: the lowest of columns 3, 4 and 5 of each consumed trip in `ZONE`, added.

    A trip whose zone is neither 1 (Zone A) nor 2 (Zone B) is an InvalidRecordError naming the
    item by its position from 1.
    """

    ZONE: ClassVar[int]
    CONSUMES: ClassVar[Mapping[str, type]] = {"trips": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"total": Decimal}

    def __init__(self, trips: ArtifactKind[RecordList], total: Money) -> None:
        """Wire the capability: the record-list kind of trips it reads and the kind it produces."""
        super().__init__(trips=trips, total=total)
        self._trips = trips
        self._total = total

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        columns = (
            TRIP_BENEFIT_OR_STANDARD_AMOUNT,
            TRIP_TRAVEL_EXPENSES,
            TRIP_LOWEST_RETURN_AIRFARE,
        )
        lines: list[ItemLesserOfLine] = []
        for position, record in enumerate(self._input(inputs, self._trips).value.records, start=1):
            zone = record[TRIP_ZONE]
            if zone not in (ZONE_A, ZONE_B):
                raise InvalidRecordError(
                    f"item {position}: {TRIP_ZONE.identifier} must be {ZONE_A} (Zone A) or "
                    f"{ZONE_B} (Zone B), got {zone}"
                )
            if zone != self.ZONE:
                continue
            parts: list[tuple[ArtifactKind[Any], Decimal]] = []
            for kind in columns:
                amount = record[kind]
                if not isinstance(amount, Decimal):
                    raise TypeError(
                        f"{kind.identifier} must be a Decimal, got {type(amount).__name__}"
                    )
                parts.append((kind, amount))
            lowest = min(amount for _kind, amount in parts)
            lines.append(ItemLesserOfLine(self._total, position, tuple(parts), lowest))
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._total, total),),
            trace=(*lines, ItemsTotalLine(self._total, items, total)),
        )
