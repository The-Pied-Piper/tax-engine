"""PrincipalResidenceWorksheetLine30Capability: line 30 of Form T2091(IND)-WS, line 28 less line 29.

It records one `PrincipalResidenceWorksheetLine30` for each property, by position from 1, then an
`ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.factor import Factor
from tax_engine.domain.parameters.rounding_only import RoundingOnly
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.principal_residence_worksheet_rows import (
    PrincipalResidenceWorksheetRows,
)
from tax_engine.jurisdictions.ca.trace import PrincipalResidenceWorksheetLine30


@capability(identifier="principal_residence_worksheet_line_30")
class PrincipalResidenceWorksheetLine30Capability(PrincipalResidenceWorksheetRows):
    """Produces `output`: the total over the consumed `properties` of worksheet line 30."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        chart_1_factor: ParameterDataset[Factor],
        properties: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding and Chart 1 factor datasets, the record list read and
        the kind produced."""
        super().__init__(rounding, chart_1_factor, properties, output)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return self._result(
            [
                PrincipalResidenceWorksheetLine30(
                    self._output,
                    row.position,
                    row.pre_1982_completed,
                    row.line_28,
                    row.line_29,
                    row.line_30,
                )
                for row in self._worksheet_rows(inputs)
            ]
        )
