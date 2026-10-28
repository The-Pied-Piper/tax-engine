"""PrincipalResidencePart2Line51: line 51 of Form T2091(IND) Part 2, the pre-1982 and
post-1981 gains together.

Form T2091(IND) Part 2, line 51 "Line 49 plus line 50": the pre-1982 gain (line 49, line 33) plus
the post-1981 gain (line 50, line 45). Area D is always completed. The output is the total of those
amounts over the consumed `properties`, 0 when there are none. It records one
`PrincipalResidenceLine51` for each property, by position from 1, then an `ItemsTotalLine`.
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
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceLine51


@capability(identifier="principal_residence_line_51")
class PrincipalResidencePart2Line51(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 51 of each one."""

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
                PrincipalResidenceLine51(
                    self._output,
                    row.position,
                    row.applies,
                    row.line_33,
                    row.line_45,
                    row.line_51,
                )
                for row in self._rows(inputs)
            ]
        )
