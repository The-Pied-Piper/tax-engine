"""CA-ON 2025 end to end: return kv (Guide T4002's Heather)."""

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


def run_kv(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return KV's inputs, as in `returns/2025_return_kv.yaml`; `overrides` replace any of them."""
    inputs: dict[str, Any] = dict(
        cpp_part_4_completed=1,
        business_statements=(
            {
                "business": {"gross_sales": "20000"},
                "business_vehicles_rows": (
                    {
                        "business_kilometres": "20000",
                        "fuel_and_oil": "2000",
                        "insurance": "1900",
                        "interest_days": "365",
                        "interest_payable": "2200",
                        "licence_and_registration": "60",
                        "maintenance_and_repairs": "1000",
                        "total_kilometres": "25000",
                    },
                ),
            },
        ),
    )
    inputs.update(overrides)
    return run("0", (), "0", "0", "0", "0", "0", **inputs)


def test_return_kvs_heathers_allowable_motor_vehicle_expenses_are_5728() -> None:
    # Chart A: 20000 / 25000 x 7160 = 5728, the interest being the lesser of 2200 and 350 / 30
    # x 365, entered on line 9281.
    result = run_kv()
    assert result["ca/t2125"][0].get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("5728.00")


def test_return_kvs_heathers_net_business_income_is_20000_less_5728() -> None:
    # Gross sales of 20000 (chosen) less 5728: line 9368 is 5728.00 and line 9946 is 14272.00,
    # which is T1 line 13500.
    result = run_kv()
    assert result["ca/t2125"][0].get(BUSINESS_TOTAL_EXPENSES).value == D("5728.00")
    assert result["ca/t2125"][0].get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("14272.00")
    assert result["ca-on/return"][0].get(BUSINESS_INCOME).value == D("14272.00")
