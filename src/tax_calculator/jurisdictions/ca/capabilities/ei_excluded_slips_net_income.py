"""EiExcludedSlipsNetIncome: the net income of the T4 slips with EI premiums, added.

Schedule 13 line 1 reads "If you received a T4 slip for self-employment income with EI premiums in
box 18, do not include any net income (or net loss) reported on lines 13500, 13700, 13900, 14100,
and 14300 of your return for that slip (Note 1)". This capability reads the record list of those
slips and adds the net income (or net loss) of every record, exactly: a net loss is negative, it has
no dataset, so it never rounds, and an empty list totals zero. Each item is named by its position
from 1 in the trace.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import RecordTotalLine
from tax_calculator.jurisdictions.ca.catalog import EI_EXCLUDED_SLIP_NET_INCOME


@capability(identifier="ei_excluded_slips_net_income")
class EiExcludedSlipsNetIncome(Capability):
    """Produces `output`: the net income of every consumed `slips` record."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"slips": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, slips: ArtifactKind[RecordList], output: Money) -> None:
        """Wire the capability: the record-list kind it reads and the kind it produces."""
        super().__init__(slips=slips, output=output)
        self._slips = slips
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amounts: list[Decimal] = []
        for record in self._input(inputs, self._slips).value.records:
            amount = record[EI_EXCLUDED_SLIP_NET_INCOME]
            if not isinstance(amount, Decimal):
                raise TypeError(
                    f"{EI_EXCLUDED_SLIP_NET_INCOME.identifier} must be a Decimal, "
                    f"got {type(amount).__name__}"
                )
            amounts.append(amount)
        total = sum(amounts, Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(
                RecordTotalLine(
                    output=self._output,
                    field=EI_EXCLUDED_SLIP_NET_INCOME,
                    amounts=tuple(amounts),
                    total=total,
                ),
            ),
        )
