"""CA-ON 2025 end to end: return lz (Guide T4002's Meadow example, a leased passenger car on a Form
T2125, with Chart C kept to the cent)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    BUSINESS_MOTOR_VEHICLE_EXPENSES,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_TOTAL_EXPENSES,
)
from tax_calculator.jurisdictions.ca.trace import BusinessVehicleLine
from tests.jurisdictions.ca_on.end_to_end.support import D, run

CAR = {
    "business_kilometres": "10000",
    "lease_charges": "3000",
    "lease_days": "184",
    "list_price": "33000",
    "passenger_vehicle": "1",
    "total_kilometres": "10000",
}


def run_lz(**car: str) -> dict[str, tuple[Worksheet, ...]]:
    """Return LZ's inputs, as in `returns/2025_return_lz.yaml`; `car` replaces any of the vehicle's
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


def test_return_lzs_meadow_chart_c_gives_2999_99_where_the_guide_prints_3000() -> None:
    # Chart C at 13%: line 24 is ($44,706 + $5,811.78) x 85% = $42,940.11 (the Guide, rounding to
    # the dollar, prints $42,940), line 25 is ($1,100 + $143) x 184 / 30 = $7,623.73 (Guide
    # $7,624), line 26 is line 25 less line 21 ($0), line 27 is ($38,000 + $4,940) x $3,000 /
    # $42,940.11 = $2,999.99 (Guide $3,000), so line 28 is the lesser, $2,999.99. Chart A:
    # 10000 / 10000 x $2,999.99.
    worksheet = run_lz()["ca/t2125"][0]

    (vehicle,) = [line for line in worksheet.trace if isinstance(line, BusinessVehicleLine)]
    assert vehicle.line_28 == D("2999.99")
    assert vehicle.line_12 == D("2999.99")
    assert vehicle.line_13 == D("2999.99")
    assert vehicle.line_16 == D("2999.99")
    assert worksheet.get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("2999.99")


def test_return_lzs_net_business_income_is_40000_less_2999_99() -> None:
    result = run_lz()
    assert result["ca/t2125"][0].get(BUSINESS_TOTAL_EXPENSES).value == D("2999.99")
    assert result["ca/t2125"][0].get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("37000.01")
    assert result["ca-on/return"][0].get(BUSINESS_INCOME).value == D("37000.01")


def test_return_lzs_line_25_is_7623_73_where_the_guide_prints_7624() -> None:
    # With $10,000 of lease charges line 27 is ($38,000 + $4,940) x $10,000 / $42,940.11 =
    # $9,999.97, above line 26, so line 28 is line 26: ($1,100 + $143) x 184 / 30 = $7,623.73
    # (Guide $7,624).
    worksheet = run_lz(lease_charges="10000")["ca/t2125"][0]
    (vehicle,) = [line for line in worksheet.trace if isinstance(line, BusinessVehicleLine)]
    assert vehicle.line_28 == D("7623.73")
