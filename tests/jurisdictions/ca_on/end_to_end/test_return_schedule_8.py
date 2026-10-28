"""CA-ON 2025 end to end: Schedule 8 as a form of none or one copy."""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import ValidationError
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_OVERPAYMENT,
    CPP_PART_5_LINE_49,
    CPP_PART_5_LINE_70,
    CPP_PART_5_LINE_88,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ZERO,
    NET_INCOME,
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_OVERPAYMENT,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

LINES = (
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_OVERPAYMENT,
    CPP_PART_5_LINE_49,
    CPP_PART_5_LINE_70,
    CPP_PART_5_LINE_88,
    CPP_ZERO,
)

# The T1 lines 30800, 22215 and 44800 are the total of Schedule 8's line plus the total of Form
# RC381's (`05j_cpp_lines.yaml`).
T1_LINES = (
    (CPP_BASE_CONTRIBUTIONS_ON_RETURN, SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN),
    (CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN, SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN),
    (CPP_OVERPAYMENT, SCHEDULE_8_CPP_OVERPAYMENT),
)


def test_a_return_with_no_schedule_8_gives_all_seven_totals_0_and_no_form_worksheet() -> None:
    # Employment income of 60000 would give base contributions of 2796.75 and enhanced ones of
    # 565.00 on a copy of Schedule 8; with an empty list of copies the form does not run, each
    # total of its lines is 0, and the enhanced contributions are no deduction from total income.
    # With no Form RC381 either, the T1 lines are 0.
    result = run("60000", (), "0", "0", "0", "0", "0", schedule_8_copies=0)

    assert result["ca/schedule_8"] == ()
    assert result["ca/rc381"] == ()
    (worksheet,) = result["ca-on/return"]
    for kind in LINES:
        assert worksheet.get(kind).value == D("0"), kind.identifier
    for line, _ in T1_LINES:
        assert worksheet.get(line).value == D("0"), line.identifier
    assert worksheet.get(TOTAL_INCOME).value == D("60000")
    assert worksheet.get(NET_INCOME).value == D("60000.00")


def test_a_return_with_one_schedule_8_totals_the_lines_of_that_copy() -> None:
    result = run("60000", (), "0", "0", "0", "0", "0", schedule_8_copies=1)

    (schedule_8,) = result["ca/schedule_8"]
    (worksheet,) = result["ca-on/return"]
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2796.75")
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("565.00")
    for kind in LINES:
        assert worksheet.get(kind).value == schedule_8.get(kind).value, kind.identifier
    assert worksheet.get(NET_INCOME).value == D("59435.00")


def test_the_t1_lines_of_a_return_with_one_schedule_8_are_that_schedule_8s_lines() -> None:
    # With Schedule 8 and no Form RC381 the Form RC381 totals are 0, so lines 30800, 22215 and 44800
    # are Schedule 8's: employment income of 60000 and a box 16 total of 3500.00 (138.25 more than
    # the required 3361.75) give an overpayment on line 44800.
    result = run(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3500.00",
    )

    (schedule_8,) = result["ca/schedule_8"]
    (worksheet,) = result["ca-on/return"]
    assert worksheet.get(CPP_OVERPAYMENT).value == D("138.25")
    for line, schedule_8_line in T1_LINES:
        assert worksheet.get(line).value == schedule_8.get(schedule_8_line).value, line.identifier


def test_the_self_employment_t1_lines_of_a_return_with_one_schedule_8_are_its_part_5() -> None:
    # Part 5 completed with self-employment income of 20000 (Return BN's case): line 42100 is
    # Part 5 line 49 if positive, line 31000 line 70 and line 22200 line 88.
    result = run(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=({"business": {"gross_sales": "20000"}, "business_income_line": 2},),
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_part_5_completed=1,
    )

    (worksheet,) = result["ca-on/return"]
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1764.20")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D(
        "559.35"
    )
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1343.10")


def test_a_second_schedule_8_is_refused_naming_the_form() -> None:
    with pytest.raises(ValidationError, match="ca/schedule_8"):
        run("60000", (), "0", "0", "0", "0", "0", schedule_8_copies=2)
