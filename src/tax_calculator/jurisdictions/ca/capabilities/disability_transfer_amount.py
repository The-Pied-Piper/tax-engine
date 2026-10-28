"""DisabilityTransferAmount: the disability amount transferred from a dependant, one claim each.

For the Federal Worksheet for line 31800, completed for each dependant who is eligible for the
disability tax credit: the `base` dataset's amount (line 1) plus, for a dependant under 18, the
`supplement` dataset's amount (line 2) less the dependant's child care and attendant care
expenses over the `threshold` dataset's amount (line 4), from 0 (lines 5 to 7), at most the
`maximum` dataset's amount (line 8); that, plus the credit amounts of the dependant's own return
(line 9), less the dependant's taxable income (line 11), from 0 (line 12); and the lesser of
lines 8 and 12 (line 13). The four figures of each dependant are fields of each record in the
consumed record list. The output is the total of those allowable amounts, 0 when there are no
dependants. Each dependant is worked on its own, never pooled with the others, and line 13 is
rounded once, with the `maximum` dataset's rule, before the total; lines 5 to 12 stay exact. It
records one `DisabilityTransferLine` for each dependant, by position from 1, then an
`ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.catalog import (
    DEPENDANT_CARE_EXPENSES,
    DEPENDANT_CREDIT_AMOUNTS,
    DEPENDANT_TAXABLE_INCOME,
    DEPENDANT_UNDER_18,
)
from tax_calculator.jurisdictions.ca.trace import DisabilityTransferLine


@capability(identifier="disability_transfer_amount")
class DisabilityTransferAmount(Capability):
    """Produces `output`: the total, over the consumed `dependants`, of each one's allowable
    amount on the worksheet for the disability amount transferred from a dependant, from the
    `base`, `supplement`, `threshold` and `maximum` datasets."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {
        "base": AMOUNT,
        "supplement": AMOUNT,
        "threshold": AMOUNT,
        "maximum": AMOUNT,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"dependants": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        base: ParameterDataset[Amount],
        supplement: ParameterDataset[Amount],
        threshold: ParameterDataset[Amount],
        maximum: ParameterDataset[Amount],
        dependants: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its four datasets, the record list it reads, the kind produced."""
        super().__init__(dependants=dependants, output=output)
        self._base = base
        self._supplement = supplement
        self._threshold = threshold
        self._maximum = maximum
        self._dependants = dependants
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._dependants).value.records
        base, supplement = self._base.values, self._supplement.values
        threshold, maximum = self._threshold.values, self._maximum.values
        rounding = self._maximum.rounding
        zero = Decimal(0)
        lines: list[DisabilityTransferLine] = []
        for position, record in enumerate(records, start=1):
            under_18 = record[DEPENDANT_UNDER_18]
            care_expenses = Decimal(record[DEPENDANT_CARE_EXPENSES])
            credit_amounts = Decimal(record[DEPENDANT_CREDIT_AMOUNTS])
            taxable_income = Decimal(record[DEPENDANT_TAXABLE_INCOME])
            line_5 = max(zero, care_expenses - threshold.value)
            line_6 = max(zero, supplement.value - line_5)
            line_7 = line_6 if under_18 else zero
            line_8 = min(base.value + line_7, maximum.value)
            line_10 = line_8 + credit_amounts
            line_12 = max(zero, line_10 - taxable_income)
            result = rounding.apply(min(line_8, line_12))
            lines.append(
                DisabilityTransferLine(
                    self._output,
                    position,
                    base,
                    supplement,
                    threshold,
                    maximum,
                    1 if under_18 else 0,
                    care_expenses,
                    line_5,
                    line_6,
                    line_7,
                    line_8,
                    credit_amounts,
                    line_10,
                    taxable_income,
                    line_12,
                    rounding,
                    result,
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
