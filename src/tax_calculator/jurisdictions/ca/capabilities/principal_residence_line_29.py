"""PrincipalResidencePart2Line29: line 29 of Form T2091(IND) Part 2, the years designated
before 1982 plus the "plus one".

Form T2091(IND) Part 2, line 29 "Line 2 plus 1 (see note on page 4)": the years designated from 1972
to 1981 (line 2) plus the "plus one" (1 or 0). It is 0 when area A is not completed. The output is
the total of those counts over the consumed `properties`, 0 when there are none. It records one
`PrincipalResidenceLine29` for each property, by position from 1, then an `ItemsTotalLine`.
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
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceLine29


@capability(identifier="principal_residence_line_29")
class PrincipalResidencePart2Line29(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 29 of each one."""

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
                PrincipalResidenceLine29(
                    self._output,
                    row.position,
                    row.pre_1982_completed,
                    row.designated_before,
                    row.plus_one,
                    Decimal(row.line_29),
                )
                for row in self._rows(inputs)
            ]
        )
