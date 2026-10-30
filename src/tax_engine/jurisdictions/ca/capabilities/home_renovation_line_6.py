"""HomeRenovationLine6: line 6 of Schedule 12, the multigenerational home renovation tax credit.

Schedule 12, Step 1, line 6 "Line 4 minus line 5": for each qualifying renovation of the consumed
`renovations`, the `maximum` dataset's amount less the amount claimed by other eligible individuals
(line 5). The output is the total of those amounts, 0 when there are no renovations. It records
one `RenovationLine6` for each renovation, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import CapabilityResult, capability
from tax_engine.domain.parameters.amount import Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.home_renovation_rows import HomeRenovationRows
from tax_engine.jurisdictions.ca.trace import RenovationLine6


@capability(identifier="home_renovation_line_6")
class HomeRenovationLine6(HomeRenovationRows):
    """Produces `output`: the total, over the consumed `renovations`, of line 6 of each."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        maximum: ParameterDataset[Amount],
        renovations: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its maximum dataset, the record list it reads, the kind produced."""
        super().__init__(maximum, renovations, output)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return self._result(
            [
                RenovationLine6(
                    self._output,
                    row.position,
                    row.maximum,
                    row.claimed_by_others,
                    row.line_6,
                )
                for row in self._rows(inputs)
            ]
        )
