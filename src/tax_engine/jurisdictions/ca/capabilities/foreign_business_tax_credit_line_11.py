"""ForeignBusinessTaxCreditLine11: line 11 of Form T2209, the federal business foreign tax credit.

Form T2209, Line 11 "Enter whichever is less: the amount from line 4, 7 or 10." "Federal business
foreign tax credit": each sheet of the consumed `sheets` is worked as `ForeignBusinessTaxCreditRows`
works it, the least of the sheet's lines 4, 7 and 10. The output is the total of those sheets, 0
when there are no sheets. It records one `ForeignBusinessLine11` for each sheet, by position from 1,
then an `ItemsTotalLine`.
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
from tax_engine.jurisdictions.ca.trace import ForeignBusinessLine11


@capability(identifier="foreign_business_tax_credit_line_11")
class ForeignBusinessTaxCreditLine11(ForeignBusinessTaxCreditRows):
    """Produces `output`: the total, over the consumed `sheets`, of line 11 of each sheet."""

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
                ForeignBusinessLine11(
                    self._output, row.position, row.line_4, row.line_7, row.line_10, row.line_11
                )
                for row in self._rows(inputs)
            ]
        )
