"""ChartBProvinceTotal: the base of the Chart B province totals of Form T2043, not registered.

For Chart B rows 1 and 4 of each designated province: one record for each designated province the
business has a permanent establishment in, in the consumed record list (its province code, row 1
gross income and row 4 salaries and wages). A record for the subclass's `PROVINCE` counts its
amount in `FIELD`; a record for any other province counts nothing. The output is the total of
those amounts, exact: there is no dataset, so it never rounds. A province with no record totals 0.
A record whose province code is not 1 to 8 is an InvalidRecordError naming the item by its
position from 1, whichever province the subclass totals. Records for one province add. A subclass
is one capability for each province's total of one line, named by its `PROVINCE` and `FIELD`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult
from tax_engine.domain.errors import InvalidRecordError
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE

PROVINCE_ON = 1
PROVINCE_MB = 2
PROVINCE_SK = 3
PROVINCE_AB = 4
PROVINCE_NS = 5
PROVINCE_PE = 6
PROVINCE_NL = 7
PROVINCE_NB = 8
PROVINCE_CODES = range(PROVINCE_ON, PROVINCE_NB + 1)


class ChartBProvinceTotal(Capability):
    """Produces `output`: the sum of `FIELD` over the consumed records whose province is `PROVINCE`.

    A record whose province code is not 1 to 8 is an InvalidRecordError naming the item by its
    position from 1.
    """

    PROVINCE: ClassVar[int]
    FIELD: ClassVar[ArtifactKind[Any]]
    CONSUMES: ClassVar[Mapping[str, type]] = {"provinces": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, provinces: ArtifactKind[RecordList], output: Money) -> None:
        """Wire the capability: the record-list kind it reads and the kind it produces."""
        super().__init__(provinces=provinces, output=output)
        self._provinces = provinces
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        items: list[tuple[int, Decimal]] = []
        for position, record in enumerate(self._input(inputs, self._provinces).value.records, 1):
            code = record[FARM_CHART_B_PROVINCE]
            if code not in PROVINCE_CODES:
                raise InvalidRecordError(
                    f"item {position}: {FARM_CHART_B_PROVINCE.identifier} must be 1 to 8 (the "
                    f"designated provinces in the form's order), got {code}"
                )
            if code != self.PROVINCE:
                continue
            amount = record[self.FIELD]
            if not isinstance(amount, Decimal):
                raise TypeError(
                    f"{self.FIELD.identifier} must be a Decimal, got {type(amount).__name__}"
                )
            items.append((position, amount))
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(ItemsTotalLine(self._output, tuple(items), total),),
        )
