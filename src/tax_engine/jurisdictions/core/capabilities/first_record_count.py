"""FirstRecordCount: takes the one count in the first record of a record list.

The record-list kind has one count field, and an empty list is refused. It reads a form's export of
one count (`<form>.<export>`) as that count; the item is named by position 1 in the trace.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError, ValidationError
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import FirstRecordCountLine


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
