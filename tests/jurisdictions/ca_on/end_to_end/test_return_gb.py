"""CA-ON 2025 end to end: return gb (the worked example of Form RC381 on the branch where line 3
of Part 3 is under the basic exemption: a T4 for Ontario employment and a T4 for Quebec
employment, 3400 in all, and a CPT20 election on 67850 of employment earnings not shown on a T4,
with Part 4 completed and carried to the T1 lines)."""

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
    RC381_PART_3_LINE_15,
    RC381_PART_3_LINE_16,
    RC381_PART_3_LINE_18,
    RC381_PART_3_LINE_27,
    RC381_PART_3_LINE_28,
    RC381_PART_3_LINE_29,
    RC381_PART_3_LINE_30,
    RC381_PART_3_LINE_31,
    RC381_PART_3_LINE_36,
    RC381_PART_3_LINE_61,
    RC381_PART_3_LINE_69,
    RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
    RC381_PART_4_LINE_4,
    RC381_PART_4_LINE_26,
    RC381_PART_4_LINE_59,
    RC381_PART_4_LINE_61,
    RC381_PART_4_LINE_62,
    RC381_PART_4_LINE_65,
    RC381_PART_4_LINE_68,
    RC381_PART_4_LINE_69,
    RC381_PART_4_LINE_70,
    RC381_PART_4_LINE_74,
    RC381_PART_4_LINE_77,
    RC381_PART_4_LINE_80,
    RC381_PART_4_LINE_83,
    RC381_PART_4_LINE_84,
    RC381_PART_4_LINE_85,
    RC381_PART_4_LINE_86,
    RC381_PART_4_LINE_87,
    RC381_PART_4_LINE_88,
    RC381_PART_4_LINE_89,
    RC381_PART_4_LINE_90,
    RC381_PART_4_LINE_111,
    RC381_PART_4_LINE_112,
    RC381_PART_4_LINE_113,
    RC381_PART_4_LINE_114,
    RC381_PART_4_LINE_115,
    RC381_PART_4_LINE_121,
    RC381_PART_4_LINE_124,
    RC381_PART_4_LINE_125,
    RC381_PART_4_LINE_127,
    RC381_PART_4_LINE_128,
    RC381_PART_4_LINE_129,
    RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, assert_values, run


def run_gb(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return GB's inputs (`returns/2025_return_gb.yaml`): employment income of 3400 on two T4s, an
    Ontario T4 (box 26 of 3000, box 16 and box 16A of 0) and a Quebec T4 (box 26 of 400, box 17 and
    box 17A of 0), with 12 months for CPP and QPP, and the CPT20 election earnings of Part 4 line 2
    (67850). The return carries one Form RC381 and no Schedule 8."""
    arguments: dict[str, Any] = {
        "cpp_months": 12,
        "qpp_months": 12,
        "t2204_insurable_earnings": "3400",
        "t2204_premiums_deducted": "55.76",
        "t4_cpp_pensionable_earnings_outside_quebec": "3000",
        "t4_qpp_pensionable_earnings_in_quebec": "400",
        "cpp_t4_base_and_first_additional_contributions": "0",
        "cpt20_earnings": "67850",
        "income_tax_deducted": "3400",
        "schedule_8_copies": 0,
        "rc381_copies": 1,
    }
    return run("3400", (), "0", "0", "0", "0", "0", **{**arguments, **overrides})


def form_gb(**overrides: Any) -> Worksheet:
    (rc381,) = run_gb(**overrides)["ca/rc381"]
    return rc381


def return_gb(**overrides: Any) -> Worksheet:
    (worksheet,) = run_gb(**overrides)["ca-on/return"]
    return worksheet


def test_return_gb_carries_form_rc381_and_no_schedule_8() -> None:
    result = run_gb()

    assert result["ca/schedule_8"] == ()
    assert len(result["ca/rc381"]) == 1


# Part 2.


def test_return_gb_part_2_line_b_is_12_and_the_twelve_month_row() -> None:
    rc381 = form_gb()

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


def test_return_gb_part_3_line_3_is_3400_and_line_6_is_0_88235() -> None:
    rc381 = form_gb()

    assert rc381.get(RC381_PART_3_LINE_3).value == D("3400")
    # 3000 divided by 3400 is 0.882352..., which is 0.88235 to the fifth decimal place.
    assert rc381.get(RC381_PART_3_LINE_6).value == Rate(D("0.88235"))


def test_return_gb_part_3_lines_7_to_10_are_the_table_amounts_times_line_6() -> None:
    assert_values(
        form_gb(),
        (
            (RC381_PART_3_LINE_7, "71646.82"),
            (RC381_PART_3_LINE_8, "62911.56"),
            (RC381_PART_3_LINE_9, "3088.23"),
            (RC381_PART_3_LINE_10, "8735.27"),
        ),
    )


def test_return_gb_line_3_not_above_line_c_puts_line_11_on_line_16() -> None:
    # Line 3 (3400) is not more than line C (71300), so lines 12 to 15 are not completed and line 11
    # goes straight to line 16. Line 15 is computed as 0 (not used); line 18 is 3000 less 3088.23,
    # and a negative amount is "0".
    rc381 = form_gb()

    assert_values(
        rc381,
        (
            (RC381_PART_3_LINE_11, "3000"),
            (RC381_PART_3_LINE_15, "0"),
            (RC381_PART_3_LINE_16, "3000"),
            (RC381_PART_3_LINE_18, "0"),
        ),
    )


def test_return_gb_part_3_lines_27_to_31_and_36_the_qpp_side_on_the_quebec_slip() -> None:
    # Line 31 is the lesser of line 2 (the Quebec 400) and line 27; line 3 is not more than line G,
    # so line 31 goes to line 36.
    assert_values(
        form_gb(),
        (
            (RC381_PART_3_LINE_27, "9553.18"),
            (RC381_PART_3_LINE_28, "8388.44"),
            (RC381_PART_3_LINE_29, "411.77"),
            (RC381_PART_3_LINE_30, "1164.73"),
            (RC381_PART_3_LINE_31, "400"),
            (RC381_PART_3_LINE_36, "400"),
        ),
    )


# Part 3, the totals and the branch.


def test_return_gb_part_3_lines_61_and_69_are_0_so_part_3b_is_the_path() -> None:
    # Line 61 is 0, so the Part 4 zero branch applies (lines 6 to 24 are not completed). Line 69 is
    # 0 (not negative, so the CPT20 election continues at Part 4 and Part 3b is completed).
    rc381 = form_gb()

    assert rc381.get(RC381_PART_3_LINE_61).value == D("0")
    assert rc381.get(RC381_PART_3_LINE_69).value == D("0")


# Part 4, the first half and the earnings.


def test_return_gb_part_4_line_4_is_the_cpt20_earnings_and_line_26_is_line_5() -> None:
    # Line 4 is 0 + 67850 + 0. Line 5 is 0, and with line 61 of Part 3 at "0" it is entered on
    # line 26 (the zero branch).
    rc381 = form_gb()

    assert rc381.get(RC381_PART_4_LINE_4).value == D("67850")
    assert rc381.get(RC381_PART_4_LINE_26).value == D("0")


def test_return_gb_part_4_lines_59_to_62_the_earnings_subject_to_contributions() -> None:
    assert_values(
        form_gb(),
        (
            (RC381_PART_4_LINE_59, "67800.00"),
            (RC381_PART_4_LINE_61, "67800.00"),
            (RC381_PART_4_LINE_62, "67800.00"),
        ),
    )


def test_return_gb_part_4_lines_65_68_69_and_70_when_line_3_is_under_the_basic_exemption() -> None:
    # Line 3 of Part 3 (3400) is less than line 58 (3500), so lines 63 to 69 are completed: line 65
    # is 3500 less 3400, line 68 is 67850 less 67800 and line 69 is 100 less 50. Line 70 is 67800
    # less 50.
    assert_values(
        form_gb(),
        (
            (RC381_PART_4_LINE_65, "100.00"),
            (RC381_PART_4_LINE_68, "50.00"),
            (RC381_PART_4_LINE_69, "50.00"),
            (RC381_PART_4_LINE_70, "67750.00"),
        ),
    )


def test_return_gb_part_4_line_74_is_not_above_line_57_so_line_83_is_0() -> None:
    # Line 74 (71250) is not more than line 57 (71300), so lines 75 to 83 are not completed.
    assert_values(
        form_gb(),
        (
            (RC381_PART_4_LINE_74, "71250"),
            (RC381_PART_4_LINE_83, "0"),
        ),
    )


def test_return_gb_part_4_lines_77_and_80_are_computed_but_not_used() -> None:
    # The engine computes lines 77 (9900 less 0) and 80 (67850 less 100); they are not used
    # because line 74 is not above line 57.
    assert_values(
        form_gb(),
        (
            (RC381_PART_4_LINE_77, "9900.00"),
            (RC381_PART_4_LINE_80, "67750.00"),
        ),
    )


# Part 4, the contributions on the self-employment income and other earnings.


def test_return_gb_part_4_lines_84_to_90_the_cpp_payable_on_the_election() -> None:
    # Line 84 is 67750 x 9.9% = 6707.25 and line 85 is 67750 x 2% = 1355.00; line 86 is 0 (line 83
    # is 0), so line 88 is 8062.25 and line 90 is 8062.25, line 42100 of the return.
    assert_values(
        form_gb(),
        (
            (RC381_PART_4_LINE_84, "6707.25"),
            (RC381_PART_4_LINE_85, "1355.00"),
            (RC381_PART_4_LINE_86, "0"),
            (RC381_PART_4_LINE_87, "1355.00"),
            (RC381_PART_4_LINE_88, "8062.25"),
            (RC381_PART_4_LINE_89, "0"),
            (RC381_PART_4_LINE_90, "8062.25"),
        ),
    )
    assert form_gb().get(RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS).value == D("67750")


def test_return_gb_part_4_lines_111_to_115_the_base_contributions_on_the_election() -> None:
    # Line 111 is line 84 x 50% (3353.63, rounded half up; line 31000 of the return) and line 112 is
    # line 85 x 50%. Line 114 is 0 (line 69 of Part 3 is not positive).
    assert_values(
        form_gb(),
        (
            (RC381_PART_4_LINE_111, "3353.63"),
            (RC381_PART_4_LINE_112, "677.50"),
            (RC381_PART_4_LINE_113, "4031.13"),
            (RC381_PART_4_LINE_114, "0"),
            (RC381_PART_4_LINE_115, "4031.13"),
        ),
    )


def test_return_gb_part_4_lines_121_to_129_the_deduction_on_the_election() -> None:
    # Line 127 is not used (line 115 is positive), so line 128 is line 126, 0.
    assert_values(
        form_gb(),
        (
            (RC381_PART_4_LINE_121, "3353.63"),
            (RC381_PART_4_LINE_124, "677.50"),
            (RC381_PART_4_LINE_125, "0"),
            (RC381_PART_4_LINE_127, "0"),
            (RC381_PART_4_LINE_128, "0"),
            (RC381_PART_4_LINE_129, "4708.63"),
        ),
    )


# The final selection and the T1 lines.


def test_return_gb_final_selection_takes_part_4_results_as_line_70_is_above_zero() -> None:
    rc381 = form_gb()

    assert rc381.get(RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS).value == D("0")
    assert rc381.get(RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS).value == D("0")
    assert rc381.get(RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS).value == D("8062.25")
    assert rc381.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("0")
    assert rc381.get(RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("0")


def test_return_gb_t1_line_30800_and_line_22215_are_zero() -> None:
    worksheet = return_gb()

    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("0")
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("0")


def test_return_gb_t1_line_44800_is_zero_as_line_90_is_positive() -> None:
    assert return_gb().get(CPP_OVERPAYMENT).value == D("0")


def test_return_gb_t1_line_42100_is_8062_25() -> None:
    assert return_gb().get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("8062.25")


def test_return_gb_t1_line_31000_and_line_22200_are_the_election_contributions() -> None:
    worksheet = return_gb()

    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D(
        "3353.63"
    )
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("4708.63")


def test_return_gb_net_income_is_0_as_the_deduction_exceeds_the_employment_income() -> None:
    # Total income is 3400 (the CPT20 earnings are not added); 3400 less 4708.63 is negative, so
    # net income is 0 (the engine's figure).
    worksheet = return_gb()

    assert worksheet.get(TOTAL_INCOME).value == D("3400.00")
    assert worksheet.get(NET_INCOME).value == D("0")


def test_return_gb_the_tax_and_the_refund_are_the_engines() -> None:
    worksheet = return_gb()

    assert worksheet.get(NET_FEDERAL_TAX).value == D("0.00")
    assert worksheet.get(ONTARIO_TAX).value == D("0.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("8062.25")
    # The income tax deducted (3400.00, a chosen figure) and 108.00 of Canada workers
    # benefit (engine figure).
    assert worksheet.get(TOTAL_CREDITS).value == D("3508.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("4554.25")
