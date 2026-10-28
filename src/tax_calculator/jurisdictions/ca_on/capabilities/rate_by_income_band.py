"""RateByIncomeBand: the rate a `rate_table` dataset gives a money artifact, as a rate artifact.

Schedule ON479-A, line 7: "If your family adjusted income on line 5 is "0", enter 75%. If not,
enter the tax credit rate that applies to your family adjusted income from the table below." A
figure of exactly 0 gives the table's `rate_at_zero`; above 0 the rate is that of the last row
whose `more_than` the figure exceeds, so where a printed row's upper bound overlaps the next row
the later row wins. The rate is a printed figure, produced as given and never rounded, so the
dataset's rounding rule is not applied. A negative figure is refused: the line's figure cannot be
negative.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import NegativeArtifactError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rate_table import RATE_TABLE, RateTable
from tax_calculator.domain.trace import RateByIncomeBandLine


@capability(identifier="rate_by_income_band")
class RateByIncomeBand(Capability):
    """Produces `output`: the rate the `table` dataset gives the consumed `income`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RateTable]]] = {"table": RATE_TABLE}
    CONSUMES: ClassVar[Mapping[str, type]] = {"income": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Rate}

    def __init__(
        self, table: ParameterDataset[RateTable], income: Money, output: ArtifactKind[Rate]
    ) -> None:
        """Wire the capability: its rate table dataset, the figure it reads, the kind produced."""
        super().__init__(income=income, output=output)
        self._table = table
        self._income = income
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        income = self._input(inputs, self._income).value
        if income < 0:
            raise NegativeArtifactError(
                f"{self._income.identifier} cannot be negative, got {income}",
                identifier=self._income.identifier,
                value=income,
            )
        table = self._table.values
        row = table.row_for(income)
        rate = table.rate_for(row)
        return CapabilityResult(
            outputs=(Artifact(self._output, rate),),
            trace=(RateByIncomeBandLine(self._output, self._income, income, row, rate),),
        )
