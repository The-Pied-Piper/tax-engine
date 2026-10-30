"""CcaClaim: the total capital cost allowance claim of the CCA table, T776 and T2125 Area A.

T776 "Line ii: Total CCA claim for the year: Total of column 23" and T2125 "Total CCA claim for the
year: Total of column 21": each class of the consumed record list is one row of the table, worked
on its own as `CcaTable` works it, with its rate, factors and half-year rule from the
`class_rates` dataset and columns 15, 17 and 18 and the maximum rounded once each with the
dataset's rule. The claim of each row is the caller's, from column 9 (0 for a class without a
DIEP) up to the maximum ("column 19 multiplied by column 20, or a lower amount") plus column 9,
and refused outside them. The output is the total of
the claims, 0 when there are no classes. It records one `CcaClaimLine` for each class, by
position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import CapabilityResult, capability
from tax_engine.domain.parameters.class_rates import ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.cca_table import CcaTable
from tax_engine.jurisdictions.ca.trace import CcaClaimLine


@capability(identifier="cca_claim")
class CcaClaim(CcaTable):
    """Produces `output`: the total, over the consumed `classes`, of each class's CCA claimed, at
    most its maximum from the `class_rates` dataset."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        classes: ArtifactKind[RecordList],
        output: Money,
        **consumed: ArtifactKind[Any],
    ) -> None:
        """Wire the capability: its class-rate dataset, the record list it reads, the kind
        produced. A subclass consuming more record lists passes them by slot name."""
        super().__init__(class_rates, classes, output, **consumed)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        lines: list[CcaClaimLine] = []
        for row in self._rows(inputs):
            columns = self._columns(row)
            lines.append(
                CcaClaimLine(
                    output=self._output,
                    position=row.position,
                    class_rate=row.class_rate,
                    no_property_left=row.no_property_left,
                    column_7=row.column_7,
                    column_14=columns.column_14,
                    column_15=columns.column_15,
                    column_16=columns.column_16,
                    column_17=columns.column_17,
                    column_18=columns.column_18,
                    column_19=columns.column_19,
                    zero_reason=row.zero_reason,
                    maximum=columns.maximum,
                    rounding=self._class_rates.rounding,
                    claim=row.claimed,
                    column_9=row.immediate_expensing,
                    half_year_rule_on_sale=row.half_year_rule_on_sale,
                    fiscal_period_days=row.fiscal_period_days,
                    full_year_days=self._class_rates.values.full_year_days,
                )
            )
        items = tuple((line.position, line.claim) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
