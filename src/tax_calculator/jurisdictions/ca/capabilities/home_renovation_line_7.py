"""HomeRenovationLine7: line 7 of Schedule 12, the multigenerational home renovation tax credit.

Schedule 12, Step 1, line 7 "Enter whichever is less: amount from line 3 or line 6. Your qualifying
expenditures for the qualifying renovation": for each qualifying renovation of the consumed
`renovations`, the lesser of its line 3 and line 6. Step 2, line 8 (line 45354) "Add the amounts
from line 7 for each qualifying renovation. Your total qualifying expenditures" is the output, the
total of those amounts, 0 when there are no renovations. It records one `RenovationLine7` for each
renovation, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import CapabilityResult, capability
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.home_renovation_rows import HomeRenovationRows
from tax_calculator.jurisdictions.ca.trace import RenovationLine7


@capability(identifier="home_renovation_line_7")
class HomeRenovationLine7(HomeRenovationRows):
    """Produces `output`: the total, over the consumed `renovations`, of line 7 of each."""

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
                RenovationLine7(
                    self._output,
                    row.position,
                    row.line_3,
                    row.line_6,
                    row.line_7,
                )
                for row in self._rows(inputs)
            ]
        )
