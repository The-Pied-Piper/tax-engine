"""ForeignPropertyTaxOverLimit: the foreign tax on income from property over 15%, per country.

Form T2209, page 1 note: "If you paid tax on income from property sourced outside of Canada (other
than real or immovable property), your non-business foreign tax credit for that income cannot be
more than 15% of your net income from that property. However, you may be able to deduct the part of
the foreign taxes you paid over 15% on line 23200 of your return."

Each country is a record of the consumed `countries` list, holding the foreign tax paid on income
from property and that income, parts of its line 1 (43100) and line 2 (43300). For each country the
limit is the `limit_rate` dataset's rate (the printed 15%) times the property income, rounded with
the dataset's rule; the excess is the property tax paid less the limit, not below zero, and the
output is the sum of the countries' excess, 0 when there are no countries. Each country is worked
on its own, never pooled. The excess is the amount for line 23200 and it is left out of the credit:
`ForeignNonBusinessTaxCredit` takes it off the country's line 1 with `excess`. A country whose
property tax paid is above its non-business tax paid, or whose property income is above its net
foreign non-business income, is refused with a ValidationError naming the country, as the property
figures are parts of lines 1 and 2. It records one `ForeignPropertyTaxLine` for each country, by
position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import ValidationError
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.catalog import (
    FOREIGN_NON_BUSINESS_TAX_PAID,
    FOREIGN_PROPERTY_TAX_PAID,
    NET_FOREIGN_NON_BUSINESS_INCOME,
    NET_FOREIGN_PROPERTY_INCOME,
)
from tax_engine.jurisdictions.ca.trace import ForeignPropertyTaxLine


@capability(identifier="foreign_property_tax_over_limit")
class ForeignPropertyTaxOverLimit(Capability):
    """Produces `output`: the total, over the consumed `countries`, of the foreign tax paid on
    income from property less `limit_rate` of that income, each not below zero."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {"limit_rate": RATE}
    CONSUMES: ClassVar[Mapping[str, type]] = {"countries": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        limit_rate: ParameterDataset[Rate],
        countries: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its limit rate dataset, the record list it reads, the kind
        produced."""
        super().__init__(countries=countries, output=output)
        self._limit_rate = limit_rate
        self._countries = countries
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._countries).value.records
        lines: list[ForeignPropertyTaxLine] = []
        for position, record in enumerate(records, start=1):
            if Decimal(record[FOREIGN_PROPERTY_TAX_PAID]) > Decimal(
                record[FOREIGN_NON_BUSINESS_TAX_PAID]
            ):
                raise ValidationError(
                    f"country {position}: {FOREIGN_PROPERTY_TAX_PAID.identifier} cannot be above "
                    f"{FOREIGN_NON_BUSINESS_TAX_PAID.identifier}, it is a part of it"
                )
            if Decimal(record[NET_FOREIGN_PROPERTY_INCOME]) > Decimal(
                record[NET_FOREIGN_NON_BUSINESS_INCOME]
            ):
                raise ValidationError(
                    f"country {position}: {NET_FOREIGN_PROPERTY_INCOME.identifier} cannot be "
                    f"above {NET_FOREIGN_NON_BUSINESS_INCOME.identifier}, it is a part of it"
                )
            tax_paid = Decimal(record[FOREIGN_PROPERTY_TAX_PAID])
            income = Decimal(record[NET_FOREIGN_PROPERTY_INCOME])
            limit = self._limit(income, self._limit_rate)
            lines.append(
                ForeignPropertyTaxLine(
                    self._output,
                    position,
                    tax_paid,
                    income,
                    self._limit_rate.values.value,
                    self._limit_rate.rounding,
                    limit,
                    max(Decimal(0), tax_paid - limit),
                )
            )
        items = tuple((line.position, line.result) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )

    @staticmethod
    def _limit(income: Decimal, limit_rate: ParameterDataset[Rate]) -> Decimal:
        """The limit on the credit for `income` from property: the dataset's rate times it,
        rounded with the dataset's rule."""
        return limit_rate.rounding.apply(income * limit_rate.values.value)

    @staticmethod
    def excess(
        record: Mapping[ArtifactKind[Any], Any], limit_rate: ParameterDataset[Rate]
    ) -> Decimal:
        """One country's foreign tax paid on income from property over the limit: the tax paid
        less the limit rate times the property income (rounded with the dataset's rule), not
        below zero."""
        limit = ForeignPropertyTaxOverLimit._limit(
            Decimal(record[NET_FOREIGN_PROPERTY_INCOME]), limit_rate
        )
        return max(Decimal(0), Decimal(record[FOREIGN_PROPERTY_TAX_PAID]) - limit)
