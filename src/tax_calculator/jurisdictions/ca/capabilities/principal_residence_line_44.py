"""PrincipalResidencePart2Line44: line 44 of Form T2091(IND) Part 2, the post-1981 exempt part.

Form T2091(IND) Part 2, line 44 "Divide line 42 by line 43.": line 42 divided by the years owned
after 1981 (line 43, "Number of years from line 5"), rounded once with the `rounding` dataset's
rule, so it may be negative. It is 0 when area B is not completed. The output is the total of those
quotients over the consumed `properties`, 0 when there are none. It records one
`PrincipalResidenceLine44` for each property, by position from 1, then an `ItemsTotalLine`.
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
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceLine44


@capability(identifier="principal_residence_line_44")
class PrincipalResidencePart2Line44(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 44 of each one."""

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
                PrincipalResidenceLine44(
                    self._output,
                    row.position,
                    row.post_1981_completed,
                    row.line_42,
                    row.owned_after,
                    row.rounding,
                    row.line_44,
                )
                for row in self._rows(inputs)
            ]
        )
