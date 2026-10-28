"""CA-ON 2025 end to end: return lt (a leased truck that is not a passenger vehicle, with lease
charges above Chart C's limit)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    BUSINESS_MOTOR_VEHICLE_EXPENSES,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_TOTAL_EXPENSES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

TRUCK = {
    "business_kilometres": "27000",
    "fuel_and_oil": "3500",
    "insurance": "1000",
    "lease_charges": "20000",
    "lease_days": "365",
    "licence_and_registration": "100",
    "list_price": "60000",
    "maintenance_and_repairs": "500",
    "passenger_vehicle": "0",
    "total_kilometres": "30000",
}


def run_lt(**truck: str) -> dict[str, tuple[Worksheet, ...]]:
    """Return LT's inputs, as in `returns/2025_return_lt.yaml`; `truck` replaces any of the
    vehicle's amounts."""
    inputs: dict[str, Any] = dict(
        cpp_part_4_completed=1,
        business_statements=(
            {
                "business": {"gross_sales": "40000", "vehicle_sales_tax_rate": "13"},
                "business_vehicles_rows": ({**TRUCK, **truck},),
            },
        ),
    )
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_lts_truck_lease_charges_of_20000_are_not_limited_by_chart_c() -> None:
    # Chart A: 27000 / 30000 x (3500 + 20000 + 1000 + 100 + 500 = 25100) = 22590, on line 9281.
    result = run_lt()
    assert result["ca/t2125"][0].get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("22590.00")


def test_return_lts_net_business_income_is_40000_less_22590() -> None:
    result = run_lt()
    assert result["ca/t2125"][0].get(BUSINESS_TOTAL_EXPENSES).value == D("22590.00")
    assert result["ca/t2125"][0].get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("17410.00")
    assert result["ca-on/return"][0].get(BUSINESS_INCOME).value == D("17410.00")


def test_the_same_truck_as_a_passenger_vehicle_is_limited_to_15123_17_of_leasing() -> None:
    # Chart C at 13%: line 25 is (1100 + 143) x 365 / 30 = 15123.17 and line 27 is
    # (38000 + 4940) x 20000 / 51000 = 16839.22, so line 28 is 15123.17; Chart A: 27000 / 30000 x
    # (3500 + 15123.17 + 1000 + 100 + 500 = 20223.17) = 18200.85 (rounded once at line 13).
    result = run_lt(passenger_vehicle="1")
    assert result["ca/t2125"][0].get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("18200.85")
