"""CA-ON 2025 end to end: return ku (Guide T4002's Murray)."""

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


def run_ku(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return KU's inputs, as in `returns/2025_return_ku.yaml`; `overrides` replace any of them."""
    inputs: dict[str, Any] = dict(
        cpp_part_4_completed=1,
        business_statements=(
            {
                "business": {"gross_sales": "20000"},
                "business_vehicles_rows": (
                    {
                        "business_kilometres": "27000",
                        "fuel_and_oil": "3500",
                        "insurance": "1000",
                        "interest_days": "0",
                        "interest_payable": "1900",
                        "licence_and_registration": "100",
                        "maintenance_and_repairs": "500",
                        "passenger_vehicle": "0",
                        "total_kilometres": "30000",
                    },
                ),
            },
        ),
    )
    inputs.update(overrides)
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_kus_murrays_truck_allowable_motor_vehicle_expenses_are_6300() -> None:
    # Chart A: 27000 / 30000 x 7000 = 6300 (the truck is not a passenger vehicle, so its interest of
    # 1900 is not limited by Chart B), entered on line 9281.
    result = run_ku()
    assert result["ca/t2125"][0].get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("6300.00")


def test_return_kus_murrays_net_business_income_is_20000_less_6300() -> None:
    # Gross sales of 20000 (chosen) less the 6300 are the only expense: line 9368 is 6300.00
    # and line 9946 is 13700.00, which is T1 line 13500.
    result = run_ku()
    assert result["ca/t2125"][0].get(BUSINESS_TOTAL_EXPENSES).value == D("6300.00")
    assert result["ca/t2125"][0].get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("13700.00")
    assert result["ca-on/return"][0].get(BUSINESS_INCOME).value == D("13700.00")
