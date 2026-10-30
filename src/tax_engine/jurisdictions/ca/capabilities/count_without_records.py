"""CountWithoutRecords: a count that may not be above 0 while a record list holds a record.

For a figure that a copy of a form makes a double count: the manifest decides which artifact is the
count and which is the record list of the copies. It is the mirror of `CountAtLeast`: a count of 0,
or a list with no records, is produced as is; a count above 0 with at least one record is not
produced but is an input error, `InputAboveBoundError`, naming both kinds. It records one
`CountWithoutRecordsLine`, and none when it raises.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import CountWithoutRecordsLine


@capability(identifier="count_without_records")
class CountWithoutRecords(Capability):
    """Produces `output`: the consumed `count`, unchanged, when it is 0 or no record is held."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"count": int, "records": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(
        self,
        count: ArtifactKind[int],
        records: RecordListKind,
        output: ArtifactKind[int],
    ) -> None:
        """Wire the capability: the count checked, the record list it may not be above 0 with, the
        count produced."""
        super().__init__(count=count, records=records, output=output)
        self._count = count
        self._records = records
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        count = self._input(inputs, self._count).value
        record_count = len(self._input(inputs, self._records).value.records)
        if count > 0 and record_count > 0:
            noun = "record" if record_count == 1 else "records"
            raise InputAboveBoundError(
                f"{self._count.identifier} {count} is above 0 while {self._records.identifier} "
                f"holds {record_count} {noun}"
            )
        return CapabilityResult(
            outputs=(Artifact(self._output, count),),
            trace=(
                CountWithoutRecordsLine(
                    output=self._output,
                    count_kind=self._count,
                    count=count,
                    records_kind=self._records,
                    record_count=record_count,
                ),
            ),
        )
