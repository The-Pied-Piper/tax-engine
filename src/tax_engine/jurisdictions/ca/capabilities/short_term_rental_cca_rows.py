"""ShortTermRentalCcaRows: the base of the capabilities of Chart B of Form T776, not registered
itself.

Form T776, Chart B, "Non-compliant amount of CCA for short-term rentals": each short-term rental
or mixed rental is a row of the consumed record list, holding column 1 "Class number", column 4
"Related portion of the available CCA from column 21 in Area A", column 5 "Number of days the
residential property was a non-compliant short-term rental" and column 6 "Number of days the
residential property was a short-term rental". Column 7, "Non-compliant amount (column 4
multiplied by column 5 divided by column 6)", is computed as an exact fraction and rounded once
with the `rounding` dataset's rule. Each row is worked on its own, never pooled with the others.
A row whose column 6 is 0, or whose column 5 is above column 6, is refused with a
ValidationError naming the row; the form prints no maximum for column 6, so any other value is
used as typed. A subclass is one capability for each form line the chart gives, building its own
trace lines and output.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability
from tax_engine.domain.errors import ValidationError
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    SHORT_TERM_RENTAL_DAYS,
    SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS,
    SHORT_TERM_RENTAL_RELATED_CCA,
)


@dataclass(frozen=True)
class ShortTermRentalCcaRow:
    """One row of Chart B at `position` (from 1): its `class_number` (column 1), `related_cca`
    (column 4), `non_compliant_days` (column 5) and `days` (column 6), and `result`, column 7
    rounded once with `rounding`."""

    position: int
    class_number: Decimal
    related_cca: Decimal
    non_compliant_days: int
    days: int
    rounding: RoundingRule
    result: Decimal


class ShortTermRentalCcaRows(Capability):
    """Reads the consumed `units`, one row each, and works column 7 of each; a subclass produces
    `output` from the rows."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "rounding": ROUNDING_ONLY,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"units": RecordList}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        units: ArtifactKind[RecordList],
        output: ArtifactKind[Any],
    ) -> None:
        """Wire the rounding dataset and the record list read; the subclass keeps `output`."""
        super().__init__(units=units, output=output)
        self._rounding = rounding
        self._units = units

    def _rows(self, inputs: tuple[Artifact[Any], ...]) -> tuple[ShortTermRentalCcaRow, ...]:
        """Each consumed record, in order, as a row with column 7 worked and rounded."""
        rounding = self._rounding.rounding
        rows: list[ShortTermRentalCcaRow] = []
        for position, record in enumerate(self._input(inputs, self._units).value.records, 1):
            related_cca = Decimal(record[SHORT_TERM_RENTAL_RELATED_CCA])
            non_compliant_days = int(record[SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS])
            days = int(record[SHORT_TERM_RENTAL_DAYS])
            if days == 0:
                raise ValidationError(
                    f"row {position}: {SHORT_TERM_RENTAL_DAYS.identifier} cannot be 0, "
                    "column 7 divides by it"
                )
            if non_compliant_days > days:
                raise ValidationError(
                    f"row {position}: {SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS.identifier} "
                    f"({non_compliant_days}) cannot be above "
                    f"{SHORT_TERM_RENTAL_DAYS.identifier} ({days})"
                )
            amount = ExactFraction(related_cca) * non_compliant_days / days
            rows.append(
                ShortTermRentalCcaRow(
                    position,
                    Decimal(record[CCA_CLASS_NUMBER]),
                    related_cca,
                    non_compliant_days,
                    days,
                    rounding,
                    rounding.apply(amount),
                )
            )
        return tuple(rows)
