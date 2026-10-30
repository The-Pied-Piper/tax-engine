"""Unit tests for the BusinessVehicleExpenses capability (`ca/business_vehicle_expenses`), the
motor vehicle expenses of Form T2125 Charts A to C, line 9281.

Form T2125 (2025 edition, confirmed 2026-10-19 from the PDF, https://www.canada.ca/content/dam/
cra-arc/formspubs/pbg/t2125/t2125-25e.pdf): Chart A line 16 "Allowable motor vehicle expenses: Add
amounts 13 to 15 (enter this total on line 9281 of Part 4)", line 13 "Business use part: amount 1
÷ amount 2 × amount 12 = 13" and line 12 "Total motor vehicle expenses: Add amounts 3 to 11.";
Chart B line 18 "($350*** ÷ 30) × the number of days in the fiscal period for which interest was
payable (accrual method) or paid (cash method)" and line 19 "Available interest expense: Amount 17
or 18, whichever is less (include this in amount 4 of Chart A above)"; Chart C line 23 "Amount 23
or ($44,706 + GST and PST, or $44,706 + HST), whichever is more", line 24 "× 85%", line 25
"[($1,100 + GST and PST, or $1,100 + HST) × amount 22] ÷ 30", line 27 "[($38,000 + GST and PST,
or $38,000 + HST) × amount 20] ÷ amount 24" and line 28 "Eligible leasing cost: Amount 26 or 27,
whichever is less (enter in amount 8 of Chart A above)". Every product and quotient is a
dollars-and-cents box and rounds with the `rounding` dataset (half-up to the cent), the owner's
decision, as the form states no rounding rule. The form is filled in for each vehicle (Guide T4002
"More than one vehicle"; the source is to be confirmed) and the line 16 amounts are added.

Charts B and C print other figures for earlier years (T2125 2025, "***" footnote of Chart B: "For
passenger vehicles bought after 2023. For passenger vehicles bought after 2000 and before 2024, the
amount is $300"; Chart C endnotes 11 to 13: leases entered into in 2024, 2023, 2022 and before
2022). Each vehicle record holds the year the vehicle was bought (`purchase_year`, Chart B) and the
year the lease was entered into (`lease_year`, Chart C); a year that does not apply is 0. Chart B's
limit is the `interest_limits` row for the purchase year, and is not looked up when the vehicle has
no interest days; with interest days, a purchase year in 2000 or earlier (or 0) is refused
(`InvalidRecordError`, "item N: ... the form prints no limit for a vehicle bought in <year>"),
as the form prints no limit for it. Chart C's three limits are the `lease_limits` row for the lease
year (2025 or later the 2025 set; 0 or any year before 2022 the "before 2022" set).

Its slots: six parameter slots, `interest_limits` and `lease_limits` (`year_amounts` datasets),
`days_divisor` (a `credit` dataset, the 30), `lease_price_rate` (a `rate` dataset, the 85%),
`deposit_minimum` (a `credit` dataset, the guide's $1,000) and `rounding` (a `rounding_only`
dataset); three consumed slots, `vehicles` (a record list, one record
per vehicle), `sales_tax_rate` (the caller's GST or HST rate, in percent) and `fiscal_period_days`
(an int, the days of the statement's fiscal period, 365 for a full year); and one produced slot
`output`, line 9281. Each vehicle is worked on its own: line 12, line 13 (0 when its total
kilometres are 0), Chart B lines 18 and 19, Chart C lines 22 to 28 and line 16 (line 13 plus the
parking fees and the supplementary insurance). A vehicle whose line 26 is below zero is refused
(`InputAboveBoundError`, naming amounts 21 and 25 of Chart C: the eligible leasing cost of line 28
cannot be negative). A vehicle
whose business kilometres (Chart A amount 1) are above its total kilometres (amount 2) is refused
(`InputAboveBoundError`, "item N: ..." and naming amounts 1 and 2 of Chart A), before any of its
lines is worked: the business use part of line 13 would be more than the vehicle's whole. Business
kilometres equal to the total are accepted, and so are 0 total kilometres with 0 business
kilometres (line 13 is 0); 0 total kilometres with business kilometres above 0 is refused too, as
the business kilometres are above the total.

A vehicle whose interest days (Chart B amount 17's days) are above the days of the fiscal period
(`fiscal_period_days`, Chart B line 18 "the number of days in the fiscal period for which interest
was payable (accrual method) or paid (cash method)") is refused (`InputAboveBoundError`, "item N:
..." naming the interest days and the fiscal period's days), before any of its lines is worked: the
interest limit would count days the fiscal period does not have. Interest days equal to the days of
the fiscal period are accepted, and so are fewer; 0 interest days are accepted in any fiscal
period. The output is the total of the line 16 amounts. It records one `BusinessVehicleLine` per
vehicle, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.credit import CREDIT
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.parameters.year_amounts import YEAR_AMOUNTS
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.business_vehicle_expenses import (
    BusinessVehicleExpenses,
)
from tax_engine.jurisdictions.ca.trace import BusinessVehicleLine
from tests.jurisdictions.ca.capabilities.vehicles_table import (
    CENT,
    FAMILIES,
    FISCAL_PERIOD_DAYS,
    LEASED,
    MOTOR_VEHICLE_EXPENSES,
    SALES_TAX_RATE,
    SOURCES,
    VEHICLES,
    capability,
    credit,
    datasets,
    fiscal_period_days,
    interest_limits,
    lease_limits,
    sales_tax_rate,
    service,
    vehicle,
    vehicles,
)

D = Decimal


def compute(
    *records: dict[Any, Decimal | int],
    rate: str = "13",
    period_days: int = 365,
    **replaced: Any,
) -> Artifact[Any]:
    inputs = (vehicles(*records), sales_tax_rate(rate), fiscal_period_days(period_days))
    (output,) = capability(**replaced).compute(inputs).outputs
    return output


def total(
    *records: dict[Any, Decimal | int],
    rate: str = "13",
    period_days: int = 365,
    **replaced: Any,
) -> Decimal:
    value = compute(*records, rate=rate, period_days=period_days, **replaced).value
    assert isinstance(value, Decimal)
    return value


def vehicle_line(
    position: int, line_12: str, line_13: str, line_19: str, line_28: str, line_16: str
) -> BusinessVehicleLine:
    return BusinessVehicleLine(
        MOTOR_VEHICLE_EXPENSES,
        position,
        D(line_12),
        D(line_13),
        D(line_19),
        D(line_28),
        D(line_16),
    )


def test_is_registered_as_ca_business_vehicle_expenses() -> None:
    assert (
        CapabilityRegistry.shared().get("ca/business_vehicle_expenses") is BusinessVehicleExpenses
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "business_vehicle_expenses" in ca_capabilities.__all__
    assert ca_capabilities.business_vehicle_expenses.BusinessVehicleExpenses is (
        BusinessVehicleExpenses
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({VEHICLES, SALES_TAX_RATE, FISCAL_PERIOD_DAYS})
    assert capability().produces == frozenset({MOTOR_VEHICLE_EXPENSES})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(BusinessVehicleExpenses)
    assert "produces" not in vars(BusinessVehicleExpenses)


def test_declares_its_slots() -> None:
    assert BusinessVehicleExpenses.PARAMETERS == {
        "interest_limits": YEAR_AMOUNTS,
        "lease_limits": YEAR_AMOUNTS,
        "days_divisor": CREDIT,
        "lease_price_rate": RATE,
        "deposit_minimum": CREDIT,
        "rounding": ROUNDING_ONLY,
    }
    assert list(BusinessVehicleExpenses.PARAMETERS) == [
        "interest_limits",
        "lease_limits",
        "days_divisor",
        "lease_price_rate",
        "deposit_minimum",
        "rounding",
    ]
    assert BusinessVehicleExpenses.CONSUMES == {
        "vehicles": RecordList,
        "sales_tax_rate": Decimal,
        "fiscal_period_days": int,
    }
    assert BusinessVehicleExpenses.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for each in (
        BusinessVehicleExpenses.PARAMETERS,
        BusinessVehicleExpenses.CONSUMES,
        BusinessVehicleExpenses.PRODUCES,
    ):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(BusinessVehicleExpenses.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(BusinessVehicleExpenses.CONSUMES, Mapping[str, type])
    assert_type(BusinessVehicleExpenses.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = BusinessVehicleExpenses(
        **datasets(),
        vehicles=VEHICLES,
        sales_tax_rate=SALES_TAX_RATE,
        fiscal_period_days=FISCAL_PERIOD_DAYS,
        output=MOTOR_VEHICLE_EXPENSES,
    )

    (output,) = wired.compute((vehicles(LEASED), sales_tax_rate(), fiscal_period_days())).outputs
    assert output == Artifact(MOTOR_VEHICLE_EXPENSES, D("2500"))


def test_is_built_from_its_slots_in_order_when_positional() -> None:
    # The six datasets in the order of PARAMETERS, then the consumed slots, then the produced one.
    found = datasets()
    wired = BusinessVehicleExpenses(
        found["interest_limits"],
        found["lease_limits"],
        found["days_divisor"],
        found["lease_price_rate"],
        found["deposit_minimum"],
        found["rounding"],
        VEHICLES,
        SALES_TAX_RATE,
        FISCAL_PERIOD_DAYS,
        MOTOR_VEHICLE_EXPENSES,
    )

    assert wired.consumes == frozenset({VEHICLES, SALES_TAX_RATE, FISCAL_PERIOD_DAYS})
    assert list(BusinessVehicleExpenses.PARAMETERS) == list(FAMILIES)


def test_rejects_a_money_kind_for_its_vehicles() -> None:
    with pytest.raises(InvalidCapabilityError, match="BusinessVehicleExpenses.*'vehicles'"):
        BusinessVehicleExpenses(
            **datasets(),
            vehicles=MOTOR_VEHICLE_EXPENSES,  # type: ignore[arg-type]
            sales_tax_rate=SALES_TAX_RATE,
            fiscal_period_days=FISCAL_PERIOD_DAYS,
            output=MOTOR_VEHICLE_EXPENSES,
        )


# --- computing ----------------------------------------------------------------------------------


def test_a_leased_vehicle_gives_the_tables_figure() -> None:
    # Chart B: line 18 is 350 ÷ 30 × 183 = 2135.00, so line 19 is the lesser of 400 and 2135.00,
    # 400. Chart C: line 23 is 60000 (more than 44706 + 5811.78 = 50517.78), line 24 is 51000.00,
    # line 25 is 1243.00 × 183 ÷ 30 = 7582.30, line 26 is 7582.30 - 0, line 27 is 42940.00 × 2550
    # ÷ 51000.00 = 2147.00 and line 28 is 2147.00. Chart A: line 12 is 1000 + 400 + 600 + 200 +
    # 2147 + 653 = 5000, line 13 is 5000 × 5000 ÷ 10000 = 2500 and line 16 is 2500.
    assert total(LEASED) == D("2500")


def test_the_output_is_a_money_artifact_of_the_output_kind() -> None:
    assert compute(LEASED) == Artifact(MOTOR_VEHICLE_EXPENSES, D("2500"))


def test_chart_b_interest_is_the_amount_payable_when_that_is_the_lesser() -> None:
    # Line 17 is 400, less than line 18 of 2135.00: line 19 is 400, so line 12 is 100 + 400 = 500
    # and line 13 is 500 × 1 ÷ 1.
    owned = vehicle(
        business_kilometres="1",
        total_kilometres="1",
        fuel_and_oil="100",
        interest_payable="400",
        interest_days="183",
    )

    assert total(owned) == D("500")


def test_chart_b_interest_is_capped_at_the_350_over_30_a_day_amount() -> None:
    # Line 17 is 3000, more than line 18 of 2135.00 (350 ÷ 30 × 183): line 19 is 2135.00, so line
    # 12 is 1000 + 2135 + 600 + 200 + 2147 + 653 = 6735 and line 13 is 3367.50.
    assert total(vehicle(**{**LEASED_FIELDS, "interest_payable": "3000"})) == D("3367.50")


def test_chart_b_interest_is_nothing_with_no_days() -> None:
    # Line 18 is 350 ÷ 30 × 0 = 0, so line 19 is the lesser of 400 and 0: 0. Line 12 is 100,
    # line 13 is 100 × 1 ÷ 1.
    owned = vehicle(
        business_kilometres="1",
        total_kilometres="1",
        fuel_and_oil="100",
        interest_payable="400",
        interest_days="0",
    )

    assert total(owned) == D("100")


def test_chart_c_takes_the_price_plus_tax_when_it_is_more_than_the_list_price() -> None:
    # Line 23 is 40000; 44706 plus 13% (5811.78) is 50517.78, the greater, and 85% of it is
    # 42940.113, which rounds to 42940.11 (line 24). Line 27 is 42940.00 × 2550 ÷ 42940.11 =
    # 2549.99 (rounded), the lesser of it and line 26 (7582.30), so line 28 is 2549.99, line 12 is
    # 1000 + 400 + 600 + 200 + 2549.99 + 653 = 5402.99 and line 13 is 2701.495, which rounds to
    # 2701.50.
    assert total(vehicle(**{**LEASED_FIELDS, "list_price": "40000"})) == D("2701.50")


def test_chart_c_takes_the_list_price_when_it_is_more_than_the_price_plus_tax() -> None:
    # Line 23 is 60000, more than 50517.78, so line 24 is 60000 × 85% = 51000.00 and line 28 is
    # 2147.00 (see the first test).
    assert total(LEASED) == D("2500")


def test_chart_c_leasing_cost_is_line_26_when_the_payments_before_make_it_the_lesser() -> None:
    # Line 25 is 7582.30 and line 21 is 7000, so line 26 is 582.30, less than line 27 (2147.00):
    # line 28 is 582.30, line 12 is 1000 + 400 + 600 + 200 + 582.30 + 653 = 3435.30 and line 13 is
    # 3435.30 × 5000 ÷ 10000 = 1717.65, line 16.
    assert total(vehicle(**{**LEASED_FIELDS, "lease_payments_before": "7000"})) == D("1717.65")


def test_chart_c_line_26_below_zero_is_refused() -> None:
    # Line 25 is 7582.30 and line 21 (payments before the year) is 9000, so line 26 is
    # 7582.30 - 9000 = -1417.70. The form prints no floor, but the eligible leasing cost (line 28)
    # is a non-negative amount, so the computation refuses it rather than inventing a floor.
    with pytest.raises(InputAboveBoundError) as raised:
        compute(vehicle(**{**LEASED_FIELDS, "lease_payments_before": "9000"}))

    assert str(raised.value) == (
        "item 1: Chart C amount 21 (lease payments deducted before the fiscal period) 9000 "
        "is above amount 25 (7582.30)"
    )


def test_the_refused_vehicle_is_named_by_its_position() -> None:
    with pytest.raises(InputAboveBoundError, match="^item 2: Chart C amount 21 "):
        compute(LEASED, vehicle(**{**LEASED_FIELDS, "lease_payments_before": "9000"}))


@pytest.mark.parametrize(
    ("business", "total"),
    [
        # One above the total, twice the total, and any amount above a total of 0.
        ("10001", "10000"),
        ("20000", "10000"),
        ("1", "0"),
        ("5000", "0"),
    ],
)
def test_business_kilometres_above_total_kilometres_is_refused(business: str, total: str) -> None:
    # Amount 1 above amount 2 makes the business use part of line 13 more than the vehicle's
    # whole, so the record is an input error, not a figure to compute; a total of 0 gives no
    # business use part, and business kilometres above it are refused too.
    with pytest.raises(InputAboveBoundError, match=r"^item 1: .*amount 1.*amount 2"):
        compute(vehicle(business_kilometres=business, total_kilometres=total, fuel_and_oil="1000"))


def test_the_business_kilometres_check_comes_before_the_vehicle_is_worked() -> None:
    # The payments before the year of 9000 would make line 26 below 0 (a refusal of its own), but
    # the vehicle is refused first, for its business kilometres above its total.
    overdrawn = {**LEASED_FIELDS, "business_kilometres": "20000", "lease_payments_before": "9000"}

    with pytest.raises(InputAboveBoundError, match=r"^item 1: "):
        compute(vehicle(**overdrawn))


def test_the_vehicle_with_business_kilometres_above_total_is_named_by_its_position() -> None:
    with pytest.raises(InputAboveBoundError, match=r"^item 2: .*amount 1.*amount 2"):
        compute(LEASED, vehicle(business_kilometres="10001", total_kilometres="10000"))


@pytest.mark.parametrize(
    ("interest_days", "period_days"),
    [
        # One above the fiscal period's days, the 365 of a full year, and a short period.
        (154, 153),
        (184, 183),
        (366, 365),
    ],
)
def test_interest_days_above_the_fiscal_period_days_are_refused(
    interest_days: int, period_days: int
) -> None:
    # Line 18 counts the days of the fiscal period, so interest days above the days of the period
    # would give an interest limit for days the period does not have: the vehicle is refused,
    # naming both figures.
    with pytest.raises(InputAboveBoundError) as raised:
        compute(
            vehicle(**{**LEASED_FIELDS, "interest_days": str(interest_days)}),
            period_days=period_days,
        )

    assert str(raised.value).startswith("item 1: ")
    assert f"{interest_days}" in str(raised.value)
    assert f"{period_days}" in str(raised.value)


def test_the_interest_days_check_comes_before_the_rest_of_the_vehicle_is_worked() -> None:
    # The payments before the year of 9000 would make line 26 below 0 (a refusal of its own), but
    # the vehicle is refused first, for its interest days above the fiscal period's days.
    overdrawn = {**LEASED_FIELDS, "interest_days": "184", "lease_payments_before": "9000"}

    with pytest.raises(InputAboveBoundError, match=r"^item 1: "):
        compute(vehicle(**overdrawn), period_days=183)


@pytest.mark.parametrize(("interest_days", "period_days"), [(153, 153), (183, 183), (365, 365)])
def test_interest_days_equal_to_the_fiscal_period_days_are_accepted(
    interest_days: int, period_days: int
) -> None:
    # Line 18 is 350 ÷ 30 × the days, more than the 400 payable for all of these, so line 19 is 400
    # and the leased vehicle gives the 2500 of the statement.
    owned = vehicle(**{**LEASED_FIELDS, "interest_days": str(interest_days)})

    assert total(owned, period_days=period_days) == D("2500")


@pytest.mark.parametrize(("interest_days", "period_days"), [(152, 153), (364, 365)])
def test_interest_days_fewer_than_the_fiscal_period_days_are_accepted(
    interest_days: int, period_days: int
) -> None:
    # 152 of 153: line 18 is 350 ÷ 30 × 152 = 1773.33, more than the 400 payable, so line 19 is 400
    # and the total is 2500.
    owned = vehicle(**{**LEASED_FIELDS, "interest_days": str(interest_days)})

    assert total(owned, period_days=period_days) == D("2500")


def test_no_interest_days_are_accepted_in_any_fiscal_period() -> None:
    # 0 interest days: line 18 is 0, so line 19 is 0 and line 12 is 5000 - 400 = 4600, and line 13
    # is 4600 × 5000 ÷ 10000 = 2300, in a one-day period too.
    owned = vehicle(**{**LEASED_FIELDS, "interest_days": "0"})

    assert total(owned, period_days=1) == D("2300")


def test_the_vehicle_with_interest_days_above_the_period_is_named_by_its_position() -> None:
    # The first vehicle has 183 interest days in a period of 183 days (equal, accepted); the second
    # has 184.
    with pytest.raises(InputAboveBoundError, match=r"^item 2: (?=.*\b184\b)(?=.*\b183\b)"):
        compute(LEASED, vehicle(**{**LEASED_FIELDS, "interest_days": "184"}), period_days=183)


def test_a_line_26_of_exactly_zero_is_not_refused() -> None:
    # Line 25 is 7582.30 and line 21 is 7582.30: line 26 is 0, so line 28 is 0, line 12 is
    # 1000 + 400 + 600 + 200 + 0 + 653 = 2853 and line 13 is 1426.50.
    assert total(vehicle(**{**LEASED_FIELDS, "lease_payments_before": "7582.30"})) == D("1426.50")


def test_a_vehicle_with_no_lease_has_no_leasing_cost() -> None:
    # Lines 20 to 22 are 0: line 25 and line 27 are 0 (line 24 is 42940.11, never 0), so line 28
    # is 0. Line 12 is 1200 + 600 + 900 + 150 + 450 = 3300 and line 13 is 3300 × 7000 ÷ 16000 =
    # 1443.75; line 16 adds the parking fees of 120.
    owned = vehicle(
        business_kilometres="7000",
        total_kilometres="16000",
        fuel_and_oil="1200",
        insurance="900",
        licence_and_registration="150",
        maintenance_and_repairs="450",
        interest_payable="600",
        interest_days="183",
        parking_fees="120",
    )

    assert total(owned) == D("1563.75")


def test_chart_a_business_use_part_is_rounded_half_up_to_the_cent() -> None:
    # Amount 1 of 1 and amount 2 of 3: 100 × 1 ÷ 3 = 33.333..., which rounds to 33.33 (line 13).
    third = vehicle(business_kilometres="1", total_kilometres="3", fuel_and_oil="100")

    assert total(third) == D("33.33")


def test_chart_a_business_use_part_rounds_a_half_cent_up() -> None:
    # Amount 12 of 0.01 times 1 ÷ 2 is 0.005, a half cent, which rounds up to 0.01 (line 13).
    half = vehicle(business_kilometres="1", total_kilometres="2", fuel_and_oil="0.01")

    assert total(half) == D("0.01")


def test_chart_a_business_use_part_is_0_when_there_are_no_total_kilometres() -> None:
    # A total of 0 kilometres with 0 business kilometres gives a business use part of 0 (no
    # division), so line 16 is only the parking fees of 300. Business kilometres above 0 with a
    # total of 0 are refused.
    no_distance = vehicle(
        business_kilometres="0", total_kilometres="0", fuel_and_oil="900", parking_fees="300"
    )

    assert total(no_distance) == D("300")


def test_chart_a_line_16_adds_the_parking_fees_and_the_supplementary_insurance() -> None:
    # Line 12 is 1000, line 13 is 1000 × 1 ÷ 2 = 500; line 16 is 500 + 120 + 60 = 680.
    leased = vehicle(
        business_kilometres="1",
        total_kilometres="2",
        fuel_and_oil="1000",
        parking_fees="120",
        supplementary_insurance="60",
    )

    assert total(leased) == D("680")


def test_chart_a_line_12_adds_each_of_amounts_3_to_11() -> None:
    # Amounts 3, 5, 6, 7, 9, 10 and 11 (amounts 4 and 8 being lines 19 and 28): 1 + 2 + 4 + 8 +
    # 16 + 32 + 64 = 127, all for business (amounts 1 and 2 equal).
    every = vehicle(
        business_kilometres="10",
        total_kilometres="10",
        fuel_and_oil="1",
        insurance="2",
        licence_and_registration="4",
        maintenance_and_repairs="8",
        electricity_zev="16",
        other_expenses_10="32",
        other_expenses_11="64",
    )

    assert total(every) == D("127")


def test_the_parking_fees_and_the_supplementary_insurance_are_not_shared_with_personal_use() -> (
    None
):
    # Amounts 14 and 15 are added to line 16 whole, whatever the share of business kilometres.
    unused = vehicle(
        business_kilometres="0", total_kilometres="10", parking_fees="120", fuel_and_oil="500"
    )

    assert total(unused) == D("120")


def test_the_sales_tax_rate_is_the_callers() -> None:
    # At 5% (GST): 1100 + 55.00 = 1155.00, 38000 + 1900.00 = 39900.00, 44706 + 2235.30 =
    # 46941.30 (less than 60000). Line 25 is 1155.00 × 183 ÷ 30 = 7045.50 and line 27 is
    # 39900.00 × 2550 ÷ 51000.00 = 1995.00 (the lesser), so line 12 is 1000 + 400 + 600 + 200 +
    # 1995 + 653 = 4848 and line 13 is 2424.
    assert total(LEASED, rate="5") == D("2424")


def test_with_no_sales_tax_the_printed_figures_stand_alone() -> None:
    # At 0%: line 25 is 1100 × 183 ÷ 30 = 6710.00, line 27 is 38000 × 2550 ÷ 51000.00 = 1900.00,
    # line 12 is 1000 + 400 + 600 + 200 + 1900 + 653 = 4753 and line 13 is 2376.50.
    assert total(LEASED, rate="0") == D("2376.50")


def test_a_vehicle_of_nothing_gives_zero() -> None:
    value = total(vehicle())

    assert value == D("0")
    assert not value.is_signed()


def test_the_line_16_amounts_of_several_vehicles_are_added() -> None:
    # Vehicle 1 (owned, with interest): line 19 is 600 (less than 2135.00), line 12 is
    # 1200 + 600 + 900 + 150 + 450 = 3300, line 13 is 3300 × 7000 ÷ 16000 = 1443.75 and line 16 is
    # 1443.75 + 120 = 1563.75. Vehicle 2 (leased): line 26 is 7582.30 - 1000 = 6582.30, line 28 is
    # 2147.00, line 12 is 600 + 450 + 108 + 2147 + 200 = 3505, line 13 is 3505 × 3000 ÷ 12000 =
    # 876.25 and line 16 is 876.25 + 60 = 936.25. Line 9281 is 1563.75 + 936.25 = 2500.00.
    assert total(OWNED, SECOND) == D("2500")


def test_the_order_of_the_vehicles_does_not_change_the_total() -> None:
    assert total(SECOND, OWNED) == total(OWNED, SECOND) == D("2500")


def test_the_same_vehicle_listed_twice_is_added_twice() -> None:
    assert total(LEASED, LEASED) == D("5000")


def test_no_vehicles_give_zero() -> None:
    output = compute()

    assert output == Artifact(MOTOR_VEHICLE_EXPENSES, D("0"))
    assert not output.value.is_signed()


def test_each_vehicle_is_worked_on_its_own() -> None:
    # The refusal of a vehicle's line 26 is the vehicle's own: another vehicle's payments do not
    # offset it, and an all-zero vehicle adds nothing.
    assert total(LEASED, vehicle()) == D("2500")


def test_missing_vehicles_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="business_vehicles"):
        capability().compute((sales_tax_rate(),))


def test_a_missing_sales_tax_rate_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="business_vehicle_sales_tax_rate"):
        capability().compute((vehicles(LEASED),))


def test_a_missing_fiscal_period_days_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="business_fiscal_period_days"):
        capability().compute((vehicles(LEASED), sales_tax_rate()))


# --- the datasets are the chart's printed figures -----------------------------------------------


@pytest.mark.parametrize(
    ("slot", "dataset", "expected"),
    [
        # Line 18 is 100 ÷ 30 × 183 = 610.00 (not 350 ÷ 30 × 183): with 3000 payable, line 19 is
        # 610.00, line 12 is 5210 and line 13 is 2605.
        ("interest_limits", interest_limits((None, "100")), "2605"),
        # Line 18 is 350 ÷ 60 × 183 = 1067.50 with 3000 payable, line 12 is 5667.50 and line 13 is
        # 2833.75; line 25 is 1243.00 × 183 ÷ 60 = 3791.15, still more than line 27.
        ("days_divisor", credit(FAMILIES["days_divisor"], "60"), "2833.75"),
        # Line 23 is 70000 + 9100.00 = 79100.00 (more than 60000), line 24 is 67235.00, line 27 is
        # 42940.00 × 2550 ÷ 67235.00 = 1628.57, line 12 is 4481.57 and line 13 is 2240.785, which
        # rounds to 2240.79.
        ("lease_limits", lease_limits((None, "70000", "1100", "38000")), "2240.79"),
        # Line 25 is (100 + 13.00) × 183 ÷ 30 = 689.30, the lesser of it and 2147.00: line 12 is
        # 3542.30 and line 13 is 1771.15.
        ("lease_limits", lease_limits((None, "44706", "100", "38000")), "1771.15"),
        # Line 27 is (20000 + 2600.00) × 2550 ÷ 51000.00 = 1130.00, line 12 is 3983 and line 13
        # is 1991.50.
        ("lease_limits", lease_limits((None, "44706", "1100", "20000")), "1991.50"),
        # Line 24 is 60000 × 50% = 30000.00, line 27 is 42940.00 × 2550 ÷ 30000.00 = 3649.90,
        # line 12 is 6502.90 and line 13 is 3251.45.
        (
            "lease_price_rate",
            ParameterDataset(
                FAMILIES["lease_price_rate"], 2025, RATE, Rate(D("0.5")), CENT, SOURCES
            ),
            "3251.45",
        ),
    ],
)
def test_each_printed_figure_comes_from_its_dataset(
    slot: str, dataset: ParameterDataset[Any], expected: str
) -> None:
    owned_with_interest = vehicle(**{**LEASED_FIELDS, "interest_payable": "3000"})
    record = owned_with_interest if slot in ("interest_limits", "days_divisor") else LEASED

    (output,) = (
        capability(**{slot: dataset})
        .compute((vehicles(record), sales_tax_rate(), fiscal_period_days()))
        .outputs
    )

    assert output.value == D(expected)


def test_the_rounding_comes_from_the_rounding_dataset() -> None:
    # To the whole dollar: 100 × 1 ÷ 3 = 33.33... rounds to 33, not 33.33.
    whole = ParameterDataset(
        FAMILIES["rounding"],
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        RoundTo(D("1"), RoundingMode.HALF_UP),
        SOURCES,
    )
    third = vehicle(business_kilometres="1", total_kilometres="3", fuel_and_oil="100")

    assert total(third, rounding=whole) == D("33")


# --- the figure set printed for the year ----------------------------------------------------------
#
# Chart B (footnote "***") prints $350 for a passenger vehicle bought after 2023 and $300 for one
# bought after 2000 and before 2024; Chart C endnotes 11 to 13 print other figures for a lease
# entered into in 2024, 2023, 2022 and before 2022. The vehicle's `purchase_year` chooses the first,
# its `lease_year` the second.


def interest_only(purchase_year: int, days: str = "183", payable: str = "3000") -> dict[Any, Any]:
    """A vehicle of nothing but Chart B: amounts 1 and 2 equal, so line 12 is line 19 and
    lines 13 and 16 are the same."""
    return vehicle(
        business_kilometres="1",
        total_kilometres="1",
        interest_payable=payable,
        interest_days=days,
        purchase_year=str(purchase_year),
    )


def lease_only(
    lease_year: int, list_price: str = "60000", payments_before: str = "0"
) -> dict[Any, Any]:
    """A vehicle of nothing but Chart C (2550 of lease charges over 183 days): amounts 1 and 2
    equal, so line 12 is line 28 and lines 13 and 16 are the same."""
    return vehicle(
        business_kilometres="1",
        total_kilometres="1",
        lease_charges="2550",
        lease_days="183",
        list_price=list_price,
        lease_payments_before=payments_before,
        lease_year=str(lease_year),
    )


@pytest.mark.parametrize(
    ("purchase_year", "expected"),
    [
        # Bought after 2023 ("$350"): line 18 is 350 ÷ 30 × 183 = 64050 ÷ 30 = 2135.00, the lesser
        # of it and the 3000 payable (line 17), so line 19 is 2135.00.
        (2025, "2135.00"),
        (2024, "2135.00"),
        # Bought after 2000 and before 2024 ("the amount is $300"): line 18 is 300 ÷ 30 × 183 =
        # 54900 ÷ 30 = 1830.00, so line 19 is 1830.00.
        (2023, "1830.00"),
        (2022, "1830.00"),
        (2010, "1830.00"),
        (2002, "1830.00"),
        (2001, "1830.00"),
    ],
)
def test_chart_b_limit_is_chosen_by_the_year_the_vehicle_was_bought(
    purchase_year: int, expected: str
) -> None:
    assert total(interest_only(purchase_year)) == D(expected)


def test_chart_b_line_19_of_a_vehicle_bought_in_2022_is_traced() -> None:
    (line, _total) = (
        capability()
        .compute((vehicles(interest_only(2022)), sales_tax_rate(), fiscal_period_days()))
        .trace
    )

    assert line == vehicle_line(1, "1830", "1830", "1830", "0", "1830")


@pytest.mark.parametrize(("purchase_year", "expected"), [(2024, "350"), (2023, "300")])
def test_chart_b_limit_is_the_day_rate_times_the_days_for_each_year(
    purchase_year: int, expected: str
) -> None:
    # 30 days: line 18 is 350 ÷ 30 × 30 = 350 (bought after 2023) or 300 ÷ 30 × 30 = 300.
    assert total(interest_only(purchase_year, days="30")) == D(expected)


@pytest.mark.parametrize("purchase_year", [2024, 2023])
def test_chart_b_interest_payable_below_either_limit_is_the_amount_payable(
    purchase_year: int,
) -> None:
    # Line 17 of 1500 is less than line 18 (2135.00 or 1830.00): line 19 is 1500.
    assert total(interest_only(purchase_year, payable="1500")) == D("1500")


@pytest.mark.parametrize("purchase_year", [2000, 1999, 1980, 1, 0])
def test_chart_b_refuses_interest_days_for_a_vehicle_bought_in_2000_or_earlier(
    purchase_year: int,
) -> None:
    # "For passenger vehicles bought after 2000 and before 2024, the amount is $300": the form
    # prints no limit for a vehicle bought in 2000 or earlier (nor for 0, no year given), so line
    # 18 cannot be worked and the vehicle is refused rather than given a limit the form does not
    # print.
    with pytest.raises(InvalidRecordError) as raised:
        compute(interest_only(purchase_year))

    assert str(raised.value).startswith("item 1: ")
    assert str(raised.value).endswith(
        f"the form prints no limit for a vehicle bought in {purchase_year}"
    )


def test_chart_b_refuses_interest_days_even_when_no_interest_is_payable() -> None:
    # Line 18 is worked for any interest days, and no limit is printed for 2000.
    with pytest.raises(InvalidRecordError, match="vehicle bought in 2000$"):
        compute(interest_only(2000, payable="0"))


def test_the_refused_vehicle_is_named_by_its_position_for_a_year_with_no_limit() -> None:
    with pytest.raises(InvalidRecordError, match="^item 2: .*vehicle bought in 1999$"):
        compute(LEASED, interest_only(1999))


@pytest.mark.parametrize("purchase_year", [2026, 2030, 9999])
@pytest.mark.parametrize("days", ["0", "183"])
def test_a_purchase_year_after_the_datasets_tax_year_is_refused(
    purchase_year: int, days: str
) -> None:
    # The form prints no limit for a vehicle bought after 2025, with interest days or not.
    with pytest.raises(InvalidRecordError) as raised:
        compute(LEASED, interest_only(purchase_year, days=days))

    assert str(raised.value) == (
        f"item 2: a vehicle bought in {purchase_year} is after 2025, "
        "the year of the figures the charts print"
    )


@pytest.mark.parametrize("purchase_year", [2025, 2000, 1999, 1, 0])
def test_chart_b_with_no_interest_days_needs_no_limit_whatever_the_year(
    purchase_year: int,
) -> None:
    # Line 18 is 350 or 300 ÷ 30 × 0 = 0: with no days there is nothing to look up, so line 19 is
    # 0 and line 12 is the fuel and oil of 100, line 13 is 100 × 1 ÷ 1.
    owned = vehicle(
        business_kilometres="1",
        total_kilometres="1",
        fuel_and_oil="100",
        interest_payable="400",
        interest_days="0",
        purchase_year=str(purchase_year),
    )

    assert total(owned) == D("100")


def test_a_vehicle_with_no_interest_and_no_purchase_year_is_not_refused() -> None:
    assert total(vehicle(purchase_year="0", lease_year="0")) == D("0")


def test_the_purchase_year_looks_up_the_interest_limits_dataset() -> None:
    # A made-up table: 400 from 2025, 200 before it, with no year left out: 2024 and 0 are both
    # in the open-ended row, so none is refused. Line 18 is 400 ÷ 30 × 30 = 400 or 200.
    limits = interest_limits((2025, "400"), (None, "200"))

    assert total(interest_only(2025, days="30"), interest_limits=limits) == D("400")
    assert total(interest_only(2024, days="30"), interest_limits=limits) == D("200")
    assert total(interest_only(0, days="30"), interest_limits=limits) == D("200")


@pytest.mark.parametrize(
    ("lease_year", "expected"),
    [
        # Line 23 is 60000, more than every price plus tax, so line 24 is 60000 × 85% = 51000.00.
        # Line 27 is (the cost limit + 13%) × 2550 ÷ 51000.00 = (the cost limit + 13%) ÷ 20, the
        # lesser of it and line 26. The 2025 set: 38000 × 1.13 = 42940.00, ÷ 20 = 2147.00.
        (2025, "2147.00"),
        # Leases entered into in 2024 (endnote 11): 37000 × 1.13 = 41810.00, ÷ 20 = 2090.50.
        (2024, "2090.50"),
        # 2023 (endnote 12): 36000 × 1.13 = 40680.00, ÷ 20 = 2034.00.
        (2023, "2034.00"),
        # 2022 (endnote 13): 34000 × 1.13 = 38420.00, ÷ 20 = 1921.00.
        (2022, "1921.00"),
        # Before 2022 (endnote 13): 30000 × 1.13 = 33900.00, ÷ 20 = 1695.00.
        (2021, "1695.00"),
        (2001, "1695.00"),
        (2000, "1695.00"),
        # No year given: the before 2022 set, as the charts print nothing else for it.
        (0, "1695.00"),
    ],
)
def test_chart_c_cost_limit_is_chosen_by_the_year_the_lease_was_entered_into(
    lease_year: int, expected: str
) -> None:
    # Each line 26 (the charge limit + 13%, × 183 ÷ 30) is far above line 27, so line 28 is
    # line 27.
    assert total(lease_only(lease_year)) == D(expected)


@pytest.mark.parametrize(
    ("lease_year", "expected"),
    [
        # 40000 against 44706 + 13% (5811.78) = 50517.78: line 23 is 50517.78, line 24 is
        # 42940.1130, which rounds to 42940.11, and line 27 is (38000 + 4940.00 = 42940.00) × 2550
        # ÷ 42940.11 = 2549.9935, which rounds to 2549.99.
        (2025, "2549.99"),
        # 43529 + 13% (5658.77) = 49187.77, line 24 is 41809.6045 = 41809.60 and line 27 is
        # (37000 + 4810.00 = 41810.00) × 2550 ÷ 41809.60 = 2550.0244 = 2550.02.
        (2024, "2550.02"),
        # 42353 + 13% (5505.89) = 47858.89, line 24 is 40680.0565 = 40680.06 and line 27 is
        # (36000 + 4680.00 = 40680.00) × 2550 ÷ 40680.06 = 2549.9962 = 2550.00.
        (2023, "2550.00"),
        # 40000 + 13% (5200.00) = 45200.00, line 24 is 38420.00 and line 27 is
        # (34000 + 4420.00 = 38420.00) × 2550 ÷ 38420.00 = 2550.00.
        (2022, "2550.00"),
        # 35294 + 13% (4588.22) = 39882.22, below the list price of 40000: line 23 is 40000, line
        # 24 is 34000.00 and line 27 is (30000 + 3900.00 = 33900.00) × 2550 ÷ 34000.00 = 2542.50.
        (2021, "2542.50"),
    ],
)
def test_chart_c_price_limit_is_chosen_by_the_year_the_lease_was_entered_into(
    lease_year: int, expected: str
) -> None:
    # Line 26 of each set (7582.30, 7237.65, 6548.35, 6203.70 and 5514.40) is above line 27, so
    # line 28 is line 27.
    assert total(lease_only(lease_year, list_price="40000")) == D(expected)


@pytest.mark.parametrize(
    ("lease_year", "line_28"),
    [
        # Line 26 is line 25 less the 6000 of payments before: line 25 is the charge limit + 13%,
        # × 183 ÷ 30. 2025: 1100 + 143.00 = 1243.00, 227469.00 ÷ 30 = 7582.30, line 26 1582.30.
        (2025, "1582.30"),
        # 2024: 1050 + 136.50 = 1186.50, × 183 = 217129.50 ÷ 30 = 7237.65, line 26 1237.65.
        (2024, "1237.65"),
        # 2023: 950 + 123.50 = 1073.50, × 183 = 196450.50 ÷ 30 = 6548.35, line 26 548.35.
        (2023, "548.35"),
        # 2022: 900 + 117.00 = 1017.00, × 183 = 186111.00 ÷ 30 = 6203.70, line 26 203.70.
        (2022, "203.70"),
    ],
)
def test_chart_c_charge_limit_is_chosen_by_the_year_the_lease_was_entered_into(
    lease_year: int, line_28: str
) -> None:
    # Each line 26 is below line 27 (2147.00, 2090.50, 2034.00 and 1921.00), so it is line 28.
    assert total(lease_only(lease_year, payments_before="6000")) == D(line_28)


def test_chart_c_line_26_below_zero_depends_on_the_lease_year() -> None:
    # Before 2022: 800 + 104.00 = 904.00, × 183 = 165432.00 ÷ 30 = 5514.40, so line 26 is
    # 5514.40 - 6000 = -485.60, which is refused; the same 6000 is fine for 2022 (203.70).
    with pytest.raises(InputAboveBoundError) as raised:
        compute(lease_only(2021, payments_before="6000"))

    assert str(raised.value) == (
        "item 1: Chart C amount 21 (lease payments deducted before the fiscal period) 6000 "
        "is above amount 25 (5514.40)"
    )


def test_the_two_years_of_a_vehicle_are_independent() -> None:
    # Bought in 2022 (line 19 is 300 ÷ 30 × 183 = 1830.00) and leased in 2023 (line 28 is
    # 36000 × 1.13 ÷ 20 = 2034.00): line 12 is 1830.00 + 2034.00 = 3864.00, and amounts 1 and 2 are
    # equal.
    both = vehicle(
        business_kilometres="1",
        total_kilometres="1",
        interest_payable="3000",
        interest_days="183",
        lease_charges="2550",
        lease_days="183",
        list_price="60000",
        purchase_year="2022",
        lease_year="2023",
    )
    assert total(both) == D("3864")

    # Bought in 2025 (2135.00) and leased in 2022 (1921.00): 4056.00.
    swapped = vehicle(
        business_kilometres="1",
        total_kilometres="1",
        interest_payable="3000",
        interest_days="183",
        lease_charges="2550",
        lease_days="183",
        list_price="60000",
        purchase_year="2025",
        lease_year="2022",
    )
    assert total(swapped) == D("4056")


def test_the_years_of_a_vehicle_with_neither_interest_nor_a_lease_change_nothing() -> None:
    # No interest days and no lease days: lines 19 and 28 are 0 in every year, and line 12 is the
    # fuel and oil of 100 (amounts 1 and 2 equal).
    for purchase_year, lease_year in (("2025", "2025"), ("2000", "0"), ("0", "0"), ("1", "1999")):
        plain = vehicle(
            business_kilometres="1",
            total_kilometres="1",
            fuel_and_oil="100",
            purchase_year=purchase_year,
            lease_year=lease_year,
        )
        assert total(plain) == D("100"), (purchase_year, lease_year)


@pytest.mark.parametrize("lease_year", [2026, 2030, 9999])
def test_a_lease_year_after_the_datasets_tax_year_is_refused(lease_year: int) -> None:
    with pytest.raises(InvalidRecordError) as raised:
        compute(LEASED, lease_only(lease_year))

    assert str(raised.value) == (
        f"item 2: a lease entered into in {lease_year} is after 2025, "
        "the year of the figures the charts print"
    )


def test_the_lease_year_looks_up_the_lease_limits_dataset() -> None:
    # A made-up table: a charge limit of 2000 from 2025, 100 before it. Line 25 is (2000 + 13% =
    # 2260.00) × 183 ÷ 30 = 13786.00 or (100 + 13% = 113.00) × 183 ÷ 30 = 689.30. Line 27 is
    # 2147.00 (the 2025 price and cost limits), so line 28 is 2147.00 from 2025 and 689.30 before.
    limits = lease_limits((2025, "44706", "2000", "38000"), (None, "44706", "100", "38000"))

    assert total(lease_only(2025), lease_limits=limits) == D("2147")
    assert total(lease_only(2024), lease_limits=limits) == D("689.30")
    assert total(lease_only(0), lease_limits=limits) == D("689.30")


def test_a_vehicle_line_records_the_figures_chosen_by_the_years() -> None:
    both = vehicle(
        business_kilometres="1",
        total_kilometres="1",
        interest_payable="3000",
        interest_days="183",
        lease_charges="2550",
        lease_days="183",
        list_price="60000",
        purchase_year="2022",
        lease_year="2023",
    )

    (line, _total) = (
        capability().compute((vehicles(both), sales_tax_rate(), fiscal_period_days())).trace
    )

    assert line == vehicle_line(1, "3864", "3864", "1830", "2034", "3864")


def test_a_computation_through_the_service_uses_the_years() -> None:
    both = vehicle(
        business_kilometres="1",
        total_kilometres="1",
        interest_payable="3000",
        interest_days="183",
        lease_charges="2550",
        lease_days="183",
        list_price="60000",
        purchase_year="2022",
        lease_year="2023",
    )

    worksheet = service().compute(
        JurisdictionCode("CA-ON"), 2025, vehicles(both), sales_tax_rate(), fiscal_period_days()
    )["ca-on/return"][0]

    assert worksheet.get(MOTOR_VEHICLE_EXPENSES).value == D("3864")


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_vehicle_line_per_vehicle_then_the_total() -> None:
    trace = (
        capability()
        .compute((vehicles(OWNED, SECOND), sales_tax_rate(), fiscal_period_days()))
        .trace
    )

    assert trace == (
        vehicle_line(1, "3300", "1443.75", "600", "0", "1563.75"),
        vehicle_line(2, "3505", "876.25", "0", "2147", "936.25"),
        ItemsTotalLine(MOTOR_VEHICLE_EXPENSES, ((1, D("1563.75")), (2, D("936.25"))), D("2500")),
    )


def test_a_vehicle_line_records_the_chart_lines_it_worked() -> None:
    (line, _total) = (
        capability().compute((vehicles(LEASED), sales_tax_rate(), fiscal_period_days())).trace
    )

    assert line == vehicle_line(1, "5000", "2500", "400", "2147", "2500")
    assert line.amount == D("2500")


def test_a_vehicle_line_records_line_16_with_the_parking_fees() -> None:
    (line, _total) = (
        capability()
        .compute((vehicles(vehicle_with_parking()), sales_tax_rate(), fiscal_period_days()))
        .trace
    )

    assert line == vehicle_line(1, "1000", "500", "0", "0", "680")


def test_a_vehicle_with_no_total_kilometres_traces_a_line_13_of_0() -> None:
    no_distance = vehicle(business_kilometres="0", total_kilometres="0", parking_fees="300")

    (line, _total) = (
        capability().compute((vehicles(no_distance), sales_tax_rate(), fiscal_period_days())).trace
    )

    assert line == vehicle_line(1, "0", "0", "0", "0", "300")


def test_traces_no_vehicles_as_only_an_empty_total() -> None:
    trace = capability().compute((vehicles(), sales_tax_rate(), fiscal_period_days())).trace

    assert trace == (ItemsTotalLine(MOTOR_VEHICLE_EXPENSES, (), D("0")),)


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((vehicles(OWNED, SECOND), sales_tax_rate(), fiscal_period_days()))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value == D("2500")


# --- through TaxComputationService --------------------------------------------------------------


def test_a_computation_gives_the_total_of_the_vehicles() -> None:
    worksheet = service().compute(
        JurisdictionCode("CA-ON"),
        2025,
        vehicles(OWNED, SECOND),
        sales_tax_rate(),
        fiscal_period_days(),
    )["ca-on/return"][0]

    assert worksheet.get(MOTOR_VEHICLE_EXPENSES).value == D("2500")
    assert isinstance(worksheet.producer_of(MOTOR_VEHICLE_EXPENSES), BusinessVehicleExpenses)


# The fields of the leased vehicle as arguments of `vehicle`, to change one of them.
LEASED_FIELDS: dict[str, str] = {
    "business_kilometres": "5000",
    "total_kilometres": "10000",
    "fuel_and_oil": "1000",
    "insurance": "600",
    "maintenance_and_repairs": "200",
    "other_expenses_10": "653",
    "interest_payable": "400",
    "interest_days": "183",
    "lease_charges": "2550",
    "lease_days": "183",
    "list_price": "60000",
}

# The two vehicles of Return BQ (returns/2025_return_bq.yaml): one owned, with Chart B interest,
# and one leased, with Chart C leasing.
OWNED = vehicle(
    business_kilometres="7000",
    total_kilometres="16000",
    fuel_and_oil="1200",
    insurance="900",
    licence_and_registration="150",
    maintenance_and_repairs="450",
    interest_payable="600",
    interest_days="183",
    parking_fees="120",
)
SECOND = vehicle(
    business_kilometres="3000",
    total_kilometres="12000",
    fuel_and_oil="600",
    insurance="450",
    maintenance_and_repairs="108",
    other_expenses_10="200",
    lease_charges="2550",
    lease_payments_before="1000",
    lease_days="183",
    list_price="60000",
    supplementary_insurance="60",
)


def vehicle_with_parking() -> dict[Any, Decimal | int]:
    return vehicle(
        business_kilometres="1",
        total_kilometres="2",
        fuel_and_oil="1000",
        parking_fees="120",
        supplementary_insurance="60",
    )


# --- Chart B is for passenger vehicles only -------------------------------------------------------
#
# Chart B is headed "Available interest expense for passenger vehicles and zero-emission passenger
# vehicles", and Guide T4002 says "When you use a passenger vehicle or a zero-emission passenger
# vehicle to earn income, there is a limit on the amount of interest you can deduct." A vehicle that
# is not one (`passenger_vehicle` 0) has no limit: its interest goes to Chart A amount 4 whole.


def truck_interest(payable: str = "5000", days: str = "365", **overrides: str) -> dict[Any, Any]:
    """A vehicle of nothing but interest that is not a passenger vehicle: the limit for 365 days
    would be 350 ÷ 30 × 365 = 4258.33, below the default 5000 payable."""
    return vehicle(
        business_kilometres="1",
        total_kilometres="1",
        interest_payable=payable,
        interest_days=days,
        passenger_vehicle="0",
        **overrides,
    )


def test_interest_of_a_vehicle_that_is_not_a_passenger_vehicle_is_not_limited() -> None:
    # Line 19 is amount 17 whole, 5000, though a passenger vehicle's would be 4258.33.
    assert total(truck_interest()) == D("5000")


def test_the_same_interest_of_a_passenger_vehicle_is_limited() -> None:
    assert total(interest_only(2025, days="365", payable="5000")) == D("4258.33")


def test_a_vehicle_that_is_not_a_passenger_vehicle_with_no_interest_days_keeps_its_interest() -> (
    None
):
    # Chart B is not filled in for it: 0 days would give a limit of 0.
    assert total(truck_interest(days="0")) == D("5000")


def test_chart_b_is_not_read_for_a_vehicle_that_is_not_a_passenger_vehicle() -> None:
    # Its interest days (above the 365 days of the period) and purchase year (no limit printed
    # for 2000) are not read, as Chart B is not worked for it.
    assert total(truck_interest(days="400", purchase_year="2000")) == D("5000")
    assert total(truck_interest(purchase_year="2030")) == D("5000")


def test_the_line_19_of_a_vehicle_that_is_not_a_passenger_vehicle_is_traced() -> None:
    (line, _total) = (
        capability()
        .compute((vehicles(truck_interest()), sales_tax_rate(), fiscal_period_days()))
        .trace
    )

    assert line == vehicle_line(1, "5000", "5000", "5000", "0", "5000")


@pytest.mark.parametrize("answer", ["2", "5"])
def test_a_passenger_vehicle_answer_above_a_yes_or_no_is_refused(answer: str) -> None:
    with pytest.raises(InputAboveBoundError, match=r"^item 2: .*passenger_vehicle .* of 1$"):
        compute(LEASED, vehicle(passenger_vehicle=answer))


def test_each_vehicle_is_limited_or_not_by_its_own_passenger_vehicle_answer() -> None:
    # The truck's 5000 passes whole; the passenger vehicle's 5000 is limited to 4258.33.
    assert total(truck_interest(), interest_only(2025, days="365", payable="5000")) == D("9258.33")


# --- Chart C is for passenger vehicles only -------------------------------------------------------
#
# Chart C is headed "Eligible leasing cost for passenger vehicles" (footnote "****": "Includes a
# vehicle that would qualify as a zero-emission passenger vehicle if you owned it."), and Guide
# T4002 says "You can deduct costs you incur to lease a passenger vehicle you use to earn income"
# and gives the limit for a passenger vehicle. A vehicle that is not one (`passenger_vehicle` 0) has
# no limit: its lease charges (amount 20) go to Chart A amount 8 whole.


def leased_truck(charges: str = "20000", days: str = "183", **overrides: str) -> dict[Any, Any]:
    """A vehicle of nothing but lease charges that is not a passenger vehicle: for 183 days the
    limit of a passenger vehicle's line 25 would be (1100 + 143) x 183 / 30 = 7582.30 at 13%."""
    return vehicle(
        business_kilometres="1",
        total_kilometres="1",
        lease_charges=charges,
        lease_days=days,
        list_price="60000",
        passenger_vehicle="0",
        **overrides,
    )


def test_leasing_cost_of_a_vehicle_that_is_not_a_passenger_vehicle_is_not_limited() -> None:
    assert total(leased_truck()) == D("20000")


def test_the_same_leasing_cost_of_a_passenger_vehicle_is_limited() -> None:
    passenger = vehicle(
        business_kilometres="1",
        total_kilometres="1",
        lease_charges="20000",
        lease_days="183",
        list_price="60000",
    )
    assert total(passenger) == D("7582.30")


def test_chart_c_is_not_read_for_a_vehicle_that_is_not_a_passenger_vehicle() -> None:
    # Its lease year (after the 2025 of the datasets), payments before the period (above amount
    # 25) and days are not read, as Chart C is not worked for it.
    assert total(leased_truck(lease_year="2030")) == D("20000")
    assert total(leased_truck(lease_payments_before="999999")) == D("20000")
    assert total(leased_truck(days="0")) == D("20000")


def test_the_line_28_of_a_vehicle_that_is_not_a_passenger_vehicle_is_traced() -> None:
    (line, _total) = (
        capability()
        .compute((vehicles(leased_truck()), sales_tax_rate(), fiscal_period_days()))
        .trace
    )

    assert line == vehicle_line(1, "20000", "20000", "0", "20000", "20000")


def test_each_vehicle_is_limited_or_not_by_its_own_leasing_answer() -> None:
    passenger = vehicle(
        business_kilometres="1",
        total_kilometres="1",
        lease_charges="20000",
        lease_days="183",
        list_price="60000",
    )
    assert total(leased_truck(), passenger) == D("27582.30")


# --- Repayment owing or imputed interest on a leased passenger vehicle ----------------------------
#
# Guide T4002 (printed page 56, "Repayments and imputed interest"): "When you lease a passenger
# vehicle, you may have a repayment owing to you, or you may have imputed interest. If so, you will
# not be able to use the chart." A passenger vehicle with a repayment owing (`lease_repayment_owing`
# 1) is refused. "Calculate imputed interest for leasing costs on a passenger vehicle only if all of
# the following apply: one or more deposits were made for the leased passenger vehicle; one or more
# deposits are refundable; the total of the deposits is more than $1,000": a passenger vehicle for
# which all three apply has imputed interest and is refused; the form and the guide print no other
# calculation. With one or two of the three failing, Chart C is worked.


def leased_car(**overrides: str) -> dict[Any, Any]:
    """A passenger vehicle of nothing but lease charges of 3000 for 184 days at a list price of
    33000, the guide's example figures (the guide rounds to whole dollars): at 13% line 24 is
    (44706 + 5811.78) x 85% = 42940.11, line 27 is 42940 x 3000 / 42940.11 = 2999.99 and line 26 is
    7623.73."""
    return vehicle(
        business_kilometres="1",
        total_kilometres="1",
        lease_charges="3000",
        lease_days="184",
        list_price="33000",
        **overrides,
    )


def test_a_leased_passenger_vehicle_with_no_repayment_owing_works_chart_c() -> None:
    assert total(leased_car()) == D("2999.99")
    assert total(leased_car(lease_repayment_owing="0")) == D("2999.99")


def test_a_leased_passenger_vehicle_with_a_repayment_owing_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 2: a repayment owing .* Chart C"):
        total(leased_car(), leased_car(lease_repayment_owing="1"))


def test_a_leased_passenger_vehicle_with_all_three_imputed_interest_conditions_is_refused() -> None:
    with pytest.raises(
        InvalidRecordError,
        match=r"^item 2: imputed interest on a leased passenger vehicle .*totalling 1000.01, "
        r"more than 1000\) .* Chart C",
    ):
        total(
            leased_car(),
            leased_car(
                lease_deposits_made="1",
                lease_deposits_refundable="1",
                lease_deposits_total="1000.01",
            ),
        )


@pytest.mark.parametrize(
    ("made", "refundable", "deposits"),
    [
        ("0", "1", "5000"),  # no deposits made
        ("1", "0", "5000"),  # none refundable
        ("1", "1", "1000"),  # the total is not more than $1,000
        ("1", "1", "800"),  # the guide's refundable $800 case
        ("0", "0", "0"),
    ],
)
def test_a_leased_passenger_vehicle_failing_a_condition_has_no_imputed_interest(
    made: str, refundable: str, deposits: str
) -> None:
    car = leased_car(
        lease_deposits_made=made,
        lease_deposits_refundable=refundable,
        lease_deposits_total=deposits,
    )
    assert total(car) == D("2999.99")


@pytest.mark.parametrize(
    "field", ["lease_repayment_owing", "lease_deposits_made", "lease_deposits_refundable"]
)
@pytest.mark.parametrize("answer", ["2", "5"])
def test_a_yes_or_no_answer_above_1_is_refused(field: str, answer: str) -> None:
    with pytest.raises(InputAboveBoundError, match=rf"^item 1: .*{field} .* of 1$"):
        total(leased_car(**{field: answer}))


def test_the_answers_are_not_read_for_a_vehicle_that_is_not_a_passenger_vehicle() -> None:
    assert total(leased_truck(lease_repayment_owing="1")) == D("20000")
    assert total(leased_truck(lease_repayment_owing="7", lease_deposits_made="9")) == D("20000")
    assert total(
        leased_truck(
            lease_deposits_made="1",
            lease_deposits_refundable="1",
            lease_deposits_total="5000",
        )
    ) == D("20000")
