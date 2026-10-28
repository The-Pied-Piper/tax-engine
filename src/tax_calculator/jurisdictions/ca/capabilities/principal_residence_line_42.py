"""PrincipalResidencePart2Line42: line 42 of Form T2091(IND) Part 2, the post-1981 gain
multiplied by the years designated after 1981.

Form T2091(IND) Part 2, line 42 "Multiply line 40 by line 41.": line 39 (line 40 is the amount from
line 39) multiplied by the years designated after 1981 (line 41, "Number of years from line 1"), not
floored, so it may be negative. It is 0 when area B is not completed. The output is the total of
those amounts over the consumed `properties`, 0 when there are none. It records one
`PrincipalResidenceLine42` for each property, by position from 1, then an `ItemsTotalLine`.
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
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceLine42


@capability(identifier="principal_residence_line_42")
class PrincipalResidencePart2Line42(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 42 of each one."""

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
                PrincipalResidenceLine42(
                    self._output,
                    row.position,
                    row.post_1981_completed,
                    row.line_39,
                    row.designated_after,
                    row.line_42,
                )
                for row in self._rows(inputs)
            ]
        )
