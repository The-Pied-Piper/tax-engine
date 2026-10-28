"""ProratedByDaysInPeriod: an amount times the days in a part of a period over the period's days.

Form T2043, Chart A amount 7 "Total number of days in the fiscal period that fall within the 2024
calendar year divided by the total number of days in the fiscal period (if the fiscal period starts
and ends in 2025, enter "0")" and amount 8 "Amount 6 multiplied by amount 7.". Amount 7 is an exact
fraction and is not an artifact: the output is `rounding.apply(amount x days / period_days)`, formed
as one exact fraction and rounded once with the `rounding_only` dataset's rule. Days of 0 give 0.
Days above `period_days` are an `InputAboveBoundError`. It records one `ProratedByDaysInPeriodLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.jurisdictions.ca.trace import ProratedByDaysInPeriodLine


@capability(identifier="prorated_by_days_in_period")
class ProratedByDaysInPeriod(Capability):
    """Produces `output`: the consumed `amount` × `days` / `period_days`, rounded once."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {
        "amount": Decimal,
        "days": int,
        "period_days": int,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        amount: Money,
        days: ArtifactKind[int],
        period_days: ArtifactKind[int],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the Decimal amount, the int kinds of the days
        and of the period's days, the Decimal kind of the output."""
        super().__init__(amount=amount, days=days, period_days=period_days, output=output)
        self._rounding = rounding
        self._amount = amount
        self._days = days
        self._period_days = period_days
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount: Decimal = self._input(inputs, self._amount).value
        days: int = self._input(inputs, self._days).value
        period_days: int = self._input(inputs, self._period_days).value
        if days > period_days:
            raise InputAboveBoundError(
                f"{self._days.identifier} {days} is above the maximum {period_days}"
            )
        result = self._rounding.rounding.apply(ExactFraction(amount) * days / period_days)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                ProratedByDaysInPeriodLine(
                    self._output,
                    self._amount,
                    amount,
                    self._days,
                    days,
                    self._period_days,
                    period_days,
                    result,
                ),
            ),
        )
