"""CA-ON 2025 end to end: return fa (the worked example of Form RC381 with Part 4 completed: a T4
for Ontario employment and a T4 for Quebec employment with the box 16A and 17A amounts, and a
CPT20 election on employment earnings, carried to the T1 lines)."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
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
    RC381_PART_3_LINE_78,
    RC381_PART_3_LINE_79,
    RC381_PART_3_LINE_80,
    RC381_PART_3_LINE_81,
    RC381_PART_3_LINE_82,
    RC381_PART_3_LINE_83,
    RC381_PART_3_LINE_85,
    RC381_PART_3_LINE_86,
    RC381_PART_3_LINE_87,
    RC381_PART_3_LINE_87_DIFFERENCE,
    RC381_PART_3_LINE_88,
    RC381_PART_3_LINE_89,
    RC381_PART_3_LINE_92,
    RC381_PART_3_LINE_93,
    RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
    RC381_PART_4_LINE_4,
    RC381_PART_4_LINE_13,
    RC381_PART_4_LINE_14,
    RC381_PART_4_LINE_17,
    RC381_PART_4_LINE_17A,
    RC381_PART_4_LINE_20,
    RC381_PART_4_LINE_21,
    RC381_PART_4_LINE_21_LESSER,
    RC381_PART_4_LINE_22,
    RC381_PART_4_LINE_23,
    RC381_PART_4_LINE_23_LESSER,
    RC381_PART_4_LINE_23_MULTIPLIED,
    RC381_PART_4_LINE_24,
    RC381_PART_4_LINE_24_LESSER,
    RC381_PART_4_LINE_25A,
    RC381_PART_4_LINE_26,
    RC381_PART_4_LINE_27,
    RC381_PART_4_LINE_32,
    RC381_PART_4_LINE_33,
    RC381_PART_4_LINE_34,
    RC381_PART_4_LINE_35A,
    RC381_PART_4_LINE_35AB,
    RC381_PART_4_LINE_35AB_FROM_LINE_20,
    RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO,
    RC381_PART_4_LINE_36,
    RC381_PART_4_LINE_40,
    RC381_PART_4_LINE_41,
    RC381_PART_4_LINE_42,
    RC381_PART_4_LINE_46,
    RC381_PART_4_LINE_46_DIFFERENCE,
    RC381_PART_4_LINE_47,
    RC381_PART_4_LINE_51,
    RC381_PART_4_LINE_51_DIFFERENCE,
    RC381_PART_4_LINE_52,
    RC381_PART_4_LINE_53,
    RC381_PART_4_LINE_56,
    RC381_PART_4_LINE_59,
    RC381_PART_4_LINE_61,
    RC381_PART_4_LINE_62,
    RC381_PART_4_LINE_70,
    RC381_PART_4_LINE_74,
    RC381_PART_4_LINE_76,
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
    RC381_PART_4_LINE_95,
    RC381_PART_4_LINE_96,
    RC381_PART_4_LINE_97,
    RC381_PART_4_LINE_98,
    RC381_PART_4_LINE_99,
    RC381_PART_4_LINE_100,
    RC381_PART_4_LINE_102,
    RC381_PART_4_LINE_103,
    RC381_PART_4_LINE_104,
    RC381_PART_4_LINE_104_DIFFERENCE,
    RC381_PART_4_LINE_105,
    RC381_PART_4_LINE_106,
    RC381_PART_4_LINE_109,
    RC381_PART_4_LINE_110,
    RC381_PART_4_LINE_111,
    RC381_PART_4_LINE_112,
    RC381_PART_4_LINE_113,
    RC381_PART_4_LINE_115,
    RC381_PART_4_LINE_121,
    RC381_PART_4_LINE_124,
    RC381_PART_4_LINE_125,
    RC381_PART_4_LINE_128,
    RC381_PART_4_LINE_129,
    RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_fa(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return FA's inputs (`returns/2025_return_fa.yaml`): employment income of 80000 on a T4 for
    Ontario employment (box 26 of 30000, box 16 of 650.00 and box 16A of 140.00) and a T4 for
    Quebec employment (box 26 of 50000, box 17 of 3200.00 and box 17A of 440.00), with 12 months
    for CPP and QPP, and the CPT20 election earnings of Part 4 lines 2 and 3 (3000 and 2000). The
    return carries one Form RC381 and no Schedule 8."""
    arguments: dict[str, Any] = {
        "cpp_months": 12,
        "qpp_months": 12,
        "t4_cpp_pensionable_earnings_outside_quebec": "30000",
        "t4_qpp_pensionable_earnings_in_quebec": "50000",
        "cpp_t4_base_and_first_additional_contributions": "650.00",
        "t4_cpp_second_additional_box_16a": "140.00",
        "t4_qpp_contributions_box_17": "3200.00",
        "t4_qpp_second_additional_box_17a": "440.00",
        "cpt20_earnings": "3000",
        "cpt20_t4_earnings": "2000",
        "income_tax_deducted": "13000",
        "schedule_8_copies": 0,
        "rc381_copies": 1,
    }
    return run("80000", (), "0", "0", "0", "0", "0", **{**arguments, **overrides})


def form_fa(**overrides: Any) -> Worksheet:
    (rc381,) = run_fa(**overrides)["ca/rc381"]
    return rc381


def return_fa(**overrides: Any) -> Worksheet:
    (worksheet,) = run_fa(**overrides)["ca-on/return"]
    return worksheet


def assert_values(worksheet: Worksheet, expected: tuple[tuple[Any, str], ...]) -> None:
    for kind, value in expected:
        assert worksheet.get(kind).value == D(value), kind.identifier


def test_return_fa_carries_form_rc381_and_no_schedule_8() -> None:
    result = run_fa()

    assert result["ca/schedule_8"] == ()
    assert len(result["ca/rc381"]) == 1


# Part 2.


def test_return_fa_part_2_lines_b_g_h_i_j_are_the_twelve_month_row() -> None:
    rc381 = form_fa()

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


def test_return_fa_part_3_line_3_is_80000_and_line_6_is_0_37500() -> None:
    rc381 = form_fa()

    assert rc381.get(RC381_PART_3_LINE_3).value == D("80000")
    # 30000 divided by 80000 is exactly 0.375, which is 0.37500 to the fifth decimal place.
    assert rc381.get(RC381_PART_3_LINE_6).value == Rate(D("0.37500"))


def test_return_fa_part_3_lines_7_to_10_are_the_table_amounts_times_line_6() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_3_LINE_7, "30450.00"),
            (RC381_PART_3_LINE_8, "26737.50"),
            (RC381_PART_3_LINE_9, "1312.50"),
            (RC381_PART_3_LINE_10, "3712.50"),
        ),
    )


def test_return_fa_line_3_above_line_c_completes_lines_12_to_15() -> None:
    # Line 3 (80000) is more than line C (71300), so lines 12 to 15 are completed: line 14 is
    # 30000.00 less 26737.50, and line 15 is the lesser of line 10 (3712.50) and line 14.
    rc381 = form_fa()

    assert_values(
        rc381,
        (
            (RC381_PART_3_LINE_11, "30000"),
            (RC381_PART_3_LINE_14, "3262.50"),
            (RC381_PART_3_LINE_15, "3262.50"),
            (RC381_PART_3_LINE_15_LESSER, "3262.50"),
            (RC381_PART_3_LINE_16, "26737.50"),
            (RC381_PART_3_LINE_18, "25425.00"),
        ),
    )


def test_return_fa_the_cpp_side_of_part_3_lines_20_to_26() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_3_LINE_20, "540.76"),
            (RC381_PART_3_LINE_21, "109.24"),
            (RC381_PART_3_LINE_22, "1258.54"),
            (RC381_PART_3_LINE_23, "254.25"),
            (RC381_PART_3_LINE_24, "1512.79"),
            (RC381_PART_3_LINE_26, "130.50"),
        ),
    )


# Part 3, the QPP side.


def test_return_fa_the_qpp_side_of_part_3_lines_27_to_31() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_3_LINE_27, "50750.00"),
            (RC381_PART_3_LINE_28, "44562.50"),
            (RC381_PART_3_LINE_29, "2187.50"),
            (RC381_PART_3_LINE_30, "6187.50"),
            (RC381_PART_3_LINE_31, "50000"),
        ),
    )


def test_return_fa_line_3_above_line_g_completes_lines_32_to_35() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_3_LINE_34, "5437.50"),
            (RC381_PART_3_LINE_35, "5437.50"),
            (RC381_PART_3_LINE_35_LESSER, "5437.50"),
            (RC381_PART_3_LINE_36, "44562.50"),
        ),
    )


def test_return_fa_the_qpp_side_of_part_3_lines_38_to_46() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_3_LINE_38, "42375.00"),
            (RC381_PART_3_LINE_40, "2700.00"),
            (RC381_PART_3_LINE_41, "500.00"),
            (RC381_PART_3_LINE_42, "2288.25"),
            (RC381_PART_3_LINE_43, "423.75"),
            (RC381_PART_3_LINE_44, "2712.00"),
            (RC381_PART_3_LINE_46, "217.50"),
        ),
    )


# Part 3, the totals.


def test_return_fa_part_3_totals_on_lines_49_to_69() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_3_LINE_49, "3240.76"),
            (RC381_PART_3_LINE_52, "3546.79"),
            (RC381_PART_3_LINE_53, "-306.03"),
            (RC381_PART_3_LINE_56, "609.24"),
            (RC381_PART_3_LINE_59, "678.00"),
            (RC381_PART_3_LINE_60, "-68.76"),
            (RC381_PART_3_LINE_61, "-374.79"),
            (RC381_PART_3_LINE_64, "580.00"),
            (RC381_PART_3_LINE_67, "348.00"),
            (RC381_PART_3_LINE_68, "232.00"),
            (RC381_PART_3_LINE_69, "-142.79"),
        ),
    )


def test_return_fa_line_69_is_negative_so_part_3b_is_the_path_for_employment_income() -> None:
    # Line 69 is -142.79: Part 3a (line 70 to 74) is not the path. The election makes Part 4 the
    # continuation, and Part 4 supplies the results (see the final selection below).
    rc381 = form_fa()

    assert rc381.get(RC381_PART_3_LINE_73).value == D("1026.00")
    assert rc381.get(RC381_PART_3_LINE_69).value == D("-142.79")


# Part 3b.


def test_return_fa_part_3b_lines_75_to_81() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_3_LINE_75, "3240.76"),
            (RC381_PART_3_LINE_76, "306.03"),
            (RC381_PART_3_LINE_78, "306.03"),
            (RC381_PART_3_LINE_79, "3240.76"),
            (RC381_PART_3_LINE_80, "232.00"),
            (RC381_PART_3_LINE_81, "3472.76"),
        ),
    )


def test_return_fa_part_3b_lines_82_to_93() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_3_LINE_82, "609.24"),
            (RC381_PART_3_LINE_83, "68.76"),
            (RC381_PART_3_LINE_85, "68.76"),
            (RC381_PART_3_LINE_86, "609.24"),
            (RC381_PART_3_LINE_87, "0"),
            (RC381_PART_3_LINE_87_DIFFERENCE, "0.00"),
            (RC381_PART_3_LINE_88, "609.24"),
            (RC381_PART_3_LINE_89, "348.00"),
            (RC381_PART_3_LINE_92, "348.00"),
            (RC381_PART_3_LINE_93, "957.24"),
        ),
    )


# Part 4, the first half.


def test_return_fa_part_4_lines_4_to_27_with_line_61_negative() -> None:
    # Line 61 of Part 3 is negative, so lines 6 to 12 are not completed and line 13 is line 5.
    # Line 22 is a rate: 1, as line 17A (862.79) is more than line 14 (374.79).
    rc381 = form_fa()

    assert rc381.get(RC381_PART_4_LINE_22).value == Rate(D("1"))
    assert_values(
        rc381,
        (
            (RC381_PART_4_LINE_4, "5000"),
            (RC381_PART_4_LINE_13, "650.00"),
            (RC381_PART_4_LINE_14, "374.79"),
            (RC381_PART_4_LINE_17, "-862.79"),
            (RC381_PART_4_LINE_17A, "862.79"),
            (RC381_PART_4_LINE_20, "488.00"),
            (RC381_PART_4_LINE_21, "488.00"),
            (RC381_PART_4_LINE_21_LESSER, "488.00"),
            (RC381_PART_4_LINE_23, "232.00"),
            (RC381_PART_4_LINE_23_LESSER, "232.00"),
            (RC381_PART_4_LINE_23_MULTIPLIED, "232.00"),
            (RC381_PART_4_LINE_24, "232.00"),
            (RC381_PART_4_LINE_24_LESSER, "232.00"),
            (RC381_PART_4_LINE_25A, "488.00"),
            (RC381_PART_4_LINE_26, "1370.00"),
            (RC381_PART_4_LINE_27, "23025.21"),
        ),
    )


# Part 4, the second half.


def test_return_fa_part_4_lines_32_to_56_the_qpp_side_and_the_second_additional() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_4_LINE_32, "3200.00"),
            (RC381_PART_4_LINE_33, "374.79"),
            (RC381_PART_4_LINE_34, "374.79"),
            (RC381_PART_4_LINE_35A, "-488.00"),
            (RC381_PART_4_LINE_35AB, "-488.00"),
            (RC381_PART_4_LINE_35AB_FROM_LINE_20, "-488.00"),
            (RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO, "-488.00"),
            (RC381_PART_4_LINE_36, "232.00"),
            (RC381_PART_4_LINE_40, "2712.00"),
            (RC381_PART_4_LINE_41, "42375.00"),
            (RC381_PART_4_LINE_42, "65400.21"),
            (RC381_PART_4_LINE_46, "9.50"),
            (RC381_PART_4_LINE_46_DIFFERENCE, "9.50"),
            (RC381_PART_4_LINE_47, "130.50"),
            (RC381_PART_4_LINE_51, "222.50"),
            (RC381_PART_4_LINE_51_DIFFERENCE, "222.50"),
            (RC381_PART_4_LINE_52, "217.50"),
            (RC381_PART_4_LINE_53, "348.00"),
            (RC381_PART_4_LINE_56, "348.00"),
        ),
    )


# Part 4, the earnings and the self-employment contributions.


def test_return_fa_part_4_lines_59_to_90_the_earnings_and_the_contributions() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_4_LINE_59, "67800.00"),
            (RC381_PART_4_LINE_61, "2399.79"),
            (RC381_PART_4_LINE_62, "2399.79"),
            (RC381_PART_4_LINE_70, "2399.79"),
            (RC381_PART_4_LINE_74, "85000"),
            (RC381_PART_4_LINE_76, "8700.00"),
            (RC381_PART_4_LINE_77, "1200.00"),
            (RC381_PART_4_LINE_80, "5000"),
            (RC381_PART_4_LINE_82, "2600.21"),
            (RC381_PART_4_LINE_83, "1200.00"),
            (RC381_PART_4_LINE_83_LESSER, "1200.00"),
            (RC381_PART_4_LINE_84, "237.58"),
            (RC381_PART_4_LINE_85, "48.00"),
            (RC381_PART_4_LINE_86, "96.00"),
            (RC381_PART_4_LINE_87, "144.00"),
            (RC381_PART_4_LINE_88, "381.58"),
            (RC381_PART_4_LINE_90, "381.58"),
        ),
    )
    assert form_fa().get(RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS).value == D("3599.79")


# Part 4, the employment income base and enhanced contributions.


def test_return_fa_part_4_lines_92_to_98_the_base_through_employment_income() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_4_LINE_92, "3240.76"),
            (RC381_PART_4_LINE_93, "306.03"),
            (RC381_PART_4_LINE_95, "306.03"),
            (RC381_PART_4_LINE_96, "3240.76"),
            (RC381_PART_4_LINE_97, "232.00"),
            (RC381_PART_4_LINE_98, "3472.76"),
        ),
    )


def test_return_fa_part_4_lines_99_to_110_the_enhanced_through_employment_income() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_4_LINE_99, "609.24"),
            (RC381_PART_4_LINE_100, "68.76"),
            (RC381_PART_4_LINE_102, "68.76"),
            (RC381_PART_4_LINE_103, "609.24"),
            (RC381_PART_4_LINE_104, "0"),
            (RC381_PART_4_LINE_104_DIFFERENCE, "0.00"),
            (RC381_PART_4_LINE_105, "609.24"),
            (RC381_PART_4_LINE_106, "348.00"),
            (RC381_PART_4_LINE_109, "348.00"),
            (RC381_PART_4_LINE_110, "957.24"),
        ),
    )


# Part 4, the self-employment and other earnings base and enhanced contributions.


def test_return_fa_part_4_lines_111_to_129_the_contributions_on_the_election() -> None:
    assert_values(
        form_fa(),
        (
            (RC381_PART_4_LINE_111, "118.79"),
            (RC381_PART_4_LINE_112, "24.00"),
            (RC381_PART_4_LINE_113, "142.79"),
            (RC381_PART_4_LINE_115, "142.79"),
            (RC381_PART_4_LINE_121, "118.79"),
            (RC381_PART_4_LINE_124, "24.00"),
            (RC381_PART_4_LINE_125, "48.00"),
            (RC381_PART_4_LINE_128, "48.00"),
            (RC381_PART_4_LINE_129, "262.79"),
        ),
    )


# The final selection and the T1 lines.


def test_return_fa_final_selection_takes_part_4_results_as_lines_70_and_83_are_above_zero() -> None:
    rc381 = form_fa()

    assert rc381.get(RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS).value == D("3472.76")
    assert rc381.get(RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS).value == D("957.24")
    assert rc381.get(RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS).value == D("381.58")
    assert rc381.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3472.76")
    assert rc381.get(RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("957.24")


def test_return_fa_t1_line_30800_and_on428_line_58240_are_3472_76() -> None:
    # ON428 line 58240 "Amount from line 30800 of your return" reads the same T1 line.
    assert return_fa().get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3472.76")


def test_return_fa_t1_line_22215_is_957_24() -> None:
    assert return_fa().get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("957.24")


def test_return_fa_t1_line_44800_is_zero_as_line_90_is_positive() -> None:
    assert return_fa().get(CPP_OVERPAYMENT).value == D("0")


def test_return_fa_t1_line_42100_is_381_58() -> None:
    assert return_fa().get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("381.58")


def test_return_fa_t1_line_31000_and_line_22200_are_the_election_contributions() -> None:
    worksheet = return_fa()

    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D(
        "118.79"
    )
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("262.79")


def test_return_fa_net_income_is_80000_less_the_two_enhanced_deductions() -> None:
    worksheet = return_fa()

    assert worksheet.get(TOTAL_INCOME).value == D("80000.00")
    # 80000.00 less 957.24 (line 22215) and 262.79 (line 22200) is 78779.97.
    assert worksheet.get(NET_INCOME).value == D("78779.97")


def test_return_fa_the_tax_and_the_balance_are_the_engines() -> None:
    worksheet = return_fa()

    assert worksheet.get(NET_FEDERAL_TAX).value == D("9478.39")
    assert worksheet.get(ONTARIO_TAX).value == D("4910.53")
    assert worksheet.get(TOTAL_PAYABLE).value == D("14770.50")
    # The income tax deducted (13000.00) and the CPP overpayment of line 44800 (0.00).
    assert worksheet.get(TOTAL_CREDITS).value == D("13000.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("1770.50")
