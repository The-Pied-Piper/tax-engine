"""OntarioCappedRecordTotal: the Ontario total of one amount field over a record list, each record
capped on its own.

For Form ON428 line 23 and line 58330 "Adoption expenses", with T2203 note (5): each child's
eligible expenses (the one amount field of each record in the consumed record list) are capped at
the `cap` dataset's amount, rounded once with the `cap` dataset's rule, and the capped amounts are
added up. Each child is worked on its own, never pooled with the others. The output is 0 when
there are no children. It records one `CappedRecordLine` for each child, by position from 1, then
an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidCapabilityError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca_on.trace import CappedRecordLine


@capability(identifier="capped_record_total")
class OntarioCappedRecordTotal(Capability):
    """Produces `output`: the total, over the consumed `records`, of the amount field of each
    record, each one at most the `cap` dataset's amount."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"cap": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"records": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self, cap: ParameterDataset[Amount], records: RecordListKind, output: Money
    ) -> None:
        """Wire the capability: its cap dataset, the record-list kind it caps, the kind produced.

        Raises InvalidCapabilityError when the list kind does not have exactly one field, an
        amount.
        """
        super().__init__(records=records, output=output)
        if not isinstance(records, RecordListKind):
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'records' must be a record-list kind"
            )
        amount_fields = [kind for kind in records.fields if issubclass(kind.value_type, Decimal)]
        if len(records.fields) != 1 or not amount_fields:
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'records' must be a record list of "
                "exactly one amount field"
            )
        self._cap = cap
        self._field = amount_fields[0]
        self._records = records
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._records).value.records
        cap, rounding = self._cap.values, self._cap.rounding
        lines: list[CappedRecordLine] = []
        for position, record in enumerate(records, start=1):
            expenditure = record[self._field]
            result = rounding.apply(min(expenditure, cap.value))
            lines.append(
                CappedRecordLine(self._output, position, expenditure, cap, rounding, result)
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
