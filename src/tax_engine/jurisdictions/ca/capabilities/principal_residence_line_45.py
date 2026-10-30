"""PrincipalResidencePart2Line45: line 45 of Form T2091(IND) Part 2, the post-1981 gain.

Form T2091(IND) Part 2, line 45 "Line 39 minus line 44 (if negative, enter "0")": line 39 less line
44, not below 0. It is 0 when area B is not completed. The output is the total of those amounts over
the consumed `properties`, 0 when there are none. It records one `PrincipalResidenceLine45` for each
property, by position from 1, then an `ItemsTotalLine`.
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
from tax_engine.jurisdictions.ca.trace import PrincipalResidenceLine45


@capability(identifier="principal_residence_line_45")
class PrincipalResidencePart2Line45(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 45 of each one."""

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
                PrincipalResidenceLine45(
                    self._output,
                    row.position,
                    row.post_1981_completed,
                    row.line_39,
                    row.line_44,
                    row.line_45,
                )
                for row in self._rows(inputs)
            ]
        )
