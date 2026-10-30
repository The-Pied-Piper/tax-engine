"""ProratedByFiscalPeriodDays: an amount prorated by the days of a short fiscal period, rounded.

Income Tax Regulations, subsection 1104(3.5), paragraph (b): "where an eligible person or
partnership has a taxation year that is less than 51 weeks, its immediate expensing limit for the
year is that proportion of its immediate expensing limit for the year determined without reference
to this paragraph that the number of days in the year is of 365". Guides T4002 and T4036,
"Immediate expensing incentive": "The limit is also prorated for tax years shorter than 365 days"
is the guides' wording; the Regulations decide over it, so only a year below the `short_year_days`
figure (357 in 2025, 51 weeks of 7 days) is prorated.

A fiscal period of fewer days than `short_year_days` gives `rounding.apply(amount x
fiscal_period_days / full_year_days)`, formed as one exact fraction and rounded once with the
`rounding_only` dataset's rule. Any other period gives the amount itself, unchanged and unrounded.
The `full_year_days` (365 in 2025) come from the `class_rates` dataset. Days below 1 are an
`InputBelowBoundError` and days above `longest_fiscal_period_days` (366 in 2025; Guide T4002,
"A fiscal period cannot be longer than 12 months") an `InputAboveBoundError`. It records one
`ProratedByDaysLine`, prorated or not, so the trace shows the figure that decided it.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InputAboveBoundError, InputBelowBoundError
from tax_engine.domain.parameters.class_rates import CLASS_RATES, ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.jurisdictions.ca.trace import ProratedByDaysLine


@capability(identifier="prorated_by_fiscal_period_days")
class ProratedByFiscalPeriodDays(Capability):
    """Produces `output`: the consumed `amount` × `fiscal_period_days` / `full_year_days`, rounded
    once, when `fiscal_period_days` is below `short_year_days`; else the `amount` as it is."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "rounding": ROUNDING_ONLY,
        "class_rates": CLASS_RATES,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {
        "amount": Decimal,
        "fiscal_period_days": int,
        "short_year_days": Decimal,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        class_rates: ParameterDataset[ClassRates],
        amount: Money,
        fiscal_period_days: ArtifactKind[int],
        short_year_days: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its rounding and class-rate datasets, the Decimal amount, the int
        kind of the days of the fiscal period, the Decimal kind of the short-year figure, the
        Decimal kind of the output."""
        super().__init__(
            amount=amount,
            fiscal_period_days=fiscal_period_days,
            short_year_days=short_year_days,
            output=output,
        )
        self._rounding = rounding
        self._class_rates = class_rates
        self._amount = amount
        self._days = fiscal_period_days
        self._short_year = short_year_days
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount: Decimal = self._input(inputs, self._amount).value
        days: int = self._input(inputs, self._days).value
        short_year: Decimal = self._input(inputs, self._short_year).value
        full_year = self._class_rates.values.full_year_days
        identifier = self._days.identifier
        if days < 1:
            raise InputBelowBoundError(f"{identifier} {days} is below the minimum 1")
        longest = self._class_rates.values.longest_fiscal_period_days
        if days > longest:
            raise InputAboveBoundError(f"{identifier} {days} is above the maximum {longest}")
        if Decimal(days) < short_year:
            result = self._rounding.rounding.apply(ExactFraction(amount) * days / full_year)
        else:
            result = amount
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                ProratedByDaysLine(
                    self._output,
                    self._amount,
                    amount,
                    self._days,
                    days,
                    full_year,
                    self._short_year,
                    short_year,
                    result,
                ),
            ),
        )
