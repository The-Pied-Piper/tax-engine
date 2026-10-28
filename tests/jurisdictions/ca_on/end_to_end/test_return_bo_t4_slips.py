"""CA-ON 2025 end to end: Return BO, RC381 T4 slip totals above the required contributions.

Form RC381 Part 3 takes the contributions from the T4 slips (box 16 line 19, box 16A line 25, box
17 line 39 and box 17A line 45) and the pensionable earnings (box 26 outside Quebec line 1, box 26
in Quebec line 2) as separate inputs. The form prints no maximum for a box 16, 16A, 17 or 17A
total: its Required lines 21, 22, 42, 43 and 46 print the yearly maximums ($3,356.10, $678.00,
$396.00, $3,661.20), and a total above the required amount is the form's own case: line 69 is
positive, and Part 3a line 74 says "Enter the amount from line 69. Enter this amount (in dollars
and cents) on line 44800 of your return". Slip values flow as typed and the excess is refunded on
line 44800 (`ca/rc381_cpp_overpayment`).
"""

from __future__ import annotations

from tests.jurisdictions.ca_on.end_to_end.support import D
from tests.jurisdictions.ca_on.end_to_end.test_return_bo import results, return_bo


def test_a_box_17_of_1500_on_20000_of_quebec_earnings_refunds_the_excess() -> None:
    # Quebec only, box 26 20000, box 17 1500. Required base and first additional contributions are
    # 6.4% x 16500 = 1056.00, so the 444.00 above them is the line 44800 overpayment.
    one = return_bo(line_1="0", line_19="0", line_2="20000", line_39="1500")
    required = return_bo(line_1="0", line_19="0", line_2="20000", line_39="1056")

    assert results(one) == (D("891.00"), D("165.00"), D("444.00"))
    assert results(required)[2] == D("0")


def test_a_box_17_of_99999_flows_as_typed_and_is_refunded_above_the_required_amount() -> None:
    assert results(return_bo(line_39="99999")) == (D("3462.75"), D("665.00"), D("97656.25"))


def test_a_box_17a_of_300_on_5000_of_quebec_earnings_refunds_300() -> None:
    # Quebec only, box 26 5000, box 17 96.00 (the required 6.4% x 1500), box 17A 300 where line
    # 46 requires 0 on 5000 of earnings: line 69 is 300.00.
    worksheet = return_bo(line_1="0", line_19="0", line_2="5000", line_39="96", line_45="300")

    assert results(worksheet) == (D("81.00"), D("15.00"), D("300.00"))


def test_a_box_16a_of_300_on_5000_of_cpp_earnings_refunds_300() -> None:
    # CPP only, box 26 5000, box 16 89.25 (the required 5.95% x 1500), box 16A 300 where line 22
    # requires 0: the 300.00 is the line 44800 overpayment.
    worksheet = return_bo(
        line_1="5000", line_19="89.25", line_2="0", line_39="0", line_25="300", line_45="0"
    )

    assert results(worksheet) == (D("74.25"), D("15.00"), D("300.00"))


def test_one_quebec_slip_with_a_box_17_of_4500_is_accepted_above_the_required_maximums() -> None:
    # Quebec only, one slip at 81200: the Required lines 42 and 43 are at their maximums 3661.20
    # and 678.00 (4339.20 together), and line 46 requires 396.00 of box 17A. Box 17 of 4500 with
    # box 17A of 396.00 is 160.80 above line 44 and is refunded on line 44800.
    worksheet = return_bo(
        line_1="0",
        line_19="0",
        line_2="81200",
        line_39="4500",
        line_45="396",
        t4_qpp_slip_count=1,
    )

    assert results(worksheet) == (D("3661.20"), D("1074.00"), D("160.80"))


def test_a_box_17_of_4500_without_box_17a_is_a_shortfall_on_line_46_not_a_refund() -> None:
    # The same slip with no box 17A: line 69 is -235.20 (160.80 over on lines 42 and 43, 396.00
    # short on line 46), so Part 3b applies and the excess lifts line 22215 instead.
    worksheet = return_bo(
        line_1="0", line_19="0", line_2="81200", line_39="4500", t4_qpp_slip_count=1
    )

    assert results(worksheet) == (D("3661.20"), D("838.80"), D("0.00"))


def test_one_quebec_slip_with_a_box_17a_of_450_is_accepted_above_the_line_46_maximum() -> None:
    # Box 17 of 4500 and box 17A of 450 where line 46 requires 396.00: 160.80 + 54.00 = 214.80.
    worksheet = return_bo(
        line_1="0",
        line_19="0",
        line_2="81200",
        line_39="4500",
        line_45="450",
        t4_qpp_slip_count=1,
    )

    assert results(worksheet) == (D("3661.20"), D("1074.00"), D("214.80"))


def test_one_cpp_slip_with_an_rc381_box_16a_of_450_is_accepted_above_the_line_22_maximum() -> None:
    at_maximum = return_bo(line_1="81200", line_19="4034.10", line_25="396", t4_cpp_slip_count=1)
    above = return_bo(line_1="81200", line_19="4034.10", line_25="450", t4_cpp_slip_count=1)

    assert results(above)[2] - results(at_maximum)[2] == D("54.00")
