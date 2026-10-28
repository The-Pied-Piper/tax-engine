"""CA-ON 2025 end to end: Return JM, the T4 box 26 totals bounded by the count of slips.

Schedule 8 Part 3 line 1 and Form RC381 Part 3 lines 1 and 2 take one total over all of the
filer's T4 slips for box 26 but print the maximum for one slip: "(maximum $81,200 per slip)". The
form takes one total, so the filer also enters the number of slips with CPP pensionable earnings
and with QPP pensionable earnings (Umar, 2026-10-26, Q6), and box 26 is refused above the count
times $81,200. With a count of 0 any box 26 above 0 is refused. The limits are not form lines and
nothing on the return reads the checked totals.

Boxes 16, 16A, 17 and 17A are not checked against the count (Umar, 2026-10-27, issue 939): the
$3,356.10, $678.00, $396.00 and $3,661.20 maximums are printed on the Required lines, not marked
per slip, and a total above them is refunded on line 44800 by the form's own lines 24 and 29
(RC381 lines 69 and 74). One job at $81,200 with box 16 typed $4,840.00 files and refunds $805.90.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_OVERPAYMENT,
    T4_CPP_PENSIONABLE_EARNINGS_SLIP_CHECKED,
    T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT,
    T4_QPP_PENSIONABLE_EARNINGS_SLIP_CHECKED,
    T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D
from tests.jurisdictions.ca_on.end_to_end.test_return_bo import return_bo
from tests.jurisdictions.ca_on.end_to_end.test_return_y_cpp_t4_slips import return_y


def schedule_8_return(**overrides: Any) -> Worksheet:
    """Return Y's inputs on a Schedule 8 return with one job of 81200, as filed on one slip."""
    return return_y("81200", **overrides)


# CPP box 26, Schedule 8 line 1 and RC381 line 1.


def test_one_slip_with_81200_of_cpp_earnings_is_accepted() -> None:
    worksheet = schedule_8_return(t4_cpp_slip_count=1)

    assert worksheet.get(T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT).value == D("81200.00")
    assert worksheet.get(T4_CPP_PENSIONABLE_EARNINGS_SLIP_CHECKED).value == D("81200")


def test_one_slip_with_81200_01_of_cpp_earnings_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=r"t4_cpp_pensionable_earnings_outside_quebec"):
        return_y(
            "81200.01",
            t4_cpp_pensionable_earnings_outside_quebec="81200.01",
            t4_cpp_slip_count=1,
        )


def test_two_slips_with_162400_of_cpp_earnings_are_accepted() -> None:
    worksheet = return_y(
        "162400", t4_cpp_pensionable_earnings_outside_quebec="162400", t4_cpp_slip_count=2
    )

    assert worksheet.get(T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT).value == D("162400.00")
    assert worksheet.get(T4_CPP_PENSIONABLE_EARNINGS_SLIP_CHECKED).value == D("162400")


def test_cpp_earnings_with_no_cpp_slip_are_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=r"t4_cpp_pensionable_earnings_outside_quebec"):
        return_y("50000", t4_cpp_slip_count=0)


# Box 16, Schedule 8 line 8: no per-slip maximum is printed, so the total is not checked.


def test_a_box_16_of_4840_on_one_slip_is_accepted_and_refunded_above_the_required_amount() -> None:
    # One job at 81200 with box 16 typed 4840.00: the Required lines 11 and 12 are at their maxima
    # 3356.10 + 678.00 = 4034.10, so line 24 is 805.90 and Part 3a line 29 sends it to line 44800.
    worksheet = schedule_8_return(
        cpp_t4_base_and_first_additional_contributions="4840.00", t4_cpp_slip_count=1
    )

    assert worksheet.get(CPP_OVERPAYMENT).value == D("805.90")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3356.10")


def test_a_box_16_total_with_no_cpp_slip_count_is_accepted() -> None:
    # Only box 26 is checked against the count of slips; box 16 is read as typed.
    worksheet = compute_with_no_earnings(cpp_t4_base_and_first_additional_contributions="5.00")

    assert worksheet.get(CPP_OVERPAYMENT).value == D("5.00")


def compute_with_no_earnings(**overrides: Any) -> Worksheet:
    return return_y(
        "0",
        income_tax_deducted="0",
        t4_cpp_pensionable_earnings_outside_quebec="0",
        t4_cpp_slip_count=0,
        **overrides,
    )


# Box 16A, Schedule 8 line 21.


def test_a_box_16a_total_of_396_01_on_one_slip_is_accepted() -> None:
    worksheet = schedule_8_return(
        cpp_t4_second_additional_contributions="396.01", t4_cpp_slip_count=1
    )

    assert worksheet.get(CPP_OVERPAYMENT).value == D("0.01")


# Form RC381: box 26 in Quebec (line 2) is checked against the count of slips; boxes 16A, 17 and
# 17A (lines 25, 39 and 45) are read as typed.


def test_one_quebec_slip_with_81200_of_earnings_is_accepted_and_81200_01_refused() -> None:
    worksheet = return_bo(line_2="81200", line_39="2500", t4_qpp_slip_count=1, form="ca-on/return")

    assert worksheet.get(T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT).value == D("81200.00")
    assert worksheet.get(T4_QPP_PENSIONABLE_EARNINGS_SLIP_CHECKED).value == D("81200")
    with pytest.raises(InputAboveBoundError, match=r"t4_qpp_pensionable_earnings_in_quebec"):
        return_bo(line_2="81200.01", line_39="2500", t4_qpp_slip_count=1)
    two = return_bo(line_2="162400", line_39="2500", t4_qpp_slip_count=2, form="ca-on/return")
    assert two.get(T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT).value == D("162400.00")


def test_an_rc381_box_17_of_5_with_no_quebec_slip_count_is_accepted() -> None:
    worksheet = return_bo(line_2="0", line_39="5.00", t4_qpp_slip_count=0, form="ca-on/return")

    assert worksheet.get(T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT).value == D("0.00")


def test_the_cpp_and_qpp_counts_are_separate() -> None:
    # A Quebec slip is not an Ontario slip: with 1 CPP slip and no QPP slip, QPP earnings fail.
    with pytest.raises(InputAboveBoundError, match=r"t4_qpp_pensionable_earnings_in_quebec"):
        return_bo(line_1="30000", line_2="40000", t4_cpp_slip_count=1, t4_qpp_slip_count=0)
