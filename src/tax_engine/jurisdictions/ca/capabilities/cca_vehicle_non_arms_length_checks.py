"""CcaVehicleNonArmsLengthChecks: the check of the cost of additions of each Class 10.1 passenger
vehicle of Form T777 Part B bought from a non-arm's-length person, the rows passed on unchanged.

Guide T4044 2025, Part B "Column 3 - Cost of additions in the year": "There is a limit on the
capital cost of a Class 10.1 vehicle you buy from a person with whom you have a non-arm's length
relationship. [...] In this case, the capital cost is the least of the following three amounts: -
the fair market value of the vehicle when you acquired it - $38,000 plus the GST and PST or HST
that you would have paid on $38,000 if you had acquired the vehicle in 2025 - the seller's cost of
the vehicle just before you acquired it."

So the cost of additions (column 3) of a Class 10.1 row with additions that the filer answers as
bought from a non-arm's-length person must be the least of its fair market value, the limit with
tax (the prescribed amount of the tax year plus the same amount at the consumed `sales_tax_rate`,
in percent, rounded once with the dataset's rule: the figure `ca/cca_vehicle_additions_checks`
refuses above) and its seller's cost; the form has the filer enter that amount, so a different
figure is refused, not replaced. The answer is 0 or 1; any other is refused. A row not answered as
bought from such a person, a Class 10.1 row with no additions (a vehicle owned from the previous
year) and a row of another class are not checked. Each record of the consumed `classes` is checked
on its own, and the output is a record list of the same fields in the caller's order. It records
one `CcaVehicleNonArmsLengthCheckLine` for each row, by position, whether it was checked, its
additions, its fair market value, limit and seller's cost and the capital cost (0 when it was not
checked); a refused row is named by its error (`InvalidRecordError`).
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidRecordError
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts
from tax_engine.domain.record_list import Record, RecordList, RecordListKind
from tax_engine.jurisdictions.ca.capabilities.cca_vehicle_proceeds import (
    prescribed_amount_with_tax,
)
from tax_engine.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CLASS_NUMBER,
    CCA_VEHICLE_FROM_NON_ARMS_LENGTH,
    CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE,
    CCA_VEHICLE_SELLER_COST,
)
from tax_engine.jurisdictions.ca.trace import CcaVehicleNonArmsLengthCheckLine

CLASS_10_1 = Decimal("10.1")


@capability(identifier="cca_vehicle_non_arms_length_checks")
class CcaVehicleNonArmsLengthChecks(Capability):
    """Produces `output`: the consumed `classes` (the Part B rows), unchanged, once the cost of
    additions of each Class 10.1 vehicle bought from a non-arm's-length person is the least of its
    three amounts (Guide T4044 2025, Part B column 3)."""

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
        lines: list[CcaVehicleNonArmsLengthCheckLine] = []
        for position, record in enumerate(records, 1):
            answer = int(record[CCA_VEHICLE_FROM_NON_ARMS_LENGTH])
            if answer > 1:
                raise InvalidRecordError(
                    f"item {position}: bought from a non-arm's-length person is {answer}, "
                    f"but it is 1 for yes or 0 for no"
                )
            additions = Decimal(record[CCA_ADDITIONS])
            checked = record[CCA_CLASS_NUMBER] == CLASS_10_1 and additions > 0 and answer == 1
            market = (
                Decimal(record[CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE])
                if checked
                else Decimal(0)
            )
            seller = Decimal(record[CCA_VEHICLE_SELLER_COST]) if checked else Decimal(0)
            limit = self._limit(position, rate) if checked else Decimal(0)
            cost = min(market, limit, seller) if checked else Decimal(0)
            if checked and additions != cost:
                raise InvalidRecordError(
                    f"item {position}: additions ({additions:.2f}) of a vehicle bought from a "
                    f"non-arm's-length person are not the least of its fair market value "
                    f"({market:.2f}), the limit with tax ({limit:.2f}) at a sales tax rate of "
                    f"{rate}% and the seller's cost ({seller:.2f}), which is {cost:.2f}"
                )
            lines.append(
                CcaVehicleNonArmsLengthCheckLine(
                    self._output,
                    position,
                    checked,
                    additions,
                    market,
                    limit,
                    seller,
                    cost,
                )
            )
            passed.append(self._passed(record))
        return CapabilityResult(
            outputs=(Artifact(self._output, RecordList(self._output.fields, passed)),),
            trace=tuple(lines),
        )

    def _limit(self, position: int, rate: Decimal) -> Decimal:
        """The limit with tax of a Class 10.1 vehicle: its prescribed amount of the tax year plus
        the same amount at `rate` (in percent), rounded once with the dataset's rule."""
        limit = prescribed_amount_with_tax(
            self._prescribed_amounts, self._rounding, self._tax_year, rate
        )
        if limit is None:
            raise InvalidRecordError(f"item {position}: no prescribed amount for {self._tax_year}")
        return limit

    def _passed(self, record: Record) -> dict[ArtifactKind[Any], Decimal | int]:
        """The row as it is passed on: the fields of the output, as entered."""
        return {field: record[field] for field in self._output.fields}
