"""FlowThroughShareExpenses: the qualifying expenses of the T1221 slips, added.

Form T1221 takes one line for each corporation or slip, "Enter the amount of qualifying
expenses.", and line 4 "Add lines 1 to 3." This capability reads the record list of those slips
and adds the one field of every record, exactly: it has no dataset, so it never rounds, and an
empty list totals zero. Each item is named by its position from 1 in the trace.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import RecordTotalLine
from tax_calculator.jurisdictions.ca_on.catalog import FLOW_THROUGH_SHARE_SLIP_EXPENSES


@capability(identifier="flow_through_share_expenses")
class FlowThroughShareExpenses(Capability):
    """Produces `output`: the qualifying expenses of every record of the consumed `slips`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"slips": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, slips: ArtifactKind[RecordList], output: Money) -> None:
        """Wire the capability: the record-list kind it reads and the kind it produces."""
        super().__init__(slips=slips, output=output)
        self._slips = slips
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amounts: list[Decimal] = []
        for record in self._input(inputs, self._slips).value.records:
            amount = record[FLOW_THROUGH_SHARE_SLIP_EXPENSES]
            if not isinstance(amount, Decimal):
                raise TypeError(
                    f"{FLOW_THROUGH_SHARE_SLIP_EXPENSES.identifier} must be a Decimal, "
                    f"got {type(amount).__name__}"
                )
            amounts.append(amount)
        total = sum(amounts, Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(
                RecordTotalLine(
                    output=self._output,
                    field=FLOW_THROUGH_SHARE_SLIP_EXPENSES,
                    amounts=tuple(amounts),
                    total=total,
                ),
            ),
        )
