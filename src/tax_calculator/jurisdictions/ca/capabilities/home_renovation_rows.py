"""HomeRenovationRows: the base of the capabilities of Schedule 12, the multigenerational home
renovation tax credit, lines 3, 6 and 7, not registered itself.

Schedule 12, Step 1, "complete this step for each qualifying renovation": each record of the
consumed `renovations` list (a qualifying renovation, holding line 1 "Total amount paid from all
sales slips and contracts", line 2 "reimbursed" and line 5 "claimed by other eligible
individuals") is worked on its own, never pooled with the others. Line 3 "Line 1 minus line 2
(maximum $50,000 per qualifying renovation)" is the renovation's line 1 less its line 2, at most
the consumed `maximum` dataset's amount (line 4 "Maximum amount per qualifying renovation
50,000.00"). Line 6 "Line 4 minus line 5" is that maximum less line 5. Line 7 "Enter whichever is
less: amount from line 3 or line 6" is the lesser of lines 3 and 6. None of them is rounded, and the
form prints no floor, so line 3 and line 6 are not floored at 0. A subclass is one capability for
each form line, building its own trace lines and output.

A record whose line 2 is above its line 1 is refused, as line 2 is "included in the amount on
line 1", and a record whose line 5 is above the `maximum` (line 4) is refused, as the total
claimed for one renovation is at most that maximum; each refusal names the renovation by its
position. A line equal to its bound is accepted.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityResult
from tax_calculator.domain.errors import ValidationError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.domain.trace.base import TraceLine
from tax_calculator.jurisdictions.ca.catalog import (
    HOME_RENOVATION_CLAIMED_BY_OTHERS,
    HOME_RENOVATION_EXPENDITURES,
    HOME_RENOVATION_REIMBURSED,
)


@dataclass(frozen=True)
class HomeRenovationRow:
    """The qualifying renovation at `position` (from 1) worked: its lines 1, 2 and 5
    (`expenditures`, `reimbursed`, `claimed_by_others`), the `maximum` (line 4), and lines 3, 6
    and 7."""

    position: int
    expenditures: Decimal
    reimbursed: Decimal
    claimed_by_others: Decimal
    maximum: Amount
    line_3: Decimal
    line_6: Decimal
    line_7: Decimal


class HomeRenovationRows(Capability):
    """Reads the consumed `renovations` and the `maximum` dataset, and works lines 3, 6 and 7 of
    each renovation; a subclass produces `output` from the rows."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"maximum": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"renovations": RecordList}

    def __init__(
        self,
        maximum: ParameterDataset[Amount],
        renovations: ArtifactKind[RecordList],
        output: ArtifactKind[Any],
    ) -> None:
        """Wire the maximum dataset and the record list read; the subclass keeps `output`."""
        super().__init__(renovations=renovations, output=output)
        self._maximum = maximum
        self._renovations = renovations
        self._output_kind = output

    def _rows(self, inputs: tuple[Artifact[Any], ...]) -> tuple[HomeRenovationRow, ...]:
        """Each consumed renovation, in order, as a row with lines 3, 6 and 7 worked."""
        records = self._input(inputs, self._renovations).value.records
        maximum = self._maximum.values
        rows: list[HomeRenovationRow] = []
        for position, record in enumerate(records, 1):
            expenditures = Decimal(record[HOME_RENOVATION_EXPENDITURES])
            reimbursed = Decimal(record[HOME_RENOVATION_REIMBURSED])
            claimed_by_others = Decimal(record[HOME_RENOVATION_CLAIMED_BY_OTHERS])
            if reimbursed > expenditures:
                raise ValidationError(
                    f"renovation {position}: line 2 (reimbursed) is {reimbursed}, more than "
                    f"line 1 (expenditures), {expenditures}"
                )
            if claimed_by_others > maximum.value:
                raise ValidationError(
                    f"renovation {position}: line 5 (claimed by other eligible individuals) is "
                    f"{claimed_by_others}, more than line 4 (maximum per qualifying renovation), "
                    f"{maximum.value}"
                )
            line_3 = min(expenditures - reimbursed, maximum.value)
            line_6 = maximum.value - claimed_by_others
            rows.append(
                HomeRenovationRow(
                    position,
                    expenditures,
                    reimbursed,
                    claimed_by_others,
                    maximum,
                    line_3,
                    line_6,
                    min(line_3, line_6),
                )
            )
        return tuple(rows)

    def _result(self, lines: list[Any]) -> CapabilityResult:
        """The `output` as the total of the `lines` (each with a `position` and a `result`), and
        the trace: those lines, then an `ItemsTotalLine`."""
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        trace: tuple[TraceLine, ...] = (
            *lines,
            ItemsTotalLine(self._output_kind, items, total),
        )
        return CapabilityResult(outputs=(Artifact(self._output_kind, total),), trace=trace)
