"""QbtBeforeQcc: a qualified business transfer claimed before any qualified capital contribution.

Form T2048: "You must claim any deduction under a QBT before any deduction under a QCC." The form
is run once for each disposition, in the order the filer designates; this checks the order of one
run against the earlier runs. The consumed `is_qbt` is 1 for a QBT and 0 for a QCC; `earlier` is a
record list of exactly one whole-number field, the answers of the earlier runs in order. The output
is the `is_qbt` answer, unchanged. A QCC is always in order; a QBT is in order when every earlier
answer is 1, and is an input error, a `ValidationError` naming the first earlier QCC, when one of
them is 0. It records one `QbtBeforeQccLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError, ValidationError
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.jurisdictions.ca.trace import QbtBeforeQccLine


@capability(identifier="qbt_before_qcc")
class QbtBeforeQcc(Capability):
    """Produces `output`: the consumed `is_qbt`, unchanged, when no QCC comes before a QBT."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"is_qbt": int, "earlier": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(
        self,
        is_qbt: ArtifactKind[int],
        earlier: RecordListKind,
        output: ArtifactKind[int],
    ) -> None:
        """Wire the capability: the run's answer, the earlier runs' answers, the answer produced.

        Raises InvalidCapabilityError when the earlier list does not have exactly one whole-number
        field.
        """
        super().__init__(is_qbt=is_qbt, earlier=earlier, output=output)
        if len(earlier.fields) != 1 or earlier.fields[0].value_type is not int:
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'earlier' must be a record list of "
                "exactly one whole-number field"
            )
        self._is_qbt = is_qbt
        self._earlier = earlier
        self._answer = earlier.fields[0]
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        is_qbt = self._input(inputs, self._is_qbt).value
        records = self._input(inputs, self._earlier).value.records
        answers = tuple(record[self._answer] for record in records)
        if is_qbt == 1 and 0 in answers:
            raise ValidationError(
                f"{self._is_qbt.identifier} is 1 but disposition {answers.index(0) + 1} before it "
                "is a QCC: the QBT must come before the QCC"
            )
        return CapabilityResult(
            outputs=(Artifact(self._output, is_qbt),),
            trace=(
                QbtBeforeQccLine(
                    output=self._output,
                    is_qbt_kind=self._is_qbt,
                    is_qbt=is_qbt,
                    earlier=len(answers),
                    earlier_qbts=answers.count(1),
                ),
            ),
        )
