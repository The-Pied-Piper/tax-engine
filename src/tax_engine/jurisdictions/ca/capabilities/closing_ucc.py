"""ClosingUcc: the UCC at the end of the year of each class of the CCA table, for next year.

T776 Area A "Column 24: UCC at the end of the year (column 7 minus column 23)" (T2125 column 22,
column 7 minus column 21), and Guide T4036 "Column 7": "You cannot claim CCA when the amount in
column 7 is: negative ... positive and you do not have any property left in that class ... In
either case, enter "0" in column 24". Each class of the consumed record list is one row of the
table, worked on its own as `CcaTable` works it, its claim refused above its maximum as
`ca/cca_claim` refuses it. The output is a record list of the class number and the UCC at the end
of the year, one record per class in the caller's order: column 7 less the claim, or 0 when column
7 is negative or is positive with no property left, or when the row used the half-year rule on
sale (Regulation 1100(2.5) allows no deduction in a later year; the rest is nil).

T776 Area A Note 9 (T2125, T2042 and T2121 print it as endnote 9, with "business" for "rental"):
"If, in the year, you disposed of a property that you used for both personal
and rental use, and your rental use of that property changed from year to year, you must subtract
any remaining personal part of this property's cost from the UCC at the end of the year." When the
consumed list lists the remaining personal part, column 24 of a row that does not close at 0 is
column 7 less the claim less that part; a part above column 7 less the claim is refused
(`InvalidRecordError`, naming the item and both figures), after the claim's own bound. A row that
closes at 0 is unaffected; a list that does not list the part leaves column 24 as before. It
records one `ClosingUccLine` for each class, by position from 1, which names why column 24 is 0
when it is, and no total.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityResult, capability
from tax_engine.domain.errors import InvalidRecordError
from tax_engine.domain.parameters.class_rates import ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.cca_table import CcaTable
from tax_engine.jurisdictions.ca.catalog import CCA_CLASS_NUMBER, CCA_UCC_AT_END
from tax_engine.jurisdictions.ca.trace import CcaZeroReason, ClosingUccLine


@capability(identifier="closing_ucc")
class ClosingUcc(CcaTable):
    """Produces `output`: for each of the consumed `classes`, its class number and its UCC at the
    end of the year, with its maximum from the `class_rates` dataset."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": RecordList}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        classes: ArtifactKind[RecordList],
        output: ArtifactKind[RecordList],
        **consumed: ArtifactKind[Any],
    ) -> None:
        """Wire the capability: its class-rate dataset, the record list it reads, the record list
        kind produced, of the class number and the UCC at the end of the year. A subclass
        consuming more record lists passes them by slot name."""
        super().__init__(class_rates, classes, output, **consumed)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        lines: list[ClosingUccLine] = []
        records: list[dict[ArtifactKind[Any], Decimal]] = []
        for row in self._rows(inputs):
            self._columns(row)
            # A sold Class 10.1 vehicle that used the half-year rule on sale closes at nil: the
            # rest of its UCC is not deductible later (Folio S3-F4-C1 paragraph 1.106).
            closes_at_zero = row.zero_reason is not CcaZeroReason.NONE or row.half_year_rule_on_sale
            part = row.personal_part_remaining
            if not closes_at_zero and part > row.column_7 - row.claimed:
                raise InvalidRecordError(
                    f"item {row.position}: personal part ({part}) is above column 7 less the "
                    f"claim ({row.column_7 - row.claimed})"
                )
            result = Decimal(0) if closes_at_zero else row.column_7 - row.claimed - part
            lines.append(
                ClosingUccLine(
                    self._output,
                    row.position,
                    row.class_rate,
                    row.no_property_left,
                    row.column_7,
                    row.zero_reason,
                    row.claimed,
                    result,
                    row.immediate_expensing,
                    row.half_year_rule_on_sale,
                    row.fiscal_period_days,
                    self._class_rates.values.full_year_days,
                    part,
                )
            )
            records.append({CCA_CLASS_NUMBER: row.class_number, CCA_UCC_AT_END: result})
        return CapabilityResult(
            outputs=(
                Artifact(self._output, RecordList((CCA_CLASS_NUMBER, CCA_UCC_AT_END), records)),
            ),
            trace=tuple(lines),
        )
