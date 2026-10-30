"""CA-ON 2025 end to end: return EZ (Schedule 8, the CPP only: employment income on T4 slips with
box 16 under-contributed and box 16A over-contributed, so line 24 is negative and Part 3b applies).

Return EZ is `returns/2025_return_ez.yaml`: one Schedule 8 and no Form RC381, all Ontario
employment. The figures are chosen and worked out by hand from the form text, as CRA prints no
Schedule 8 example. The tests check the hand figure of each line the catalog names; the lines the
catalog does not name (for example Part 3 lines 4, 5 and 7) are checked in the YAML's description
only, and the tax figures are the engine's and are checked in the YAML only.
"""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CPP_ACTUAL_BASE_CONTRIBUTIONS,
    CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_BASE_CONTRIBUTIONS,
    CPP_BASE_CONTRIBUTIONS_DIFFERENCE,
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_CONTRIBUTIONS_DIFFERENCE,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ENHANCED_CONTRIBUTIONS,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_LINE_23_AND_LINE_33_POSITIVE,
    CPP_LINE_23_AND_LINE_40_POSITIVE,
    CPP_LINE_23_NOT_NEGATIVE,
    CPP_LINE_24_POSITIVE,
    CPP_OVERPAYMENT,
    CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_PART_3_LINE_2,
    CPP_PART_3_OVERPAYMENT,
    CPP_PART_3B_LINE_23_LESS_LINE_35,
    CPP_PART_3B_LINE_30,
    CPP_PART_3B_LINE_31,
    CPP_PART_3B_LINE_32,
    CPP_PART_3B_LINE_32_LESSER,
    CPP_PART_3B_LINE_33,
    CPP_PART_3B_LINE_34,
    CPP_PART_3B_LINE_35,
    CPP_PART_3B_LINE_35_LESSER,
    CPP_PART_3B_LINE_36,
    CPP_PART_3B_LINE_37,
    CPP_PART_3B_LINE_38,
    CPP_PART_3B_LINE_39_LESSER,
    CPP_PART_3B_LINE_40,
    CPP_PART_3B_LINE_41,
    CPP_PART_3B_LINE_42,
    CPP_PART_3B_LINE_42_LESSER,
    CPP_PART_3B_LINE_43,
    CPP_PART_3B_LINE_44,
    CPP_PART_3B_LINE_45,
    CPP_PART_3B_LINE_46,
    CPP_PART_3B_LINE_46_LESSER,
    CPP_PART_3B_LINE_47,
    CPP_PART_3B_LINE_48,
    CPP_PART_5_LINE_7,
    CPP_PART_5_LINE_8,
    CPP_PART_5_LINE_9,
    CPP_PART_5_LINE_10,
    CPP_PART_5_LINE_12,
    CPP_PART_5_LINE_13,
    CPP_PART_5_LINE_16,
    CPP_PART_5_LINE_19,
    CPP_PART_5_LINE_20,
    CPP_PART_5_LINE_21,
    CPP_PART_5_LINE_33,
    CPP_PART_5_LINE_35,
    CPP_PART_5_LINE_36,
    CPP_PART_5_LINE_51,
    CPP_PART_5_LINE_52,
    CPP_PART_5_LINE_53_LESSER,
    CPP_PART_5_LINE_54,
    CPP_PART_5_LINE_55,
    CPP_PART_5_LINE_56,
    CPP_PART_5_LINE_57,
    CPP_PART_5_LINE_58,
    CPP_PART_5_LINE_59,
    CPP_PART_5_LINE_60_LESSER,
    CPP_PART_5_LINE_61,
    CPP_PART_5_LINE_62,
    CPP_PART_5_LINE_63,
    CPP_PART_5_LINE_64,
    CPP_PART_5_LINE_65,
    CPP_PART_5_LINE_68,
    CPP_PART_5_LINE_69,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    NET_INCOME,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_ez(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return EZ's inputs (`returns/2025_return_ez.yaml`): employment income of 74000 on T4 slips
    for Ontario employment (box 26 of 74000, box 16 of 3775.00 and box 16A of 340.00), with 12
    months for CPP, no self-employment income and no election. The return carries one Schedule 8
    and no Form RC381."""
    arguments: dict[str, Any] = {
        "cpp_months": 12,
        "t4_cpp_pensionable_earnings_outside_quebec": "74000",
        "cpp_t4_base_and_first_additional_contributions": "3775.00",
        "cpp_t4_second_additional_contributions": "340.00",
        "income_tax_deducted": "13000",
        "schedule_8_copies": 1,
        "rc381_copies": 0,
    }
    return run("74000", (), "0", "0", "0", "0", "0", **{**arguments, **overrides})


def schedule_8_ez(**overrides: Any) -> Worksheet:
    (schedule_8,) = run_ez(**overrides)["ca/schedule_8"]
    return schedule_8


def return_ez(**overrides: Any) -> Worksheet:
    (worksheet,) = run_ez(**overrides)["ca-on/return"]
    return worksheet


def test_return_ez_carries_schedule_8_and_no_form_rc381() -> None:
    result = run_ez()

    assert result["ca/rc381"] == ()
    assert len(result["ca/schedule_8"]) == 1


def test_return_ez_part_3_lines_are_the_hand_figures() -> None:
    # Part 3 lines the catalog names: 2, 9 to 13, 16, 19, 20, 22, 23 and 24.
    schedule_8 = schedule_8_ez()

    for kind, expected in (
        (CPP_PART_3_LINE_2, "74000"),
        (CPP_ACTUAL_BASE_CONTRIBUTIONS, "3140.55"),
        (CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS, "634.45"),
        (CPP_BASE_CONTRIBUTIONS, "3356.10"),
        (CPP_FIRST_ADDITIONAL_CONTRIBUTIONS, "678.00"),
        (CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS, "4034.10"),
        (CPP_BASE_CONTRIBUTIONS_DIFFERENCE, "-215.55"),
        (CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, "-43.55"),
        (CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, "-259.10"),
        (CPP_SECOND_ADDITIONAL_CONTRIBUTIONS, "108.00"),
        (CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, "232.00"),
        (CPP_CONTRIBUTIONS_DIFFERENCE, "-27.10"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_ez_line_24_is_negative_so_part_3b_applies_and_the_branch_tests_hold() -> None:
    schedule_8 = schedule_8_ez()

    assert schedule_8.get(CPP_LINE_24_POSITIVE).value == 0
    assert schedule_8.get(CPP_LINE_23_NOT_NEGATIVE).value == 1
    assert schedule_8.get(CPP_LINE_23_AND_LINE_33_POSITIVE).value == 1
    assert schedule_8.get(CPP_LINE_23_AND_LINE_40_POSITIVE).value == 1


def test_return_ez_part_3a_is_not_selected_and_its_lines_are_computed() -> None:
    # Part 3a is the path for a positive line 24, which this return does not take. Line 26 is line
    # 18 (678.00), line 28 is line 26 plus line 27 (678.00 plus 108.00), and line 29 is 0 here.
    schedule_8 = schedule_8_ez()

    assert schedule_8.get(CPP_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("678.00")
    assert schedule_8.get(CPP_ENHANCED_CONTRIBUTIONS).value == D("786.00")
    assert schedule_8.get(CPP_PART_3_OVERPAYMENT).value == D("0")


def test_return_ez_part_3b_lines_30_to_36_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_ez()

    for kind, expected in (
        (CPP_PART_3B_LINE_30, "3140.55"),
        (CPP_PART_3B_LINE_31, "215.55"),
        # Line 32 takes 0: line 19 is not positive. The lesser of lines 19 and 31 is -43.55, the
        # candidate the engine computes, which is not taken.
        (CPP_PART_3B_LINE_32_LESSER, "-43.55"),
        (CPP_PART_3B_LINE_32, "0"),
        (CPP_PART_3B_LINE_33, "215.55"),
        (CPP_PART_3B_LINE_34, "3140.55"),
        # Line 35 is the lesser of lines 23 and 33, both positive.
        (CPP_PART_3B_LINE_35_LESSER, "215.55"),
        (CPP_PART_3B_LINE_35, "215.55"),
        (CPP_PART_3B_LINE_36, "3356.10"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_ez_part_3b_lines_37_to_48_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_ez()

    for kind, expected in (
        (CPP_PART_3B_LINE_37, "634.45"),
        (CPP_PART_3B_LINE_38, "43.55"),
        # Line 39 takes 0: line 16 is not positive. The lesser of lines 16 and 38 is -215.55, not
        # taken.
        (CPP_PART_3B_LINE_39_LESSER, "-215.55"),
        (CPP_PART_3B_LINE_40, "43.55"),
        (CPP_PART_3B_LINE_41, "634.45"),
        (CPP_PART_3B_LINE_23_LESS_LINE_35, "16.45"),
        # Line 42 is the lesser of line 40 (43.55) and line 23 less line 35 (16.45).
        (CPP_PART_3B_LINE_42_LESSER, "16.45"),
        (CPP_PART_3B_LINE_42, "16.45"),
        (CPP_PART_3B_LINE_43, "650.90"),
        (CPP_PART_3B_LINE_44, "108.00"),
        (CPP_PART_3B_LINE_45, "0"),
        # Line 46 takes 0: line 20 is not positive. The lesser of lines 20 and 45 is -259.10, not
        # taken.
        (CPP_PART_3B_LINE_46_LESSER, "-259.10"),
        (CPP_PART_3B_LINE_46, "0"),
        (CPP_PART_3B_LINE_47, "108.00"),
        (CPP_PART_3B_LINE_48, "758.90"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_ez_part_3_route_is_part_3b_line_36_and_line_48() -> None:
    schedule_8 = schedule_8_ez()

    assert schedule_8.get(CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3356.10")
    assert schedule_8.get(CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("758.90")


def test_return_ez_part_5_lines_7_to_21_are_computed_but_not_selected() -> None:
    # Part 5 is not completed (no self-employment income and no election), so these lines are the
    # engine's figures for the route the return does not take.
    schedule_8 = schedule_8_ez()

    for kind, expected in (
        (CPP_PART_5_LINE_7, "3775.00"),
        (CPP_PART_5_LINE_8, "259.10"),
        (CPP_PART_5_LINE_9, "232.00"),
        (CPP_PART_5_LINE_10, "4007.00"),
        (CPP_PART_5_LINE_12, "232.00"),
        (CPP_PART_5_LINE_13, "108.00"),
        (CPP_PART_5_LINE_16, "108.00"),
        (CPP_PART_5_LINE_19, "67800"),
        (CPP_PART_5_LINE_20, "67344.53"),
        (CPP_PART_5_LINE_21, "455.47"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_ez_part_5_lines_33_to_69_are_computed_but_not_selected() -> None:
    schedule_8 = schedule_8_ez()

    for kind, expected in (
        (CPP_PART_5_LINE_33, "74000"),
        (CPP_PART_5_LINE_35, "2700.00"),
        (CPP_PART_5_LINE_36, "7200.00"),
        (CPP_PART_5_LINE_51, "3140.55"),
        (CPP_PART_5_LINE_52, "215.55"),
        # Line 53 takes 0: line 19 of Part 3 is not positive. The candidate is -43.55.
        (CPP_PART_5_LINE_53_LESSER, "-43.55"),
        (CPP_PART_5_LINE_54, "215.55"),
        (CPP_PART_5_LINE_55, "3140.55"),
        (CPP_PART_5_LINE_56, "215.55"),
        (CPP_PART_5_LINE_57, "3356.10"),
        (CPP_PART_5_LINE_58, "634.45"),
        (CPP_PART_5_LINE_59, "43.55"),
        # Line 60 takes 0: line 16 of Part 3 is not positive. The candidate is -215.55.
        (CPP_PART_5_LINE_60_LESSER, "-215.55"),
        (CPP_PART_5_LINE_61, "43.55"),
        (CPP_PART_5_LINE_62, "634.45"),
        (CPP_PART_5_LINE_63, "16.45"),
        (CPP_PART_5_LINE_64, "650.90"),
        (CPP_PART_5_LINE_65, "108.00"),
        (CPP_PART_5_LINE_68, "108.00"),
        (CPP_PART_5_LINE_69, "758.90"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_ez_t1_line_30800_and_on428_line_58240_are_3356_10() -> None:
    # ON428 line 58240 "Amount from line 30800 of your return" reads the same T1 line.
    assert return_ez().get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3356.10")


def test_return_ez_t1_line_22215_is_758_90() -> None:
    assert return_ez().get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("758.90")


def test_return_ez_t1_line_44800_is_zero_because_line_24_is_negative() -> None:
    assert return_ez().get(CPP_OVERPAYMENT).value == D("0")


def test_return_ez_lines_42100_31000_and_22200_are_zero() -> None:
    worksheet = return_ez()

    for kind in (
        CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    ):
        assert worksheet.get(kind).value == D("0"), kind.identifier


def test_return_ez_net_income_is_total_income_less_the_enhanced_deduction() -> None:
    worksheet = return_ez()

    assert worksheet.get(TOTAL_INCOME).value == D("74000.00")
    # 74000.00 less the deduction of line 22215 (758.90).
    assert worksheet.get(NET_INCOME).value == D("73241.10")
    assert worksheet.get(TAXABLE_INCOME).value == D("73241.10")
