"""ForeignBusinessTaxCreditLine4: line 4 of Form T2209, the federal business foreign tax credit.

Form T2209, Line 4 (43400) "Business income tax paid to a foreign country (5) for the year, plus any
unused foreign tax credits for that country for the 10 years (6) before, and the 3 years after this
year": each sheet of the consumed `sheets` is worked as `ForeignBusinessTaxCreditRows` works it, the
sheet's business income tax paid for the year plus its unused business foreign tax credits. The
output is the total of those sheets, 0 when there are no sheets. It records one
`ForeignBusinessLine4` for each sheet, by position from 1, then an `ItemsTotalLine`.
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
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_rows import (
    ForeignBusinessTaxCreditRows,
)
from tax_engine.jurisdictions.ca.trace import ForeignBusinessLine4


@capability(identifier="foreign_business_tax_credit_line_4")
class ForeignBusinessTaxCreditLine4(ForeignBusinessTaxCreditRows):
    """Produces `output`: the total, over the consumed `sheets`, of line 4 of each sheet."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        sheets: ArtifactKind[RecordList],
        net_income: ArtifactKind[Decimal],
        basic_federal_tax: ArtifactKind[Decimal],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the kinds it reads, the kind produced."""
        super().__init__(rounding, sheets, net_income, basic_federal_tax, output)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return self._result(
            [
                ForeignBusinessLine4(
                    self._output, row.position, row.tax_paid, row.unused_credits, row.line_4
                )
                for row in self._rows(inputs)
            ]
        )
