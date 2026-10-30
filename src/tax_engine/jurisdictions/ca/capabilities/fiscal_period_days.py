"""FiscalPeriodDays: the days of the fiscal period that a prorated CCA claim is based on.

Guide T4002 2025, "You were asking?": "Q. How do I calculate my CCA claim if I start a business and
my first fiscal period is from June 1, 2025, to December 31, 2025? A. Since your fiscal period is
less than 365 days, you have to prorate your CCA claim. Calculate your CCA using the rules
discussed in this chapter. However, base your CCA claim on the number of days in your fiscal
period compared to 365 days. In this case, your fiscal period is 214 days." The output is the
consumed `entered` days when they are above 0, else the `class_rates` dataset's `full_year_days`:
a fiscal period that is not entered is a full year, so the claim is not prorated. Days entered
above `longest_fiscal_period_days` (366 in 2025, the days of the longest 12 months; Guide T4002,
"A fiscal period cannot be longer than 12 months") are refused (`InputAboveBoundError`). Days from
`full_year_days` up to it are a period of 12 months, kept as entered. It records one
`FiscalPeriodDaysLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.parameters.class_rates import CLASS_RATES, ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.jurisdictions.ca.trace import FiscalPeriodDaysLine


@capability(identifier="fiscal_period_days")
class FiscalPeriodDays(Capability):
    """Produces `output`: the consumed `entered` days, or the dataset's days in a full year when
    none are entered."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[ClassRates]]] = {"class_rates": CLASS_RATES}
    CONSUMES: ClassVar[Mapping[str, type]] = {"entered": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        entered: ArtifactKind[int],
        output: ArtifactKind[int],
    ) -> None:
        """Wire the capability: its class-rate dataset, the int kind of the days entered, the int
        kind of the days of the fiscal period produced."""
        super().__init__(entered=entered, output=output)
        self._class_rates = class_rates
        self._entered = entered
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        entered: int = self._input(inputs, self._entered).value
        full_year = self._class_rates.values.full_year_days
        longest = self._class_rates.values.longest_fiscal_period_days
        if entered > longest:
            raise InputAboveBoundError(
                f"{self._entered.identifier} {entered} is above the maximum {longest}"
            )
        days = entered if entered > 0 else full_year
        return CapabilityResult(
            outputs=(Artifact(self._output, days),),
            trace=(FiscalPeriodDaysLine(self._output, entered, days, full_year),),
        )
