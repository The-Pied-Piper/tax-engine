"""CA-ON 2025 end to end: return dx (Schedule 8 line 1 is the T4 box 26 total, not the employment
income: pay of 60000, box 26 of 56500 and box 16 of 3361.75, with one Schedule 8)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_BASE_CONTRIBUTIONS,
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_LINE_24_POSITIVE,
    CPP_OVERPAYMENT,
    CPP_PART_3_LINE_2,
    CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    NET_INCOME,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_dx(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return DX's inputs (`returns/2025_return_dx.yaml`): employment income of 60000 on one T4
    whose box 26 is 56500 and whose box 16 is 3361.75 (the contributions on the 60000 of box 14
    pay, exactly 5.95% of box 26), with 12 months for CPP and QPP, and no other income. The
    return carries one Schedule 8 and no Form RC381."""
    arguments: dict[str, Any] = {
        "cpp_months": 12,
        "qpp_months": 12,
        "t4_cpp_pensionable_earnings_outside_quebec": "56500",
        "cpp_t4_base_and_first_additional_contributions": "3361.75",
        "income_tax_deducted": "12000",
        "schedule_8_copies": 1,
        "rc381_copies": 0,
    }
    return run("60000", (), "0", "0", "0", "0", "0", **{**arguments, **overrides})


def schedule_8_dx() -> Worksheet:
    (schedule_8,) = run_dx()["ca/schedule_8"]
    return schedule_8


def return_dx() -> Worksheet:
    (worksheet,) = run_dx()["ca-on/return"]
    return worksheet


def test_return_dx_schedule_8_line_2_is_the_box_26_total_not_the_employment_income() -> None:
    # Schedule 8 Part 3 line 2 is the lesser of line D (81200) and line 1, the box 26 total of
    # 56500, not the employment income of 60000.
    assert schedule_8_dx().get(CPP_PART_3_LINE_2).value == D("56500")


def test_return_dx_schedule_8_line_11_is_4_95_percent_of_the_box_26_band() -> None:
    # Line 7 is 56500 less the 3500 exemption, 53000; line 11 is 53000 x 4.95% = 2623.50. On the
    # employment income it would be 56500 x 4.95% = 2796.75.
    assert schedule_8_dx().get(CPP_BASE_CONTRIBUTIONS).value == D("2623.50")


def test_return_dx_schedule_8_line_12_is_1_percent_of_the_box_26_band() -> None:
    # Line 12 is 53000 x 1% = 530.00; on the employment income it would be 565.00.
    assert schedule_8_dx().get(CPP_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("530.00")


def test_return_dx_schedule_8_line_13_is_the_required_base_and_first_additional_contributions() -> (
    None
):
    # Line 13 is line 11 plus line 12: 2623.50 + 530.00 = 3153.50.
    assert schedule_8_dx().get(CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D(
        "3153.50"
    )


def test_return_dx_schedule_8_line_24_is_positive_so_part_3a_applies() -> None:
    # Line 24 is line 20 (208.25: the base 173.25 and the first additional 35.00 that box 16 of
    # 3361.75 exceeds the required contributions by) plus line 23 (0): positive, so Part 3a.
    assert schedule_8_dx().get(CPP_LINE_24_POSITIVE).value == 1


def test_return_dx_t1_line_30800_is_the_required_base_contributions_on_box_26() -> None:
    assert return_dx().get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2623.50")


def test_return_dx_t1_line_22215_is_the_required_first_additional_contributions_on_box_26() -> None:
    assert return_dx().get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("530.00")


def test_return_dx_t1_line_44800_is_the_overpayment_of_box_16_over_the_box_26_contributions() -> (
    None
):
    # Line 29 of Part 3a is line 24, 208.25: the box 16 total less the required contributions.
    assert return_dx().get(CPP_OVERPAYMENT).value == D("208.25")


def test_return_dx_the_enhanced_deduction_of_530_is_taken_from_total_income() -> None:
    worksheet = return_dx()

    assert worksheet.get(NET_INCOME).value == D("59470.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("59470.00")
