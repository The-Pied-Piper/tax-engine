"""ShortTermRentalNonCompliantCcaByClass: the non-compliant CCA of short-term rentals, per class.

Form T776, Chart B: "*** For each class, add the amounts from column 7 of Chart B and enter each
total in column 22 of Area A, in the respective row." Each row of the consumed record list is
worked as `ShortTermRentalCcaRows` works it, column 7 rounded once with the `rounding` dataset's
rule. The output is a record list of the class number and column 22 "Non-compliant amount of CCA
(see Chart B below)", one record per distinct class in the order it first appears: the total of
that class's rounded column 7 amounts. It records one `ShortTermRentalNonCompliantCcaByClassLine`
for each class, by position from 1, and no total.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityResult, capability
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rounding_only import RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.short_term_rental_cca_rows import ShortTermRentalCcaRows
from tax_calculator.jurisdictions.ca.catalog import CCA_CLASS_NUMBER, NON_COMPLIANT_CCA
from tax_calculator.jurisdictions.ca.trace import ShortTermRentalNonCompliantCcaByClassLine


@capability(identifier="short_term_rental_non_compliant_cca_by_class")
class ShortTermRentalNonCompliantCcaByClass(ShortTermRentalCcaRows):
    """Produces `output`: for each class of the consumed `units`, its class number and the total
    of its rows' column 7 amounts, each rounded by `rounding`."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": RecordList}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        units: ArtifactKind[RecordList],
        output: ArtifactKind[RecordList],
    ) -> None:
        """Wire the capability: its rounding dataset, the record list it
        reads, the record list kind produced, of the class number and column 22."""
        super().__init__(rounding, units, output)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amounts: dict[Decimal, list[Decimal]] = {}
        for row in self._rows(inputs):
            amounts.setdefault(row.class_number, []).append(row.result)
        lines: list[ShortTermRentalNonCompliantCcaByClassLine] = []
        records: list[dict[ArtifactKind[Any], Decimal]] = []
        for position, (class_number, class_amounts) in enumerate(amounts.items(), start=1):
            total = sum(class_amounts, Decimal(0))
            lines.append(
                ShortTermRentalNonCompliantCcaByClassLine(
                    self._output, position, class_number, tuple(class_amounts), total
                )
            )
            records.append({CCA_CLASS_NUMBER: class_number, NON_COMPLIANT_CCA: total})
        return CapabilityResult(
            outputs=(
                Artifact(self._output, RecordList((CCA_CLASS_NUMBER, NON_COMPLIANT_CCA), records)),
            ),
            trace=tuple(lines),
        )
