"""CcaEntriesTotal: the base of the totals over the rows of the CCA table, not registered.

Guide T4036 p.13 (confirmed 2026-10-27 from the PDF; no .txt published): "If you determine that you
are a member of a partnership and you received a T5013 slip, fill in only the following fields on
Form T776": the business number, the percentage and amount 7. A row of Area A with an opening UCC
(column 2), additions (column 3 and its parts in columns 4, 11 and 12) or a remaining personal part
(Note 9) is an entry of the form even when its claim is 0, so the check of the T5013 slip answer
reads these totals. Each class of the consumed record list is one row. The output is the sum over
the rows of the row's `FIELDS` added; a column the list does not list counts 0. The total is exact
(no dataset, no rounding), 0 when there are no classes, and is a test of any entry, not a figure of
the form. The trace is one `RecordTotalLine` for the one column `FIELDS` names. A subclass is one
capability for the total of one entry of the rows, named by its `FIELDS`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import RecordTotalLine, TraceLine
from tax_calculator.jurisdictions.ca.capabilities.cca_table import CcaTable

_ZERO = Decimal(0)


class CcaEntriesTotal(Capability):
    """Produces `output`: the sum over every consumed class of its `FIELDS` added, exact.

    The trace is one line: each class's amount in the list's order, then the total.
    """

    FIELDS: ClassVar[tuple[Money, ...]]
    CONSUMES: ClassVar[Mapping[str, type]] = {"classes": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, classes: ArtifactKind[RecordList], output: Money) -> None:
        """Wire the capability: the record-list kind it reads and the kind it produces."""
        super().__init__(classes=classes, output=output)
        self._classes = classes
        self._output = output

    def _line(self, amounts: tuple[Decimal, ...], total: Decimal) -> TraceLine:
        """The trace line of the total: its column `FIELDS` names, for the one column."""
        (field,) = self.FIELDS
        return RecordTotalLine(output=self._output, field=field, amounts=amounts, total=total)

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._classes).value.records
        amounts = tuple(
            sum((CcaTable._optional(record, field) for field in self.FIELDS), _ZERO)
            for record in records
        )
        total = sum(amounts, _ZERO)
        return CapabilityResult(
            outputs=(Artifact(self._output, total),), trace=(self._line(amounts, total),)
        )
