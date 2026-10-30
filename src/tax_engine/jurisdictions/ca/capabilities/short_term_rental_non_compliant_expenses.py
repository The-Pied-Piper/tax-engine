"""ShortTermRentalNonCompliantExpenses: the non-compliant expenses of short-term rentals, per row.

Form T776, Chart A, "Non-compliant amount of expenses for short-term rentals": each short-term
rental or mixed rental is a row of the consumed record list, holding column 3 "Related portion of
the total from line 9365 of Part 4", column 4 "Number of days the residential property was a non
compliant short-term rental" and column 5 "Number of days the residential property was a
short-term rental". Column 6, "Non-compliant amount (column 3 multiplied by column 4 divided by
column 5)", is computed as an exact fraction and rounded once with the `rounding` dataset's rule.
The output, line B "Total of column 6", is the total of those rounded rows, 0 when there are no
rows. Each row is worked on its own, never pooled with the others. A row whose column 5 is 0, or
whose column 4 is above column 5, is refused with a ValidationError naming the row; the form
prints no maximum for column 5, so any other value is used as typed. It records
one `ShortTermRentalNonCompliantLine` for each row, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import ValidationError
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.catalog import (
    SHORT_TERM_RENTAL_DAYS,
    SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS,
    SHORT_TERM_RENTAL_RELATED_EXPENSES,
)
from tax_engine.jurisdictions.ca.trace import ShortTermRentalNonCompliantLine


@capability(identifier="short_term_rental_non_compliant_expenses")
class ShortTermRentalNonCompliantExpenses(Capability):
    """Produces `output`: the total, over the consumed `units`, of each row's related expenses
    times its non-compliant days over its days, each rounded by `rounding`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "rounding": ROUNDING_ONLY,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"units": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        units: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the record list it reads, the kind it
        produces."""
        super().__init__(units=units, output=output)
        self._rounding = rounding
        self._units = units
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._units).value.records
        rounding = self._rounding.rounding
        lines: list[ShortTermRentalNonCompliantLine] = []
        for position, record in enumerate(records, start=1):
            related_expenses = Decimal(record[SHORT_TERM_RENTAL_RELATED_EXPENSES])
            non_compliant_days = int(record[SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS])
            days = int(record[SHORT_TERM_RENTAL_DAYS])
            if days == 0:
                raise ValidationError(
                    f"row {position}: {SHORT_TERM_RENTAL_DAYS.identifier} cannot be 0, "
                    "column 6 divides by it"
                )
            if non_compliant_days > days:
                raise ValidationError(
                    f"row {position}: {SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS.identifier} "
                    f"({non_compliant_days}) cannot be above "
                    f"{SHORT_TERM_RENTAL_DAYS.identifier} ({days})"
                )
            amount = ExactFraction(related_expenses) * non_compliant_days / days
            lines.append(
                ShortTermRentalNonCompliantLine(
                    self._output,
                    position,
                    related_expenses,
                    non_compliant_days,
                    days,
                    rounding,
                    rounding.apply(amount),
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
