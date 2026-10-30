"""CaregiverAmount: the Canada caregiver amount for other infirm dependants, one claim each.

For Schedule 5's chart for line 30450, filled in for each dependant: the `base` dataset's amount
less that dependant's net income (a field of each record in the consumed record list), from 0 up
to the `maximum` dataset's amount. The output is the total of those allowable amounts, 0 when
there are no dependants. Each dependant is worked on its own, never pooled with the others, and
its allowable amount is rounded once, with the `maximum` dataset's rule, before the total. It
records one `CaregiverClaimLine` for each dependant, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.catalog import DEPENDANT_NET_INCOME
from tax_engine.jurisdictions.ca.trace import CaregiverClaimLine


@capability(identifier="caregiver_amount")
class CaregiverAmount(Capability):
    """Produces `output`: the total, over the consumed `dependants`, of the `base` dataset's
    amount less each one's net income, from 0 up to the `maximum` dataset's amount."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"base": AMOUNT, "maximum": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"dependants": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        base: ParameterDataset[Amount],
        maximum: ParameterDataset[Amount],
        dependants: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its base and maximum datasets, the record list it reads, the kind
        produced."""
        super().__init__(dependants=dependants, output=output)
        self._base = base
        self._maximum = maximum
        self._dependants = dependants
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._dependants).value.records
        base, maximum = self._base.values, self._maximum.values
        rounding = self._maximum.rounding
        lines: list[CaregiverClaimLine] = []
        for position, record in enumerate(records, start=1):
            net_income = Decimal(record[DEPENDANT_NET_INCOME])
            lesser = min(max(Decimal(0), base.value - net_income), maximum.value)
            result = rounding.apply(lesser)
            lines.append(
                CaregiverClaimLine(
                    self._output, position, base, net_income, maximum, rounding, result
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
