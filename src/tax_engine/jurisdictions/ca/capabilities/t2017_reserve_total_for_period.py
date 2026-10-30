"""T2017ReserveTotalForPeriod: the reserve change of the dispositions a Form T657 chart takes,
added.

Form T657 asks, for each year or period it has a chart for, for "Amount from line 6 of Form T2017
(do not include reserves from dispositions of QFFP in any year other than 2016)" and for line 12 the
same of QSBCS. Line 6 is "Line 1 minus line 5": the 2024 reserve less the 2025 reserve, so for the
dispositions of one year it is the total, over those dispositions, of each one's 2024 reserve less
its 2025 reserve (`ca/t2017_row_change`, a Form T2017 row form's export). The `conditions` dataset
says which dispositions the chart takes, in the form's words, by four counts of each record of
the lists read, in this order: 1 the years after the disposition, 2 the disposed of in Period 1 of
2024 answer, 3 the reported on a T5013 slip or letter answer and 4 the partnership year began
before June 25, 2024 answer. The consumed `rows` are the
record lists of the dispositions (Form T2017 lines 2, 3 and 4, or 8, 9 and 10) and the consumed
`amounts` the same row forms' exports of the reserve change, each list at the same position as the
rows it belongs to: the form ran once for each record, in order. Every disposition is traced, then
the total of the ones counted. The yes or no answers are checked by the row forms
(`ca/yes_or_no_count`), so they are 0 or 1 here. An empty list adds 0.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError, ValidationError
from tax_engine.domain.parameters.conditions import CONDITIONS, ConditionList, ConditionTest
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.catalog import (
    T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
    T2017_RESERVE_PERIOD_1_OF_2024,
    T2017_RESERVE_REPORTED_ON_SLIP,
    T2017_RESERVE_YEARS_AFTER_DISPOSITION,
)
from tax_engine.jurisdictions.ca.trace.gains import ReserveRowForPeriodLine

_COUNT_FIELDS = (
    T2017_RESERVE_YEARS_AFTER_DISPOSITION,
    T2017_RESERVE_PERIOD_1_OF_2024,
    T2017_RESERVE_REPORTED_ON_SLIP,
    T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
)


@capability(identifier="t2017_reserve_total_for_period")
class T2017ReserveTotalForPeriod(Capability):
    """Produces `total`: the consumed `amounts` of the dispositions in the consumed `rows` that
    the `conditions` take, added."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[ConditionList]]] = {"conditions": CONDITIONS}
    CONSUMES: ClassVar[Mapping[str, type]] = {
        "rows": list[RecordList],
        "amounts": list[RecordList],
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"total": Decimal}

    def __init__(
        self,
        conditions: ParameterDataset[ConditionList],
        rows: tuple[RecordListKind, ...],
        amounts: tuple[RecordListKind, ...],
        total: Money,
    ) -> None:
        """Wire the capability: the conditions dataset, the record lists of the dispositions, the
        lists of their reserve changes (one for each, in the same order) and the kind produced.

        Raises InvalidCapabilityError when the lists are not paired, a list of dispositions
        lacks one of the four counts, a list of amounts is not one amount, the dataset reads an
        amount or a count beyond the four, or it does not count the dispositions it applies to.
        """
        super().__init__(rows=rows, amounts=amounts, total=total)
        name = type(self).__name__
        if len(rows) != len(amounts):
            raise InvalidCapabilityError(f"{name}: needs one list of amounts for each list of rows")
        for kind in rows:
            missing = [field for field in _COUNT_FIELDS if field not in kind.fields]
            if missing:
                raise InvalidCapabilityError(
                    f"{name}: {kind.identifier!r} lacks the field {missing[0].identifier!r}"
                )
        for kind in amounts:
            if len(kind.fields) != 1 or not issubclass(kind.fields[0].value_type, Decimal):
                raise InvalidCapabilityError(
                    f"{name}: {kind.identifier!r} must be a record list of exactly one amount field"
                )
        values = conditions.values
        if values.amount_positions_read or values.highest_count_position > len(_COUNT_FIELDS):
            raise InvalidCapabilityError(
                f"{name}: the conditions may read only counts 1 to {len(_COUNT_FIELDS)}"
            )
        if values.count_when_any_applies != 1:
            raise InvalidCapabilityError(f"{name}: the conditions must give 1 when one applies")
        self._conditions = values
        self._rows = rows
        self._amounts = amounts
        self._total = total

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        lines: list[ReserveRowForPeriodLine] = []
        items: list[tuple[int, Decimal]] = []
        for list_position, (rows_kind, amounts_kind) in enumerate(
            zip(self._rows, self._amounts, strict=True), start=1
        ):
            records = self._input(inputs, rows_kind).value.records
            changes = self._input(inputs, amounts_kind).value.records
            if len(records) != len(changes):
                raise ValidationError(
                    f"{type(self).__name__}: {rows_kind.identifier} has {len(records)} records "
                    f"but {amounts_kind.identifier} has {len(changes)}"
                )
            for position, (record, change) in enumerate(
                zip(records, changes, strict=True), start=1
            ):
                counts = tuple(record[field] for field in _COUNT_FIELDS)
                (amount,) = (change[field] for field in amounts_kind.fields)
                counted = self._applies(counts)
                lines.append(
                    ReserveRowForPeriodLine(
                        output=self._total,
                        list_position=list_position,
                        position=position,
                        years_after=counts[0],
                        period_1=counts[1],
                        on_slip=counts[2],
                        partnership_year_before_june_25=counts[3],
                        change=amount,
                        counted=counted,
                    )
                )
                items.append((len(items) + 1, amount if counted else Decimal(0)))
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._total, total),),
            trace=(*lines, ItemsTotalLine(self._total, tuple(items), total)),
        )

    def _applies(self, counts: tuple[int, ...]) -> bool:
        """Whether some condition applies to a disposition: all of its parts hold, each part when
        any one of its tests holds."""
        return any(
            all(any(self._holds(test, counts) for test in part.tests) for part in condition.parts)
            for condition in self._conditions.conditions
        )

    @staticmethod
    def _holds(test: ConditionTest, counts: tuple[int, ...]) -> bool:
        """Whether the count at the test's position stands in its relation to the printed figure
        (a count test always has one: `against` is only for an amount)."""
        than = test.than
        if than is None:
            raise InvalidCapabilityError("a test of a count compares it with a printed figure")
        return test.holds(Decimal(counts[test.position - 1]), than)
