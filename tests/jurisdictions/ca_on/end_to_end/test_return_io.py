"""CA-ON 2025 end to end: return io (returns/2025_return_io.yaml)."""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FISH_EXPENSES_SUBTOTAL,
    FISH_INSURANCE_RECOVERY,
    FISH_NET_INCOME_BEFORE_ADJUSTMENTS,
    FISH_REPAIRS_TOTAL,
    FISH_REPAIRS_YOUR_COST,
    FISHING_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return IO's T2121: fish products of 40000 (amount 3A), expenses of 25000 (salt, bait and ice 10000
# on line 9138, and fishing gear 15000 on line 9136), and repairs of 1000 on the fishing boat
# (amount 1) with an insurance recovery of 400 (amount 5), so your cost (line 8963) is 600.
FISH = {
    "fish_products": "40000",
    "salt_bait_and_ice": "10000",
    "fishing_gear": "15000",
    "repairs_fishing_boat": "1000",
    "insurance_recovery": "400",
    "vehicle_sales_tax_rate": "13",
}

# One vehicle of the statement, a record of `ca/business_vehicles`: business kilometres 0, so line
# 9281 is 0, as in Return BD.
VEHICLE = {
    "business_kilometres": "0",
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


def run_io(**amounts: str) -> dict[str, tuple[Worksheet, ...]]:
    """Return IO's inputs, as in `returns/2025_return_io.yaml`, with the T2121 amounts `amounts`
    replaced: a sole proprietor whose only activity is a fishing business, one T2121 statement.
    """
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        fish_statements=({"fish": {**FISH, **amounts}, "fish_vehicles_rows": (VEHICLE,)},),
    )


def statement_io() -> Worksheet:
    """The worksheet of Return IO's one T2121 statement: its lines, as the form computes them."""
    return run_io()["ca/t2121"][0]


# --- your cost on the repairs (T2121 Part 4, amounts 4 and 5) -----------------------------------


def test_return_ios_repairs_total_1000_and_your_cost_600() -> None:
    # Repairs and maintenance: the fishing boat 1000 is amount 1, so the total of amounts 1 to 3
    # (amount 4) is 1000. The insurance recovery (amount 5) is 400, so your cost (line 8963, amount
    # 4 minus amount 5) is 1000 - 400 = 600.
    statement = statement_io()

    assert statement.get(FISH_REPAIRS_TOTAL).value == D("1000")
    assert statement.get(FISH_REPAIRS_YOUR_COST).value == D("600")


def test_return_ios_expenses_are_25600_and_net_income_before_adjustments_14400() -> None:
    # Amount 4Q is 10000 + 15000 + 600 (your cost) = 25600, so line 9369 is 40000 - 25600 = 14400.
    statement = statement_io()

    assert statement.get(FISH_EXPENSES_SUBTOTAL).value == D("25600")
    assert statement.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("14400")


def test_return_io_net_fishing_income_is_14400_on_t1_line_14300() -> None:
    # Line 9946 is 14400 and T1 line 14300 is the same, so line 27 is 14400 with no other income.
    result = run_io()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2121"][0].get(FISHING_INCOME).value == D("14400")
    assert worksheet.get(FISHING_INCOME).value == D("14400")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("14400")


# --- an insurance recovery above the repairs is an input error (T2121 Part 4, amount 5) ---------
# No printed bound limits an insurance recovery to the repairs: Return IO's repairs total is
# 1000, so a recovery of 5000 is not refused, and your cost is 1000 less 5000 = -4000 as printed.


def test_return_io_insurance_recovery_above_repairs_is_not_refused() -> None:
    worksheet = run_io(insurance_recovery="5000")["ca/t2121"][0]

    assert worksheet.get(FISH_REPAIRS_YOUR_COST).value == D("-4000")
    assert worksheet.get(FISH_EXPENSES_SUBTOTAL).value == D("21000")


def test_return_io_insurance_recovery_with_no_repairs_is_not_refused() -> None:
    # No repairs: your cost is 0 less 400 = -400 as printed, so the expenses are 25000 less 400.
    worksheet = run_io(repairs_fishing_boat="0", insurance_recovery="400")["ca/t2121"][0]

    assert worksheet.get(FISH_REPAIRS_YOUR_COST).value == D("-400")
    assert worksheet.get(FISH_EXPENSES_SUBTOTAL).value == D("24600")


def test_return_io_insurance_recovery_equal_to_repairs_is_accepted() -> None:
    # The recovery 1000 equals the repairs 1000: accepted, the checked recovery is 1000, and your
    # cost is 0.
    statement = run_io(insurance_recovery="1000")["ca/t2121"][0]

    assert statement.get(FISH_INSURANCE_RECOVERY).value == D("1000")
    assert statement.get(FISH_REPAIRS_YOUR_COST).value == D("0")
