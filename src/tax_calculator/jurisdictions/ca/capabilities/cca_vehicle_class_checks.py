"""CcaVehicleClassChecks: the check of the class condition of each passenger vehicle of Form T777
Part B, the rows passed on unchanged.

Guide T4044 2025, "Class 10.1": "Your passenger vehicle can belong to Class 10 or Class 10.1. You
only include a passenger vehicle in Class 10.1 if it meets certain conditions." and "Include your
passenger vehicle in Class 10.1 if it meets one of the following conditions: - You acquired it after
December 31, 2000, and before January 1, 2022, and it cost you more than $30,000 - ... - You
acquired it after December 31, 2024, and it cost you more than $38,000. If your passenger vehicle
does not meet any of these conditions, then it belongs in Class 10." and "To determine what class
your passenger vehicle belongs to, do not include the GST and PST or HST when calculating the cost
of the vehicle."

The "Date acquired (yyyy-mm-dd)" is printed on every row of Part B, so it is required on every row:
a row with no date acquired (year 0) is refused, whatever its class. So the "Cost of vehicle"
(before tax) of a Class 10.1 row, with its "Date acquired" (its year), must be more than the
`class_conditions` amount (`minimum_cost`) of the row for that year, else the row is refused: the
vehicle belongs in Class 10, which Part A calculates, not in Part B.
A year before the oldest row of the dataset (before 2001) meets none of the conditions and is
refused. A cost equal to the amount is refused too ("more than"). A row with a date acquired but a
class other than 10.1 is not checked.
Each record of the consumed `classes` is checked on its own, and the output is a record list of the
same fields in the caller's order. It records one `CcaVehicleClassCheckLine` for each row, by
position, whether it was checked, its year, cost and minimum (0 when it was not checked); a refused
row is named by its error (`InvalidRecordError`).
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts
from tax_calculator.domain.record_list import Record, RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
)
from tax_calculator.jurisdictions.ca.trace import CcaVehicleClassCheckLine

CLASS_10_1 = Decimal("10.1")


@capability(identifier="cca_vehicle_class_checks")
class CcaVehicleClassChecks(Capability):
    """Produces `output`: the consumed `classes` (the Part B rows), unchanged, once the cost before
    tax of each Class 10.1 vehicle has passed the condition of its year (Guide T4044 2025,
    "Class 10.1"), and every row has a date acquired."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "class_conditions": YEAR_AMOUNTS,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"classes": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": RecordList}

    def __init__(
        self,
        class_conditions: ParameterDataset[YearAmounts],
        classes: ArtifactKind[RecordList],
        output: RecordListKind,
    ) -> None:
        """Wire the capability: its class conditions dataset (Class 10.1), the record list it
        reads, the record list kind it passes on."""
        super().__init__(classes=classes, output=output)
        self._class_conditions = class_conditions.values
        self._classes = classes
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._classes).value.records
        passed: list[dict[ArtifactKind[Any], Decimal | int]] = []
        lines: list[CcaVehicleClassCheckLine] = []
        for position, record in enumerate(records, 1):
            year = record[CCA_VEHICLE_ACQUIRED_YEAR]
            cost = record[CCA_VEHICLE_COST]
            if year == 0:
                raise InvalidRecordError(
                    f"item {position}: the date acquired is required: enter the year the "
                    f"vehicle was acquired"
                )
            checked = record[CCA_CLASS_NUMBER] == CLASS_10_1
            minimum = self._minimum(position, year) if checked else Decimal(0)
            if checked and cost <= minimum:
                raise InvalidRecordError(
                    f"item {position}: a vehicle acquired in {year} that cost {cost:.2f} before "
                    f"tax is not more than {minimum:.2f}, so it belongs in Class 10, not Class 10.1"
                )
            lines.append(
                CcaVehicleClassCheckLine(self._output, position, checked, year, cost, minimum)
            )
            passed.append(self._passed(record))
        return CapabilityResult(
            outputs=(Artifact(self._output, RecordList(self._output.fields, passed)),),
            trace=tuple(lines),
        )

    def _minimum(self, position: int, year: int) -> Decimal:
        """The cost a Class 10.1 vehicle acquired in `year` must be more than."""
        found = self._class_conditions.row_for(year)
        if found is None:
            raise InvalidRecordError(
                f"item {position}: a vehicle acquired in {year} meets none of the Class 10.1 "
                f"conditions, so it belongs in Class 10, not Class 10.1"
            )
        return found.amount("minimum_cost")

    def _passed(self, record: Record) -> dict[ArtifactKind[Any], Decimal | int]:
        """The row as it is passed on: the fields of the output, as entered."""
        return {field: record[field] for field in self._output.fields}
