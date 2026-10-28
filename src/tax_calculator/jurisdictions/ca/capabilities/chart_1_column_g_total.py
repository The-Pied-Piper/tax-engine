"""Chart1ColumnGTotal: Form T657 Chart 1, columns E, F and G for each year row, the column G
amounts added.

Chart 1 is "Calculate your net capital losses of other years (line 14 of Step 2)". For each
printed year row, with columns A to D entered by the filer: column E is "(C – D) (If negative,
enter "0")", so E is C minus D, floored at 0; column F is "(B + E)"; column G is "(A – F) (If
negative, enter "0")", so G is A minus F, floored at 0. "Add the amounts in column G and enter the
result on line 14 of Step 2" is the total this capability produces, the sum of every row's G. An
empty list of rows gives 0. Each row is traced as one line, then the total line.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.catalog import (
    T657_CHART_1_COLUMN_A,
    T657_CHART_1_COLUMN_B,
    T657_CHART_1_COLUMN_C,
    T657_CHART_1_COLUMN_D,
)
from tax_calculator.jurisdictions.ca.trace.gains import NetCapitalLossesRowLine


@capability(identifier="chart_1_column_g_total")
class Chart1ColumnGTotal(Capability):
    """Produces `total`: the column G of each consumed year row, added."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"rows": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"total": Decimal}

    def __init__(self, rows: ArtifactKind[RecordList], total: Money) -> None:
        """Wire the capability: the record-list kind of the year rows it reads and the kind of
        the total it produces."""
        super().__init__(rows=rows, total=total)
        self._rows = rows
        self._total = total

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        """Work each row's columns E, F and G, trace each row, then add the column G amounts."""
        lines: list[NetCapitalLossesRowLine] = []
        records = self._input(inputs, self._rows).value.records
        for position, record in enumerate(records, start=1):
            a = self._column(record, T657_CHART_1_COLUMN_A, position)
            b = self._column(record, T657_CHART_1_COLUMN_B, position)
            c = self._column(record, T657_CHART_1_COLUMN_C, position)
            d = self._column(record, T657_CHART_1_COLUMN_D, position)
            e = max(c - d, Decimal(0))
            f = b + e
            g = max(a - f, Decimal(0))
            lines.append(NetCapitalLossesRowLine(self._total, position, a, b, c, d, e, f, g))
        items = tuple((line.position, line.column_g) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._total, total),),
            trace=(*lines, ItemsTotalLine(self._total, items, total)),
        )

    @staticmethod
    def _column(record: Any, kind: ArtifactKind[Any], position: int) -> Decimal:
        """The Decimal the row holds for `kind`; a row without it is a type error naming the
        column and the row's position from 1."""
        amount = record[kind]
        if not isinstance(amount, Decimal):
            raise TypeError(
                f"item {position}: {kind.identifier} must be a Decimal, got {type(amount).__name__}"
            )
        return amount
