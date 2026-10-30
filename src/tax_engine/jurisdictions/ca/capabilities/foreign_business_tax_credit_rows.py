"""ForeignBusinessTaxCreditRows: the base of the capabilities of lines 4 to 11 of Form T2209, not
registered itself.

Form T2209, "Federal business foreign tax credit": each sheet of the consumed `sheets` list (the
T2209 "separate sheet" of each country, or the one pooled sheet) is worked on its own, never
pooled with the others. Line 4 (43400) "Business income tax paid to a foreign country (5) for the
year, plus any unused foreign tax credits for that country for the 10 years (6) before, and the 3
years after this year" is the sheet's business tax paid plus its unused credits. Line 5 "Net
foreign business income (7) 43900" "× Basic federal tax (8)" over "Net income (3)" is the sheet's
business income (already capped at net income, note (7)) times the consumed `basic_federal_tax`
over the consumed `net_income`, an exact fraction worked by `ApplyRatio.ratio_of` and rounded once
with the `rounding` dataset's rule. Line 6 "Federal surtax on income allocated to "Other (Outside
Canada)"" is the sheet's own figure. Line 7 "Add lines 5 and 6.", line 8 "Add basic federal tax
(8) and the amount from line 6.", line 9 "Enter the amount from line 3, if any." (the sheet's
line 3), line 10 "Line 8 minus line 9" and line 11 "Enter whichever is less: the amount from line
4, 7 or 10." follow from those. A net income of zero or less makes line 5 0 without a division (no
tax is payable, so no credit, Income Tax Act s.126(1)), and the lines that follow work from the
other figures; no sheets give 0 and do not consult net income. A subclass is one
capability for each form line, building its own trace lines and output.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_ratio import ApplyRatio
from tax_engine.domain.capability import Capability, CapabilityResult
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.domain.trace.base import TraceLine
from tax_engine.jurisdictions.ca.catalog import (
    FOREIGN_BUSINESS_TAX_PAID,
    FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
    FOREIGN_SURTAX_OUTSIDE_CANADA,
    FOREIGN_TAX_CREDIT_SHEET_LINE_3,
    NET_FOREIGN_BUSINESS_INCOME,
)


@dataclass(frozen=True)
class ForeignBusinessSheetRow:
    """The sheet at `position` (from 1) worked: `tax_paid` and `unused_credits` into `line_4`,
    `income` over `net_income` times `basic_federal_tax` into `line_5` (rounded with `rounding`),
    `line_6`, `line_7`, `line_8`, `line_3` (line 9), `line_10` and `line_11`."""

    position: int
    tax_paid: Decimal
    unused_credits: Decimal
    income: Decimal
    net_income: Decimal
    basic_federal_tax: Decimal
    rounding: RoundingRule
    line_3: Decimal
    line_4: Decimal
    line_5: Decimal
    line_6: Decimal
    line_7: Decimal
    line_8: Decimal
    line_10: Decimal
    line_11: Decimal


class ForeignBusinessTaxCreditRows(Capability):
    """Reads the consumed `sheets`, `net_income` and `basic_federal_tax`, and works lines 4 to 11
    of each sheet; a subclass produces `output` from the rows."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {
        "sheets": RecordList,
        "net_income": Decimal,
        "basic_federal_tax": Decimal,
    }

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        sheets: ArtifactKind[RecordList],
        net_income: ArtifactKind[Decimal],
        basic_federal_tax: ArtifactKind[Decimal],
        output: ArtifactKind[Any],
    ) -> None:
        """Wire the rounding dataset and the kinds read; the subclass keeps `output`."""
        super().__init__(
            sheets=sheets,
            net_income=net_income,
            basic_federal_tax=basic_federal_tax,
            output=output,
        )
        self._rounding = rounding
        self._sheets = sheets
        self._net_income = net_income
        self._basic_federal_tax = basic_federal_tax
        self._output_kind = output

    def _rows(self, inputs: tuple[Artifact[Any], ...]) -> tuple[ForeignBusinessSheetRow, ...]:
        """Each consumed sheet, in order, as a row with lines 4 to 11 worked."""
        records = self._input(inputs, self._sheets).value.records
        if not records:
            return ()
        net_income = self._input(inputs, self._net_income).value
        basic_federal_tax = self._input(inputs, self._basic_federal_tax).value
        rule = self._rounding.rounding
        rows: list[ForeignBusinessSheetRow] = []
        for position, record in enumerate(records, 1):
            tax_paid = Decimal(record[FOREIGN_BUSINESS_TAX_PAID])
            unused_credits = Decimal(record[FOREIGN_BUSINESS_UNUSED_TAX_CREDITS])
            income = Decimal(record[NET_FOREIGN_BUSINESS_INCOME])
            line_6 = Decimal(record[FOREIGN_SURTAX_OUTSIDE_CANADA])
            line_3 = Decimal(record[FOREIGN_TAX_CREDIT_SHEET_LINE_3])
            line_4 = tax_paid + unused_credits
            line_5 = (
                Decimal(0)
                if net_income <= 0
                else ApplyRatio.ratio_of(income, basic_federal_tax, net_income, rule)
            )
            line_7 = line_5 + line_6
            line_8 = basic_federal_tax + line_6
            line_10 = line_8 - line_3
            rows.append(
                ForeignBusinessSheetRow(
                    position,
                    tax_paid,
                    unused_credits,
                    income,
                    net_income,
                    basic_federal_tax,
                    rule,
                    line_3,
                    line_4,
                    line_5,
                    line_6,
                    line_7,
                    line_8,
                    line_10,
                    min(line_4, line_7, line_10),
                )
            )
        return tuple(rows)

    def _result(self, lines: list[Any]) -> CapabilityResult:
        """The `output` as the total of the `lines` (each with a `position` and a `result`), and
        the trace: those lines, then an `ItemsTotalLine`."""
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        trace: tuple[TraceLine, ...] = (
            *lines,
            ItemsTotalLine(self._output_kind, items, total),
        )
        return CapabilityResult(outputs=(Artifact(self._output_kind, total),), trace=trace)
