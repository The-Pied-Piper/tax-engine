"""CA-ON 2025 end to end: return FX (Schedule 8, the CPP only: employment income on T4 slips with
box 16 over-contributed and box 16A under-contributed, so line 20 of Part 3 is positive, line 23 is
negative and line 24 is negative, and Part 3b applies, reaching Part 3b lines 45 and 46 and Part 5
lines 14, 15, 66 and 67).

Return FX is `returns/2025_return_fx.yaml`: one Schedule 8 and no Form RC381, all Ontario
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
    CPP_PART_3B_LINE_33,
    CPP_PART_3B_LINE_34,
    CPP_PART_3B_LINE_35,
    CPP_PART_3B_LINE_35_LESSER,
    CPP_PART_3B_LINE_36,
    CPP_PART_3B_LINE_37,
    CPP_PART_3B_LINE_38,
    CPP_PART_3B_LINE_39,
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
    CPP_PART_5_LINE_6,
    CPP_PART_5_LINE_7,
    CPP_PART_5_LINE_8,
    CPP_PART_5_LINE_9,
    CPP_PART_5_LINE_9_LESSER,
    CPP_PART_5_LINE_10,
    CPP_PART_5_LINE_13,
    CPP_PART_5_LINE_14,
    CPP_PART_5_LINE_15,
    CPP_PART_5_LINE_15_LESSER,
    CPP_PART_5_LINE_16,
    CPP_PART_5_LINE_19,
    CPP_PART_5_LINE_20,
    CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE,
    CPP_PART_5_LINE_21,
    CPP_PART_5_LINE_23_LESS_LINE_56,
    CPP_PART_5_LINE_33,
    CPP_PART_5_LINE_35,
    CPP_PART_5_LINE_36,
    CPP_PART_5_LINE_51,
    CPP_PART_5_LINE_55,
    CPP_PART_5_LINE_56_LESSER,
    CPP_PART_5_LINE_57,
    CPP_PART_5_LINE_58,
    CPP_PART_5_LINE_62,
    CPP_PART_5_LINE_63_LESSER,
    CPP_PART_5_LINE_64,
    CPP_PART_5_LINE_65,
    CPP_PART_5_LINE_66,
    CPP_PART_5_LINE_67,
    CPP_PART_5_LINE_67_LESSER,
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


def run_fx(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return FX's inputs (`returns/2025_return_fx.yaml`): employment income of 72000 on T4 slips
    for Ontario employment (box 26 of 72000, box 16 of 4044.10 and box 16A of 12.00), with 12
    months for CPP, no self-employment income and no election. The return carries one Schedule 8
    and no Form RC381."""
    arguments: dict[str, Any] = {
        "cpp_months": 12,
        "t4_cpp_pensionable_earnings_outside_quebec": "72000",
        "cpp_t4_base_and_first_additional_contributions": "4044.10",
        "cpp_t4_second_additional_contributions": "12.00",
        "income_tax_deducted": "13000",
        "schedule_8_copies": 1,
        "rc381_copies": 0,
    }
    return run("72000", (), "0", "0", "0", "0", "0", **{**arguments, **overrides})


def schedule_8_fx(**overrides: Any) -> Worksheet:
    (schedule_8,) = run_fx(**overrides)["ca/schedule_8"]
    return schedule_8


def return_fx(**overrides: Any) -> Worksheet:
    (worksheet,) = run_fx(**overrides)["ca-on/return"]
    return worksheet


def test_return_fx_carries_schedule_8_and_no_form_rc381() -> None:
    result = run_fx()

    assert result["ca/rc381"] == ()
    assert len(result["ca/schedule_8"]) == 1


def test_return_fx_part_3_lines_2_to_19_are_the_hand_figures() -> None:
    # Part 3 lines the catalog names: 2, 9 to 13, 14 to 19 and the required amounts.
    schedule_8 = schedule_8_fx()

    for kind, expected in (
        (CPP_PART_3_LINE_2, "72000"),
        (CPP_ACTUAL_BASE_CONTRIBUTIONS, "3364.42"),
        (CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS, "679.68"),
        (CPP_BASE_CONTRIBUTIONS, "3356.10"),
        (CPP_FIRST_ADDITIONAL_CONTRIBUTIONS, "678.00"),
        (CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS, "4034.10"),
        (CPP_BASE_CONTRIBUTIONS_DIFFERENCE, "8.32"),
        (CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, "1.68"),
        (CPP_SECOND_ADDITIONAL_CONTRIBUTIONS, "28.00"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fx_part_3_lines_20_23_and_24_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_fx()

    assert schedule_8.get(CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D(
        "10.00"
    )
    assert schedule_8.get(CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D("-16.00")
    assert schedule_8.get(CPP_CONTRIBUTIONS_DIFFERENCE).value == D("-6.00")


def test_return_fx_line_24_is_negative_so_part_3b_applies_and_part_3a_is_not_selected() -> None:
    schedule_8 = schedule_8_fx()

    assert schedule_8.get(CPP_LINE_24_POSITIVE).value == 0
    assert schedule_8.get(CPP_LINE_23_NOT_NEGATIVE).value == 0
    assert schedule_8.get(CPP_LINE_23_AND_LINE_33_POSITIVE).value == 0
    # Part 3a is the path for a positive line 24, which this return does not take. Line 28 is line
    # 26 plus line 27 (678.00 plus 28.00), and the overpayment of line 29 is 0 here.
    assert schedule_8.get(CPP_ENHANCED_CONTRIBUTIONS).value == D("706.00")
    assert schedule_8.get(CPP_PART_3_OVERPAYMENT).value == D("0")


def test_return_fx_part_3b_lines_30_to_36_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_fx()

    for kind, expected in (
        (CPP_PART_3B_LINE_30, "3356.10"),
        # Lines 31 to 35 are not taken on this branch (line 16 is positive); the arithmetic gives
        # the values below.
        (CPP_PART_3B_LINE_31, "0"),
        (CPP_PART_3B_LINE_32, "0"),
        (CPP_PART_3B_LINE_33, "0"),
        (CPP_PART_3B_LINE_34, "3356.10"),
        # Line 35 takes 0: line 23 is negative. The lesser of lines 23 and 33 is -16.00, not taken.
        (CPP_PART_3B_LINE_35_LESSER, "-16.00"),
        (CPP_PART_3B_LINE_35, "0"),
        (CPP_PART_3B_LINE_36, "3356.10"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fx_part_3b_lines_37_to_48_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_fx()

    for kind, expected in (
        (CPP_PART_3B_LINE_37, "678.00"),
        (CPP_PART_3B_LINE_38, "0"),
        (CPP_PART_3B_LINE_39, "0"),
        (CPP_PART_3B_LINE_40, "0"),
        (CPP_PART_3B_LINE_41, "678.00"),
        # Line 42 takes 0: line 23 is negative. The lesser of line 40 (0) and line 23 less line 35
        # (-16.00) is -16.00, not taken.
        (CPP_PART_3B_LINE_23_LESS_LINE_35, "-16.00"),
        (CPP_PART_3B_LINE_42_LESSER, "-16.00"),
        (CPP_PART_3B_LINE_42, "0"),
        (CPP_PART_3B_LINE_43, "678.00"),
        (CPP_PART_3B_LINE_44, "12.00"),
        # Line 45 is line 23 as a positive amount: the second additional contributions are short.
        (CPP_PART_3B_LINE_45, "16.00"),
        # Line 46 is the lesser of line 20 (10.00) and line 45 (16.00).
        (CPP_PART_3B_LINE_46_LESSER, "10.00"),
        (CPP_PART_3B_LINE_46, "10.00"),
        (CPP_PART_3B_LINE_47, "22.00"),
        (CPP_PART_3B_LINE_48, "700.00"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fx_part_3_route_is_part_3b_line_36_and_line_48() -> None:
    schedule_8 = schedule_8_fx()

    assert schedule_8.get(CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3356.10")
    assert schedule_8.get(CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("700.00")


def test_return_fx_part_5_lines_6_to_21_are_computed_but_not_selected() -> None:
    # Part 5 is not completed (no self-employment income and no election), so these lines are the
    # engine's figures for the route the return does not take.
    schedule_8 = schedule_8_fx()

    for kind, expected in (
        (CPP_PART_5_LINE_6, "10.00"),
        (CPP_PART_5_LINE_7, "4034.10"),
        (CPP_PART_5_LINE_8, "0"),
        (CPP_PART_5_LINE_9, "0"),
        (CPP_PART_5_LINE_9_LESSER, "-16.00"),
        (CPP_PART_5_LINE_10, "4034.10"),
        (CPP_PART_5_LINE_13, "12.00"),
        (CPP_PART_5_LINE_16, "22.00"),
        (CPP_PART_5_LINE_19, "67800"),
        (CPP_PART_5_LINE_20, "67799.99"),
        (CPP_PART_5_LINE_21, "0.01"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fx_part_5_lines_14_and_15_are_the_hand_figures() -> None:
    # Line 20 of Part 3 is positive and line 23 negative, so lines 14 and 15 are completed.
    schedule_8 = schedule_8_fx()

    assert schedule_8.get(CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE).value == 1
    assert schedule_8.get(CPP_PART_5_LINE_14).value == D("16.00")
    assert schedule_8.get(CPP_PART_5_LINE_15_LESSER).value == D("10.00")
    assert schedule_8.get(CPP_PART_5_LINE_15).value == D("10.00")


def test_return_fx_part_5_lines_33_to_69_are_computed_but_not_selected() -> None:
    schedule_8 = schedule_8_fx()

    for kind, expected in (
        (CPP_PART_5_LINE_33, "72000"),
        (CPP_PART_5_LINE_35, "550.00"),
        (CPP_PART_5_LINE_36, "9350.00"),
        (CPP_PART_5_LINE_51, "3356.10"),
        (CPP_PART_5_LINE_55, "3356.10"),
        # Line 56 takes 0: line 23 of Part 3 is negative. The candidate is -16.00.
        (CPP_PART_5_LINE_56_LESSER, "-16.00"),
        (CPP_PART_5_LINE_23_LESS_LINE_56, "-16.00"),
        (CPP_PART_5_LINE_57, "3356.10"),
        (CPP_PART_5_LINE_58, "678.00"),
        (CPP_PART_5_LINE_62, "678.00"),
        # Line 63 takes 0 (line 23 of Part 3 is negative); the candidate is -16.00.
        (CPP_PART_5_LINE_63_LESSER, "-16.00"),
        (CPP_PART_5_LINE_64, "678.00"),
        (CPP_PART_5_LINE_65, "12.00"),
        (CPP_PART_5_LINE_66, "16.00"),
        (CPP_PART_5_LINE_67_LESSER, "10.00"),
        (CPP_PART_5_LINE_67, "10.00"),
        (CPP_PART_5_LINE_68, "22.00"),
        (CPP_PART_5_LINE_69, "700.00"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fx_t1_line_30800_and_on428_line_58240_are_3356_10() -> None:
    # ON428 line 58240 "Amount from line 30800 of your return" reads the same T1 line.
    assert return_fx().get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3356.10")


def test_return_fx_t1_line_22215_is_700_00() -> None:
    assert return_fx().get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("700.00")


def test_return_fx_t1_line_44800_is_zero_because_line_24_is_negative() -> None:
    assert return_fx().get(CPP_OVERPAYMENT).value == D("0")


def test_return_fx_lines_42100_31000_and_22200_are_zero() -> None:
    worksheet = return_fx()

    for kind in (
        CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    ):
        assert worksheet.get(kind).value == D("0"), kind.identifier


def test_return_fx_net_income_is_total_income_less_the_enhanced_deduction() -> None:
    worksheet = return_fx()

    assert worksheet.get(TOTAL_INCOME).value == D("72000.00")
    # 72000.00 less the deduction of line 22215 (700.00).
    assert worksheet.get(NET_INCOME).value == D("71300.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("71300.00")
