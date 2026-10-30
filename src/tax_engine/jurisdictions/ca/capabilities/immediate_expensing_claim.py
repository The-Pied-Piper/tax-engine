"""ImmediateExpensingClaim: the total immediate expensing claim of the CCA table.

The rental form (T776, Area A), the business form (T2125, Area A), the farm form (T2042, Area A)
and the fishing form (T2121, Area A) all print it.
T776 "Line i: Total immediate expensing claim for the year: Total of column 9", with Note 5: "The
total immediate expensing amount for the tax year (total of column 9) is limited to the lesser of"
the immediate expensing limit, "the UCC of DIEPs in column 8" and "the amount of income, if any,
earned from the source of income that is a property (before any CCA deductions) in which the
relevant DIEP is used for the tax year". Each class of the consumed record list is one row of the
table, worked on its own as `CcaTable` works it: column 8 is column 4 minus column 6, at most
column 7 and at least 0, and the column 9 of a row is refused above it, so the total of column 9
cannot pass the total of column 8. The output is the total of column 9, 0 when there are no
classes or the list does not list the DIEP columns. A total above the consumed
`immediate_expensing_limit`, or above the consumed `income_before_cca` (a loss counting as 0), is
refused (`InputAboveBoundError`), naming the lesser of the two. It records one
`ImmediateExpensingLine` for each class, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import CapabilityResult, capability
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.parameters.class_rates import ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.cca_table import CcaTable
from tax_engine.jurisdictions.ca.trace import ImmediateExpensingLine


@capability(identifier="immediate_expensing_claim")
class ImmediateExpensingClaim(CcaTable):
    """Produces `output`: the total, over the consumed `classes`, of each class's immediate
    expensing amount, at most the consumed `immediate_expensing_limit` and the consumed
    `income_before_cca`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {
        "classes": RecordList,
        "immediate_expensing_limit": Decimal,
        "income_before_cca": Decimal,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        classes: ArtifactKind[RecordList],
        immediate_expensing_limit: Money,
        income_before_cca: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its class-rate dataset, the record list it reads, the immediate
        expensing limit and the income before CCA, the kind produced."""
        super().__init__(
            class_rates,
            classes,
            output,
            immediate_expensing_limit=immediate_expensing_limit,
            income_before_cca=income_before_cca,
        )
        self._limit_kind = immediate_expensing_limit
        self._income_kind = income_before_cca
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        lines = tuple(
            ImmediateExpensingLine(
                self._output,
                row.position,
                row.class_rate,
                row.diep_additions,
                row.diep_proceeds,
                row.column_7,
                row.column_8,
                row.immediate_expensing,
            )
            for row in self._rows(inputs)
        )
        items = tuple((line.position, line.column_9) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        limit = self._input(inputs, self._limit_kind).value
        income = max(Decimal(0), self._input(inputs, self._income_kind).value)
        if total > min(limit, income):
            name, bound = (
                ("immediate expensing limit", limit)
                if limit <= income
                else ("income before CCA", income)
            )
            raise InputAboveBoundError(f"total of column 9 ({total}) is above the {name} ({bound})")
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
