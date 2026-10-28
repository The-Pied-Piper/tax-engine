"""ShortTermRentalNonCompliantCca: the non-compliant CCA of short-term rentals, line 9367.

Form T776, Chart B, "Non-compliant amount of CCA for short-term rentals": each row of the
consumed record list is worked as `ShortTermRentalCcaRows` works it, column 7 "Non-compliant
amount (column 4 multiplied by column 5 divided by column 6)" rounded once with the `rounding`
dataset's rule. The output, "Line C: Total non-compliant amount of CCA for short-term rentals:
Total of column 7 (enter on line 9367 of Part 4)", is the total of those rounded rows, whatever
their classes, 0 when there are no rows. It records one `ShortTermRentalNonCompliantCcaLine` for
each row, by position from 1, then an `ItemsTotalLine`.
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
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.short_term_rental_cca_rows import (
    ShortTermRentalCcaRows,
)
from tax_calculator.jurisdictions.ca.trace import ShortTermRentalNonCompliantCcaLine


@capability(identifier="short_term_rental_non_compliant_cca")
class ShortTermRentalNonCompliantCca(ShortTermRentalCcaRows):
    """Produces `output`: the total, over the consumed `units`, of each row's related CCA times
    its non-compliant days over its days, each rounded by `rounding`."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        units: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the record list it
        reads, the kind produced."""
        super().__init__(rounding, units, output)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        lines = [
            ShortTermRentalNonCompliantCcaLine(
                self._output,
                row.position,
                row.class_number,
                row.related_cca,
                row.non_compliant_days,
                row.days,
                row.rounding,
                row.result,
            )
            for row in self._rows(inputs)
        ]
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
