"""CA-ON 2025 end to end: return fz (the worked example of Form RC381 with the CPP over-contributed,
the QPP under-contributed and the second additional QPP contributions short, so that Part 3 line 53
is negative, line 61 positive and line 68 negative; Part 4 completed by the CPT20 election and
carried to the T1 lines)."""

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
    RC381_PART_3_LINE_90,
    RC381_PART_3_LINE_91,
    RC381_PART_3_LINE_92,
    RC381_PART_3_LINE_93,
    RC381_PART_4_LINE_4,
    RC381_PART_4_LINE_8,
    RC381_PART_4_LINE_11,
    RC381_PART_4_LINE_12,
    RC381_PART_4_LINE_13,
    RC381_PART_4_LINE_17,
    RC381_PART_4_LINE_20,
    RC381_PART_4_LINE_21,
    RC381_PART_4_LINE_26,
    RC381_PART_4_LINE_27,
    RC381_PART_4_LINE_31,
    RC381_PART_4_LINE_31_DIFFERENCE,
    RC381_PART_4_LINE_32,
    RC381_PART_4_LINE_40,
    RC381_PART_4_LINE_41,
    RC381_PART_4_LINE_42,
    RC381_PART_4_LINE_47,
    RC381_PART_4_LINE_52,
    RC381_PART_4_LINE_53,
    RC381_PART_4_LINE_54,
    RC381_PART_4_LINE_55,
    RC381_PART_4_LINE_56,
    RC381_PART_4_LINE_59,
    RC381_PART_4_LINE_61,
    RC381_PART_4_LINE_62,
    RC381_PART_4_LINE_70,
    RC381_PART_4_LINE_74,
    RC381_PART_4_LINE_77,
    RC381_PART_4_LINE_80,
    RC381_PART_4_LINE_82,
    RC381_PART_4_LINE_83,
    RC381_PART_4_LINE_83_LESSER,
    RC381_PART_4_LINE_84,
    RC381_PART_4_LINE_85,
    RC381_PART_4_LINE_86,
    RC381_PART_4_LINE_87,
    RC381_PART_4_LINE_88,
    RC381_PART_4_LINE_90,
    RC381_PART_4_LINE_92,
    RC381_PART_4_LINE_93,
    RC381_PART_4_LINE_94,
    RC381_PART_4_LINE_95,
    RC381_PART_4_LINE_96,
    RC381_PART_4_LINE_97,
    RC381_PART_4_LINE_98,
    RC381_PART_4_LINE_99,
    RC381_PART_4_LINE_104_DIFFERENCE,
    RC381_PART_4_LINE_105,
    RC381_PART_4_LINE_106,
    RC381_PART_4_LINE_107,
    RC381_PART_4_LINE_108,
    RC381_PART_4_LINE_109,
    RC381_PART_4_LINE_110,
    RC381_PART_4_LINE_111,
    RC381_PART_4_LINE_112,
    RC381_PART_4_LINE_113,
    RC381_PART_4_LINE_115,
    RC381_PART_4_LINE_125,
    RC381_PART_4_LINE_128,
    RC381_PART_4_LINE_129,
    RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, assert_values, run


def run_fz(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return FZ's inputs (`returns/2025_return_fz.yaml`): employment income of 80000 on a T4 for
    Ontario employment (box 26 of 60000, box 16 of 3521.31 and box 16A of 100.00) and a T4 for
    Quebec employment (box 26 of 36000, box 17 of 637.20 and box 17A of 150.00), with 12 months for
    CPP and QPP, and the CPT20 election earnings of Part 4 lines 2 and 3 (3000 and 2000). The return
    carries one Form RC381 and no Schedule 8."""
    arguments: dict[str, Any] = {
        "cpp_months": 12,
        "qpp_months": 12,
        "t4_cpp_pensionable_earnings_outside_quebec": "60000",
        "t4_qpp_pensionable_earnings_in_quebec": "36000",
        "cpp_t4_base_and_first_additional_contributions": "3521.31",
        "t4_cpp_second_additional_box_16a": "100.00",
        "t4_qpp_contributions_box_17": "637.20",
        "t4_qpp_second_additional_box_17a": "150.00",
        "cpt20_earnings": "3000",
        "cpt20_t4_earnings": "2000",
        "income_tax_deducted": "13000",
        "schedule_8_copies": 0,
        "rc381_copies": 1,
    }
    return run("80000", (), "0", "0", "0", "0", "0", **{**arguments, **overrides})


def form_fz(**overrides: Any) -> Worksheet:
    (rc381,) = run_fz(**overrides)["ca/rc381"]
    return rc381


def return_fz(**overrides: Any) -> Worksheet:
    (worksheet,) = run_fz(**overrides)["ca-on/return"]
    return worksheet


def test_return_fz_carries_form_rc381_and_no_schedule_8() -> None:
    result = run_fz()

    assert result["ca/schedule_8"] == ()
    assert len(result["ca/rc381"]) == 1


# Part 2.


def test_return_fz_part_2_lines_b_g_h_i_j_are_the_twelve_month_row() -> None:
    rc381 = form_fz()

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


# Part 3, the totals: the CPP over-contributed (line 53 negative) and the QPP under-contributed
# (line 60 positive), so line 61 is positive, and the second additional QPP is short (line 68).


def test_return_fz_part_3_line_3_is_96000_and_line_6_is_0_62500() -> None:
    rc381 = form_fz()

    assert rc381.get(RC381_PART_3_LINE_3).value == D("96000")
    # 60000 divided by 96000 is exactly 0.625, which is 0.62500 to the fifth decimal place.
    assert rc381.get(RC381_PART_3_LINE_6).value == Rate(D("0.62500"))


def test_return_fz_part_3_totals_on_lines_49_to_69_with_line_61_positive_and_line_68_negative() -> (
    None
):
    assert_values(
        form_fz(),
        (
            (RC381_PART_3_LINE_49, "3467.13"),
            (RC381_PART_3_LINE_52, "3470.51"),
            (RC381_PART_3_LINE_53, "-3.38"),
            (RC381_PART_3_LINE_56, "691.38"),
            (RC381_PART_3_LINE_59, "678.00"),
            (RC381_PART_3_LINE_60, "13.38"),
            (RC381_PART_3_LINE_61, "10.00"),
            (RC381_PART_3_LINE_64, "250.00"),
            (RC381_PART_3_LINE_67, "396.00"),
            (RC381_PART_3_LINE_68, "-146.00"),
            (RC381_PART_3_LINE_69, "-136.00"),
        ),
    )


# Part 3b, the branch for line 69 "0" or negative: line 53 negative and line 60 positive give
# line 77; the second additional QPP short (line 68 negative) gives line 80 of "0".


def test_return_fz_part_3b_lines_75_to_81_give_the_cpp_over_contribution_on_line_77() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_3_LINE_75, "3467.13"),
            (RC381_PART_3_LINE_76, "3.38"),
            (RC381_PART_3_LINE_77, "3.38"),
            (RC381_PART_3_LINE_78, "0"),
            (RC381_PART_3_LINE_79, "3470.51"),
            (RC381_PART_3_LINE_80, "0"),
            (RC381_PART_3_LINE_81, "3470.51"),
        ),
    )


def test_return_fz_part_3b_lines_82_to_88_line_60_positive_takes_line_59() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_3_LINE_82, "678.00"),
            (RC381_PART_3_LINE_83, "0"),
            (RC381_PART_3_LINE_84, "0"),
            (RC381_PART_3_LINE_85, "0"),
            (RC381_PART_3_LINE_86, "678.00"),
            (RC381_PART_3_LINE_87, "0"),
            (RC381_PART_3_LINE_87_DIFFERENCE, "-146.00"),
            (RC381_PART_3_LINE_88, "678.00"),
        ),
    )


def test_return_fz_part_3b_lines_89_to_93_line_68_negative_gives_the_enhanced_deduction() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_3_LINE_89, "250.00"),
            (RC381_PART_3_LINE_90, "146.00"),
            (RC381_PART_3_LINE_91, "10.00"),
            (RC381_PART_3_LINE_92, "260.00"),
            (RC381_PART_3_LINE_93, "938.00"),
        ),
    )


# Part 4, the self-employment and other earnings the CPT20 election makes (line 61 positive).


def test_return_fz_part_4_lines_4_to_13_are_completed_as_line_61_is_positive() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_4_LINE_4, "5000"),
            (RC381_PART_4_LINE_8, "831.93"),
            (RC381_PART_4_LINE_11, "168.07"),
            (RC381_PART_4_LINE_12, "1000.00"),
            (RC381_PART_4_LINE_13, "2521.31"),
        ),
    )


def test_return_fz_part_4_lines_17_20_and_21_are_computed_but_not_used() -> None:
    # Lines 14 to 24 are not completed when line 61 of Part 3 is positive: the engine computes
    # line 17 (1000.00), line 20 (-990.00) and line 21 (-1000.00) before the form's gate, and they
    # are not used on this branch.
    assert_values(
        form_fz(),
        (
            (RC381_PART_4_LINE_17, "1000.00"),
            (RC381_PART_4_LINE_20, "-990.00"),
            (RC381_PART_4_LINE_21, "-1000.00"),
        ),
    )


def test_return_fz_part_4_lines_26_to_42_are_the_qpp_side_on_line_61_positive() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_4_LINE_26, "2521.31"),
            (RC381_PART_4_LINE_27, "42374.95"),
            (RC381_PART_4_LINE_31, "-990.00"),
            (RC381_PART_4_LINE_31_DIFFERENCE, "-990.00"),
            (RC381_PART_4_LINE_32, "1627.20"),
            (RC381_PART_4_LINE_40, "1627.20"),
            (RC381_PART_4_LINE_41, "25425.00"),
            (RC381_PART_4_LINE_42, "67799.95"),
        ),
    )


def test_return_fz_part_4_lines_47_to_56_the_second_additional_contributions() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_4_LINE_47, "100.00"),
            (RC381_PART_4_LINE_52, "150.00"),
            (RC381_PART_4_LINE_53, "250.00"),
            (RC381_PART_4_LINE_54, "146.00"),
            (RC381_PART_4_LINE_55, "10.00"),
            (RC381_PART_4_LINE_56, "260.00"),
        ),
    )


def test_return_fz_part_4_lines_59_to_70_the_earnings_subject_to_contributions() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_4_LINE_59, "67800"),
            (RC381_PART_4_LINE_61, "0.05"),
            (RC381_PART_4_LINE_62, "0.05"),
            (RC381_PART_4_LINE_70, "0.05"),
        ),
    )


def test_return_fz_part_4_lines_74_to_90_the_self_employment_contributions() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_4_LINE_74, "86200"),
            (RC381_PART_4_LINE_77, "3400.00"),
            (RC381_PART_4_LINE_80, "5000"),
            (RC381_PART_4_LINE_82, "4999.95"),
            (RC381_PART_4_LINE_83, "3400.00"),
            (RC381_PART_4_LINE_83_LESSER, "3400.00"),
            (RC381_PART_4_LINE_84, "0"),
            (RC381_PART_4_LINE_85, "0"),
            (RC381_PART_4_LINE_86, "272.00"),
            (RC381_PART_4_LINE_87, "272.00"),
            (RC381_PART_4_LINE_88, "272.00"),
            (RC381_PART_4_LINE_90, "272.00"),
        ),
    )


def test_return_fz_part_4_lines_92_to_99_the_base_through_employment_income() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_4_LINE_92, "3467.13"),
            (RC381_PART_4_LINE_93, "3.38"),
            (RC381_PART_4_LINE_94, "3.38"),
            (RC381_PART_4_LINE_95, "0"),
            (RC381_PART_4_LINE_96, "3470.51"),
            (RC381_PART_4_LINE_97, "0"),
            (RC381_PART_4_LINE_98, "3470.51"),
            (RC381_PART_4_LINE_99, "678.00"),
        ),
    )


def test_return_fz_part_4_lines_104_to_110_the_enhanced_through_employment_income() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_4_LINE_104_DIFFERENCE, "-146.00"),
            (RC381_PART_4_LINE_105, "678.00"),
            (RC381_PART_4_LINE_106, "250.00"),
            (RC381_PART_4_LINE_107, "146.00"),
            (RC381_PART_4_LINE_108, "10.00"),
            (RC381_PART_4_LINE_109, "260.00"),
            (RC381_PART_4_LINE_110, "938.00"),
        ),
    )


def test_return_fz_part_4_lines_111_to_129_the_contributions_on_self_employment() -> None:
    assert_values(
        form_fz(),
        (
            (RC381_PART_4_LINE_111, "0"),
            (RC381_PART_4_LINE_112, "0"),
            (RC381_PART_4_LINE_113, "0"),
            (RC381_PART_4_LINE_115, "0"),
            (RC381_PART_4_LINE_125, "136.00"),
            (RC381_PART_4_LINE_128, "136.00"),
            (RC381_PART_4_LINE_129, "272.00"),
        ),
    )


# The final selection and the T1 lines.


def test_return_fz_final_selection_takes_part_4_results_as_lines_70_and_83_are_above_zero() -> None:
    rc381 = form_fz()

    assert rc381.get(RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS).value == D("3470.51")
    assert rc381.get(RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS).value == D("938.00")
    assert rc381.get(RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS).value == D("272.00")
    assert rc381.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3470.51")
    assert rc381.get(RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("938.00")


def test_return_fz_t1_line_30800_and_on428_line_58240_are_3470_51() -> None:
    # ON428 line 58240 "Amount from line 30800 of your return" reads the same T1 line.
    assert return_fz().get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3470.51")


def test_return_fz_t1_line_22215_is_938_00() -> None:
    assert return_fz().get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("938.00")


def test_return_fz_t1_line_44800_is_zero_as_line_91_of_part_4_is_nil() -> None:
    assert return_fz().get(CPP_OVERPAYMENT).value == D("0")


def test_return_fz_t1_line_42100_is_272_00() -> None:
    assert return_fz().get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("272.00")


def test_return_fz_t1_line_31000_is_zero_as_line_84_of_part_4_is_nil() -> None:
    assert return_fz().get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D(
        "0"
    )


def test_return_fz_t1_line_22200_is_272_00() -> None:
    assert return_fz().get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("272.00")


def test_return_fz_net_income_is_80000_less_the_two_enhanced_deductions() -> None:
    worksheet = return_fz()

    assert worksheet.get(TOTAL_INCOME).value == D("80000.00")
    # 80000.00 less 938.00 (line 22215) and 272.00 (line 22200) is 78790.00.
    assert worksheet.get(NET_INCOME).value == D("78790.00")


def test_return_fz_the_tax_and_the_balance_are_the_engines() -> None:
    worksheet = return_fz()

    assert worksheet.get(NET_FEDERAL_TAX).value == D("9498.00")
    assert worksheet.get(ONTARIO_TAX).value == D("4917.56")
    assert worksheet.get(TOTAL_PAYABLE).value == D("14687.56")
    # The income tax deducted (13000.00) and the CPP overpayment of line 44800 (0.00).
    assert worksheet.get(TOTAL_CREDITS).value == D("13000.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("1687.56")
