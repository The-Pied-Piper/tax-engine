"""ApprenticeshipWagesTotal: the apprenticeship job creation tax credit's wages, one apprentice at a
time.

For Form T2038(IND) Part B, Table 1, column 3, filled in for each apprentice: the lesser of that
apprentice's eligible salary and wages (a field of each record in the consumed record list) and the
`maximum` dataset's amount. The output is the total of those amounts, 0 when there are no
apprentices. Each apprentice is worked on its own, never pooled with the others, and its amount is
rounded once, with the `maximum` dataset's rule, before the total. It records one
`ApprenticeWagesLine` for each apprentice, by position from 1, then an `ItemsTotalLine`.
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
from tax_calculator.jurisdictions.ca.catalog import ITC_APPRENTICE_SALARY_AND_WAGES
from tax_calculator.jurisdictions.ca.trace import ApprenticeWagesLine


@capability(identifier="apprenticeship_wages_total")
class ApprenticeshipWagesTotal(Capability):
    """Produces `output`: the total, over the consumed `apprentices`, of the lesser of each one's
    eligible salary and wages and the `maximum` dataset's amount."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"maximum": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"apprentices": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        maximum: ParameterDataset[Amount],
        apprentices: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its maximum dataset, the record list it reads, the kind produced."""
        super().__init__(apprentices=apprentices, output=output)
        self._maximum = maximum
        self._apprentices = apprentices
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._apprentices).value.records
        maximum = self._maximum.values
        rounding = self._maximum.rounding
        lines: list[ApprenticeWagesLine] = []
        for position, record in enumerate(records, start=1):
            salary_and_wages = Decimal(record[ITC_APPRENTICE_SALARY_AND_WAGES])
            lesser = min(salary_and_wages, maximum.value)
            result = rounding.apply(lesser)
            lines.append(
                ApprenticeWagesLine(
                    self._output, position, salary_and_wages, maximum, rounding, result
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
