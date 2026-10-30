"""CA-ON 2025 end to end: return lr (a truck that is not a passenger vehicle, with interest above
Chart B's limit)."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
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
    "interest_payable": "5000",
    "licence_and_registration": "100",
    "maintenance_and_repairs": "500",
    "passenger_vehicle": "0",
    "total_kilometres": "30000",
}


def run_lr(**truck: str) -> dict[str, tuple[Worksheet, ...]]:
    """Return LR's inputs, as in `returns/2025_return_lr.yaml`; `truck` replaces any of the
    vehicle's amounts."""
    inputs: dict[str, Any] = dict(
        cpp_part_4_completed=1,
        business_statements=(
            {
                "business": {"gross_sales": "20000"},
                "business_vehicles_rows": ({**TRUCK, **truck},),
            },
        ),
    )
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_lrs_truck_interest_of_5000_is_not_limited_by_chart_b() -> None:
    # Chart A: 27000 / 30000 x (3500 + 5000 + 1000 + 100 + 500 = 10100) = 9090, on line 9281.
    result = run_lr()
    assert result["ca/t2125"][0].get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("9090.00")


def test_return_lrs_net_business_income_is_20000_less_9090() -> None:
    result = run_lr()
    assert result["ca/t2125"][0].get(BUSINESS_TOTAL_EXPENSES).value == D("9090.00")
    assert result["ca/t2125"][0].get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("10910.00")
    assert result["ca-on/return"][0].get(BUSINESS_INCOME).value == D("10910.00")


def test_the_same_truck_as_a_passenger_vehicle_is_limited_to_4258_33_of_interest() -> None:
    # Chart B: the lesser of 5000 and 350 / 30 x 365 = 4258.33 (365 days), so 27000 / 30000 x
    # (3500 + 4258.33 + 1000 + 100 + 500 = 9358.33) = 8422.50 (rounded once at line 13).
    result = run_lr(passenger_vehicle="1", interest_days="365")
    assert result["ca/t2125"][0].get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("8422.50")
