"""CA-ON 2025 end to end: return hs, two fishing statements with the Part 9 equity lines."""

from __future__ import annotations

from collections.abc import Mapping

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FISH_CAPITAL_CONTRIBUTIONS,
    FISH_DRAWINGS,
    FISH_LIABILITIES,
    FISH_NET_INCOME_AFTER_ADJUSTMENTS,
    FISHING_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return HS's first T2121 is Return HL's business (fish products 40000, salt, bait and ice 10000 and
# fishing gear 15000, so net income 15000), with its Part 9 "Details of equity" lines: 125000.00 on
# line 9931 "Total business liabilities", 9000.00 on line 9932 "Drawings in the current year" and
# 25000.00 on line 9933 "Capital contributions in the current year". The second is a business that
# breaks even (fish products 30000, salt, bait and ice 10000 and fishing gear 20000, so net income
# 0), with its own lines: 48500.50, 3200.25 and 7500.00. All are starting amounts, taken as entered.
FIRST = {
    "fish_products": "40000",
    "salt_bait_and_ice": "10000",
    "fishing_gear": "15000",
    "vehicle_sales_tax_rate": "13",
    "liabilities": "125000.00",
    "drawings": "9000.00",
    "capital_contributions": "25000.00",
}
SECOND = {
    "fish_products": "30000",
    "salt_bait_and_ice": "10000",
    "fishing_gear": "20000",
    "vehicle_sales_tax_rate": "13",
    "liabilities": "48500.50",
    "drawings": "3200.25",
    "capital_contributions": "7500.00",
}
NO_LINES = {"liabilities": "0", "drawings": "0", "capital_contributions": "0"}

# One vehicle of the first statement, as in Return HL: business kilometres 0, so line 9281 is 0.
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


def run_hs(
    first: Mapping[str, str] = FIRST,
    second: Mapping[str, str] = SECOND,
) -> dict[str, tuple[Worksheet, ...]]:
    """Return HS's inputs, as in `returns/2025_return_hs.yaml`: a sole proprietor whose only
    activity is two fishing businesses, one T2121 statement each, for a full fiscal period (0 days
    entered); the first statement carries one vehicle, the second none."""
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        fish_statements=(
            {"fish": first, "fish_vehicles_rows": (VEHICLE,)},
            {"fish": second},
        ),
    )


def test_return_hs_first_statement_exports_its_part_9_equity_lines_unread() -> None:
    # Part 9 "9931 Total business liabilities" is the entered 125000.00, "9932 Drawings in the
    # current year" is 9000.00 and "9933 Capital contributions in the current year" is 25000.00.
    # Nothing earlier on the form computes them.
    first = run_hs()["ca/t2121"][0]

    assert first.get(FISH_LIABILITIES).value == D("125000.00")
    assert first.get(FISH_DRAWINGS).value == D("9000.00")
    assert first.get(FISH_CAPITAL_CONTRIBUTIONS).value == D("25000.00")


def test_return_hs_second_statement_exports_its_own_part_9_equity_lines_unread() -> None:
    # The second statement carries its own three lines: 48500.50, 3200.25 and 7500.00.
    second = run_hs()["ca/t2121"][1]

    assert second.get(FISH_LIABILITIES).value == D("48500.50")
    assert second.get(FISH_DRAWINGS).value == D("3200.25")
    assert second.get(FISH_CAPITAL_CONTRIBUTIONS).value == D("7500.00")


def test_the_part_9_equity_lines_change_no_fishing_income_or_total_income() -> None:
    # Net fishing income of each statement (line 9946) is 15000.00 and 0.00, and the return's
    # fishing income and total income 15000.00, with or without the three lines: none of them
    # enters a line of income.
    with_lines = run_hs()
    without_lines = run_hs({**FIRST, **NO_LINES}, {**SECOND, **NO_LINES})

    assert [
        each.get(FISH_NET_INCOME_AFTER_ADJUSTMENTS).value for each in with_lines["ca/t2121"]
    ] == [D("15000"), D("0")]
    worksheet = with_lines["ca-on/return"][0]
    assert worksheet.get(FISHING_INCOME).value == D("15000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("15000.00")
    assert (
        without_lines["ca-on/return"][0].get(FISHING_INCOME).value
        == worksheet.get(FISHING_INCOME).value
    )
    assert (
        without_lines["ca-on/return"][0].get(TOTAL_INCOME).value
        == worksheet.get(TOTAL_INCOME).value
    )
