"""ForeignTaxCountriesTotal: the base of the totals over the foreign tax countries, not registered.

For Form T2209, one record for each country in the consumed record list. The output is the sum of
`FIELD` over every record, in the record list's order: a record with 0 in `FIELD` adds 0 and is
still listed, and an empty list totals 0. The sum is exact and never rounds, as there is no
dataset. The trace is one ItemsTotalLine: each record's amount by its position from 1, then the
total. A subclass is one capability for the total of one figure of the records, named by its
`FIELD`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine


class ForeignTaxCountriesTotal(Capability):
    """Produces `output`: the sum of `FIELD` over every consumed country record, exact.

    The trace lists each record's `FIELD` by its position from 1, then the total.
    """

    FIELD: ClassVar[ArtifactKind[Any]]
    CONSUMES: ClassVar[Mapping[str, type]] = {"countries": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, countries: ArtifactKind[RecordList], output: Money) -> None:
        """Wire the capability: the record-list kind it reads and the kind it produces."""
        super().__init__(countries=countries, output=output)
        self._countries = countries
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        items: list[tuple[int, Decimal]] = []
        for position, record in enumerate(self._input(inputs, self._countries).value.records, 1):
            amount = record[self.FIELD]
            if not isinstance(amount, Decimal):
                raise TypeError(
                    f"{self.FIELD.identifier} must be a Decimal, got {type(amount).__name__}"
                )
            items.append((position, amount))
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(ItemsTotalLine(self._output, tuple(items), total),),
        )
