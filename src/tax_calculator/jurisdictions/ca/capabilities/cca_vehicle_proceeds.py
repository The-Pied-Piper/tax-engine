"""CcaVehicleProceeds: the proceeds of disposition of a Class 10.1 passenger vehicle scaled to its
prescribed amount, for the CCA table of Form T2125 Area A (columns 5 and 6).

T2125 (2025) Area A endnote 2 (T776 Column 5 Note 2, and T2042 and T2121 endnote 2, say the same):
"The proceeds of disposition of a zero-emission passenger vehicle (ZEPV) that has been included in
Class 54, or a passenger vehicle bought after April 18, 2021, that has been included in Class
10.1, and whose cost is more than the prescribed amount will be adjusted based on a factor equal
to its prescribed amount as a proportion of the actual cost of the vehicle. For dispositions after
July 29, 2019, you will have to adjust the actual cost of the vehicle for any payments or
repayments of government assistance that you may have received or repaid for the vehicle. If the
passenger vehicle in Class 10.1 is not designated for immediate expensing treatment, this special
rule does not apply." Guide T4036, "Class 10.1 (30%)": the prescribed amounts are $30,000
(acquired before 2022), $34,000 (2022), $36,000 (2023), $37,000 (2024) and $38,000 (2025), each
"plus the GST/HST or PST".

Each record of the consumed `classes` is one row of the table. A record holds the year the vehicle
was acquired (0 when the rule does not apply to the row, which the caller decides: the vehicle is
not designated for immediate expensing, or was not sold at arm's length), its actual cost and the
government assistance received less repaid. A row (or sold vehicle) of year 0 is copied as it is,
and refused when a cost or assistance (a repayment too) is entered with it (`InvalidRecordError`,
naming the item). For a year, the class must be 10.1 (Class 54 is not modelled) and the year 2021 or
later (a vehicle bought after April 18, 2021), else the row is refused (`InvalidRecordError`, naming
the item); a year later than the newest row of the `prescribed_amounts` dataset uses that row. The
prescribed amount with tax is the year's amount plus that amount times the consumed `sales_tax_rate`
(the caller's GST or HST rate, in percent), rounded; the actual cost is the cost less the
assistance. When the actual cost is more than the prescribed amount with tax, the proceeds (column
5) and the DIEP part of them (column 6) each become the exact product of the column and the
prescribed amount with tax over the actual cost, rounded once with the dataset's rule; otherwise
they are unchanged. The output is a record list of the row's other fields, one record per row in the
caller's order. It records one `CcaVehicleProceedsLine` for each row, by position from 1, and no
total.

Guide T4036 2025, "Class 54 (30%)": "If a zero-emission passenger vehicle is disposed of to a
person or partnership with whom you deal at arm's length, and its cost exceeds the prescribed
amount ($55,000 for vehicles acquired after March 18, 2019, and before January 1, 2022; $59,000
for vehicles acquired after December 31, 2021, and before January 1, 2023; or $61,000 for vehicles
acquired after December 31, 2022), the proceeds of disposition will be adjusted based on a factor
equal to the prescribed amount as a proportion of the actual cost of the vehicle." A Class 54 row
also holds the list of its sold zero-emission passenger vehicles (`ca/cca_sold_zepvs`), which may
be non-empty only on a Class 54 row, else the row is refused (`InvalidRecordError`, naming the item
and the vehicle). Each vehicle of a year is scaled on its own, with the `zepv_prescribed_amounts`
dataset (a year before its oldest row is refused) and the same rule as a Class 10.1 vehicle; a
vehicle of year 0 is copied as entered. Columns 5 and 6 of a Class 54 row are the sum of the
proceeds of its vehicles, scaled, and nothing is entered in them on the row itself: a Class 54
row with an amount entered in either column is refused (`InvalidRecordError`, naming the item).
Each vehicle records one `CcaZepvProceedsLine` after the row's own line, by position of the row and
of the vehicle from 1. A Class 54 row does not use the year, cost and assistance of Class 10.1.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts
from tax_calculator.domain.record_list import Record, RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_DIEP_PROCEEDS,
    CCA_PROCEEDS,
    CCA_SOLD_ZEPVS,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
    CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
    CCA_ZEPV_DIEP_PROCEEDS,
    CCA_ZEPV_PROCEEDS,
)
from tax_calculator.jurisdictions.ca.trace import CcaVehicleProceedsLine, CcaZepvProceedsLine

CLASS_10_1 = Decimal("10.1")
CLASS_54 = Decimal(54)
FIRST_YEAR = 2021  # "a passenger vehicle bought after April 18, 2021"


def prescribed_amount_with_tax(
    amounts: YearAmounts, rounding: RoundingRule, year: int, rate: Decimal
) -> Decimal | None:
    """The prescribed amount of `year` plus the same amount at `rate` (in percent), the tax rounded
    once with `rounding`; None when `amounts` has no row for `year`."""
    found = amounts.row_for(year)
    if found is None:
        return None
    printed = found.amount("prescribed_amount")
    return printed + rounding.apply(ExactFraction(printed) * ExactFraction(rate) / 100)


@dataclass(frozen=True)
class _Scaled:
    """The proceeds of one vehicle after the adjustment, with the figures that worked it out."""

    applied: bool
    prescribed: Decimal
    actual_cost: Decimal
    proceeds: Decimal
    diep_proceeds: Decimal


@capability(identifier="cca_vehicle_proceeds")
class CcaVehicleProceeds(Capability):
    """Produces `output`: the consumed `classes` with the proceeds of each Class 10.1 vehicle and
    of each zero-emission passenger vehicle sold from a Class 54 row scaled to its prescribed
    amount, at the consumed `sales_tax_rate`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "prescribed_amounts": YEAR_AMOUNTS,
        "zepv_prescribed_amounts": YEAR_AMOUNTS,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"classes": RecordList, "sales_tax_rate": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": RecordList}

    def __init__(
        self,
        prescribed_amounts: ParameterDataset[YearAmounts],
        zepv_prescribed_amounts: ParameterDataset[YearAmounts],
        classes: ArtifactKind[RecordList],
        sales_tax_rate: Money,
        output: RecordListKind,
    ) -> None:
        """Wire the capability: its prescribed amounts datasets (Class 10.1 and Class 54), the
        record list and the sales tax rate it reads, the record list kind produced."""
        super().__init__(classes=classes, sales_tax_rate=sales_tax_rate, output=output)
        self._prescribed_amounts = prescribed_amounts.values
        self._rounding: RoundingRule = prescribed_amounts.rounding
        self._zepv_prescribed_amounts = zepv_prescribed_amounts.values
        self._zepv_rounding: RoundingRule = zepv_prescribed_amounts.rounding
        self._classes = classes
        self._sales_tax_rate = sales_tax_rate
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        rows = self._input(inputs, self._classes).value.records
        rate = self._input(inputs, self._sales_tax_rate).value
        lines: list[CcaVehicleProceedsLine | CcaZepvProceedsLine] = []
        records: list[dict[ArtifactKind[Any], Decimal | int]] = []
        for position, row in enumerate(rows, 1):
            row_line, record = self._row(position, row, rate)
            lines.append(row_line)
            lines.extend(self._sold(position, row, rate, record))
            records.append(record)
        return CapabilityResult(
            outputs=(Artifact(self._output, RecordList(self._output.fields, records)),),
            trace=tuple(lines),
        )

    @staticmethod
    def _scale(
        where: str,
        year: int,
        cost: Decimal,
        assistance: Decimal,
        proceeds: Decimal,
        diep_proceeds: Decimal,
        rate: Decimal,
        amounts: YearAmounts,
        rounding: RoundingRule,
    ) -> _Scaled:
        """The proceeds of a vehicle acquired in `year` scaled to the prescribed amount of `amounts`
        (plus the tax at `rate`) when its actual cost is more; unchanged for year 0, which is
        refused when a cost or assistance is entered with it."""
        if year <= 0:
            if cost != 0 or assistance != 0:
                raise InvalidRecordError(
                    f"{where}: a vehicle cost or government assistance is entered but the "
                    f"vehicle year is 0"
                )
            return _Scaled(False, Decimal(0), Decimal(0), proceeds, diep_proceeds)
        prescribed = prescribed_amount_with_tax(amounts, rounding, year, rate)
        if prescribed is None:
            raise InvalidRecordError(f"{where}: no prescribed amount for {year}")
        actual_cost = cost - assistance
        if actual_cost <= prescribed:
            return _Scaled(False, prescribed, actual_cost, proceeds, diep_proceeds)
        factor = ExactFraction(prescribed) / ExactFraction(actual_cost)
        return _Scaled(
            True,
            prescribed,
            actual_cost,
            rounding.apply(ExactFraction(proceeds) * factor),
            rounding.apply(ExactFraction(diep_proceeds) * factor),
        )

    def _row(
        self, position: int, row: Record, rate: Decimal
    ) -> tuple[CcaVehicleProceedsLine, dict[ArtifactKind[Any], Decimal | int]]:
        """The line and the output record of one row, before the sold vehicles are added."""
        proceeds = row[CCA_PROCEEDS]
        diep_proceeds = row[CCA_DIEP_PROCEEDS]
        year = row[CCA_VEHICLE_ACQUIRED_YEAR]
        if year > 0:
            if row[CCA_CLASS_NUMBER] != CLASS_10_1:
                raise InvalidRecordError(
                    f"item {position}: a vehicle year is given but the class is "
                    f"{row[CCA_CLASS_NUMBER]}, not 10.1"
                )
            if year < FIRST_YEAR:
                raise InvalidRecordError(
                    f"item {position}: a vehicle acquired in {year} is not a passenger vehicle "
                    f"bought after April 18, 2021"
                )
        scaled = self._scale(
            f"item {position}",
            year,
            row[CCA_VEHICLE_COST],
            row[CCA_VEHICLE_GOVERNMENT_ASSISTANCE],
            proceeds,
            diep_proceeds,
            rate,
            self._prescribed_amounts,
            self._rounding,
        )
        record: dict[ArtifactKind[Any], Decimal | int] = {
            field: row[field] for field in self._output.fields
        }
        record[CCA_PROCEEDS] = scaled.proceeds
        record[CCA_DIEP_PROCEEDS] = scaled.diep_proceeds
        line = CcaVehicleProceedsLine(
            self._output,
            position,
            scaled.applied,
            scaled.prescribed,
            scaled.actual_cost,
            proceeds,
            scaled.proceeds,
            diep_proceeds,
            scaled.diep_proceeds,
        )
        return line, record

    def _sold(
        self,
        position: int,
        row: Record,
        rate: Decimal,
        record: dict[ArtifactKind[Any], Decimal | int],
    ) -> list[CcaZepvProceedsLine]:
        """The lines of the vehicles sold from the row `position`, and their scaled proceeds as
        columns 5 and 6 of its output `record`; the vehicles of a row of another class than 54 are
        refused, and so is an amount entered in column 5 or 6 of a Class 54 row."""
        vehicles = row[CCA_SOLD_ZEPVS].records
        if row[CCA_CLASS_NUMBER] == CLASS_54 and (row[CCA_PROCEEDS] or row[CCA_DIEP_PROCEEDS]):
            raise InvalidRecordError(
                f"item {position}: an amount is entered in column 5 or 6 of a Class 54 row; "
                f"a Class 54 sale price must be listed as a vehicle"
            )
        if not vehicles:
            return []
        if row[CCA_CLASS_NUMBER] != CLASS_54:
            raise InvalidRecordError(
                f"item {position} vehicle 1: sold vehicles are given but the class is "
                f"{row[CCA_CLASS_NUMBER]}, not 54"
            )
        lines: list[CcaZepvProceedsLine] = []
        proceeds = Decimal(0)
        diep_proceeds = Decimal(0)
        for number, vehicle in enumerate(vehicles, 1):
            entered = vehicle[CCA_ZEPV_PROCEEDS]
            entered_diep = vehicle[CCA_ZEPV_DIEP_PROCEEDS]
            scaled = self._scale(
                f"item {position} vehicle {number}",
                vehicle[CCA_VEHICLE_ACQUIRED_YEAR],
                vehicle[CCA_VEHICLE_COST],
                vehicle[CCA_VEHICLE_GOVERNMENT_ASSISTANCE],
                entered,
                entered_diep,
                rate,
                self._zepv_prescribed_amounts,
                self._zepv_rounding,
            )
            proceeds += scaled.proceeds
            diep_proceeds += scaled.diep_proceeds
            lines.append(
                CcaZepvProceedsLine(
                    self._output,
                    position,
                    number,
                    scaled.applied,
                    scaled.prescribed,
                    scaled.actual_cost,
                    entered,
                    scaled.proceeds,
                    entered_diep,
                    scaled.diep_proceeds,
                )
            )
        record[CCA_PROCEEDS] = proceeds
        record[CCA_DIEP_PROCEEDS] = diep_proceeds
        return lines
