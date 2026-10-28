"""HomeRenovationLine3: line 3 of Schedule 12, the multigenerational home renovation tax credit.

Schedule 12, Step 1, line 3 "Line 1 minus line 2 (maximum $50,000 per qualifying renovation)": for
each qualifying renovation of the consumed `renovations`, its line 1 less its line 2, at most the
`maximum` dataset's amount. The output is the total of those amounts, 0 when there are no
renovations. It records one `RenovationLine3` for each renovation, by position from 1, then an
`ItemsTotalLine`.
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
from tax_calculator.jurisdictions.ca.trace import RenovationLine3


@capability(identifier="home_renovation_line_3")
class HomeRenovationLine3(HomeRenovationRows):
    """Produces `output`: the total, over the consumed `renovations`, of line 3 of each."""

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
                RenovationLine3(
                    self._output,
                    row.position,
                    row.expenditures,
                    row.reimbursed,
                    row.maximum,
                    row.line_3,
                )
                for row in self._rows(inputs)
            ]
        )
