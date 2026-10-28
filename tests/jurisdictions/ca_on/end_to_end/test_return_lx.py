"""CA-ON 2025 end to end: return lx (a leased farm truck on a Form T2042 and a leased fishing truck
on a Form T2121, neither a passenger vehicle, with lease charges above Chart C's limit)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FARM_MOTOR_VEHICLE_EXPENSES,
    FARM_NET_INCOME_AFTER_ADJUSTMENTS,
    FARM_TOTAL_EXPENSES,
    FARMING_INCOME,
    FISH_MOTOR_VEHICLE_EXPENSES,
    FISH_NET_INCOME_AFTER_ADJUSTMENTS,
    FISH_TOTAL_EXPENSES,
    NET_FARMING_INCOME,
    NET_FISHING_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

FARM_TRUCK = {
    "business_kilometres": "16000",
    "fuel_and_oil": "2000",
    "insurance": "1200",
    "lease_charges": "20000",
    "lease_days": "365",
    "licence_and_registration": "150",
    "list_price": "60000",
    "maintenance_and_repairs": "450",
    "passenger_vehicle": "0",
    "total_kilometres": "20000",
}
FISH_TRUCK = {
    "business_kilometres": "9000",
    "fuel_and_oil": "1600",
    "insurance": "800",
    "lease_charges": "18000",
    "lease_days": "365",
    "licence_and_registration": "100",
    "list_price": "60000",
    "maintenance_and_repairs": "500",
    "passenger_vehicle": "0",
    "total_kilometres": "12000",
}


def run_lx(
    farm_truck: dict[str, str] | None = None, fish_truck: dict[str, str] | None = None
) -> dict[str, tuple[Worksheet, ...]]:
    """Return LX's inputs, as in `returns/2025_return_lx.yaml`; `farm_truck` and `fish_truck`
    replace any of the vehicles' amounts."""
    arguments: dict[str, Any] = {
        "farm_statements": (
            {
                "farm": {"wheat": "50000", "vehicle_sales_tax_rate": "13"},
                "farm_vehicles_rows": ({**FARM_TRUCK, **(farm_truck or {})},),
            },
        ),
        "fish_statements": (
            {
                "fish": {"fish_products": "40000", "vehicle_sales_tax_rate": "13"},
                "fish_vehicles_rows": ({**FISH_TRUCK, **(fish_truck or {})},),
            },
        ),
    }
    return run("0", (), "0", "0", "0", "0", "0", **arguments)


def test_return_lxs_farm_truck_lease_charges_of_20000_are_not_limited_by_chart_c() -> None:
    # T2042 Chart A: amount 12 is 2000 + 20000 + 1200 + 150 + 450 = 23800 and amount 13 is
    # 16000 / 20000 x 23800 = 19040, on line 9819.
    result = run_lx()
    assert result["ca/t2042"][0].get(FARM_MOTOR_VEHICLE_EXPENSES).value == D("19040.00")
    assert result["ca/t2042"][0].get(FARM_TOTAL_EXPENSES).value == D("19040.00")
    assert result["ca/t2042"][0].get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value == D("30960.00")
    assert result["ca/t2042"][0].get(FARMING_INCOME).value == D("30960.00")


def test_return_lxs_fishing_truck_lease_charges_of_18000_are_not_limited_by_chart_c() -> None:
    # T2121 Chart A: amount 12 is 1600 + 18000 + 800 + 100 + 500 = 21000 and amount 13 is
    # 9000 / 12000 x 21000 = 15750, on line 9281.
    result = run_lx()
    assert result["ca/t2121"][0].get(FISH_MOTOR_VEHICLE_EXPENSES).value == D("15750.00")
    assert result["ca/t2121"][0].get(FISH_TOTAL_EXPENSES).value == D("15750.00")
    assert result["ca/t2121"][0].get(FISH_NET_INCOME_AFTER_ADJUSTMENTS).value == D("24250.00")


def test_return_lxs_total_income_is_the_net_farming_and_net_fishing_income() -> None:
    worksheet = run_lx()["ca-on/return"][0]
    assert worksheet.get(NET_FARMING_INCOME).value == D("30960.00")
    assert worksheet.get(NET_FISHING_INCOME).value == D("24250.00")
    assert worksheet.get(TOTAL_INCOME).value == D("55210.00")


def test_the_same_farm_truck_as_a_passenger_vehicle_is_limited_to_15123_17_of_leasing() -> None:
    # Chart C at 13%: line 25 is (1100 + 143) x 365 / 30 = 15123.17 and line 27 is
    # (38000 + 4940) x 20000 / 51000 = 16839.22, so line 28 is 15123.17; Chart A: 16000 / 20000 x
    # (2000 + 15123.17 + 1200 + 150 + 450 = 18923.17) = 15138.54 (rounded once at amount 13).
    result = run_lx(farm_truck={"passenger_vehicle": "1"})
    assert result["ca/t2042"][0].get(FARM_MOTOR_VEHICLE_EXPENSES).value == D("15138.54")


def test_the_same_fishing_truck_as_a_passenger_vehicle_is_limited_to_15123_17_of_leasing() -> None:
    # Chart C: line 27 is (38000 + 4940) x 18000 / 51000 = 15155.29, more than line 26's
    # 15123.17, so line 28 is 15123.17; Chart A: 9000 / 12000 x
    # (1600 + 15123.17 + 800 + 100 + 500 = 18123.17) = 13592.38 (rounded once at amount 13).
    result = run_lx(fish_truck={"passenger_vehicle": "1"})
    assert result["ca/t2121"][0].get(FISH_MOTOR_VEHICLE_EXPENSES).value == D("13592.38")
