"""CcaClaimAfterColumn22: the total capital cost allowance claim of the T776 CCA table, its claim
limited by column 22.

T776 "Line ii: Total CCA claim for the year: Total of column 23": `CcaClaim` with each class's
claim refused above column 21 ("column 19 multiplied by column 20, or a lower amount", plus column
9) less column 22 ("Non-compliant amount of CCA (see Chart B below)", from the consumed
`non_compliant` record list, 0 for a class it does not list), which is column 23 as printed
("column 21 minus column 22"). It subclasses `CcaClaim` alone and overrides only the limit step of
`CcaTable`; the output and the trace are those of `CcaClaim`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import ArtifactKind, Money
from tax_engine.domain.capability import capability
from tax_engine.domain.parameters.class_rates import ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.cca_claim import CcaClaim
from tax_engine.jurisdictions.ca.capabilities.cca_table import CcaRow


@capability(identifier="cca_claim_after_column_22")
class CcaClaimAfterColumn22(CcaClaim):
    """Produces `output`: the total, over the consumed `classes`, of each class's CCA claimed, at
    most its maximum from the `class_rates` dataset less its column 22 from `non_compliant`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"classes": RecordList, "non_compliant": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        classes: ArtifactKind[RecordList],
        non_compliant: ArtifactKind[RecordList],
        output: Money,
        **consumed: ArtifactKind[Any],
    ) -> None:
        """Wire the capability: its class-rate dataset, the record list it reads, the record list
        of column 22 amounts, the kind produced. A subclass consuming more kinds passes them by slot
        name."""
        super().__init__(class_rates, classes, output, non_compliant=non_compliant, **consumed)

    def _limit(self, row: CcaRow, maximum: Decimal) -> Decimal:
        return max(Decimal(0), maximum + row.immediate_expensing - row.column_22)
