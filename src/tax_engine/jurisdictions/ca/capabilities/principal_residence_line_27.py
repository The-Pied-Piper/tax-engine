"""PrincipalResidencePart2Line27: line 27 of Form T2091(IND) Part 2, the pre-1982 gain before the
exemption.

Form T2091(IND) Part 2, line 27 "Line 25 minus line 26": the fair market value on December 31, 1981
(line 25, line 12) less the adjusted cost base on that date (line 26, line 11), not floored. It is 0
when area A is not completed. The output is the total of those amounts over the consumed
`properties`, 0 when there are none. It records one `PrincipalResidenceLine27` for each property, by
position from 1, then an `ItemsTotalLine`.
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
from tax_engine.jurisdictions.ca.trace import PrincipalResidenceLine27


@capability(identifier="principal_residence_line_27")
class PrincipalResidencePart2Line27(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of line 27 of each one."""

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
                PrincipalResidenceLine27(
                    self._output,
                    row.position,
                    row.pre_1982_completed,
                    row.fmv_1981,
                    row.cost_base_1981,
                    row.line_27,
                )
                for row in self._rows(inputs)
            ]
        )
