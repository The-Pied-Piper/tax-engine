"""FirstRecordCount: takes the one count in the first record of a record list.

The record-list kind has exactly one field, a count; the capability takes that field of the first
record (position 0, fixed) and produces it as `output`. It has no dataset, so it never rounds. An
empty list has no first record and is refused. It reads a form's export of one count
(`<form>.<export>`), a list of one record, as that one count. The item is named by its position
from 1 in the trace.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidCapabilityError, ValidationError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.trace import FirstRecordCountLine


@capability(identifier="first_record_count")
class FirstRecordCount(Capability):
    """Produces `output`: the one count in the first record of the consumed `records`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"records": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(self, records: RecordListKind, output: ArtifactKind[int]) -> None:
        """Wire the capability: the record-list kind it reads and the kind it produces.

        Raises InvalidCapabilityError when the list kind does not have exactly one field, a
        count.
        """
        super().__init__(records=records, output=output)
        if not isinstance(records, RecordListKind):
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'records' must be a record-list kind"
            )
        count_fields = [kind for kind in records.fields if issubclass(kind.value_type, int)]
        if len(records.fields) != 1 or not count_fields:
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'records' must be a record list of "
                "exactly one count field"
            )
        self._field = count_fields[0]
        self._records = records
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._records).value.records
        if not records:
            raise ValidationError(
                f"{type(self).__name__}: the record list is empty, so it has no first record"
            )
        value = records[0][self._field]
        return CapabilityResult(
            outputs=(Artifact(self._output, value),),
            trace=(
                FirstRecordCountLine(
                    output=self._output,
                    field=self._field,
                    value=value,
                    record_count=len(records),
                ),
            ),
        )
