"""CcaPartAChecks: the checks of the Part A rows of Form T777 (the classes 8, 10, 54 and 55), the
rows passed on unchanged.

T777 Part A "Part A - Classes 8, 10, 54, and 55", with the printed class column "8 / 10 / 54 / 55":
one row for each class. A class listed in an earlier row of the consumed `classes` is refused, as
the two rows would each start from their own UCC and claim the CCA of the class twice
(`InvalidRecordError`, naming both items). Part B (Class 10.1) is one row for each vehicle and is
checked by `ca/cca_part_b_checks`; the other forms take any number of rows of a class.

Each record of `classes` is checked against the class numbers of the rows before it, and the output
is a record list of the same fields in the caller's order. It records one `CcaPartACheckLine` for
each row that passes, by position and with its class number and no amount; a refused row is named
by its error.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.catalog import CCA_CLASS_NUMBER
from tax_calculator.jurisdictions.ca.trace import CcaPartACheckLine


@capability(identifier="cca_part_a_checks")
class CcaPartAChecks(Capability):
    """Produces `output`: the consumed `classes` (the Part A rows), unchanged, once no class number
    is listed twice in them."""

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
        lines: list[CcaPartACheckLine] = []
        listed: dict[Decimal, int] = {}
        for position, record in enumerate(records, 1):
            item = f"item {position}"
            class_number = Decimal(record[CCA_CLASS_NUMBER])
            if class_number in listed:
                raise InvalidRecordError(
                    f"{item}: class {class_number} is already listed in item "
                    f"{listed[class_number]}; Part A has one row for each class"
                )
            listed[class_number] = position
            lines.append(CcaPartACheckLine(self._output, position, class_number))
            passed.append({field: record[field] for field in self._output.fields})
        return CapabilityResult(
            outputs=(Artifact(self._output, RecordList(self._output.fields, passed)),),
            trace=tuple(lines),
        )
