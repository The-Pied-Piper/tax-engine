"""PrincipalResidencePart2Line48: line 48 of Form T2091(IND) Part 2, the post-1981 loss.

Form T2091(IND) Part 2, line 48 "Line 46 minus line 47 (if negative, enter "0")": the fair market
value on December 31, 1981 (line 46, line 12) less the proceeds (line 47, line 8), not below 0. It
is 0 when area C is not completed. The output is the total of those amounts over the consumed
`properties`, 0 when there are none. It records one `PrincipalResidenceLine48` for each property, by
position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import CapabilityResult, capability
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rounding_only import RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_rows import (
    PrincipalResidenceRows,
)
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceLine48


@capability(identifier="principal_residence_line_48")
class PrincipalResidencePart2Line48(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 48 of each one."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        properties: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the record list read, the kind produced."""
        super().__init__(rounding, properties, output)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return self._result(
            [
                PrincipalResidenceLine48(
                    self._output,
                    row.position,
                    row.post_1981_loss_completed,
                    row.fmv_1981,
                    row.proceeds,
                    row.line_48,
                )
                for row in self._rows(inputs)
            ]
        )
