"""TerminalLoss: the terminal loss of the CCA table, T776 and T2125 Area A.

Note 3: "If no property is left in the class and there is a positive amount in this column, deduct
the amount from your income as a terminal loss under "Terminal loss" on line 9948" (T2125: "in
Part 4 on line 9270"), and "Recapture and terminal loss do not apply to a Class 10.1 property
unless it is a DIEP". Each class of the consumed record list is one row of the table, worked on
its own as `CcaTable` works it: its terminal loss is column 7 less column 9 (the immediate expensing
amount), not below 0, when column 7 is positive and no property is left in the class, else 0, and 0
for a class the `class_rates` dataset excludes unless the row has DIEP additions (column 4). Column
9 comes off because Regulation 1100(0.2) deducts it from the UCC of the class first, and Guide
T4036 calls the terminal loss "an amount you have not deducted as CCA", so the part expensed is
not lost twice. Column 7 is exact, so nothing is rounded. The output is the total of
the terminal losses, 0 when there are no classes. It records one `TerminalLossLine` for each class,
by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import CapabilityResult, capability
from tax_calculator.domain.parameters.class_rates import ClassRates
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.cca_table import CcaTable
from tax_calculator.jurisdictions.ca.trace import CcaZeroReason, TerminalLossLine


@capability(identifier="terminal_loss")
class TerminalLoss(CcaTable):
    """Produces `output`: the total, over the consumed `classes`, of each class's terminal loss,
    for the classes the `class_rates` dataset does not exclude."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        classes: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its class-rate dataset, the record list it reads, the kind
        produced."""
        super().__init__(class_rates, classes, output)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        lines = tuple(
            TerminalLossLine(
                self._output,
                row.position,
                row.class_rate,
                row.no_property_left,
                row.column_7,
                row.zero_reason,
                row.column_7 > 0,
                max(Decimal(0), row.column_7 - row.immediate_expensing)
                if row.zero_reason is CcaZeroReason.NO_PROPERTY_LEFT and row.note_3_applies
                else Decimal(0),
                row.diep_additions > 0,
                row.immediate_expensing,
                row.half_year_rule_on_sale,
            )
            for row in self._rows(inputs)
        )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
