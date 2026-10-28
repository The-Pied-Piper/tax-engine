"""ClosingUccAfterColumn22: the UCC at the end of the year of each class of the T776 CCA table, its
claim limited by column 22.

T776 Area A "Column 24: UCC at the end of the year (column 7 minus column 23)": `ClosingUcc` with
each class's claim refused above its column 21 less its column 22 ("Non-compliant amount of CCA
(see Chart B below)", from the consumed `non_compliant` record list, 0 for a class it does not
list), which is column 23 as printed. It subclasses `ClosingUcc` alone and overrides only the
limit step of `CcaTable`; the output and the trace are those of `ClosingUcc`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.capability import capability
from tax_calculator.domain.parameters.class_rates import ClassRates
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.cca_table import CcaRow
from tax_calculator.jurisdictions.ca.capabilities.closing_ucc import ClosingUcc


@capability(identifier="closing_ucc_after_column_22")
class ClosingUccAfterColumn22(ClosingUcc):
    """Produces `output`: for each of the consumed `classes`, its class number and its UCC at the
    end of the year, with its maximum from the `class_rates` dataset less its column 22."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"classes": RecordList, "non_compliant": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": RecordList}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        classes: ArtifactKind[RecordList],
        non_compliant: ArtifactKind[RecordList],
        output: ArtifactKind[RecordList],
        **consumed: ArtifactKind[Any],
    ) -> None:
        """Wire the capability: its class-rate dataset, the record list it reads, the record list
        of column 22 amounts, the record list kind produced, of the class number and the UCC at
        the end of the year. A subclass consuming more kinds passes them by slot name."""
        super().__init__(class_rates, classes, output, non_compliant=non_compliant, **consumed)

    def _limit(self, row: CcaRow, maximum: Decimal) -> Decimal:
        return max(Decimal(0), maximum + row.immediate_expensing - row.column_22)
