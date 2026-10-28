"""CA-ON 2025 end to end: return y, T4 slip CPP totals above the required contributions.

Schedule 8 Part 3 takes the CPP contributions from the T4 slips (box 16, line 8, and box 16A, line
21) and the pensionable earnings (box 26, line 1) as separate inputs. The form prints no maximum
for box 16 or box 16A: its lines 11, 12 and 22 print the required contributions ("maximum
$3,356.10", "maximum $678.00", "maximum $396.00"), a yearly figure and not marked per slip. A slip
total above the required amount is the form's own case: line 24 is positive, and Part 3a line 29
says "Enter the amount from line 24 ... on line 44800 of your return". Slip values flow as typed;
lines 30800 and 22215 stay at the required amounts and the excess is refunded on line 44800.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_OVERPAYMENT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_y(employment_income: str = "60000", **overrides: Any) -> Worksheet:
    """Return Y's inputs, as in `returns/2025_return_y.yaml`, with the T4 slip amounts in
    `overrides` (box 16, box 16A); box 26 is the employment income, as the return gives it."""
    inputs: dict[str, Any] = {
        "dependent_children": 1,
        "eligible_dependants": 1,
        "cwb_eligible_dependants": 1,
        "child_care_expenses_paid": "6000",
        "children_seven_to_sixteen": 1,
        "income_tax_deducted": "8000",
        "care_supporting_persons_adjusted_income": "30000",
    }
    return compute(employment_income, (), "0", "0", "10800", "0", "0", **{**inputs, **overrides})


def lines(worksheet: Worksheet) -> tuple[Any, Any, Any]:
    """T1 lines 30800, 22215 and 44800 of the worksheet."""
    return (
        worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value,
        worksheet.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value,
        worksheet.get(CPP_OVERPAYMENT).value,
    )


def test_return_ys_box_16_of_3361_75_is_the_required_amount_and_has_no_overpayment() -> None:
    # Return Y as filed: box 16 3361.75 is the required base and first additional contributions on
    # 60000, so line 24 is 0 and nothing is refunded.
    assert lines(return_y()) == (D("2796.75"), D("565.00"), D("0.00"))


def test_a_box_16_of_1500_on_20000_of_earnings_files_and_refunds_the_excess() -> None:
    # Box 26 20000, box 16 1500 (the employer over-deducted). Schedule 8: line 7 16500, line 11
    # 816.75, line 12 165.00, line 9 1247.90, line 10 252.10, line 20 and line 24 518.25, and
    # line 29 sends it to line 44800.
    worksheet = return_y(
        "20000", income_tax_deducted="1000", cpp_t4_base_and_first_additional_contributions="1500"
    )

    assert lines(worksheet) == (D("816.75"), D("165.00"), D("518.25"))


def test_a_box_16_of_99999_on_60000_of_earnings_flows_as_typed() -> None:
    # A slip that really shows 99999: the required 3361.75 is claimed on lines 30800 and 22215
    # and the rest, 96637.25, is the line 44800 overpayment.
    worksheet = return_y(cpp_t4_base_and_first_additional_contributions="99999")

    assert lines(worksheet) == (D("2796.75"), D("565.00"), D("96637.25"))


def test_a_box_16a_of_300_on_5000_of_earnings_refunds_the_second_additional_excess() -> None:
    # Box 26 5000, box 16 89.25, box 16A 300: line 4 is 0, so line 22 is 0 and line 23 and line 24
    # are 300.00, the line 44800 overpayment.
    worksheet = return_y(
        "5000",
        income_tax_deducted="100",
        cpp_t4_base_and_first_additional_contributions="89.25",
        cpp_t4_second_additional_contributions="300",
    )

    assert lines(worksheet) == (D("74.25"), D("15.00"), D("300.00"))


def test_one_slip_with_a_box_16_of_4500_is_accepted_above_the_required_maximums() -> None:
    # One slip at 81200: the required lines 11 and 12 are at their maxima 3356.10 and 678.00
    # (4034.10 together). Box 16 4500 is 465.90 above them: line 16 387.60, line 19 78.30.
    worksheet = return_y(
        "81200",
        income_tax_deducted="1000",
        cpp_t4_base_and_first_additional_contributions="4500",
        t4_cpp_slip_count=1,
    )

    assert lines(worksheet) == (D("3356.10"), D("1074.00"), D("465.90"))


def test_one_slip_with_a_box_16a_of_450_is_accepted_above_the_line_22_maximum() -> None:
    # Line 22 is at its maximum 396.00 on 81200, so box 16A 450 leaves 54.00 on line 44800.
    worksheet = return_y(
        "81200",
        income_tax_deducted="1000",
        cpp_t4_second_additional_contributions="450",
        t4_cpp_slip_count=1,
    )

    assert lines(worksheet) == (D("3356.10"), D("1074.00"), D("54.00"))
