"""PrincipalResidencePart2Line33: line 33 of Form T2091(IND) Part 2, the pre-1982 gain.

Form T2091(IND) Part 2, line 33 "Line 27 minus line 32 (if negative, enter "0")": line 27 less line
32, not below 0. It is 0 when area A is not completed. The output is the total of those amounts over
the consumed `properties`, 0 when there are none. It records one `PrincipalResidenceLine33` for each
property, by position from 1, then an `ItemsTotalLine`.
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
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceLine33


@capability(identifier="principal_residence_line_33")
class PrincipalResidencePart2Line33(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 33 of each one."""

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
                PrincipalResidenceLine33(
                    self._output,
                    row.position,
                    row.pre_1982_completed,
                    row.line_27,
                    row.line_32,
                    row.line_33,
                )
                for row in self._rows(inputs)
            ]
        )
