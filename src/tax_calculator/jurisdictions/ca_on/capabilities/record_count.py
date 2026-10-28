"""RecordCount: the number of records of a record list.

Form ON479 line 63260 is the "Number of eligible work placements" claimed. The capability reads
a record list and produces how many records it holds, whatever they hold; an empty list gives 0.
It has no dataset.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import RecordCountLine


@capability(identifier="record_count")
class RecordCount(Capability):
    """Produces `output`: the number of records of the consumed `records`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"records": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(self, records: ArtifactKind[RecordList], output: ArtifactKind[int]) -> None:
        """Wire the capability: the record-list kind it counts and the count kind it produces."""
        super().__init__(records=records, output=output)
        self._records = records
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        count = len(self._input(inputs, self._records).value.records)
        return CapabilityResult(
            outputs=(Artifact(self._output, count),),
            trace=(RecordCountLine(output=self._output, records=self._records, count=count),),
        )
