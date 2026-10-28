"""YearAmount: the figure a form prints for the year something was entered into.

For a printed amount that has footnoted figures for earlier years, such as Guide T4044 (2025),
"Eligible leasing costs for passenger vehicles leased after December 31, 2000", line 5 "44,706* +
GST** and PST** or HST**": "* For leases entered into in 2024, this amount is $43,529. For leases
entered into in 2023, this amount is $42,353. For leases entered into in 2022, this amount is
$40,000. For leases entered into in 2021 or before, the amount is $35,294." The output is the
`amount` of the row of the `amounts` dataset that applies to the consumed `year` (a year before
the dataset's oldest dated row uses its open-ended row). A `year` after the tax year of the dataset
is an `InputAboveBoundError`: the form prints no figure for it, and the figures of the tax year
must not be used silently. It records one `YearAmountLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InputAboveBoundError, InvalidYearAmountsError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts
from tax_calculator.jurisdictions.ca.trace import YearAmountLine

AMOUNT_NAME = "amount"


@capability(identifier="year_amount")
class YearAmount(Capability):
    """Produces `output`: the `amount` of the `amounts` dataset's row for the consumed `year`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[YearAmounts]]] = {"amounts": YEAR_AMOUNTS}
    CONSUMES: ClassVar[Mapping[str, type]] = {"year": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        amounts: ParameterDataset[YearAmounts],
        year: ArtifactKind[int],
        output: Money,
    ) -> None:
        """Wire the capability: its year amounts dataset, the year it reads, the kind produced."""
        super().__init__(year=year, output=output)
        self._amounts = amounts
        self._year = year
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        year = self._input(inputs, self._year).value
        latest = self._amounts.tax_year
        if year > latest:
            raise InputAboveBoundError(
                f"{self._year.identifier} {year} is after {latest}, the year of the figures the "
                f"form prints"
            )
        row = self._amounts.values.row_for(year)
        if row is None:
            raise InvalidYearAmountsError(f"the form prints no figure for {year}")
        result = row.amount(AMOUNT_NAME)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                YearAmountLine(
                    output=self._output, year_kind=self._year, year_value=year, result=result
                ),
            ),
        )
