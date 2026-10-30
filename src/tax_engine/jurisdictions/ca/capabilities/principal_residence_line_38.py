"""PrincipalResidencePart2Line38: line 38 of Form T2091(IND) Part 2, the post-1981 amounts added.

Form T2091(IND) Part 2, line 38 "Add lines 35 to 37.": the fair market value on December 31, 1981
(line 35, line 12), the adjustments made to the cost base after 1981 (line 36, line 13) and the
outlays (line 37, line 9), added. It is 0 when area B is not completed. The output is the total of
those amounts over the consumed `properties`, 0 when there are none. It records one
`PrincipalResidenceLine38` for each property, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding_only import RoundingOnly
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.principal_residence_rows import (
    PrincipalResidenceRows,
)
from tax_engine.jurisdictions.ca.trace import PrincipalResidenceLine38


@capability(identifier="principal_residence_line_38")
class PrincipalResidencePart2Line38(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 38 of each one."""

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
                PrincipalResidenceLine38(
                    self._output,
                    row.position,
                    row.post_1981_completed,
                    row.fmv_1981,
                    row.adjustments_after_1981,
                    row.outlays,
                    row.line_38,
                )
                for row in self._rows(inputs)
            ]
        )
