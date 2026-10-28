"""CcaVehicleAdditionsChecks: the check of the cost of additions of each Class 10.1 passenger
vehicle of the CCA table of Form T2125 Area A (and of Forms T2042 and T2121, which share the
table; of Form T776 Area A, the rental table; and of Form T777 Part B, the employee vehicles), the
rows passed on unchanged.

Guide T4002 2025, "Class 10.1 (30%)": "Include your passenger vehicle in Class 10.1 if you bought it
in 2025 and it cost more than $38,000 before tax. List each Class 10.1 vehicle separately. The
capital cost limits of a Class 10.1 passenger vehicle are the following prescribed amounts: ...
$38,000 for vehicles acquired in 2025, plus the GST/HST or PST." and "Use the GST rate of 5% and the
appropriate PST rate for your province or territory. If your province is a participating province,
use the appropriate HST rate."

So the cost of additions (column 3) of a Class 10.1 row, which is a vehicle bought in the tax year,
is refused when it is more than the prescribed amount of the tax year plus the same amount times
the consumed `sales_tax_rate` (in percent), rounded once with the dataset's rule; the form has the
filer enter the capped amount, so the figure is refused, not capped. Additions equal to the limit
pass. A Class 10.1 row with no additions (a vehicle owned from the previous year, with its UCC at
the start of the year) and a row of another class are not checked. Each record of the consumed
`classes` is checked on its own, and the output is a record list of the same fields in the caller's
order. It records one `CcaVehicleAdditionsCheckLine` for each row, by position, whether it was
checked, its additions and its limit (0 when it was not checked); a refused row is named by its
error (`InvalidRecordError`).
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts
from tax_calculator.domain.record_list import Record, RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.cca_vehicle_proceeds import (
    prescribed_amount_with_tax,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CLASS_NUMBER,
)
from tax_calculator.jurisdictions.ca.trace import CcaVehicleAdditionsCheckLine

CLASS_10_1 = Decimal("10.1")


@capability(identifier="cca_vehicle_additions_checks")
class CcaVehicleAdditionsChecks(Capability):
    """Produces `output`: the consumed `classes` (the Area A rows), unchanged, once the cost of
    additions of each Class 10.1 vehicle has passed its limit with tax (Guide T4002 2025,
    "Class 10.1 (30%)")."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "prescribed_amounts": YEAR_AMOUNTS,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"classes": RecordList, "sales_tax_rate": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": RecordList}

    def __init__(
        self,
        prescribed_amounts: ParameterDataset[YearAmounts],
        classes: ArtifactKind[RecordList],
        sales_tax_rate: Money,
        output: RecordListKind,
    ) -> None:
        """Wire the capability: its prescribed amounts dataset (Class 10.1), the record list and
        the sales tax rate it reads, the record list kind it passes on."""
        super().__init__(classes=classes, sales_tax_rate=sales_tax_rate, output=output)
        self._prescribed_amounts = prescribed_amounts.values
        self._tax_year: int = prescribed_amounts.tax_year
        self._rounding: RoundingRule = prescribed_amounts.rounding
        self._classes = classes
        self._sales_tax_rate = sales_tax_rate
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._classes).value.records
        rate = self._input(inputs, self._sales_tax_rate).value
        passed: list[dict[ArtifactKind[Any], Decimal | int]] = []
        lines: list[CcaVehicleAdditionsCheckLine] = []
        for position, record in enumerate(records, 1):
            additions = Decimal(record[CCA_ADDITIONS])
            checked = record[CCA_CLASS_NUMBER] == CLASS_10_1 and additions > 0
            limit = self._limit(position, rate) if checked else Decimal(0)
            if checked and additions > limit:
                raise InvalidRecordError(
                    f"item {position}: additions ({additions:.2f}) are more than the Class 10.1 "
                    f"limit with tax ({limit:.2f}) at a sales tax rate of {rate}%, which is GST "
                    f"plus PST, or HST"
                )
            lines.append(
                CcaVehicleAdditionsCheckLine(self._output, position, checked, additions, limit)
            )
            passed.append(self._passed(record))
        return CapabilityResult(
            outputs=(Artifact(self._output, RecordList(self._output.fields, passed)),),
            trace=tuple(lines),
        )

    def _limit(self, position: int, rate: Decimal) -> Decimal:
        """The limit with tax of a Class 10.1 vehicle bought in the tax year: its prescribed amount
        plus the same amount at `rate` (in percent), rounded once with the dataset's rule."""
        limit = prescribed_amount_with_tax(
            self._prescribed_amounts, self._rounding, self._tax_year, rate
        )
        if limit is None:
            raise InvalidRecordError(f"item {position}: no prescribed amount for {self._tax_year}")
        return limit

    def _passed(self, record: Record) -> dict[ArtifactKind[Any], Decimal | int]:
        """The row as it is passed on: the fields of the output, as entered."""
        return {field: record[field] for field in self._output.fields}
