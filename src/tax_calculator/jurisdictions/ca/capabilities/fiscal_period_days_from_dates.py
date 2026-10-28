"""FiscalPeriodDaysFromDates: the days of the fiscal period that a prorated CCA claim is based on,
taken from the period's first and last dates.

Form T2125 page 1 "Fiscal period From / to, Date (YYYYMMDD)": the caller enters the start and the
end of the fiscal period as whole numbers like 20250601, and 0 for either when none is entered.
Guide T4002 2025, "You were asking?": "Q. How do I calculate my CCA claim if I start a business and
my first fiscal period is from June 1, 2025, to December 31, 2025? A. Since your fiscal period is
less than 365 days, you have to prorate your CCA claim. Calculate your CCA using the rules
discussed in this chapter. However, base your CCA claim on the number of days in your fiscal
period compared to 365 days. In this case, your fiscal period is 214 days." The output is the
inclusive number of days from the start to the end. Both dates 0 is no dates entered, a full year:
the `class_rates` dataset's `full_year_days`, so the claim is not prorated. Exactly one 0, a date
that is not a real YYYYMMDD day, or an end before the start is refused. A period is at most 12
months (Guide T4002, "A fiscal period cannot be longer than 12 months."): an end after the day
before the same date a year later is refused (`InputAboveBoundError`). It records one
`FiscalPeriodDaysFromDatesLine`, which carries the two dates.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, timedelta
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InputAboveBoundError, InputBelowBoundError, InputOutOfRangeError
from tax_calculator.domain.parameters.class_rates import CLASS_RATES, ClassRates
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.jurisdictions.ca.trace import FiscalPeriodDaysFromDatesLine


@capability(identifier="fiscal_period_days_from_dates")
class FiscalPeriodDaysFromDates(Capability):
    """Produces `output`: the inclusive days from `from_date` to `to_date`, or the dataset's days in
    a full year when neither date is entered."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[ClassRates]]] = {"class_rates": CLASS_RATES}
    CONSUMES: ClassVar[Mapping[str, type]] = {"from_date": int, "to_date": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        from_date: ArtifactKind[int],
        to_date: ArtifactKind[int],
        output: ArtifactKind[int],
    ) -> None:
        """Wire the capability: its class-rate dataset, the int kinds of the first and last dates
        (YYYYMMDD, 0 for none), the int kind of the days of the fiscal period produced."""
        super().__init__(from_date=from_date, to_date=to_date, output=output)
        self._class_rates = class_rates
        self._from_date = from_date
        self._to_date = to_date
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        start_value: int = self._input(inputs, self._from_date).value
        end_value: int = self._input(inputs, self._to_date).value
        full_year = self._class_rates.values.full_year_days
        if start_value == 0 and end_value == 0:
            return self._produced(start_value, end_value, full_year, full_year)
        if start_value == 0 or end_value == 0:
            raise InputOutOfRangeError(
                f"{self._from_date.identifier} and {self._to_date.identifier} must both be 0"
                " or both be dates (YYYYMMDD)"
            )
        start = self._day(self._from_date, start_value)
        end = self._day(self._to_date, end_value)
        if end < start:
            raise InputBelowBoundError(
                f"{self._to_date.identifier} {end_value} is below the start {start_value}"
            )
        last = self._last_day_of_12_months(start)
        if end > last:
            raise InputAboveBoundError(
                f"{self._to_date.identifier} {end_value} is above the last day of 12 months "
                f"{last:%Y%m%d}"
            )
        days = (end - start).days + 1
        return self._produced(start_value, end_value, days, full_year)

    def _day(self, kind: ArtifactKind[int], value: int) -> date:
        """The day `value` (YYYYMMDD) is; InputOutOfRangeError when it is not a real date."""
        message = f"{kind.identifier} {value} is not a date (YYYYMMDD)"
        if not 10_000_000 <= value <= 99_999_999:
            raise InputOutOfRangeError(message)
        try:
            return date(value // 10_000, value // 100 % 100, value % 100)
        except ValueError as error:
            raise InputOutOfRangeError(message) from error

    @staticmethod
    def _last_day_of_12_months(start: date) -> date:
        """The day before the anniversary of `start` a year later, 1 March for 29 February."""
        try:
            anniversary = start.replace(year=start.year + 1)
        except ValueError:
            anniversary = date(start.year + 1, 3, 1)
        return anniversary - timedelta(days=1)

    def _produced(
        self, start_value: int, end_value: int, days: int, full_year: int
    ) -> CapabilityResult:
        """The result for `days`, with its trace line carrying the dates entered."""
        return CapabilityResult(
            outputs=(Artifact(self._output, days),),
            trace=(
                FiscalPeriodDaysFromDatesLine(
                    self._output, start_value, end_value, days, full_year
                ),
            ),
        )
