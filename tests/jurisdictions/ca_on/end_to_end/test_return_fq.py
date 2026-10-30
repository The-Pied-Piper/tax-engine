"""CA-ON 2025 end to end: return fq."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    MOVING_DISTANCE_DIFFERENCE,
    MOVING_EXPENSES_CLAIM,
    MOVING_EXPENSES_DEDUCTION,
    MOVING_UNUSED_EXPENSES,
    MOVING_UNUSED_EXPENSES_BEFORE_TEST,
    NET_INCOME_BEFORE_ADJUSTMENTS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# The three moves of Return FQ, as the return's inputs give them (see
# `returns/2025_return_fq.yaml`).
MOVE_A = {
    "old_home_distance": "70",
    "new_home_distance": "40",
    "transportation_and_storage": "5000",
    "old_home_maintenance": "5000",
    "net_eligible_income": "2000",
}
MOVE_B = {
    "old_home_distance": "150",
    "new_home_distance": "110",
    "transportation_and_storage": "800",
    "old_home_maintenance": "1250",
    "net_eligible_income": "10000",
}
MOVE_C = {
    "old_home_distance": "20",
    "new_home_distance": "60",
    "transportation_and_storage": "3000",
    "net_eligible_income": "5000",
}


def return_fq(*moves: dict[str, Any]) -> dict[str, tuple[Worksheet, ...]]:
    """Return FQ's worksheets for the moves given (all three by default), the employment income of
    10,000 being the income lines that each move's net eligible income (line 28) is at most."""
    return run("10000", (), "0", "0", "0", "0", "0", moving_moves=moves or (MOVE_A, MOVE_B, MOVE_C))


def test_a_difference_of_30_kilometres_gives_a_claim_of_0() -> None:
    # Line 3 is 30, under the 40 kilometres of Part 2, so the move claims nothing although line 29
    # would be 2,000.00 and line 30 before the test would be 8,000.00.
    (first, _, _) = return_fq()["ca/t1_m"]

    assert first.get(MOVING_DISTANCE_DIFFERENCE).value == D("30")
    assert first.get(MOVING_EXPENSES_CLAIM).value == D("0.00")
    assert first.get(MOVING_UNUSED_EXPENSES_BEFORE_TEST).value == D("8000.00")
    assert first.get(MOVING_UNUSED_EXPENSES).value == D("0.00")


def test_a_difference_of_exactly_40_kilometres_gives_a_claim_of_2050() -> None:
    # Line 3 is exactly 40, which is "at least 40", so the move claims line 29, 2,050.00.
    (_, second, _) = return_fq()["ca/t1_m"]

    assert second.get(MOVING_DISTANCE_DIFFERENCE).value == D("40")
    assert second.get(MOVING_EXPENSES_CLAIM).value == D("2050.00")


def test_a_negative_difference_gives_a_claim_of_0() -> None:
    # Line 3 is -40, under 40 kilometres, so the move claims nothing although line 29 would be
    # 3,000.00.
    (_, _, third) = return_fq()["ca/t1_m"]

    assert third.get(MOVING_DISTANCE_DIFFERENCE).value == D("-40")
    assert third.get(MOVING_EXPENSES_CLAIM).value == D("0.00")


def test_the_three_moves_give_line_21900_of_2050() -> None:
    worksheet = return_fq()["ca-on/return"][0]

    assert worksheet.get(MOVING_EXPENSES_DEDUCTION).value == D("2050.00")


def test_line_23300_and_line_23400_take_line_21900_and_the_enhanced_cpp() -> None:
    # Line 23300 "Add lines 35 to 52." is line 21900, 2,050.00, and the enhanced CPP contributions
    # of line 22215 on the 10,000.00 of employment income, 65.00 (1% of 6,500.00), so line 23400
    # "Line 34 minus line 53" is 10,000.00 less 2,115.00. Engine output, to be confirmed.
    worksheet = return_fq()["ca-on/return"][0]

    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("2115.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("7885.00")
