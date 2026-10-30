"""RecapturedCca: the recaptured capital cost allowance of the CCA table, T776 and T2125 Area A.

Note 3: "If you have a negative amount in column 7, add it to income as a recapture under
"Recaptured capital cost allowance" on line 9947" (T2125: "in Part 3C on line 8230"), and
"Recapture and terminal loss do not apply to a Class 10.1 property unless it is a DIEP". Each class
of the consumed record list is one row of the table, worked on its own as `CcaTable` works it: its
recapture is column 7 made positive when column 7 is negative, else 0, and 0 for a class the
`class_rates` dataset excludes unless the row has DIEP additions (column 4). Column 7 is exact, so
nothing is rounded. The output is the total of the recaptures, 0 when there are no classes. It
records one `RecapturedCcaLine` for each class, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import CapabilityResult, capability
from tax_engine.domain.parameters.class_rates import ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.cca_table import CcaTable
from tax_engine.jurisdictions.ca.trace import CcaZeroReason, RecapturedCcaLine


@capability(identifier="recaptured_cca")
class RecapturedCca(CcaTable):
    """Produces `output`: the total, over the consumed `classes`, of each class's recapture, for
    the classes the `class_rates` dataset does not exclude."""

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
            RecapturedCcaLine(
                self._output,
                row.position,
                row.class_rate,
                row.column_7,
                row.zero_reason,
                -row.column_7
                if row.zero_reason is CcaZeroReason.COLUMN_7_NEGATIVE and row.note_3_applies
                else Decimal(0),
                row.diep_additions > 0,
            )
            for row in self._rows(inputs)
        )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
