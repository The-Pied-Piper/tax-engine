"""RecordPositiveTotal: adds the positive amounts of one amount field over the records of a
record list, exactly.

The record-list kind has exactly one field, an amount; the capability adds each amount above zero
over the records in order, and a zero or negative amount counts 0. An empty list, or a list with
no positive amount, totals zero. It has no dataset, so it never rounds. Each item is named by its
position from 1 in the trace.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidCapabilityError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.trace import RecordPositiveTotalLine


@capability(identifier="record_positive_total")
class RecordPositiveTotal(Capability):
    """Produces `output`: the sum of the positive amounts of the one amount field over the
    consumed `records`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"records": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, records: RecordListKind, output: Money) -> None:
        """Wire the capability: the record-list kind it adds and the kind it produces.

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
        self._field = amount_fields[0]
        self._records = records
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._records).value.records
        amounts = tuple(record[self._field] for record in records)
        total = sum((amount for amount in amounts if amount > 0), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(
                RecordPositiveTotalLine(
                    output=self._output, field=self._field, amounts=amounts, total=total
                ),
            ),
        )
