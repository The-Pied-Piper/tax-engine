"""LoggingTaxCredit: the federal logging tax credit by province, one province at a time.

5000-G, "Federal logging tax credit": "To calculate your credit for each province where you
operated, use the lower of the following amounts for each province you had a logging operation
in: 66.6667% of the logging tax that you paid to that province for the year; 6.6667% of your net
logging income in that province for the year. Add up the amounts for all provinces for the year,
up to 6.6667% of your taxable income from line 26000 of your return, ..."

For each province in the consumed record list, the lesser of `tax_rate` times the logging tax paid
and `income_rate` times the net logging income, each rounded with its dataset's rule, then the
total of those amounts. The cap of line 133 is not here: it is wired from artifacts in the
manifest. Each province is worked on its own, never pooled: its amount is rounded once for each
side, the lesser is taken, and the output is the sum. It records one `LoggingTaxCreditLine` for
each province, by position from 1, then an `ItemsTotalLine`; the total is 0 when there are none.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.catalog import LOGGING_TAX_PAID, NET_LOGGING_INCOME
from tax_calculator.jurisdictions.ca.trace import LoggingTaxCreditLine


@capability(identifier="logging_tax_credit")
class LoggingTaxCredit(Capability):
    """Produces `output`: the total, over the consumed `provinces`, of the lesser of the
    `tax_rate` dataset's share of the logging tax paid and the `income_rate` dataset's share of
    the net logging income, each rounded with its own dataset's rule."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Rate]]] = {
        "tax_rate": RATE,
        "income_rate": RATE,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"provinces": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        tax_rate: ParameterDataset[Rate],
        income_rate: ParameterDataset[Rate],
        provinces: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its two rate datasets, the record list it reads, the kind
        produced."""
        super().__init__(provinces=provinces, output=output)
        self._tax_rate = tax_rate
        self._income_rate = income_rate
        self._provinces = provinces
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._provinces).value.records
        tax_rate, income_rate = self._tax_rate.values, self._income_rate.values
        tax_rounding, income_rounding = self._tax_rate.rounding, self._income_rate.rounding
        lines: list[LoggingTaxCreditLine] = []
        for position, record in enumerate(records, start=1):
            tax_paid = Decimal(record[LOGGING_TAX_PAID])
            net_income = Decimal(record[NET_LOGGING_INCOME])
            tax_share = tax_rounding.apply(tax_rate.value * tax_paid)
            income_share = income_rounding.apply(income_rate.value * net_income)
            result = min(tax_share, income_share)
            lines.append(
                LoggingTaxCreditLine(
                    output=self._output,
                    position=position,
                    tax_paid=tax_paid,
                    tax_rate=tax_rate,
                    tax_share=tax_share,
                    net_logging_income=net_income,
                    income_rate=income_rate,
                    income_share=income_share,
                    tax_rounding=tax_rounding,
                    income_rounding=income_rounding,
                    result=result,
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )
