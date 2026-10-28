"""CA-ON 2025 end to end: return lw (a leased passenger vehicle with refundable deposits of $800,
so there is no imputed interest and Chart C is worked)."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    BUSINESS_MOTOR_VEHICLE_EXPENSES,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_TOTAL_EXPENSES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

CAR = {
    "business_kilometres": "27000",
    "fuel_and_oil": "3500",
    "insurance": "1000",
    "lease_charges": "20000",
    "lease_days": "365",
    "licence_and_registration": "100",
    "lease_deposits_made": "1",
    "lease_deposits_refundable": "1",
    "lease_deposits_total": "800",
    "list_price": "60000",
    "maintenance_and_repairs": "500",
    "passenger_vehicle": "1",
    "total_kilometres": "30000",
}


def run_lw(**car: str) -> dict[str, tuple[Worksheet, ...]]:
    """Return LW's inputs, as in `returns/2025_return_lw.yaml`; `car` replaces any of the vehicle's
    amounts."""
    inputs: dict[str, Any] = dict(
        cpp_part_4_completed=1,
        business_statements=(
            {
                "business": {"gross_sales": "40000", "vehicle_sales_tax_rate": "13"},
                "business_vehicles_rows": ({**CAR, **car},),
            },
        ),
    )
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_lws_car_is_limited_by_chart_c_to_15123_17_of_its_lease_charges() -> None:
    # Chart C at 13%: line 25 is (1100 + 143) x 365 / 30 = 15123.17 and line 27 is
    # (38000 + 4940) x 20000 / 51000 = 16839.22, so line 28 is 15123.17; Chart A: 27000 / 30000 x
    # (3500 + 15123.17 + 1000 + 100 + 500 = 20223.17) = 18200.85 (rounded once at line 13).
    result = run_lw()
    assert result["ca/t2125"][0].get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("18200.85")


def test_return_lws_net_business_income_is_40000_less_18200_85() -> None:
    result = run_lw()
    assert result["ca/t2125"][0].get(BUSINESS_TOTAL_EXPENSES).value == D("18200.85")
    assert result["ca/t2125"][0].get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("21799.15")
    assert result["ca-on/return"][0].get(BUSINESS_INCOME).value == D("21799.15")


def test_deposits_of_more_than_1000_mean_imputed_interest_and_chart_c_cannot_be_used() -> None:
    # All three conditions apply: made, refundable, and a total of 1000.01 is more than 1000.
    with pytest.raises(InvalidRecordError, match=r"item 1: imputed interest on a leased passenger"):
        run_lw(lease_deposits_total="1000.01")


def test_deposits_of_exactly_1000_are_not_more_than_1000_so_chart_c_is_worked() -> None:
    result = run_lw(lease_deposits_total="1000")
    assert result["ca/t2125"][0].get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("18200.85")


def test_deposits_that_are_not_refundable_have_no_imputed_interest() -> None:
    result = run_lw(lease_deposits_refundable="0", lease_deposits_total="5000")
    assert result["ca/t2125"][0].get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("18200.85")
