"""CA-ON 2025 end to end: return ga (the worked example of Form RC381 on Part 3b with line 53
positive and line 60 negative: a T4 for Ontario employment and a T4 for Quebec employment with the
box 16A and 17A amounts, no CPT20 election, carried to the T1 lines)."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_OVERPAYMENT,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    NET_FEDERAL_TAX,
    NET_INCOME,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS,
    RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS,
    RC381_PART_2_LINE_B,
    RC381_PART_2_LINE_G,
    RC381_PART_2_LINE_H,
    RC381_PART_2_LINE_I,
    RC381_PART_2_LINE_J,
    RC381_PART_3_LINE_3,
    RC381_PART_3_LINE_6,
    RC381_PART_3_LINE_7,
    RC381_PART_3_LINE_8,
    RC381_PART_3_LINE_9,
    RC381_PART_3_LINE_10,
    RC381_PART_3_LINE_11,
    RC381_PART_3_LINE_14,
    RC381_PART_3_LINE_15,
    RC381_PART_3_LINE_15_LESSER,
    RC381_PART_3_LINE_16,
    RC381_PART_3_LINE_18,
    RC381_PART_3_LINE_20,
    RC381_PART_3_LINE_21,
    RC381_PART_3_LINE_22,
    RC381_PART_3_LINE_23,
    RC381_PART_3_LINE_24,
    RC381_PART_3_LINE_26,
    RC381_PART_3_LINE_27,
    RC381_PART_3_LINE_28,
    RC381_PART_3_LINE_29,
    RC381_PART_3_LINE_30,
    RC381_PART_3_LINE_31,
    RC381_PART_3_LINE_34,
    RC381_PART_3_LINE_35,
    RC381_PART_3_LINE_35_LESSER,
    RC381_PART_3_LINE_36,
    RC381_PART_3_LINE_38,
    RC381_PART_3_LINE_40,
    RC381_PART_3_LINE_41,
    RC381_PART_3_LINE_42,
    RC381_PART_3_LINE_43,
    RC381_PART_3_LINE_44,
    RC381_PART_3_LINE_46,
    RC381_PART_3_LINE_49,
    RC381_PART_3_LINE_52,
    RC381_PART_3_LINE_53,
    RC381_PART_3_LINE_56,
    RC381_PART_3_LINE_59,
    RC381_PART_3_LINE_60,
    RC381_PART_3_LINE_61,
    RC381_PART_3_LINE_64,
    RC381_PART_3_LINE_67,
    RC381_PART_3_LINE_68,
    RC381_PART_3_LINE_69,
    RC381_PART_3_LINE_73,
    RC381_PART_3_LINE_75,
    RC381_PART_3_LINE_76,
    RC381_PART_3_LINE_77,
    RC381_PART_3_LINE_78,
    RC381_PART_3_LINE_79,
    RC381_PART_3_LINE_80,
    RC381_PART_3_LINE_81,
    RC381_PART_3_LINE_82,
    RC381_PART_3_LINE_83,
    RC381_PART_3_LINE_84,
    RC381_PART_3_LINE_85,
    RC381_PART_3_LINE_86,
    RC381_PART_3_LINE_87,
    RC381_PART_3_LINE_87_DIFFERENCE,
    RC381_PART_3_LINE_88,
    RC381_PART_3_LINE_89,
    RC381_PART_3_LINE_92,
    RC381_PART_3_LINE_93,
    RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, assert_values, run


def run_ga(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return GA's inputs (`returns/2025_return_ga.yaml`): employment income of 80000 on a T4 for
    Ontario employment (box 26 of 50000, box 16 of 2245.51 and box 16A of 210.00) and a T4 for
    Quebec employment (box 26 of 30000, box 17 of 1900.00 and box 17A of 140.00), with 12 months for
    CPP and QPP and no CPT20 election. The return carries one Form RC381 and no Schedule 8."""
    arguments: dict[str, Any] = {
        "cpp_months": 12,
        "qpp_months": 12,
        "t4_cpp_pensionable_earnings_outside_quebec": "50000",
        "t4_qpp_pensionable_earnings_in_quebec": "30000",
        "cpp_t4_base_and_first_additional_contributions": "2245.51",
        "t4_cpp_second_additional_box_16a": "210.00",
        "t4_qpp_contributions_box_17": "1900.00",
        "t4_qpp_second_additional_box_17a": "140.00",
        "income_tax_deducted": "13000",
        "schedule_8_copies": 0,
        "rc381_copies": 1,
    }
    return run("80000", (), "0", "0", "0", "0", "0", **{**arguments, **overrides})


def form_ga(**overrides: Any) -> Worksheet:
    (rc381,) = run_ga(**overrides)["ca/rc381"]
    return rc381


def return_ga(**overrides: Any) -> Worksheet:
    (worksheet,) = run_ga(**overrides)["ca-on/return"]
    return worksheet


def test_return_ga_carries_form_rc381_and_no_schedule_8() -> None:
    result = run_ga()

    assert result["ca/schedule_8"] == ()
    assert len(result["ca/rc381"]) == 1


# Part 2.


def test_return_ga_part_2_lines_b_g_h_i_j_are_the_twelve_month_row() -> None:
    rc381 = form_ga()

    assert rc381.get(RC381_PART_2_LINE_B).value == 12
    assert_values(
        rc381,
        (
            (RC381_PART_2_LINE_G, "71300.00"),
            (RC381_PART_2_LINE_H, "9900.00"),
            (RC381_PART_2_LINE_I, "81200.00"),
            (RC381_PART_2_LINE_J, "3500.00"),
        ),
    )


# Part 3, the CPP side.


def test_return_ga_part_3_line_3_is_80000_and_line_6_is_0_62500() -> None:
    rc381 = form_ga()

    assert rc381.get(RC381_PART_3_LINE_3).value == D("80000")
    # 50000 divided by 80000 is exactly 0.625, which is 0.62500 to the fifth decimal place.
    assert rc381.get(RC381_PART_3_LINE_6).value == Rate(D("0.62500"))


def test_return_ga_part_3_lines_7_to_10_are_the_table_amounts_times_line_6() -> None:
    assert_values(
        form_ga(),
        (
            (RC381_PART_3_LINE_7, "50750.00"),
            (RC381_PART_3_LINE_8, "44562.50"),
            (RC381_PART_3_LINE_9, "2187.50"),
            (RC381_PART_3_LINE_10, "6187.50"),
        ),
    )


def test_return_ga_line_3_above_line_c_completes_lines_12_to_15() -> None:
    # Line 3 (80000) is more than line C (71300), so lines 12 to 15 are completed: line 14 is
    # 50000.00 less 44562.50, and line 15 is the lesser of line 10 (6187.50) and line 14.
    assert_values(
        form_ga(),
        (
            (RC381_PART_3_LINE_11, "50000"),
            (RC381_PART_3_LINE_14, "5437.50"),
            (RC381_PART_3_LINE_15, "5437.50"),
            (RC381_PART_3_LINE_15_LESSER, "5437.50"),
            (RC381_PART_3_LINE_16, "44562.50"),
            (RC381_PART_3_LINE_18, "42375.00"),
        ),
    )


def test_return_ga_the_cpp_side_of_part_3_lines_20_to_26() -> None:
    # Box 16 (2245.51) is under the 2521.31 required on line 24: the base is over and the first
    # additional contributions are short, which lines 53 and 60 carry below.
    assert_values(
        form_ga(),
        (
            (RC381_PART_3_LINE_20, "1868.11"),
            (RC381_PART_3_LINE_21, "377.40"),
            (RC381_PART_3_LINE_22, "2097.56"),
            (RC381_PART_3_LINE_23, "423.75"),
            (RC381_PART_3_LINE_24, "2521.31"),
            (RC381_PART_3_LINE_26, "217.50"),
        ),
    )


# Part 3, the QPP side.


def test_return_ga_the_qpp_side_of_part_3_lines_27_to_31() -> None:
    assert_values(
        form_ga(),
        (
            (RC381_PART_3_LINE_27, "30450.00"),
            (RC381_PART_3_LINE_28, "26737.50"),
            (RC381_PART_3_LINE_29, "1312.50"),
            (RC381_PART_3_LINE_30, "3712.50"),
            (RC381_PART_3_LINE_31, "30000"),
        ),
    )


def test_return_ga_line_3_above_line_g_completes_lines_32_to_35() -> None:
    assert_values(
        form_ga(),
        (
            (RC381_PART_3_LINE_34, "3262.50"),
            (RC381_PART_3_LINE_35, "3262.50"),
            (RC381_PART_3_LINE_35_LESSER, "3262.50"),
            (RC381_PART_3_LINE_36, "26737.50"),
        ),
    )


def test_return_ga_the_qpp_side_of_part_3_lines_38_to_46() -> None:
    assert_values(
        form_ga(),
        (
            (RC381_PART_3_LINE_38, "25425.00"),
            (RC381_PART_3_LINE_40, "1603.13"),
            (RC381_PART_3_LINE_41, "296.87"),
            (RC381_PART_3_LINE_42, "1372.95"),
            (RC381_PART_3_LINE_43, "254.25"),
            (RC381_PART_3_LINE_44, "1627.20"),
            (RC381_PART_3_LINE_46, "130.50"),
        ),
    )


# Part 3, the totals.


def test_return_ga_part_3_totals_on_lines_49_to_69() -> None:
    assert_values(
        form_ga(),
        (
            (RC381_PART_3_LINE_49, "3471.24"),
            (RC381_PART_3_LINE_52, "3470.51"),
            (RC381_PART_3_LINE_53, "0.73"),
            (RC381_PART_3_LINE_56, "674.27"),
            (RC381_PART_3_LINE_59, "678.00"),
            (RC381_PART_3_LINE_60, "-3.73"),
            (RC381_PART_3_LINE_61, "-3.00"),
            (RC381_PART_3_LINE_64, "350.00"),
            (RC381_PART_3_LINE_67, "348.00"),
            (RC381_PART_3_LINE_68, "2.00"),
            (RC381_PART_3_LINE_69, "-1.00"),
        ),
    )


def test_return_ga_line_69_is_negative_so_part_3b_is_the_path() -> None:
    # Line 69 is -1.00, so Part 3a (lines 70 to 74) is not the path; its lines are the table's
    # copies, and line 73 is 678.00 plus 348.00.
    rc381 = form_ga()

    assert rc381.get(RC381_PART_3_LINE_73).value == D("1026.00")
    assert rc381.get(RC381_PART_3_LINE_69).value == D("-1.00")


# Part 3b.


def test_return_ga_part_3b_lines_75_to_81_with_line_53_positive() -> None:
    # Line 53 is positive, so line 52 is entered at lines 75 and 81 and the form continues at line
    # 82. Line 79 is the sheet's figure (line 75 plus line 77), which is 3470.51 either way.
    assert_values(
        form_ga(),
        (
            (RC381_PART_3_LINE_75, "3470.51"),
            (RC381_PART_3_LINE_76, "0"),
            (RC381_PART_3_LINE_77, "0"),
            (RC381_PART_3_LINE_78, "0"),
            (RC381_PART_3_LINE_79, "3470.51"),
            (RC381_PART_3_LINE_80, "0"),
            (RC381_PART_3_LINE_81, "3470.51"),
        ),
    )


def test_return_ga_part_3b_lines_82_to_93_with_line_60_negative() -> None:
    assert_values(
        form_ga(),
        (
            (RC381_PART_3_LINE_82, "674.27"),
            (RC381_PART_3_LINE_83, "3.73"),
            (RC381_PART_3_LINE_84, "0.73"),
            (RC381_PART_3_LINE_85, "3.00"),
            (RC381_PART_3_LINE_86, "675.00"),
            (RC381_PART_3_LINE_87, "2.00"),
            (RC381_PART_3_LINE_87_DIFFERENCE, "2.00"),
            (RC381_PART_3_LINE_88, "677.00"),
            (RC381_PART_3_LINE_89, "348.00"),
            (RC381_PART_3_LINE_92, "348.00"),
            (RC381_PART_3_LINE_93, "1025.00"),
        ),
    )


def test_return_ga_line_84_is_reached_as_line_53_is_positive_and_line_60_is_negative() -> None:
    # Line 84 is the lesser of line 53 (0.73) and line 83 (3.73), since line 53 is positive.
    rc381 = form_ga()

    assert rc381.get(RC381_PART_3_LINE_84).value == D("0.73")
    assert rc381.get(RC381_PART_3_LINE_53).value > D("0")
    assert rc381.get(RC381_PART_3_LINE_60).value < D("0")


def test_return_ga_line_77_is_zero_as_line_53_is_not_negative() -> None:
    # Line 77 needs line 53 negative and line 60 positive, so it is reached on Return FZ, not here.
    rc381 = form_ga()

    assert rc381.get(RC381_PART_3_LINE_77).value == D("0")


# The final selection and the T1 lines.


def test_return_ga_final_selection_takes_part_3b_results_as_part_4_is_not_completed() -> None:
    rc381 = form_ga()

    assert rc381.get(RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS).value == D("3470.51")
    assert rc381.get(RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS).value == D("1025.00")
    assert rc381.get(RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS).value == D("0")
    assert rc381.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3470.51")
    assert rc381.get(RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("1025.00")


def test_return_ga_t1_line_30800_is_part_3b_line_81_at_3470_51() -> None:
    assert return_ga().get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3470.51")


def test_return_ga_t1_line_22215_is_part_3b_line_93_at_1025_00() -> None:
    assert return_ga().get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("1025.00")


def test_return_ga_t1_line_44800_is_zero_as_no_overpayment_is_entered() -> None:
    # The overpayment is entered at Part 3a line 74 (line 69 is not positive) or Part 4 line 91
    # (Part 4 is not completed), so it is zero.
    assert return_ga().get(CPP_OVERPAYMENT).value == D("0")


def test_return_ga_t1_line_42100_is_zero_as_part_4_is_not_completed() -> None:
    assert return_ga().get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("0")


def test_return_ga_t1_line_31000_and_line_22200_are_zero_as_part_4_is_not_completed() -> None:
    worksheet = return_ga()

    base = worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS)
    deduction = worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS)

    assert base.value == D("0")
    assert deduction.value == D("0")


def test_return_ga_net_income_is_80000_less_the_line_22215_deduction() -> None:
    worksheet = return_ga()

    assert worksheet.get(TOTAL_INCOME).value == D("80000.00")
    # 80000.00 less 1025.00 (line 22215) and 0.00 (line 22200) is 78975.00.
    assert worksheet.get(NET_INCOME).value == D("78975.00")


def test_return_ga_the_tax_and_the_balance_are_the_engines() -> None:
    worksheet = return_ga()

    assert worksheet.get(NET_FEDERAL_TAX).value == D("9535.92")
    assert worksheet.get(ONTARIO_TAX).value == D("4934.48")
    assert worksheet.get(TOTAL_PAYABLE).value == D("14470.40")
    # The income tax deducted (13000.00) and the CPP overpayment of line 44800 (0.00).
    assert worksheet.get(TOTAL_CREDITS).value == D("13000.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("1470.40")
