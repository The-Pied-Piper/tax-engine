"""ForeignBusinessTaxCreditLine8: line 8 of Form T2209, the federal business foreign tax credit.

Form T2209, Line 8 "Add basic federal tax (8) and the amount from line 6.": each sheet of the
consumed `sheets` is worked as `ForeignBusinessTaxCreditRows` works it, the basic federal tax plus
the sheet's line 6. The output is the total of those sheets, 0 when there are no sheets. It records
one `ForeignBusinessLine8` for each sheet, by position from 1, then an `ItemsTotalLine`.
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
from tax_calculator.jurisdictions.ca.capabilities.foreign_business_tax_credit_rows import (
    ForeignBusinessTaxCreditRows,
)
from tax_calculator.jurisdictions.ca.trace import ForeignBusinessLine8


@capability(identifier="foreign_business_tax_credit_line_8")
class ForeignBusinessTaxCreditLine8(ForeignBusinessTaxCreditRows):
    """Produces `output`: the total, over the consumed `sheets`, of line 8 of each sheet."""

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
                ForeignBusinessLine8(
                    self._output, row.position, row.basic_federal_tax, row.line_6, row.line_8
                )
                for row in self._rows(inputs)
            ]
        )
