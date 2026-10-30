"""BusinessVehicleExpenses: the motor vehicle expenses of Form T2125 Charts A to C, line 9281.

Forms T2042 (line 9819) and T2121 (line 9281) repeat the same charts and use this capability too.

T2125 Part 4 line 9281 "Motor vehicle expenses (not including CCA) (amount 16 of Chart A)", where
Chart A line 16 reads "Allowable motor vehicle expenses: Add amounts 13 to 15 (enter this total on
line 9281 of Part 4)". The charts are filled in for each vehicle, so each record of the consumed
`vehicles` list is one vehicle, worked on its own, and the output is the total of their line 16
amounts, 0 when there are no vehicles. A vehicle works these lines, in this order (Charts B and C
only for a passenger vehicle):

- Chart B, headed "Available interest expense for passenger vehicles and zero-emission passenger
  vehicles", worked only for a passenger vehicle (below). Line 18 "($350*** ÷ 30) × the number of
  days in the fiscal period for which interest was payable (accrual method) or paid (cash
  method)" and line 19 "Available interest expense: Amount 17 or 18, whichever is less (include
  this in amount 4 of Chart A above)".
- Chart C, headed "Eligible leasing cost for passenger vehicles", worked only for a passenger
  vehicle (below). Line 23 "Amount 23 or ($44,706 + GST and PST, or $44,706 + HST), whichever is
  more", where the tax is the printed amount times the `sales_tax_rate` (the caller's GST or HST
  rate, in percent), rounded; line 24 "× 85%"; line 25 "[($1,100 + GST and PST, or $1,100 + HST) ×
  amount 22] ÷ 30"; line 26 "Amount 25: amount 21"; line 27 "[($38,000 + GST and PST, or $38,000 +
  HST) × amount 20] ÷ amount 24"; and line 28 "Eligible leasing cost: Amount 26 or 27, whichever is
  less (enter in amount 8 of Chart A above)". The form prints no floor on line 26, but line 28 is
  not negative, so a vehicle whose amount 21 is above amount 25 (line 26 below 0) is refused
  (`InputAboveBoundError`, "item N: ..." naming amounts 21 and 25 of Chart C).
- Chart A line 12 "Total motor vehicle expenses: Add amounts 3 to 11.", amounts 4 and 8 being
  lines 19 and 28; line 13 "Business use part: amount 1 ÷ amount 2 × amount 12 = 13", 0 when
  amount 2 is 0; and line 16, line 13 plus amount 14 (parking fees) and amount 15 (supplementary
  business insurance).

Chart B is for passenger vehicles and zero-emission passenger vehicles only, and Guide T4002 says
"When you use a passenger vehicle or a zero-emission passenger vehicle to earn income, there is a
limit on the amount of interest you can deduct." Each vehicle record holds whether it is one
(`passenger_vehicle`, 1 or 0, the guide's definitions and chart of vehicle types deciding). For a
vehicle that is not, Chart B is not filled in: its amount 17 goes to Chart A amount 4 whole, with no
limit, and its interest days and purchase year are not read (not bounded either). A
`passenger_vehicle` answer above 1 is refused (`InputAboveBoundError`, "item N: ..."), as a yes or
no answer, not capped.

Chart C is headed "Eligible leasing cost for passenger vehicles" (footnote "****": "Includes a
vehicle that would qualify as a zero-emission passenger vehicle if you owned it."), and Guide T4002
says "You can deduct costs you incur to lease a passenger vehicle you use to earn income" and gives
the limit for a passenger vehicle: the same `passenger_vehicle` answer decides it. For a vehicle
that is not one, Chart C is not filled in: its amount 20 (the lease charges) goes to Chart A amount
8 whole, with no limit, and its lease year, list price, lease days, payments before the period,
repayment owing and deposit answers are not read (not bounded either).

Guide T4002 (printed page 56, "Repayments and imputed interest") says "When you lease a passenger
vehicle, you may have a repayment owing to you, or you may have imputed interest. If so, you will
not be able to use the chart." Each vehicle record holds whether its lease has a repayment owing to
the filer (`lease_repayment_owing`, 1 or 0), and the guide's three conditions for imputed interest:
"Calculate imputed interest for leasing costs on a passenger vehicle only if all of the following
apply: one or more deposits were made for the leased passenger vehicle; one or more deposits are
refundable; the total of the deposits is more than $1,000". They are `lease_deposits_made` (1 or 0),
`lease_deposits_refundable` (1 or 0) and `lease_deposits_total` (an amount, more than the printed
$1,000, the dataset `deposit_minimum`, being the third condition; a total of exactly $1,000 is not
more). For a passenger vehicle a repayment owing of 1 is refused (`InvalidRecordError`, "item N:
..."), and so is a lease for which all three conditions apply, as it has imputed interest, the chart
cannot be used and neither the form nor the guide prints another calculation (the guide only points
to Interpretation Bulletin IT-521); a lease for which one or two conditions fail has no imputed
interest and works Chart C. The guide prints no link between the conditions, so each is read as
typed (deposits made 0 with a total above $1,000 is not read as deposits made). An answer above 1
to a yes or no (`InputAboveBoundError`) is refused, not capped.

A vehicle whose business kilometres (Chart A amount 1) are above its total kilometres (amount 2) is
refused (`InputAboveBoundError`, "item N: ..." naming amounts 1 and 2 of Chart A), before any of its
lines is worked: the business use part of line 13 would be more than the vehicle's whole. Business
kilometres equal to the total are accepted, and so are 0 total kilometres with 0 business
kilometres (line 13 is 0); 0 total kilometres with business kilometres above 0 is refused too.

A vehicle whose interest days (Chart B amount 17's days) are above the days of the fiscal period
(the consumed `fiscal_period_days`, Chart B line 18 "the number of days in the fiscal period for
which interest was payable (accrual method) or paid (cash method)") is refused
(`InputAboveBoundError`, "item N: ..." naming the interest days and the fiscal period's days),
before any of its lines is worked: the interest limit would count days the fiscal period does not
have. Interest days equal to the days of the fiscal period are accepted, and so are fewer; 0
interest days are accepted in any fiscal period.

Charts B and C print other figures for earlier years (T2125 2025, Chart B footnote "***": "For
passenger vehicles bought after 2023. For passenger vehicles bought after 2000 and before 2024, the
amount is $300"; Chart C endnotes 11 to 13: leases entered into in 2024, 2023, 2022 and before
2022). Each vehicle record holds the year the vehicle was bought (`purchase_year`, Chart B) and the
year the lease was entered into (`lease_year`, Chart C); a year that does not apply is 0. Chart B's
limit is the `interest_limits` row for the purchase year, not looked up when the vehicle has no
interest days; with interest days, a purchase year in 2000 or earlier (or 0) is refused
(`InvalidRecordError`), as the form prints no limit for it. Chart C's three limits are the
`lease_limits` row for the lease year (2025 the 2025 set; 0 or any year before 2022 the "before
2022" set). A purchase year or lease year after the tax year of the datasets (2025) is refused
(`InvalidRecordError`), before any of its lines is worked: the form prints no limit for it, and the
2025 figures must not be used silently.

The printed $350, 30, $44,706, $1,100, $38,000 and 85% are the datasets `interest_limits` (the
`interest_limit` of each row), `days_divisor`, `lease_limits` (the `list_price_limit`,
`lease_charge_limit` and `lease_cost_limit` of each row) and `lease_price_rate`. The form states no
rounding rule, but each line is a dollars-and-cents box, so each quotient or product (lines 13, 18,
24, 25 and 27 and the tax on a printed amount) is worked as an exact fraction and rounded once with
the `rounding` dataset's rule. It records one `BusinessVehicleLine` for each vehicle, by position
from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InvalidRecordError,
    ValidationError,
)
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingRule
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts
from tax_engine.domain.record_list import Record, RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_VEHICLE_BUSINESS_KILOMETRES,
    BUSINESS_VEHICLE_ELECTRICITY_ZEV,
    BUSINESS_VEHICLE_FUEL_AND_OIL,
    BUSINESS_VEHICLE_INSURANCE,
    BUSINESS_VEHICLE_INTEREST_DAYS,
    BUSINESS_VEHICLE_INTEREST_PAYABLE,
    BUSINESS_VEHICLE_LEASE_CHARGES,
    BUSINESS_VEHICLE_LEASE_DAYS,
    BUSINESS_VEHICLE_LEASE_DEPOSITS_MADE,
    BUSINESS_VEHICLE_LEASE_DEPOSITS_REFUNDABLE,
    BUSINESS_VEHICLE_LEASE_DEPOSITS_TOTAL,
    BUSINESS_VEHICLE_LEASE_PAYMENTS_BEFORE,
    BUSINESS_VEHICLE_LEASE_REPAYMENT_OWING,
    BUSINESS_VEHICLE_LEASE_YEAR,
    BUSINESS_VEHICLE_LICENCE_AND_REGISTRATION,
    BUSINESS_VEHICLE_LIST_PRICE,
    BUSINESS_VEHICLE_MAINTENANCE_AND_REPAIRS,
    BUSINESS_VEHICLE_OTHER_EXPENSES_10,
    BUSINESS_VEHICLE_OTHER_EXPENSES_11,
    BUSINESS_VEHICLE_PARKING_FEES,
    BUSINESS_VEHICLE_PASSENGER_VEHICLE,
    BUSINESS_VEHICLE_PURCHASE_YEAR,
    BUSINESS_VEHICLE_SUPPLEMENTARY_INSURANCE,
    BUSINESS_VEHICLE_TOTAL_KILOMETRES,
)
from tax_engine.jurisdictions.ca.trace import BusinessVehicleLine


@capability(identifier="business_vehicle_expenses")
class BusinessVehicleExpenses(Capability):
    """Produces `output`: the total, over the consumed `vehicles`, of each vehicle's allowable
    motor vehicle expenses (Chart A line 16), at the consumed `sales_tax_rate`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "interest_limits": YEAR_AMOUNTS,
        "lease_limits": YEAR_AMOUNTS,
        "days_divisor": CREDIT,
        "lease_price_rate": RATE,
        "deposit_minimum": CREDIT,
        "rounding": ROUNDING_ONLY,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {
        "vehicles": RecordList,
        "sales_tax_rate": Decimal,
        "fiscal_period_days": int,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        interest_limits: ParameterDataset[YearAmounts],
        lease_limits: ParameterDataset[YearAmounts],
        days_divisor: ParameterDataset[Credit],
        lease_price_rate: ParameterDataset[Rate],
        deposit_minimum: ParameterDataset[Credit],
        rounding: ParameterDataset[RoundingOnly],
        vehicles: ArtifactKind[RecordList],
        sales_tax_rate: Money,
        fiscal_period_days: ArtifactKind[int],
        output: Money,
    ) -> None:
        """Wire the capability: its six datasets, the record list of vehicles, the sales tax
        rate and the fiscal period's days it reads, the kind produced."""
        super().__init__(
            vehicles=vehicles,
            sales_tax_rate=sales_tax_rate,
            fiscal_period_days=fiscal_period_days,
            output=output,
        )
        self._interest_limits = interest_limits.values
        self._purchase_year_limit: int = interest_limits.tax_year
        self._lease_limits = lease_limits.values
        self._lease_year_limit: int = lease_limits.tax_year
        self._days_divisor = days_divisor.values.amount
        self._lease_price_rate = lease_price_rate.values.value
        self._rate_rounding: RoundingRule = lease_price_rate.rounding
        self._deposit_minimum = deposit_minimum.values.amount
        self._rounding: RoundingRule = rounding.rounding
        self._vehicles = vehicles
        self._sales_tax_rate = sales_tax_rate
        self._fiscal_period_days = fiscal_period_days
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._vehicles).value.records
        rate = self._input(inputs, self._sales_tax_rate).value
        period_days: int = self._input(inputs, self._fiscal_period_days).value
        lines = tuple(
            self._vehicle(position, record, rate, period_days)
            for position, record in enumerate(records, 1)
        )
        items = tuple((line.position, line.line_16) for line in lines)
        total = sum((amount for _position, amount in items), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(*lines, ItemsTotalLine(self._output, items, total)),
        )

    def _vehicle(
        self, position: int, record: Record, rate: Decimal, period_days: int
    ) -> BusinessVehicleLine:
        """The lines of one vehicle's Charts A to C."""
        business_kilometres = Decimal(record[BUSINESS_VEHICLE_BUSINESS_KILOMETRES])
        total_kilometres = Decimal(record[BUSINESS_VEHICLE_TOTAL_KILOMETRES])
        if business_kilometres > total_kilometres:
            raise InputAboveBoundError(
                f"item {position}: Chart A amount 1 (business kilometres) {business_kilometres} "
                f"is above amount 2 (total kilometres) {total_kilometres}"
            )
        # Chart B.
        passenger_vehicle = record[BUSINESS_VEHICLE_PASSENGER_VEHICLE]
        if passenger_vehicle > 1:
            raise InputAboveBoundError(
                f"item {position}: {BUSINESS_VEHICLE_PASSENGER_VEHICLE.identifier} "
                f"{passenger_vehicle} is above a yes or no answer of 1"
            )
        interest_payable = Decimal(record[BUSINESS_VEHICLE_INTEREST_PAYABLE])
        line_19 = (
            self._available_interest(position, record, interest_payable, period_days)
            if passenger_vehicle == 1
            else interest_payable
        )
        # Chart C.
        line_28 = (
            self._eligible_leasing_cost(position, record, rate)
            if passenger_vehicle == 1
            else Decimal(record[BUSINESS_VEHICLE_LEASE_CHARGES])
        )
        # Chart A.
        line_12 = (
            Decimal(record[BUSINESS_VEHICLE_FUEL_AND_OIL])
            + line_19
            + Decimal(record[BUSINESS_VEHICLE_INSURANCE])
            + Decimal(record[BUSINESS_VEHICLE_LICENCE_AND_REGISTRATION])
            + Decimal(record[BUSINESS_VEHICLE_MAINTENANCE_AND_REPAIRS])
            + line_28
            + Decimal(record[BUSINESS_VEHICLE_ELECTRICITY_ZEV])
            + Decimal(record[BUSINESS_VEHICLE_OTHER_EXPENSES_10])
            + Decimal(record[BUSINESS_VEHICLE_OTHER_EXPENSES_11])
        )
        line_13 = (
            self._quotient(line_12, record[BUSINESS_VEHICLE_BUSINESS_KILOMETRES], total_kilometres)
            if total_kilometres != 0
            else self._rounding.apply(ExactFraction(0))
        )
        line_16 = (
            line_13
            + Decimal(record[BUSINESS_VEHICLE_PARKING_FEES])
            + Decimal(record[BUSINESS_VEHICLE_SUPPLEMENTARY_INSURANCE])
        )
        return BusinessVehicleLine(
            self._output, position, line_12, line_13, line_19, line_28, line_16
        )

    def _available_interest(
        self, position: int, record: Record, interest_payable: Decimal, period_days: int
    ) -> Decimal:
        """Chart B lines 18 and 19 of a passenger vehicle."""
        purchase_year = record[BUSINESS_VEHICLE_PURCHASE_YEAR]
        if purchase_year > self._purchase_year_limit:
            raise InvalidRecordError(
                f"item {position}: a vehicle bought in {purchase_year} is after "
                f"{self._purchase_year_limit}, the year of the figures the charts print"
            )
        interest_days = record[BUSINESS_VEHICLE_INTEREST_DAYS]
        if interest_days > period_days:
            raise InputAboveBoundError(
                f"item {position}: Chart B interest days {interest_days} are above the "
                f"{period_days} days in the fiscal period"
            )
        if interest_days == 0:
            line_18 = self._rounding.apply(ExactFraction(0))
        else:
            interest_row = self._interest_limits.row_for(purchase_year)
            if interest_row is None:
                raise InvalidRecordError(
                    f"item {position}: interest days are given but "
                    f"the form prints no limit for a vehicle bought in {purchase_year}"
                )
            line_18 = self._quotient(
                interest_row.amount("interest_limit"), interest_days, self._days_divisor
            )
        return min(interest_payable, line_18)

    def _check_repayment_and_imputed_interest(self, position: int, record: Record) -> None:
        """Refuse a leased passenger vehicle with a repayment owing, or with imputed interest (all
        three conditions of Guide T4002's "Repayments and imputed interest" apply)."""
        yes_or_no = (
            BUSINESS_VEHICLE_LEASE_REPAYMENT_OWING,
            BUSINESS_VEHICLE_LEASE_DEPOSITS_MADE,
            BUSINESS_VEHICLE_LEASE_DEPOSITS_REFUNDABLE,
        )
        for kind in yes_or_no:
            if record[kind] > 1:
                raise InputAboveBoundError(
                    f"item {position}: {kind.identifier} {record[kind]} is above a yes or no "
                    "answer of 1"
                )
        if record[BUSINESS_VEHICLE_LEASE_REPAYMENT_OWING] == 1:
            raise InvalidRecordError(
                f"item {position}: a repayment owing on a leased passenger vehicle means the "
                "filer cannot use Chart C, and the form prints no other calculation"
            )
        deposits_total = Decimal(record[BUSINESS_VEHICLE_LEASE_DEPOSITS_TOTAL])
        if (
            record[BUSINESS_VEHICLE_LEASE_DEPOSITS_MADE] == 1
            and record[BUSINESS_VEHICLE_LEASE_DEPOSITS_REFUNDABLE] == 1
            and deposits_total > self._deposit_minimum
        ):
            raise InvalidRecordError(
                f"item {position}: imputed interest on a leased passenger vehicle (deposits made, "
                f"refundable, totalling {deposits_total}, more than {self._deposit_minimum}) "
                "means the filer cannot use Chart C, and the form prints no other calculation"
            )

    def _eligible_leasing_cost(self, position: int, record: Record, rate: Decimal) -> Decimal:
        """Chart C lines 23 to 28 of a passenger vehicle."""
        self._check_repayment_and_imputed_interest(position, record)
        lease_year = record[BUSINESS_VEHICLE_LEASE_YEAR]
        if lease_year > self._lease_year_limit:
            raise InvalidRecordError(
                f"item {position}: a lease entered into in {lease_year} is after "
                f"{self._lease_year_limit}, the year of the figures the charts print"
            )
        lease_row = self._lease_limits.row_for(lease_year)
        if lease_row is None:
            raise InvalidRecordError(f"item {position}: the form prints no lease limits")
        list_price_limit = lease_row.amount("list_price_limit")
        lease_charge_limit = lease_row.amount("lease_charge_limit")
        lease_cost_limit = lease_row.amount("lease_cost_limit")
        price_with_tax = list_price_limit + self._tax(list_price_limit, rate)
        line_23 = max(Decimal(record[BUSINESS_VEHICLE_LIST_PRICE]), price_with_tax)
        line_24 = self._rate_rounding.apply(
            ExactFraction(line_23) * ExactFraction(self._lease_price_rate)
        )
        charge_with_tax = lease_charge_limit + self._tax(lease_charge_limit, rate)
        line_25 = self._quotient(
            charge_with_tax, record[BUSINESS_VEHICLE_LEASE_DAYS], self._days_divisor
        )
        payments_before = Decimal(record[BUSINESS_VEHICLE_LEASE_PAYMENTS_BEFORE])
        if payments_before > line_25:
            raise InputAboveBoundError(
                f"item {position}: Chart C amount 21 (lease payments deducted before the "
                f"fiscal period) {payments_before} is above amount 25 ({line_25})"
            )
        line_26 = line_25 - payments_before
        cost_with_tax = lease_cost_limit + self._tax(lease_cost_limit, rate)
        line_27 = self._quotient(cost_with_tax, record[BUSINESS_VEHICLE_LEASE_CHARGES], line_24)
        line_28 = min(line_26, line_27)
        return line_28

    def _tax(self, printed: Decimal, rate: Decimal) -> Decimal:
        """The GST and PST, or HST, on `printed` at `rate` percent, rounded once."""
        return self._rounding.apply(ExactFraction(printed) * ExactFraction(rate) / 100)

    def _quotient(self, amount: Decimal, factor: Decimal, divisor: Decimal) -> Decimal:
        """`amount` × `factor` ÷ `divisor` as an exact fraction, rounded once; a zero divisor is
        refused."""
        if divisor == 0:
            raise ValidationError(f"{amount * factor} cannot be divided by {divisor}")
        return self._rounding.apply(
            ExactFraction(amount) * ExactFraction(factor) / ExactFraction(divisor)
        )
