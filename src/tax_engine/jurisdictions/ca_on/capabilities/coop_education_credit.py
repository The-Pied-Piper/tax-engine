"""CoopEducationCredit: the Ontario co-operative education tax credit of every work placement.

Worksheet ON479, "Line 20 - Ontario co-operative education tax credit", is completed for each
qualifying work placement: line 1 is the eligible expenditures (line A) "multiplied by 25%"; line
3 is amount A multiplied by the 5% of line 2; line 12 is line 3 multiplied by line 11; line 13 is
"Line 1 plus line 12 (maximum $3,000 per student)". "Enter the total amount claimed for all
qualifying work placements on line 20". This capability reads the record list of the placements
and line 11 and produces the total of every placement's line 13.

Lines 1, 3 and 12 are exact: the two rate datasets round nothing. Line 13 is the lesser of line 1
plus line 12 and the maximum, rounded with the maximum dataset's rule, like `core/capped_amount`;
the total adds those rounded lines. Each placement is named by its position from 1 in the trace.
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
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca_on.catalog import COOP_EDUCATION_PLACEMENT_EXPENDITURES
from tax_engine.jurisdictions.ca_on.trace import PlacementCreditLine


@capability(identifier="coop_education_credit")
class CoopEducationCredit(Capability):
    """Produces `output`: the total of line 13 of every consumed placement at `remaining_share`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "expenditure_rate": RATE,
        "supplement_rate": RATE,
        "maximum": AMOUNT,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"placements": RecordList, "remaining_share": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        expenditure_rate: ParameterDataset[Rate],
        supplement_rate: ParameterDataset[Rate],
        maximum: ParameterDataset[Amount],
        placements: ArtifactKind[RecordList],
        remaining_share: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its two rates and its maximum, the placement list, line 11, the
        kind it produces."""
        super().__init__(placements=placements, remaining_share=remaining_share, output=output)
        self._expenditure_rate = expenditure_rate
        self._supplement_rate = supplement_rate
        self._maximum = maximum
        self._placements = placements
        self._remaining_share = remaining_share
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._placements).value.records
        share = self._input(inputs, self._remaining_share).value
        expenditure_rate = self._expenditure_rate.values
        supplement_rate = self._supplement_rate.values
        maximum, rounding = self._maximum.values, self._maximum.rounding
        lines: list[PlacementCreditLine] = []
        for position, record in enumerate(records, start=1):
            expenditure = record[COOP_EDUCATION_PLACEMENT_EXPENDITURES]
            if not isinstance(expenditure, Decimal):
                raise TypeError(
                    f"{COOP_EDUCATION_PLACEMENT_EXPENDITURES.identifier} must be a Decimal, "
                    f"got {type(expenditure).__name__}"
                )
            line_1 = expenditure * expenditure_rate.value
            line_3 = expenditure * supplement_rate.value
            line_12 = line_3 * share
            total = line_1 + line_12
            line_13 = rounding.apply(maximum.value if total > maximum.value else total)
            lines.append(
                PlacementCreditLine(
                    output=self._output,
                    position=position,
                    field=COOP_EDUCATION_PLACEMENT_EXPENDITURES,
                    expenditure=expenditure,
                    line_1=line_1,
                    line_3=line_3,
                    line_12=line_12,
                    line_13=line_13,
                    remaining_share=self._remaining_share,
                    remaining_share_amount=share,
                    expenditure_rate=expenditure_rate,
                    supplement_rate=supplement_rate,
                    maximum=maximum,
                    rounding=rounding,
                )
            )
        total = sum((line.line_13 for line in lines), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(
                *lines,
                ItemsTotalLine(
                    output=self._output,
                    items=tuple((line.position, line.line_13) for line in lines),
                    total=total,
                ),
            ),
        )
