"""PrincipalResidencePart2Line32: line 32 of Form T2091(IND) Part 2, the pre-1982 exempt part.

Form T2091(IND) Part 2, line 32 "Divide line 30 by line 31.": line 30 divided by the years owned
from 1972 to 1981 (line 31, "Number of years from line 6"), rounded once with the `rounding`
dataset's rule. It is 0 when area A is not completed. The output is the total of those quotients
over the consumed `properties`, 0 when there are none. It records one `PrincipalResidenceLine32` for
each property, by position from 1, then an `ItemsTotalLine`.
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
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceLine32


@capability(identifier="principal_residence_line_32")
class PrincipalResidencePart2Line32(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 32 of each one."""

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
                PrincipalResidenceLine32(
                    self._output,
                    row.position,
                    row.pre_1982_completed,
                    row.line_30,
                    row.owned_before,
                    row.rounding,
                    row.line_32,
                )
                for row in self._rows(inputs)
            ]
        )
