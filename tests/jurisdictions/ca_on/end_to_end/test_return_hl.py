"""CA-ON 2025 end to end: return hl."""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FISH_LAND_ADDITIONS,
    FISH_LAND_DISPOSITIONS,
    FISH_NET_INCOME_AFTER_ADJUSTMENTS,
    FISH_NET_INCOME_BEFORE_ADJUSTMENTS,
    FISHING_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return HL's T2121 is Return BD's (fish products 40000, salt, bait and ice 10000 and fishing gear
# 15000, so net income 15000), with Area F: the land lines are chosen figures, 21500.00 on line 9923
# "Total cost of all land additions in the year" and 8200.00 on line 9924 "Total proceeds from all
# land dispositions in the year". Both are starting amounts, taken as entered.
FISH = {
    "fish_products": "40000",
    "salt_bait_and_ice": "10000",
    "fishing_gear": "15000",
    "vehicle_sales_tax_rate": "13",
    "land_additions": "21500.00",
    "land_dispositions": "8200.00",
}

# One vehicle of the statement, as in Return BD: the amounts of Charts A to C, with business
# kilometres 0, so line 9281 is 0 and changes no fishing line.
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


def run_hl(changes: dict[str, str] | None = None) -> dict[str, tuple[Worksheet, ...]]:
    """Return HL's inputs, as in `returns/2025_return_hl.yaml`: a sole proprietor whose only
    activity is a fishing business, one T2121 statement for it (as Return BD), with the land lines
    of Area F on the statement, for a full fiscal period (0 days entered)."""
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        fish_statements=({"fish": {**FISH, **(changes or {})}, "fish_vehicles_rows": (VEHICLE,)},),
    )


def test_return_hls_land_additions_are_21500_on_line_9923_and_8200_on_line_9924() -> None:
    # Area F "Line 9923: Total cost of all land additions in the year" is the entered 21500.00 and
    # "Line 9924: Total proceeds from all land dispositions in the year" is the entered 8200.00.
    # Nothing earlier on the form computes either line, so both are carried through unchanged.
    statement = run_hl()["ca/t2121"][0]

    assert statement.get(FISH_LAND_ADDITIONS).value == D("21500.00")
    assert statement.get(FISH_LAND_DISPOSITIONS).value == D("8200.00")


def test_the_land_lines_change_no_fishing_income_or_t1_line_14300() -> None:
    # Net fishing income (line 9946, T1 line 14300) is 15000.00 with or without the land lines:
    # neither line enters the expenses, the gross or the CCA claim.
    with_land = run_hl()
    without_land = run_hl({"land_additions": "0", "land_dispositions": "0"})
    statement = with_land["ca/t2121"][0]
    worksheet = with_land["ca-on/return"][0]

    assert statement.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("15000.00")
    assert statement.get(FISH_NET_INCOME_AFTER_ADJUSTMENTS).value == D("15000.00")
    assert worksheet.get(FISHING_INCOME).value == D("15000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("15000.00")
    assert (
        without_land["ca-on/return"][0].get(FISHING_INCOME).value
        == worksheet.get(FISHING_INCOME).value
    )
    assert (
        without_land["ca-on/return"][0].get(TOTAL_INCOME).value == worksheet.get(TOTAL_INCOME).value
    )
