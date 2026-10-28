"""CcaPartBChecks: the checks of the Part B rows of Form T777 (Class 10.1 passenger vehicles), the
rows passed on unchanged.

T777 Part B "List each passenger vehicle on a separate line" and notes (11) and (12): a vehicle is
either owned from the previous year (UCC at the start of the year, column 2, note (11)) or bought
in the year (cost of additions, column 3), not both, so a row with both is refused;
proceeds of dispositions (column 4) are entered only for a vehicle sold in the year, the tick "no
property left" of the table, so proceeds without the tick are refused; and a tick is entered only
with proceeds, so a tick without proceeds is refused (`InvalidRecordError`, naming the item). Each
record of the consumed `classes` is checked on its own, and the output is a record list of the same
fields in the caller's order. It records one `CcaPartBCheckLine` for each row that passes, by
position and with no total; a refused row is named by its error.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_NO_PROPERTY_LEFT,
    CCA_PROCEEDS,
    CCA_UCC_AT_START,
)
from tax_calculator.jurisdictions.ca.trace import CcaPartBCheckLine


@capability(identifier="cca_part_b_checks")
class CcaPartBChecks(Capability):
    """Produces `output`: the consumed `classes` (the Part B rows), unchanged, once each row has
    passed the three checks of Form T777 Part B."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"classes": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": RecordList}

    def __init__(
        self,
        classes: ArtifactKind[RecordList],
        output: RecordListKind,
    ) -> None:
        """Wire the capability: the Part B record list it reads and the record list kind it
        passes on, of the same fields."""
        super().__init__(classes=classes, output=output)
        self._classes = classes
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._classes).value.records
        passed: list[dict[ArtifactKind[Any], Decimal | int]] = []
        lines: list[CcaPartBCheckLine] = []
        for position, record in enumerate(records, 1):
            item = f"item {position}"
            ucc_at_start = Decimal(record[CCA_UCC_AT_START])
            additions = Decimal(record[CCA_ADDITIONS])
            proceeds = Decimal(record[CCA_PROCEEDS])
            sold_in_year = int(record[CCA_NO_PROPERTY_LEFT])
            if ucc_at_start > 0 and additions > 0:
                raise InvalidRecordError(
                    f"{item}: a UCC at the start ({ucc_at_start}) and additions ({additions}) "
                    "are both entered; a vehicle is owned from the previous year or bought in "
                    "the year, not both"
                )
            if proceeds > 0 and not sold_in_year:
                raise InvalidRecordError(
                    f"{item}: proceeds ({proceeds}) are entered without the sold in the year "
                    "tick (no property left)"
                )
            if sold_in_year and proceeds == 0:
                raise InvalidRecordError(
                    f"{item}: the sold in the year tick (no property left) is entered without "
                    "proceeds"
                )
            lines.append(
                CcaPartBCheckLine(
                    self._output,
                    position,
                    ucc_at_start,
                    additions,
                    proceeds,
                    bool(sold_in_year),
                )
            )
            passed.append({field: record[field] for field in self._output.fields})
        return CapabilityResult(
            outputs=(Artifact(self._output, RecordList(self._output.fields, passed)),),
            trace=tuple(lines),
        )
