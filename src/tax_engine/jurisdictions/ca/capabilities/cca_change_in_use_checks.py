"""CcaChangeInUseChecks: the check of the cost of additions of each row of Form T777 Part A (the
classes 8, 10, 54 and 55) that started being used for employment in the year, the rows passed on
unchanged.

Guide T4044 2025, Part A "Column 3 - Cost of additions in the year": "If you owned property for
personal use and then started using it for employment in 2025, there is a change in use. In most
cases when this happens, the amount you will enter in this column is the fair market value of the
property at the time you start using the property for employment."

So the cost of additions (column 3) of a Part A row with additions that the filer answers as a
change in use must be its fair market value at that time; the form has the filer enter that amount,
so a different figure is refused, not replaced. The answer is 0 or 1; any other is refused. A row
not answered as a change in use and a row with no additions are not checked, whatever its class.
Each record of the consumed `classes` is checked on its own, and the output is a record list of the
same fields in the caller's order. It records one `CcaChangeInUseCheckLine` for each row, by
position, whether it was checked, its additions and its fair market value (0 when it was not
checked); a refused row is named by its error (`InvalidRecordError`).
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidRecordError
from tax_engine.domain.record_list import Record, RecordList, RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CHANGE_IN_USE,
    CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE,
)
from tax_engine.jurisdictions.ca.trace import CcaChangeInUseCheckLine


@capability(identifier="cca_change_in_use_checks")
class CcaChangeInUseChecks(Capability):
    """Produces `output`: the consumed `classes` (the Part A rows), unchanged, once the cost of
    additions of each row with a change in use is its fair market value at the time (Guide T4044
    2025, Part A column 3)."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"classes": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": RecordList}

    def __init__(
        self,
        classes: ArtifactKind[RecordList],
        output: RecordListKind,
    ) -> None:
        """Wire the capability: the Part A record list it reads and the record list kind it
        passes on, of the same fields."""
        super().__init__(classes=classes, output=output)
        self._classes = classes
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._classes).value.records
        passed: list[dict[ArtifactKind[Any], Decimal | int]] = []
        lines: list[CcaChangeInUseCheckLine] = []
        for position, record in enumerate(records, 1):
            answer = int(record[CCA_CHANGE_IN_USE])
            if answer > 1:
                raise InvalidRecordError(f"item {position}: change in use is {answer}")
            additions = Decimal(record[CCA_ADDITIONS])
            checked = additions > 0 and answer == 1
            market = Decimal(record[CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE]) if checked else Decimal(0)
            if checked and additions != market:
                raise InvalidRecordError(
                    f"item {position}: additions ({additions:.2f}) of property with a change in "
                    f"use are not its fair market value ({market:.2f}) when it started being used "
                    f"for employment"
                )
            lines.append(
                CcaChangeInUseCheckLine(self._output, position, checked, additions, market)
            )
            passed.append(self._passed(record))
        return CapabilityResult(
            outputs=(Artifact(self._output, RecordList(self._output.fields, passed)),),
            trace=tuple(lines),
        )

    def _passed(self, record: Record) -> dict[ArtifactKind[Any], Decimal | int]:
        """The row as it is passed on: the fields of the output, as entered."""
        return {field: record[field] for field in self._output.fields}
