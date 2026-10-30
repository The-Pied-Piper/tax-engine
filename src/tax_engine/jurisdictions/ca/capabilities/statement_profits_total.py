"""StatementProfitsTotal: the profit of the statements a form is filled in for, added.

Form T1139 is filled in for one business, and its amounts A, H and I are "the net income (loss)"
of that business's income and expenses statement or statements, "the amount found on line 9946" of
the form that applies to the type of business income (T2125, T2121 or T2042). Readers that take
"net self-employment income (not including losses)" use "only the profit amounts" of the
statements, so when a Form T1139 takes the place of statements this capability gives the profit
those statements would have added: each statement counts its amount, or 0 when it is a loss. The
statements of each form are a record list with one record per statement in the order the filer
gave them, so the filer names a statement by its position from 1. The consumed `records` are the
record lists of one amount field, one for each type of business income, in the order of the form's
list of lines (13500, 13700, 13900, 14100, 14300); the consumed `line` is the filer's choice of the
list, from 1; the consumed `positions` is a record list of one count field, the positions of the
statements in that list. No positions add up to 0. A `line` outside the lists, a position that is
not a statement of the list or a position named twice is refused (`InputOutOfRangeError`): no
statement is guessed at or counted twice. It has no dataset, so it never rounds. It records one
`ItemsTotalLine` naming each statement by its position and the profit it counts.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InputOutOfRangeError, InvalidCapabilityError
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import ItemsTotalLine


@capability(identifier="statement_profits_total")
class StatementProfitsTotal(Capability):
    """Produces `total`: the profits of the statements at the consumed `positions` of the list the
    consumed `line` names among the consumed `records`, each loss counted as 0, added."""

    CONSUMES: ClassVar[Mapping[str, type]] = {
        "records": list[RecordList],
        "line": int,
        "positions": RecordList,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"total": Decimal}

    def __init__(
        self,
        records: tuple[RecordListKind, ...],
        line: ArtifactKind[int],
        positions: RecordListKind,
        total: Money,
    ) -> None:
        """Wire the capability: the lists of statements, the count that names one of them, the
        record list of the positions and the kind produced.

        Raises InvalidCapabilityError when a list of statements is not one amount field or the
        positions are not one count field.
        """
        super().__init__(records=records, line=line, positions=positions, total=total)
        name = type(self).__name__
        for kind in records:
            if len(kind.fields) != 1 or not issubclass(kind.fields[0].value_type, Decimal):
                raise InvalidCapabilityError(
                    f"{name}: {kind.identifier!r} must be a record list of exactly one amount field"
                )
        if len(positions.fields) != 1 or not issubclass(positions.fields[0].value_type, int):
            raise InvalidCapabilityError(
                f"{name}: {positions.identifier!r} must be a record list of exactly one count field"
            )
        self._records = records
        self._line = line
        self._positions = positions
        self._position_field = positions.fields[0]
        self._total = total

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        line = self._input(inputs, self._line).value
        if not 1 <= line <= len(self._records):
            raise InputOutOfRangeError(
                f"{self._line.identifier} {line} is not one of the {len(self._records)} lines"
            )
        kind = self._records[line - 1]
        (amount_field,) = kind.fields
        statements = self._input(inputs, kind).value.records
        named = tuple(
            record[self._position_field]
            for record in self._input(inputs, self._positions).value.records
        )
        items: list[tuple[int, Decimal]] = []
        for position in named:
            if not 1 <= position <= len(statements):
                raise InputOutOfRangeError(
                    f"{self._position_field.identifier} {position} names no statement of "
                    f"{kind.identifier}, which has {len(statements)}"
                )
            if position in named[: len(items)]:
                raise InputOutOfRangeError(
                    f"{self._position_field.identifier} {position} names a statement of "
                    f"{kind.identifier} twice"
                )
            items.append((position, max(statements[position - 1][amount_field], Decimal(0))))
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._total, total),),
            trace=(ItemsTotalLine(self._total, tuple(items), total),),
        )
