"""CA-ON 2025 end to end: return dk."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    MOVING_EXPENSES_CLAIM,
    MOVING_EXPENSES_DEDUCTION,
    MOVING_NET_ELIGIBLE_INCOME_CHECKED,
    MOVING_UNUSED_EXPENSES,
    NET_INCOME_BEFORE_ADJUSTMENTS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# The two moves of Return DK, as the return's inputs give them (see `returns/2025_return_dk.yaml`).
FIRST_MOVE = {
    "old_home_distance": "100",
    "new_home_distance": "10",
    "transportation_and_storage": "2000",
    "travel_expenses": "500",
    "net_eligible_income": "40000",
}
SECOND_MOVE = {
    "old_home_distance": "200",
    "new_home_distance": "50",
    "transportation_and_storage": "1000",
    "net_eligible_income": "40000",
}


def return_dk(*moves: dict[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Return DK's worksheets for the moves given (both moves by default), the employment income
    of 40,000 being the net eligible income of each move."""
    return run(
        "40000", (), "0", "0", "0", "0", "0", moving_moves=moves or (FIRST_MOVE, SECOND_MOVE)
    )


def test_the_first_move_gives_line_29_of_2500_and_line_30_of_0() -> None:
    (first, _) = return_dk()["ca/t1_m"]

    assert first.get(MOVING_EXPENSES_CLAIM).value == D("2500.00")
    assert first.get(MOVING_UNUSED_EXPENSES).value == D("0.00")


def test_the_second_move_gives_line_29_of_1000() -> None:
    (_, second) = return_dk()["ca/t1_m"]

    assert second.get(MOVING_EXPENSES_CLAIM).value == D("1000.00")


def test_the_two_moves_give_line_21900_of_3500() -> None:
    worksheet = return_dk()["ca-on/return"][0]

    assert worksheet.get(MOVING_EXPENSES_DEDUCTION).value == D("3500.00")


def test_line_23300_and_line_23400_take_line_21900_and_the_enhanced_cpp() -> None:
    # Line 23300 "Add lines 35 to 52." is line 21900, 3,500.00, and the enhanced CPP of
    # line 22215, 365.00, so line 23400 "Line 34 minus line 53" is 40,000.00 less 3,865.00.
    worksheet = return_dk()["ca-on/return"][0]

    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("3865.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("36135.00")


def test_the_first_move_alone_gives_line_21900_of_2500() -> None:
    worksheet = return_dk(FIRST_MOVE)["ca-on/return"][0]

    assert worksheet.get(MOVING_EXPENSES_DEDUCTION).value == D("2500.00")


def test_each_move_line_28_of_40000_is_at_the_employment_income_and_is_accepted() -> None:
    # Each move's line 28 of 40,000 is at most the return's 40,000 of employment income (line
    # 10100), so it is accepted as entered: the checked amount of each move is 40,000.
    (first, second) = return_dk()["ca/t1_m"]

    assert first.get(MOVING_NET_ELIGIBLE_INCOME_CHECKED).value == D("40000")
    assert second.get(MOVING_NET_ELIGIBLE_INCOME_CHECKED).value == D("40000")
