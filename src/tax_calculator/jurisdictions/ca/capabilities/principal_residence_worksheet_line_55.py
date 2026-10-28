"""PrincipalResidenceWorksheetLine55Capability: line 55 of Form T2091(IND)-WS, line 53 less line 54,
not below 0.

It records one `PrincipalResidenceWorksheetLine55` for each property, by position from 1, then an
`ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import CapabilityResult, capability
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.factor import Factor
from tax_calculator.domain.parameters.rounding_only import RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_rows import (
    PrincipalResidenceWorksheetRows,
)
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceWorksheetLine55


@capability(identifier="principal_residence_worksheet_line_55")
class PrincipalResidenceWorksheetLine55Capability(PrincipalResidenceWorksheetRows):
    """Produces `output`: the total over the consumed `properties` of worksheet line 55."""

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
                PrincipalResidenceWorksheetLine55(
                    self._output,
                    row.position,
                    row.part_2_completed,
                    row.line_53,
                    row.part_2_line_54,
                    row.line_55,
                )
                for row in self._worksheet_rows(inputs)
            ]
        )
