"""CA-ON 2025 end to end: return fp."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    MOVING_EXPENSES_CLAIM,
    MOVING_EXPENSES_DEDUCTION,
    MOVING_NET_EXPENSES,
    MOVING_OLD_HOME_MAINTENANCE_CHECKED,
    MOVING_UNUSED_EXPENSES,
    NET_INCOME_BEFORE_ADJUSTMENTS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# The two moves of Return FP, as the return's inputs give them (see `returns/2025_return_fp.yaml`).
FIRST_MOVE = {
    "old_home_distance": "150",
    "new_home_distance": "60",
    "transportation_and_storage": "3200",
    "travel_expenses": "600.50",
    "accommodation_expenses": "400.25",
    "meal_expenses": "250.75",
    "temporary_lodging": "300",
    "temporary_meals": "150.40",
    "lease_cancellation": "1200",
    "incidental_costs": "380.60",
    "old_home_maintenance": "5000",
    "selling_commission": "12000",
    "selling_legal_fees": "1500",
    "selling_advertising": "800",
    "selling_other_costs": "350",
    "buying_legal_fees": "1800",
    "buying_taxes": "2200",
    "reimbursement": "2500",
    "net_eligible_income": "18000",
}
SECOND_MOVE = {
    "old_home_distance": "80",
    "new_home_distance": "30",
    "transportation_and_storage": "1000",
    "reimbursement": "1500",
    "net_eligible_income": "20000",
}


def return_fp(*moves: dict[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Return FP's worksheets for the moves given (both moves by default), the employment income of
    20,000 being the income lines that each move's net eligible income (line 28) is at most."""
    return run(
        "20000", (), "0", "0", "0", "0", "0", moving_moves=moves or (FIRST_MOVE, SECOND_MOVE)
    )


def test_the_first_move_gives_line_29_of_18000_and_line_30_of_9632_50() -> None:
    (first, _) = return_fp()["ca/t1_m"]

    assert first.get(MOVING_EXPENSES_CLAIM).value == D("18000.00")
    assert first.get(MOVING_UNUSED_EXPENSES).value == D("9632.50")


def test_the_old_home_maintenance_of_5000_is_taken_at_the_maximum() -> None:
    (first, _) = return_fp()["ca/t1_m"]

    assert first.get(MOVING_OLD_HOME_MAINTENANCE_CHECKED).value == D("5000.00")


def test_the_old_home_maintenance_of_6200_is_refused_not_capped_at_5000() -> None:
    # Line 14 "(maximum $5,000)": 6,200 is above the maximum, so it is an input error.
    with pytest.raises(InputAboveBoundError, match="moving_old_home_maintenance_cap 5000"):
        return_fp({**FIRST_MOVE, "old_home_maintenance": "6200"})


def test_a_reimbursement_above_line_24_gives_line_26_of_0() -> None:
    # Line 24 of the second move is 1,000.00 and the reimbursement 1,500.00, so line 26 is
    # "0" (if negative, enter "0"), and line 29 and line 30 of that move are 0.00.
    (_, second) = return_fp()["ca/t1_m"]

    assert second.get(MOVING_NET_EXPENSES).value == D("0.00")
    assert second.get(MOVING_EXPENSES_CLAIM).value == D("0.00")
    assert second.get(MOVING_UNUSED_EXPENSES).value == D("0.00")


def test_the_two_moves_give_line_21900_of_18000() -> None:
    worksheet = return_fp()["ca-on/return"][0]

    assert worksheet.get(MOVING_EXPENSES_DEDUCTION).value == D("18000.00")


def test_line_23300_and_line_23400_take_line_21900_and_the_enhanced_cpp() -> None:
    # Line 23300 "Add lines 35 to 52." is line 21900, 18,000.00, and the enhanced CPP contributions
    # of line 22215 on the 20,000.00 of employment income, 165.00 (1% of 16,500.00), so line 23400
    # "Line 34 minus line 53" is 20,000.00 less 18,165.00. Engine output, to be confirmed.
    worksheet = return_fp()["ca-on/return"][0]

    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("18165.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("1835.00")
