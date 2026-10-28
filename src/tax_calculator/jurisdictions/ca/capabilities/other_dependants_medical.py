"""OtherDependantsMedical: the allowable medical expenses for other dependants, one claim each.

For the Federal Worksheet's chart for line 33199, filled in for each dependant: that dependant's
medical expenses (a field of each record in the consumed record list) less the `reduction`
dataset's lesser of its ceiling and its rate times that dependant's net income (the dependant's
own line 109, worked out from this return's figures), from 0 up to the dataset's maximum when it
has one. The output is the total of those allowable amounts, 0 when there are no dependants. Each
dependant is worked on its own, never pooled with the others. The reduction is a cent figure on
the dependant's return, so it is rounded with the dataset's rule before it is taken off, and the
allowable amount is rounded with it too, before the total. It
records one `OtherDependantMedicalLine` for each dependant, by position from 1, then an
`ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.claim_reduction import CLAIM_REDUCTION, ClaimReduction
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.catalog import (
    DEPENDANT_NET_INCOME,
    OTHER_DEPENDANT_MEDICAL_EXPENSES,
)
from tax_calculator.jurisdictions.ca.trace import OtherDependantMedicalLine


@capability(identifier="other_dependants_medical")
class OtherDependantsMedical(Capability):
    """Produces `output`: the total, over the consumed `dependants`, of each one's medical
    expenses less the `reduction` dataset's lesser of its ceiling and its rate times their net
    income, from 0 up to the dataset's maximum when it has one."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[ClaimReduction]]] = {
        "reduction": CLAIM_REDUCTION
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"dependants": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        reduction: ParameterDataset[ClaimReduction],
        dependants: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its reduction dataset, the record list it reads, the kind
        produced."""
        super().__init__(dependants=dependants, output=output)
        self._reduction = reduction
        self._dependants = dependants
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._dependants).value.records
        reduction = self._reduction.values
        rounding = self._reduction.rounding
        lines: list[OtherDependantMedicalLine] = []
        for position, record in enumerate(records, start=1):
            expenses = Decimal(record[OTHER_DEPENDANT_MEDICAL_EXPENSES])
            net_income = Decimal(record[DEPENDANT_NET_INCOME])
            taken_off = rounding.apply(min(reduction.ceiling, reduction.rate.value * net_income))
            allowable = max(Decimal(0), expenses - taken_off)
            if reduction.maximum is not None:
                allowable = min(allowable, reduction.maximum)
            lines.append(
                OtherDependantMedicalLine(
                    self._output,
                    position,
                    expenses,
                    net_income,
                    reduction,
                    rounding,
                    rounding.apply(allowable),
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
