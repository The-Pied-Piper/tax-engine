"""CA-ON 2025 end to end: return bo (Form RC381 Part 2, Part 3 lines 1 to 93, Part 4 lines 1 to
129 and the final selection of the results for the return)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.capabilities.amount_by_count import AmountForCount
from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.contribution_tier import TieredContribution
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InputBelowBoundError,
    NegativeArtifactError,
    NoAmountForCountError,
)
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.capabilities.amount_when_more import AmountWhenMore
from tax_engine.jurisdictions.ca.capabilities.apply_chosen_rate import ApplyChosenRate
from tax_engine.jurisdictions.ca.capabilities.choose_by_sign import ChooseBySign
from tax_engine.jurisdictions.ca.capabilities.count_at_least import CountAtLeast
from tax_engine.jurisdictions.ca.capabilities.divided_by_rate import DividedByRate
from tax_engine.jurisdictions.ca.capabilities.lesser_of_when_positive import (
    LesserOfWhenPositive,
    LesserOfWhenPositiveInBrackets,
)
from tax_engine.jurisdictions.ca.capabilities.positive_part_of_negation import (
    PositivePartOfNegation,
)
from tax_engine.jurisdictions.ca.capabilities.ratio_truncated import (
    RatioTruncated,
    RatioTruncatedAtMostOne,
)
from tax_engine.jurisdictions.ca.catalog import (
    CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_BASE_CONTRIBUTIONS,
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_BASIC_EXEMPTION,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ENHANCED_CONTRIBUTIONS,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_OVERPAYMENT,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM,
    NET_INCOME,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_OVERPAYMENT,
    RC381_CPP_OVERPAYMENT_ON_RETURN,
    RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
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
    RC381_PART_3_LINE_90,
    RC381_PART_3_LINE_91,
    RC381_PART_3_LINE_92,
    RC381_PART_3_LINE_93,
    RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
    RC381_PART_4_LINE_4,
    RC381_PART_4_LINE_8,
    RC381_PART_4_LINE_11,
    RC381_PART_4_LINE_12,
    RC381_PART_4_LINE_13,
    RC381_PART_4_LINE_13_DIFFERENCE,
    RC381_PART_4_LINE_14,
    RC381_PART_4_LINE_17,
    RC381_PART_4_LINE_17A,
    RC381_PART_4_LINE_20,
    RC381_PART_4_LINE_21,
    RC381_PART_4_LINE_21_FROM_LINE_17,
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
    RC381_PART_4_LINE_31,
    RC381_PART_4_LINE_31_DIFFERENCE,
    RC381_PART_4_LINE_32,
    RC381_PART_4_LINE_33,
    RC381_PART_4_LINE_34,
    RC381_PART_4_LINE_35,
    RC381_PART_4_LINE_35A,
    RC381_PART_4_LINE_35AA,
    RC381_PART_4_LINE_35AA_FROM_LINE_17,
    RC381_PART_4_LINE_35AB,
    RC381_PART_4_LINE_35AB_FROM_LINE_20,
    RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO,
    RC381_PART_4_LINE_36,
    RC381_PART_4_LINE_38,
    RC381_PART_4_LINE_39,
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
    RC381_PART_4_LINE_54,
    RC381_PART_4_LINE_55,
    RC381_PART_4_LINE_56,
    RC381_PART_4_LINE_59,
    RC381_PART_4_LINE_61,
    RC381_PART_4_LINE_62,
    RC381_PART_4_LINE_65,
    RC381_PART_4_LINE_68,
    RC381_PART_4_LINE_69,
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
    RC381_PART_4_LINE_89,
    RC381_PART_4_LINE_89_FROM_LINE_69,
    RC381_PART_4_LINE_90,
    RC381_PART_4_LINE_91,
    RC381_PART_4_LINE_91_FROM_LINE_90,
    RC381_PART_4_LINE_92,
    RC381_PART_4_LINE_93,
    RC381_PART_4_LINE_94,
    RC381_PART_4_LINE_95,
    RC381_PART_4_LINE_96,
    RC381_PART_4_LINE_97,
    RC381_PART_4_LINE_98,
    RC381_PART_4_LINE_99,
    RC381_PART_4_LINE_100,
    RC381_PART_4_LINE_101,
    RC381_PART_4_LINE_102,
    RC381_PART_4_LINE_103,
    RC381_PART_4_LINE_104,
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
    RC381_PART_4_LINE_114,
    RC381_PART_4_LINE_115,
    RC381_PART_4_LINE_116,
    RC381_PART_4_LINE_116_LESSER,
    RC381_PART_4_LINE_118,
    RC381_PART_4_LINE_121,
    RC381_PART_4_LINE_124,
    RC381_PART_4_LINE_125,
    RC381_PART_4_LINE_127,
    RC381_PART_4_LINE_128,
    RC381_PART_4_LINE_129,
    RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS,
    REFUND_OR_BALANCE_OWING,
    SELF_EMPLOYED_CPP_BASE_CREDIT,
    SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE,
    SELF_EMPLOYED_CPP_DEDUCTION,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    compute_form,
    compute_with_schedule_8,
    routed_statement,
)


def return_bo(
    line_1: str = "30000",
    line_2: str = "40000",
    line_19: str = "1785.00",
    line_39: str = "2500.00",
    *,
    line_25: str = "0",
    line_45: str = "0",
    cpp_months: int = 12,
    qpp_months: int = 12,
    cpt20_earnings: str = "10000",
    cpt20_t4_earnings: str = "2500",
    net_partnership_income: str = "0",
    form: str = "ca/rc381",
    cpp_part_4_completed: int = 0,
    cpp_part_5_completed: int = 0,
    t4_cpp_slip_count: int | None = None,
    t4_qpp_slip_count: int | None = None,
) -> Worksheet:
    """Return BO's inputs (`returns/2025_return_bo.yaml`): employment income of 70000 on a T4 for
    Ontario employment (box 26 `line_1`, box 16 `line_19`, box 16A `line_25`) and a T4 for Quebec
    employment (box 26 `line_2`, box 17 `line_39`, box 17A `line_45`), and the CPT20 election
    earnings of Part 4 lines 2 and 3 (50373 and 50399).

    The return carries Form RC381 instead of Schedule 8 (the exclusive group `ca/cpp_calculation`),
    and the worksheet is that of the one Form RC381 unless `form` is the return's own form
    `ca-on/return`."""
    return compute_form(
        form,
        "70000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_months=cpp_months,
        qpp_months=qpp_months,
        t4_cpp_pensionable_earnings_outside_quebec=line_1,
        t4_qpp_pensionable_earnings_in_quebec=line_2,
        cpp_t4_base_and_first_additional_contributions=line_19,
        t4_cpp_second_additional_box_16a=line_25,
        t4_qpp_contributions_box_17=line_39,
        t4_qpp_second_additional_box_17a=line_45,
        cpt20_earnings=cpt20_earnings,
        cpt20_t4_earnings=cpt20_t4_earnings,
        net_partnership_income=net_partnership_income,
        income_tax_deducted="12000",
        cpp_part_4_completed=cpp_part_4_completed,
        cpp_part_5_completed=cpp_part_5_completed,
        t4_cpp_slip_count=t4_cpp_slip_count,
        t4_qpp_slip_count=t4_qpp_slip_count,
    )


# Part 2.


def test_return_bo_line_b_is_the_qpp_months_when_line_a_is_not_more() -> None:
    # Lines A and B are both 12 (chosen figures): "The number you enter on line A cannot be more
    # than the number you enter on line B." is met, and line B is passed on as entered.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_2_LINE_B).value == 12
    assert isinstance(worksheet.producer_of(RC381_PART_2_LINE_B), CountAtLeast)


def test_return_bo_line_b_may_be_more_than_line_a() -> None:
    # Line A is 6 and line B is 12 (the months differ when, for example, a CPP election to stop
    # contributing applies): line B is 12.
    worksheet = return_bo(cpp_months=6, qpp_months=12)

    assert worksheet.get(RC381_PART_2_LINE_B).value == 12


def test_return_bo_lines_g_to_j_are_the_row_of_the_table_for_12_months() -> None:
    # Line B is 12, the table's row "12": 71,300.00, 9,900.00, 81,200.00 and 3,500.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_2_LINE_G).value == D("71300.00")
    assert worksheet.get(RC381_PART_2_LINE_H).value == D("9900.00")
    assert worksheet.get(RC381_PART_2_LINE_I).value == D("81200.00")
    assert worksheet.get(RC381_PART_2_LINE_J).value == D("3500.00")
    for kind in (
        RC381_PART_2_LINE_G,
        RC381_PART_2_LINE_H,
        RC381_PART_2_LINE_I,
        RC381_PART_2_LINE_J,
    ):
        assert isinstance(worksheet.producer_of(kind), AmountForCount)


def test_return_bo_lines_g_to_j_read_line_b_and_lines_c_to_f_read_line_a() -> None:
    # Line A is 6: lines C to F are the row "6" (35,650.00, 4,950.00, 40,600.00 and 1,750.00),
    # the existing Schedule 8 lines. Line B is 12: lines G to J are the row "12".
    worksheet = return_bo(cpp_months=6, qpp_months=12)

    assert worksheet.get(CPP_MAXIMUM_PENSIONABLE_EARNINGS).value == D("35650.00")
    assert worksheet.get(CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM).value == D("4950.00")
    assert worksheet.get(CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS).value == D("40600.00")
    assert worksheet.get(CPP_BASIC_EXEMPTION).value == D("1750.00")
    assert worksheet.get(RC381_PART_2_LINE_G).value == D("71300.00")
    assert worksheet.get(RC381_PART_2_LINE_H).value == D("9900.00")
    assert worksheet.get(RC381_PART_2_LINE_I).value == D("81200.00")
    assert worksheet.get(RC381_PART_2_LINE_J).value == D("3500.00")


def test_return_bo_lines_g_to_j_for_6_months_when_both_months_are_6() -> None:
    # Lines A and B are 6 (equal is allowed): lines G to J are the row "6".
    worksheet = return_bo(cpp_months=6, qpp_months=6)

    assert worksheet.get(RC381_PART_2_LINE_G).value == D("35650.00")
    assert worksheet.get(RC381_PART_2_LINE_H).value == D("4950.00")
    assert worksheet.get(RC381_PART_2_LINE_I).value == D("40600.00")
    assert worksheet.get(RC381_PART_2_LINE_J).value == D("1750.00")


def test_return_bo_line_a_more_than_line_b_is_an_input_error() -> None:
    # "The number you enter on line A cannot be more than the number you enter on line B.": 12
    # months of CPP against 11 of QPP is refused, not corrected.
    with pytest.raises(InputBelowBoundError, match="qpp_months"):
        return_bo(cpp_months=12, qpp_months=11)


def test_return_bo_a_blank_line_b_is_an_input_error_when_line_a_is_filled() -> None:
    # A line B of 0 (left blank) is below line A's 12.
    with pytest.raises(InputBelowBoundError):
        return_bo(cpp_months=12, qpp_months=0)


def test_return_bo_a_line_b_without_a_row_in_the_table_is_refused() -> None:
    # The table has rows for 1 to 12 months: 13 is not below line A, but has no row.
    with pytest.raises(NoAmountForCountError):
        return_bo(cpp_months=12, qpp_months=13)


# Part 3, the ticket's example.


def test_return_bo_line_3_adds_lines_1_and_2() -> None:
    # Line 1 (50339) 30,000 plus line 2 (50329) 40,000 is 70,000.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_3).value == D("70000.00")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_3), Sum)


def test_return_bo_line_6_is_line_4_over_line_5_cut_at_the_fifth_decimal_place() -> None:
    # 30,000 / 70,000 = 0.4285714..., calculated to the fifth decimal place without rounding:
    # 0.42857 (rounding would give the same here, so see the next test for a tie that goes down).
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_6).value == Rate(D("0.42857"))
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_6), RatioTruncated)


def test_return_bo_line_6_is_cut_not_rounded() -> None:
    # 20,000 / 30,000 = 0.66666..., which rounding would make 0.66667.
    worksheet = return_bo(line_1="20000", line_2="10000", line_19="1190.00")

    assert worksheet.get(RC381_PART_3_LINE_6).value == Rate(D("0.66666"))


def test_return_bo_line_6_is_zero_when_there_are_no_pensionable_earnings() -> None:
    # Line 3 is 0, so line 6 is 0 and not an error.
    worksheet = return_bo(line_1="0", line_2="0", line_19="0")

    assert worksheet.get(RC381_PART_3_LINE_3).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_6).value == Rate(D("0"))


def test_return_bo_lines_7_to_10_are_the_table_amounts_times_line_6() -> None:
    # Line 6 is 0.42857. Line 7: line E 81,200.00 x 0.42857 = 34,799.884, 34,799.88; line 8: line
    # C 71,300.00 x 0.42857 = 30,557.041, 30,557.04; line 9: line F 3,500.00 x 0.42857 =
    # 1,499.995, 1,500.00 (half up); line 10: line D 9,900.00 x 0.42857 = 4,242.843, 4,242.84.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_7).value == D("34799.88")
    assert worksheet.get(RC381_PART_3_LINE_8).value == D("30557.04")
    assert worksheet.get(RC381_PART_3_LINE_9).value == D("1500.00")
    assert worksheet.get(RC381_PART_3_LINE_10).value == D("4242.84")


def test_return_bo_line_11_is_the_lesser_of_line_1_and_line_7() -> None:
    # The lesser of 30,000 and 34,799.88 is 30,000.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_11).value == D("30000.00")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_11), LesserOf)


def test_return_bo_line_14_is_line_11_less_line_8_and_not_below_zero() -> None:
    # 30,000.00 less 30,557.04 is negative, entered as "0".
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_14).value == D("0")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_14), SubtractNotBelowZero)


def test_return_bo_line_15_is_zero_when_line_3_is_not_more_than_line_c() -> None:
    # Line 3 (70,000.00) is not more than line C (71,300.00): "If not, enter the amount from line
    # 11 on line 16", so line 15 is 0 and line 16 is line 11 less 0 = 30,000.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_15_LESSER).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_15).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_16).value == D("30000.00")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_15), AmountWhenMore)
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_16), Subtract)


def test_return_bo_line_18_is_line_16_less_line_9() -> None:
    # 30,000.00 less 1,500.00 is 28,500.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_18).value == D("28500.00")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_18), SubtractNotBelowZero)


def test_return_bo_line_18_is_zero_when_line_9_is_more_than_line_16() -> None:
    # Line 1 is 1,000 and line 2 is 1,000: line 6 is 0.5, line 9 is 3,500.00 x 0.5 = 1,750.00, line
    # 11 is the lesser of 1,000 and 40,600.00, 1,000; line 3 (2,000) is not more than line C, so
    # line 15 is 0 and line 16 is 1,000. Line 16 less line 9 is negative, entered as "0", so lines
    # 22 and 23 are 0.00.
    worksheet = return_bo(line_1="1000", line_2="1000", line_19="50.00")

    assert worksheet.get(RC381_PART_3_LINE_9).value == D("1750.00")
    assert worksheet.get(RC381_PART_3_LINE_16).value == D("1000")
    assert worksheet.get(RC381_PART_3_LINE_18).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_22).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_23).value == D("0")


def test_return_bo_a_small_share_outside_quebec_scales_every_line_down() -> None:
    # Line 1 is 1,000 and line 2 is 99,000: line 3 is 100,000, line 6 is 0.01 and line 9 is 3,500.00
    # x 0.01 = 35.00. Line 7 is 812.00, so line 11 is the lesser of 1,000 and 812.00, 812.00. Line 3
    # is more than line C: line 14 is 812.00 less line 8 (713.00) = 99.00, line 15 is the lesser of
    # line 10 (99.00) and line 14 (99.00), 99.00, line 16 is 812.00 less 99.00 = 713.00 and line
    # 18 is 713.00 less 35.00 = 678.00.
    worksheet = return_bo(line_1="1000", line_2="99000", line_19="0")

    assert worksheet.get(RC381_PART_3_LINE_6).value == Rate(D("0.01"))
    assert worksheet.get(RC381_PART_3_LINE_9).value == D("35.00")
    assert worksheet.get(RC381_PART_3_LINE_15).value == D("99.00")
    assert worksheet.get(RC381_PART_3_LINE_16).value == D("713.00")
    assert worksheet.get(RC381_PART_3_LINE_18).value == D("678.00")
    assert worksheet.get(RC381_PART_3_LINE_26).value == D("3.96")


def test_return_bo_line_20_is_83_1933_percent_of_line_19() -> None:
    # 1,785.00 x 83.1933% = 1,485.0004, 1,485.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_20).value == D("1485.00")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_20), ApplyRate)


def test_return_bo_line_21_is_line_19_less_line_20() -> None:
    # 1,785.00 less 1,485.00 is 300.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_21).value == D("300.00")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_21), Subtract)


def test_return_bo_line_22_is_4_95_percent_of_line_18() -> None:
    # 28,500.00 x 4.95% = 1,410.75.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_22).value == D("1410.75")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_22), TieredContribution)


def test_return_bo_line_23_is_1_percent_of_line_18() -> None:
    # 28,500.00 x 1% = 285.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_23).value == D("285.00")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_23), TieredContribution)


def test_return_bo_line_24_adds_lines_22_and_23() -> None:
    # 1,410.75 plus 285.00 is 1,695.75.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_24).value == D("1695.75")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_24), Sum)


def test_return_bo_line_26_is_4_percent_of_line_15() -> None:
    # Line 15 is 0, so 0 x 4% is 0.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_26).value == D("0")
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_26), TieredContribution)


# Part 3 above line C.


def test_return_bo_above_line_c_lines_12_to_15_are_completed() -> None:
    # Line 1 is 50,000 and line 2 is 40,000: line 3 is 90,000.00, more than line C (71,300.00).
    # Line 6 = 50,000 / 90,000 = 0.555555... cut at 0.55555. Line 7 = 81,200.00 x 0.55555 =
    # 45,110.66 (45,110.660), line 8 = 71,300.00 x 0.55555 = 39,610.715, 39,610.72 (half up),
    # line 9 = 3,500.00 x 0.55555 = 1,944.425, 1,944.43, line 10 = 9,900.00 x 0.55555 = 5,499.945,
    # 5,499.95. Line 11 = the lesser of 50,000 and 45,110.66 = 45,110.66. Line 14 = 45,110.66 less
    # 39,610.72 = 5,499.94. Line 15 = the lesser of line 10 (5,499.95) and line 14 (5,499.94) =
    # 5,499.94. Line 16 = 45,110.66 less 5,499.94 = 39,610.72. Line 18 = 39,610.72 less 1,944.43 =
    # 37,666.29. Line 22 = 37,666.29 x 4.95% = 1,864.48 (1,864.4814), line 23 = 376.66, line 24 =
    # 2,241.14, line 26 = 5,499.94 x 4% = 219.9976, 220.00.
    worksheet = return_bo(line_1="50000", line_2="40000", line_19="2975.00")

    assert worksheet.get(RC381_PART_3_LINE_3).value == D("90000")
    assert worksheet.get(RC381_PART_3_LINE_6).value == Rate(D("0.55555"))
    assert worksheet.get(RC381_PART_3_LINE_7).value == D("45110.66")
    assert worksheet.get(RC381_PART_3_LINE_8).value == D("39610.72")
    assert worksheet.get(RC381_PART_3_LINE_9).value == D("1944.43")
    assert worksheet.get(RC381_PART_3_LINE_10).value == D("5499.95")
    assert worksheet.get(RC381_PART_3_LINE_11).value == D("45110.66")
    assert worksheet.get(RC381_PART_3_LINE_14).value == D("5499.94")
    assert worksheet.get(RC381_PART_3_LINE_15_LESSER).value == D("5499.94")
    assert worksheet.get(RC381_PART_3_LINE_15).value == D("5499.94")
    assert worksheet.get(RC381_PART_3_LINE_16).value == D("39610.72")
    assert worksheet.get(RC381_PART_3_LINE_18).value == D("37666.29")
    assert worksheet.get(RC381_PART_3_LINE_20).value == D("2475.00")
    assert worksheet.get(RC381_PART_3_LINE_21).value == D("500.00")
    assert worksheet.get(RC381_PART_3_LINE_22).value == D("1864.48")
    assert worksheet.get(RC381_PART_3_LINE_23).value == D("376.66")
    assert worksheet.get(RC381_PART_3_LINE_24).value == D("2241.14")
    assert worksheet.get(RC381_PART_3_LINE_26).value == D("220.00")


def test_return_bo_line_15_is_zero_when_line_3_is_exactly_line_c() -> None:
    # Line 1 is 30,000 and line 2 is 41,300: line 3 is 71,300, which is line C, not more. Line 6 is
    # 0.42075, line 8 is 29,999.48, so line 14 is 30,000 less 29,999.48 = 0.52 and the lesser of
    # lines 10 (4,165.43) and 14 is 0.52, but line 3 is not more than line C: line 15 is 0.
    worksheet = return_bo(line_1="30000", line_2="41300", line_19="0")

    assert worksheet.get(RC381_PART_3_LINE_14).value == D("0.52")
    assert worksheet.get(RC381_PART_3_LINE_15_LESSER).value == D("0.52")
    assert worksheet.get(RC381_PART_3_LINE_15).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_16).value == D("30000")
    assert worksheet.get(RC381_PART_3_LINE_18).value == D("28527.37")


def test_return_bo_line_15_is_the_lesser_when_line_3_is_one_dollar_more_than_line_c() -> None:
    # Line 2 of 41,301 makes line 3 71,301, more than line C: line 15 is 0.52, line 16 is 30,000
    # less 0.52 = 29,999.48 and line 18 is 29,999.48 less line 9 (1,472.63) = 28,526.85.
    worksheet = return_bo(line_1="30000", line_2="41301", line_19="0")

    assert worksheet.get(RC381_PART_3_LINE_15).value == D("0.52")
    assert worksheet.get(RC381_PART_3_LINE_16).value == D("29999.48")
    assert worksheet.get(RC381_PART_3_LINE_18).value == D("28526.85")


def test_return_bo_with_all_the_earnings_outside_quebec_line_6_is_1() -> None:
    # Line 1 is 80,000 and line 2 is 0: line 6 is 1, so lines 7 to 10 are the table's own amounts
    # (81,200.00, 71,300.00, 3,500.00 and 9,900.00). Line 11 is the lesser of 80,000 and 81,200.00,
    # 80,000. Line 3 is above line C: line 14 = 80,000 less 71,300.00 = 8,700.00 = line 15 (below
    # line 10), line 16 = 71,300.00, line 18 = 67,800.00 and the required contributions are the
    # maxima: line 22 3,356.10, line 23 678.00, line 24 4,034.10, line 26 8,700.00 x 4% = 348.00.
    worksheet = return_bo(line_1="80000", line_2="0", line_19="4000.00")

    assert worksheet.get(RC381_PART_3_LINE_6).value == Rate(D("1"))
    assert worksheet.get(RC381_PART_3_LINE_7).value == D("81200.00")
    assert worksheet.get(RC381_PART_3_LINE_8).value == D("71300.00")
    assert worksheet.get(RC381_PART_3_LINE_9).value == D("3500.00")
    assert worksheet.get(RC381_PART_3_LINE_10).value == D("9900.00")
    assert worksheet.get(RC381_PART_3_LINE_11).value == D("80000")
    assert worksheet.get(RC381_PART_3_LINE_15).value == D("8700.00")
    assert worksheet.get(RC381_PART_3_LINE_16).value == D("71300.00")
    assert worksheet.get(RC381_PART_3_LINE_18).value == D("67800.00")
    assert worksheet.get(RC381_PART_3_LINE_20).value == D("3327.73")
    assert worksheet.get(RC381_PART_3_LINE_21).value == D("672.27")
    assert worksheet.get(RC381_PART_3_LINE_22).value == D("3356.10")
    assert worksheet.get(RC381_PART_3_LINE_23).value == D("678.00")
    assert worksheet.get(RC381_PART_3_LINE_24).value == D("4034.10")
    assert worksheet.get(RC381_PART_3_LINE_26).value == D("348.00")


def test_return_bo_with_6_months_the_lines_read_the_row_of_line_a() -> None:
    # Line A is 6 (lines C to F: 35,650.00, 4,950.00, 40,600.00 and 1,750.00), line B is 12. Line
    # 1 is 20,000 and line 2 is 10,000: line 6 = 0.66666 (cut). Line 7 = 40,600.00 x 0.66666 =
    # 27,066.396, 27,066.40; line 8 = 35,650.00 x 0.66666 = 23,766.429, 23,766.43; line 9 =
    # 1,750.00 x 0.66666 = 1,166.655, 1,166.66; line 10 = 4,950.00 x 0.66666 = 3,299.967, 3,299.97.
    # Line 11 = the lesser of 20,000 and 27,066.40 = 20,000; line 3 (30,000) is not more than line C
    # (35,650.00), so line 15 is 0, line 16 20,000, line 18 20,000 less 1,166.66 = 18,833.34.
    worksheet = return_bo(
        line_1="20000", line_2="10000", line_19="900.00", cpp_months=6, qpp_months=12
    )

    assert worksheet.get(RC381_PART_3_LINE_6).value == Rate(D("0.66666"))
    assert worksheet.get(RC381_PART_3_LINE_7).value == D("27066.40")
    assert worksheet.get(RC381_PART_3_LINE_8).value == D("23766.43")
    assert worksheet.get(RC381_PART_3_LINE_9).value == D("1166.66")
    assert worksheet.get(RC381_PART_3_LINE_10).value == D("3299.97")
    assert worksheet.get(RC381_PART_3_LINE_11).value == D("20000")
    assert worksheet.get(RC381_PART_3_LINE_15).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_16).value == D("20000")
    assert worksheet.get(RC381_PART_3_LINE_18).value == D("18833.34")
    assert worksheet.get(RC381_PART_3_LINE_20).value == D("748.74")
    assert worksheet.get(RC381_PART_3_LINE_21).value == D("151.26")
    assert worksheet.get(RC381_PART_3_LINE_22).value == D("932.25")
    assert worksheet.get(RC381_PART_3_LINE_23).value == D("188.33")
    assert worksheet.get(RC381_PART_3_LINE_24).value == D("1120.58")


# Part 3, the QPP side.


def test_return_bo_lines_27_to_30_are_the_qpp_row_of_the_table_less_lines_7_to_10() -> None:
    # Line 27 = line I (81,200.00) less line 7 (34,799.88) = 46,400.12; line 28 = line G
    # (71,300.00) less line 8 (30,557.04) = 40,742.96; line 29 = line J (3,500.00) less line 9
    # (1,500.00) = 2,000.00; line 30 = line H (9,900.00) less line 10 (4,242.84) = 5,657.16.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_27).value == D("46400.12")
    assert worksheet.get(RC381_PART_3_LINE_28).value == D("40742.96")
    assert worksheet.get(RC381_PART_3_LINE_29).value == D("2000.00")
    assert worksheet.get(RC381_PART_3_LINE_30).value == D("5657.16")


def test_return_bo_lines_27_to_30_are_subtractions_of_lines_7_to_10() -> None:
    worksheet = return_bo()

    for kind in (
        RC381_PART_3_LINE_27,
        RC381_PART_3_LINE_28,
        RC381_PART_3_LINE_29,
        RC381_PART_3_LINE_30,
    ):
        assert isinstance(worksheet.producer_of(kind), Subtract), kind.identifier


def test_return_bo_line_31_is_the_lesser_of_line_2_and_line_27() -> None:
    # Line 2 is 40,000 and line 27 is 46,400.12: line 31 is 40,000.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_31).value == D("40000")


def test_return_bo_line_31_is_line_27_when_that_is_the_lesser() -> None:
    # Line 1 is 80,000 and line 2 is 40,000: line 3 is 120,000.00 and line 6 is 0.66666. Line 7 =
    # 81,200.00 x 0.66666 = 54,132.79 (54,132.7920), so line 27 = 81,200.00 less 54,132.79 =
    # 27,067.21, less than line 2 (40,000): line 31 is 27,067.21.
    worksheet = return_bo(line_1="80000", line_2="40000", line_19="0", line_39="0")

    assert worksheet.get(RC381_PART_3_LINE_27).value == D("27067.21")
    assert worksheet.get(RC381_PART_3_LINE_31).value == D("27067.21")


def test_return_bo_line_34_is_line_31_less_line_28_and_not_below_zero() -> None:
    # Line 31 is 40,000.00 and line 28 is 40,742.96: the difference is negative, so line 34 is 0.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_34).value == D("0")


def test_return_bo_line_35_is_zero_when_line_3_is_not_more_than_line_g() -> None:
    # Line 3 (70,000.00) is not more than line G (71,300.00), so lines 32 to 35 are not completed:
    # line 35 is 0 (line 34, line 31 less line 28 = 40,000.00 less 40,742.96, is 0 as it is
    # negative, so the lesser of line 30 (5,657.16) and line 34 is 0), the amount from line 31 is
    # entered on line 36 (40,000.00 less 0), and line 38 = line 36 less line 29 = 38,000.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_35_LESSER).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_35).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_36).value == D("40000")
    assert worksheet.get(RC381_PART_3_LINE_38).value == D("38000.00")


def test_return_bo_line_35_is_zero_when_line_3_is_exactly_line_g() -> None:
    # Line 1 is 17,825 and line 2 is 53,475: line 3 is 71,300, which is line G, not more. Line 6
    # is 0.25, line 8 is 17,825.00 so line 28 is 53,475.00 and line 34 (53,475 less 53,475.00) is
    # 0.00, line 35 is 0, line 36 is 53,475 and line 38 = 53,475 less line 29 (2,625.00) =
    # 50,850.00.
    worksheet = return_bo(line_1="17825", line_2="53475", line_19="0", line_39="0")

    assert worksheet.get(RC381_PART_3_LINE_28).value == D("53475.00")
    assert worksheet.get(RC381_PART_3_LINE_34).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_35_LESSER).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_35).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_36).value == D("53475")
    assert worksheet.get(RC381_PART_3_LINE_38).value == D("50850.00")
    assert worksheet.get(RC381_PART_3_LINE_46).value == D("0.00")


def test_return_bo_line_35_is_the_lesser_when_line_3_is_one_dollar_more_than_line_g() -> None:
    # Line 2 of 53,476 makes line 3 71,301, more than line G. Line 6 is 0.24999; line 7 =
    # 20,299.19, line 8 = 17,824.29, line 9 = 874.97, line 10 = 2,474.90. Line 27 = 60,900.81,
    # line 28 = 53,475.71, line 29 = 2,625.03, line 30 = 7,425.10; line 31 = 53,476 (line 2), line
    # 34 = 53,476 less 53,475.71 = 0.29 and line 35 is the lesser of line 30 (7,425.10) and line
    # 34 (0.29): 0.29. Line 36 = 53,476 less 0.29 = 53,475.71 and line 38 = 53,475.71 less
    # 2,625.03 = 50,850.68; line 46 = 0.29 x 4% = 0.0116, 0.01.
    worksheet = return_bo(line_1="17825", line_2="53476", line_19="0", line_39="0")

    assert worksheet.get(RC381_PART_3_LINE_27).value == D("60900.81")
    assert worksheet.get(RC381_PART_3_LINE_28).value == D("53475.71")
    assert worksheet.get(RC381_PART_3_LINE_29).value == D("2625.03")
    assert worksheet.get(RC381_PART_3_LINE_30).value == D("7425.10")
    assert worksheet.get(RC381_PART_3_LINE_31).value == D("53476")
    assert worksheet.get(RC381_PART_3_LINE_34).value == D("0.29")
    assert worksheet.get(RC381_PART_3_LINE_35_LESSER).value == D("0.29")
    assert worksheet.get(RC381_PART_3_LINE_35).value == D("0.29")
    assert worksheet.get(RC381_PART_3_LINE_36).value == D("53475.71")
    assert worksheet.get(RC381_PART_3_LINE_38).value == D("50850.68")
    assert worksheet.get(RC381_PART_3_LINE_46).value == D("0.01")


def test_return_bo_above_line_g_lines_32_to_35_are_completed() -> None:
    # Line 1 is 50,000 and line 2 is 40,000 (box 17 of 2,500.00, box 17A of 100.00, box 16 of
    # 2,975.00 and box 16A of 150.00): line 3 is 90,000.00, more than line G (71,300.00). The CPP
    # side is the same as in the test of lines 12 to 15 above (line 7 45,110.66, line 8 39,610.72,
    # line 9 1,944.43, line 10 5,499.95; box 16 is 2,975.00 there too). Line 27 = 81,200.00 less
    # 45,110.66 = 36,089.34, line 28 = 71,300.00 less 39,610.72 = 31,689.28, line 29 = 3,500.00
    # less 1,944.43 = 1,555.57, line 30 = 9,900.00 less 5,499.95 = 4,400.05. Line 31 = the lesser
    # of 40,000 and 36,089.34 = 36,089.34. Line 34 = 36,089.34 less 31,689.28 = 4,400.06; line
    # 35 = the lesser of line 30 (4,400.05) and line 34 (4,400.06) = 4,400.05. Line 36 =
    # 36,089.34 less 4,400.05 = 31,689.29; line 38 = 31,689.29 less 1,555.57 = 30,133.72. Line
    # 40 = 2,500.00 x 84.375% = 2,109.38 (2,109.375); line 41 = 390.62. Line 42 = 30,133.72 x 5.4% =
    # 1,627.22 (1,627.2209); line 43 = 301.34 (301.3372); line 44 = 1,928.56; line 46 =
    # 4,400.05 x 4% = 176.00 (176.002). Line 49 = 2,475.00 + 2,109.38 = 4,584.38; line 52 =
    # 1,864.48 + 1,627.22 = 3,491.70; line 53 = 1,092.68. Line 56 = 500.00 + 390.62 = 890.62;
    # line 59 = 376.66 + 301.34 = 678.00; line 60 = 212.62; line 61 = 1,305.30. Line 64 =
    # 150.00 + 100.00 = 250.00; line 67 = 220.00 + 176.00 = 396.00; line 68 = 250.00 less
    # 396.00 = -146.00; line 69 = 1,305.30 less 146.00 = 1,159.30.
    worksheet = return_bo(
        line_1="50000",
        line_2="40000",
        line_19="2975.00",
        line_39="2500.00",
        line_25="150.00",
        line_45="100.00",
    )

    assert worksheet.get(RC381_PART_3_LINE_27).value == D("36089.34")
    assert worksheet.get(RC381_PART_3_LINE_28).value == D("31689.28")
    assert worksheet.get(RC381_PART_3_LINE_29).value == D("1555.57")
    assert worksheet.get(RC381_PART_3_LINE_30).value == D("4400.05")
    assert worksheet.get(RC381_PART_3_LINE_31).value == D("36089.34")
    assert worksheet.get(RC381_PART_3_LINE_34).value == D("4400.06")
    assert worksheet.get(RC381_PART_3_LINE_35_LESSER).value == D("4400.05")
    assert worksheet.get(RC381_PART_3_LINE_35).value == D("4400.05")
    assert worksheet.get(RC381_PART_3_LINE_36).value == D("31689.29")
    assert worksheet.get(RC381_PART_3_LINE_38).value == D("30133.72")
    assert worksheet.get(RC381_PART_3_LINE_40).value == D("2109.38")
    assert worksheet.get(RC381_PART_3_LINE_41).value == D("390.62")
    assert worksheet.get(RC381_PART_3_LINE_42).value == D("1627.22")
    assert worksheet.get(RC381_PART_3_LINE_43).value == D("301.34")
    assert worksheet.get(RC381_PART_3_LINE_44).value == D("1928.56")
    assert worksheet.get(RC381_PART_3_LINE_46).value == D("176.00")
    assert worksheet.get(RC381_PART_3_LINE_49).value == D("4584.38")
    assert worksheet.get(RC381_PART_3_LINE_52).value == D("3491.70")
    assert worksheet.get(RC381_PART_3_LINE_53).value == D("1092.68")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("890.62")
    assert worksheet.get(RC381_PART_3_LINE_59).value == D("678.00")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("212.62")
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("1305.30")
    assert worksheet.get(RC381_PART_3_LINE_64).value == D("250.00")
    assert worksheet.get(RC381_PART_3_LINE_67).value == D("396.00")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("-146.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("1159.30")


def test_return_bo_line_35_is_capped_by_line_30_and_line_38_by_the_table() -> None:
    # Line 1 is 0 and line 2 is 85,000 (the Quebec slips together): line 6 is 0, so lines 27 to 30
    # are the table's row (81,200.00, 71,300.00, 3,500.00 and 9,900.00). Line 31 = the lesser of
    # 85,000 and 81,200.00 = 81,200.00; line 34 = 81,200.00 less 71,300.00 = 9,900.00; line 35 =
    # the lesser of line 30 (9,900.00) and line 34 (9,900.00) = 9,900.00 (line 3 of 85,000.00 is
    # more than line G). Line 36 = 71,300.00; line 38 = 71,300.00 less 3,500.00 = 67,800.00, so
    # the required contributions are the maxima: line 42 3,661.20, line 43 678.00, line 44
    # 4,339.20, line 46 396.00.
    worksheet = return_bo(
        line_1="0", line_2="85000", line_19="0", line_39="3000.00", line_45="400.00"
    )

    assert worksheet.get(RC381_PART_3_LINE_27).value == D("81200.00")
    assert worksheet.get(RC381_PART_3_LINE_28).value == D("71300.00")
    assert worksheet.get(RC381_PART_3_LINE_29).value == D("3500.00")
    assert worksheet.get(RC381_PART_3_LINE_30).value == D("9900.00")
    assert worksheet.get(RC381_PART_3_LINE_31).value == D("81200.00")
    assert worksheet.get(RC381_PART_3_LINE_34).value == D("9900.00")
    assert worksheet.get(RC381_PART_3_LINE_35).value == D("9900.00")
    assert worksheet.get(RC381_PART_3_LINE_36).value == D("71300.00")
    assert worksheet.get(RC381_PART_3_LINE_38).value == D("67800.00")
    assert worksheet.get(RC381_PART_3_LINE_42).value == D("3661.20")
    assert worksheet.get(RC381_PART_3_LINE_43).value == D("678.00")
    assert worksheet.get(RC381_PART_3_LINE_44).value == D("4339.20")
    assert worksheet.get(RC381_PART_3_LINE_46).value == D("396.00")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("4.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-1335.20")


def test_return_bo_line_40_is_84_375_percent_of_line_39() -> None:
    # 2,500.00 x 84.375% = 2,109.375, which rounds half up to 2,109.38.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_40).value == D("2109.38")


def test_return_bo_line_40_is_produced_by_apply_rate_and_line_41_by_subtract() -> None:
    worksheet = return_bo()

    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_40), ApplyRate)
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_41), Subtract)


def test_return_bo_line_41_is_line_39_less_line_40() -> None:
    # 2,500.00 less 2,109.38 is 390.62.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_41).value == D("390.62")


def test_return_bo_line_42_is_5_4_percent_of_line_38() -> None:
    # 38,000.00 x 5.4% = 2,052.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_42).value == D("2052.00")


def test_return_bo_line_43_is_1_percent_of_line_38() -> None:
    # 38,000.00 x 1% = 380.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_43).value == D("380.00")


def test_return_bo_line_44_adds_lines_42_and_43() -> None:
    # 2,052.00 plus 380.00 is 2,432.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_44).value == D("2432.00")


def test_return_bo_line_46_is_4_percent_of_line_35() -> None:
    # Line 35 is 0, so 0 x 4% is 0.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_46).value == D("0.00")


def test_return_bo_the_qpp_required_lines_are_tiered_contributions() -> None:
    worksheet = return_bo()

    for kind in (RC381_PART_3_LINE_42, RC381_PART_3_LINE_43, RC381_PART_3_LINE_46):
        assert isinstance(worksheet.producer_of(kind), TieredContribution), kind.identifier
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_44), Sum)
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_35), AmountWhenMore)
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_35_LESSER), LesserOf)
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_31), LesserOf)
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_34), SubtractNotBelowZero)
    assert isinstance(worksheet.producer_of(RC381_PART_3_LINE_38), SubtractNotBelowZero)


# Part 3 lines 49 to 69, the totals.


def test_return_bo_lines_49_and_52_are_the_base_contribution_totals() -> None:
    # Line 49 = line 20 (1,485.00) + line 40 (2,109.38) = 3,594.38; line 52 = line 22 (1,410.75) +
    # line 42 (2,052.00) = 3,462.75.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_49).value == D("3594.38")
    assert worksheet.get(RC381_PART_3_LINE_52).value == D("3462.75")


def test_return_bo_line_53_is_line_49_less_line_52() -> None:
    # 3,594.38 less 3,462.75 is 131.63.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_53).value == D("131.63")


def test_return_bo_lines_56_and_59_are_the_first_additional_totals() -> None:
    # Line 56 = line 21 (300.00) + line 41 (390.62) = 690.62; line 59 = line 23 (285.00) + line 43
    # (380.00) = 665.00.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_56).value == D("690.62")
    assert worksheet.get(RC381_PART_3_LINE_59).value == D("665.00")


def test_return_bo_line_60_is_line_56_less_line_59() -> None:
    # 690.62 less 665.00 is 25.62.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_60).value == D("25.62")


def test_return_bo_line_61_is_line_53_plus_line_60() -> None:
    # 131.63 plus 25.62 is 157.25.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("157.25")


def test_return_bo_lines_64_and_67_are_the_second_additional_contributions() -> None:
    # With no box 16A or 17A, line 64 is 0 + 0 = 0, and line 67 = line 26 (0) + line 46 (0) = 0.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_64).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_67).value == D("0.00")


def test_return_bo_line_68_is_zero_when_there_are_no_second_additional_contributions() -> None:
    # Line 64 (0) less line 67 (0) is 0.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_68).value == D("0.00")


def test_return_bo_line_69_is_line_61_plus_line_68_and_matches_the_tickets_example() -> None:
    # 157.25 plus 0 is 157.25: positive, so Part 3a will carry line 52 (3,462.75) to line 30800,
    # line 59 + line 67 (665.00) to line 22215 and line 69 (157.25) to line 44800.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_27).value == D("46400.12")
    assert worksheet.get(RC381_PART_3_LINE_28).value == D("40742.96")
    assert worksheet.get(RC381_PART_3_LINE_29).value == D("2000.00")
    assert worksheet.get(RC381_PART_3_LINE_30).value == D("5657.16")
    assert worksheet.get(RC381_PART_3_LINE_31).value == D("40000")
    assert worksheet.get(RC381_PART_3_LINE_34).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_35_LESSER).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_35).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_36).value == D("40000")
    assert worksheet.get(RC381_PART_3_LINE_38).value == D("38000.00")
    assert worksheet.get(RC381_PART_3_LINE_40).value == D("2109.38")
    assert worksheet.get(RC381_PART_3_LINE_41).value == D("390.62")
    assert worksheet.get(RC381_PART_3_LINE_42).value == D("2052.00")
    assert worksheet.get(RC381_PART_3_LINE_43).value == D("380.00")
    assert worksheet.get(RC381_PART_3_LINE_44).value == D("2432.00")
    assert worksheet.get(RC381_PART_3_LINE_46).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_49).value == D("3594.38")
    assert worksheet.get(RC381_PART_3_LINE_52).value == D("3462.75")
    assert worksheet.get(RC381_PART_3_LINE_53).value == D("131.63")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("690.62")
    assert worksheet.get(RC381_PART_3_LINE_59).value == D("665.00")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("25.62")
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("157.25")
    assert worksheet.get(RC381_PART_3_LINE_64).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_67).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("157.25")


def test_return_bo_the_totals_are_sums_and_differences() -> None:
    worksheet = return_bo()

    for kind in (
        RC381_PART_3_LINE_49,
        RC381_PART_3_LINE_52,
        RC381_PART_3_LINE_56,
        RC381_PART_3_LINE_59,
        RC381_PART_3_LINE_61,
        RC381_PART_3_LINE_64,
        RC381_PART_3_LINE_67,
        RC381_PART_3_LINE_69,
    ):
        assert isinstance(worksheet.producer_of(kind), Sum), kind.identifier
    for kind in (RC381_PART_3_LINE_53, RC381_PART_3_LINE_60, RC381_PART_3_LINE_68):
        assert isinstance(worksheet.producer_of(kind), Subtract), kind.identifier


# Part 3 totals that are negative.


def test_return_bo_line_53_is_negative_when_actual_base_is_less_than_required() -> None:
    # With no box 16 or 17 contributions, line 49 is 0.00 and line 52 is 3,462.75: line 53 is
    # -3,462.75 (shown in brackets). Line 56 is 0.00 and line 59 is 665.00: line 60 is -665.00,
    # line 61 = -3,462.75 + -665.00 = -4,127.75, and so is line 69.
    worksheet = return_bo(line_19="0", line_39="0")

    assert worksheet.get(RC381_PART_3_LINE_49).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_52).value == D("3462.75")
    assert worksheet.get(RC381_PART_3_LINE_53).value == D("-3462.75")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_59).value == D("665.00")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("-665.00")
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("-4127.75")
    assert worksheet.get(RC381_PART_3_LINE_64).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_67).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-4127.75")


def test_return_bo_line_53_may_be_negative_while_line_60_is_positive() -> None:
    # Line 1 is 14,500, line 2 is 40,000, box 16 is 850 and box 17 is 2,350 (chosen figures; the
    # form takes the totals as entered): line 20 = 850 x 83.1933% = 707.14 (707.1431), line 21 =
    # 142.86, line 40 = 2,350 x 84.375% = 1,982.81 (1,982.8125), line 41 = 367.19, line 38 =
    # 37,431.18, line 42 = 2,021.28, line 43 = 374.31. Line 49 = 707.14 + 1,982.81 = 2,689.95 and
    # line 52 = 671.66 + 2,021.28 = 2,692.94 (line 22 = 671.66): line 53 = -2.99. Line 56 = 142.86 +
    # 367.19 = 510.05 and line 59 = 135.69 + 374.31 = 510.00 (line 23 = 135.69): line 60 = 0.05.
    # Line 61 = -2.99 + 0.05 = -2.94.
    worksheet = return_bo(line_1="14500", line_2="40000", line_19="850", line_39="2350")

    assert worksheet.get(RC381_PART_3_LINE_38).value == D("37431.18")
    assert worksheet.get(RC381_PART_3_LINE_42).value == D("2021.28")
    assert worksheet.get(RC381_PART_3_LINE_43).value == D("374.31")
    assert worksheet.get(RC381_PART_3_LINE_49).value == D("2689.95")
    assert worksheet.get(RC381_PART_3_LINE_52).value == D("2692.94")
    assert worksheet.get(RC381_PART_3_LINE_53).value == D("-2.99")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("510.05")
    assert worksheet.get(RC381_PART_3_LINE_59).value == D("510.00")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("0.05")
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("-2.94")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-2.94")


def test_return_bo_line_60_is_negative_when_line_53_is_positive() -> None:
    # Line 1 is 30,000 and line 2 is 10,000, box 16 is 1,563.00 and box 17 is 650.00 (chosen
    # figures, box 17 the most a line 2 of 10,000 allows; the form takes the totals as entered).
    # Line 6 is 0.75, line 18 = 27,375.00, line 22 = 1,355.06 and line 23 = 273.75; line 27 =
    # 20,300.00 and line 38 = 9,125.00, so line 42 = 492.75 and line 43 = 91.25. Line 20 =
    # 1,300.31 and line 21 = 262.69; line 40 = 650.00 x 84.375% = 548.44 (548.4375) and line 41 =
    # 101.56. Line 53 = (1,300.31 + 548.44) less (1,355.06 + 492.75) = 0.94; line 60 = (262.69 +
    # 101.56) less (273.75 + 91.25) = -0.75 (shown in brackets); line 61 = 0.94 + -0.75 = 0.19.
    worksheet = return_bo(line_1="30000", line_2="10000", line_19="1563.00", line_39="650.00")

    assert worksheet.get(RC381_PART_3_LINE_6).value == Rate(D("0.75000"))
    assert worksheet.get(RC381_PART_3_LINE_18).value == D("27375.00")
    assert worksheet.get(RC381_PART_3_LINE_22).value == D("1355.06")
    assert worksheet.get(RC381_PART_3_LINE_23).value == D("273.75")
    assert worksheet.get(RC381_PART_3_LINE_27).value == D("20300.00")
    assert worksheet.get(RC381_PART_3_LINE_38).value == D("9125.00")
    assert worksheet.get(RC381_PART_3_LINE_40).value == D("548.44")
    assert worksheet.get(RC381_PART_3_LINE_41).value == D("101.56")
    assert worksheet.get(RC381_PART_3_LINE_42).value == D("492.75")
    assert worksheet.get(RC381_PART_3_LINE_43).value == D("91.25")
    assert worksheet.get(RC381_PART_3_LINE_49).value == D("1848.75")
    assert worksheet.get(RC381_PART_3_LINE_52).value == D("1847.81")
    assert worksheet.get(RC381_PART_3_LINE_53).value == D("0.94")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("364.25")
    assert worksheet.get(RC381_PART_3_LINE_59).value == D("365.00")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("-0.75")
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("0.19")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("0.19")


def test_return_bo_line_68_is_negative_when_actual_is_less_than_required() -> None:
    # Line 1 is 50,000 and line 2 is 40,000 with box 16A and box 17A of 0: line 26 = 220.00 and
    # line 46 = 176.00, so line 67 = 396.00 and line 64 = 0.00: line 68 = -396.00. Line 61 is
    # -1,194.70 (line 53 -1,016.70, line 60 -178.00), so line 69 = -1,194.70 + -396.00 = -1,590.70.
    worksheet = return_bo(line_1="50000", line_2="40000", line_19="2975.00", line_39="0")

    assert worksheet.get(RC381_PART_3_LINE_26).value == D("220.00")
    assert worksheet.get(RC381_PART_3_LINE_46).value == D("176.00")
    assert worksheet.get(RC381_PART_3_LINE_53).value == D("-1016.70")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("-178.00")
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("-1194.70")
    assert worksheet.get(RC381_PART_3_LINE_64).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_67).value == D("396.00")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("-396.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-1590.70")


def test_return_bo_line_68_is_positive_when_actual_is_more_than_required() -> None:
    # Line 1 is 40,000 and line 2 is 40,000 (box 16 of 2,380.00, box 16A of 200.00, box 17 of
    # 2,570.00 and box 17A of 300.00): line 15 = 4,350.00 and line 35 = 4,350.00, so line 26 =
    # line 46 = 174.00 and line 67 = 348.00; line 64 = 200.00 + 300.00 = 500.00 and line 68 =
    # 152.00. Line 61 = 763.35, so line 69 = 915.35.
    worksheet = return_bo(
        line_1="40000",
        line_2="40000",
        line_19="2380.00",
        line_39="2570.00",
        line_25="200.00",
        line_45="300.00",
    )

    assert worksheet.get(RC381_PART_3_LINE_15).value == D("4350.00")
    assert worksheet.get(RC381_PART_3_LINE_26).value == D("174.00")
    assert worksheet.get(RC381_PART_3_LINE_35).value == D("4350.00")
    assert worksheet.get(RC381_PART_3_LINE_46).value == D("174.00")
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("763.35")
    assert worksheet.get(RC381_PART_3_LINE_64).value == D("500.00")
    assert worksheet.get(RC381_PART_3_LINE_67).value == D("348.00")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("152.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("915.35")


def test_return_bo_with_6_and_12_months_lines_27_to_30_read_line_b() -> None:
    # Line A is 6 (lines C to F: 35,650.00, 4,950.00, 40,600.00 and 1,750.00), line B is 12 (lines
    # G to J: 71,300.00, 9,900.00, 81,200.00 and 3,500.00). Line 6 = 0.42857: line 7 = 40,600.00 x
    # 0.42857 = 17,399.94, line 8 = 15,278.52, line 9 = 750.00 and line 10 = 2,121.42. Line 27 =
    # 81,200.00 less 17,399.94 = 63,800.06, line 28 = 71,300.00 less 15,278.52 = 56,021.48, line
    # 29 = 3,500.00 less 750.00 = 2,750.00, line 30 = 9,900.00 less 2,121.42 = 7,778.58. Line 3
    # (70,000.00) is more than line C (35,650.00), so line 15 = 2,121.42 and line 26 = 84.86, but
    # not more than line G (71,300.00), so line 35 is 0. Line 38 = 40,000.00 less 2,750.00 =
    # 37,250.00, line 42 = 2,011.50, line 43 = 372.50. Line 52 = 719.16 + 2,011.50 = 2,730.66,
    # line 53 = 3,594.38 less 2,730.66 = 863.72; line 59 = 145.29 + 372.50 = 517.79, line 60 =
    # 690.62 less 517.79 = 172.83; line 61 = 1,036.55. Line 67 = 84.86 + 0 = 84.86, line 68 =
    # -84.86, so line 69 = 951.69.
    worksheet = return_bo(cpp_months=6, qpp_months=12)

    assert worksheet.get(RC381_PART_3_LINE_7).value == D("17399.94")
    assert worksheet.get(RC381_PART_3_LINE_8).value == D("15278.52")
    assert worksheet.get(RC381_PART_3_LINE_9).value == D("750.00")
    assert worksheet.get(RC381_PART_3_LINE_10).value == D("2121.42")
    assert worksheet.get(RC381_PART_3_LINE_15).value == D("2121.42")
    assert worksheet.get(RC381_PART_3_LINE_26).value == D("84.86")
    assert worksheet.get(RC381_PART_3_LINE_27).value == D("63800.06")
    assert worksheet.get(RC381_PART_3_LINE_28).value == D("56021.48")
    assert worksheet.get(RC381_PART_3_LINE_29).value == D("2750.00")
    assert worksheet.get(RC381_PART_3_LINE_30).value == D("7778.58")
    assert worksheet.get(RC381_PART_3_LINE_31).value == D("40000")
    assert worksheet.get(RC381_PART_3_LINE_34).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_35_LESSER).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_35).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_36).value == D("40000")
    assert worksheet.get(RC381_PART_3_LINE_38).value == D("37250.00")
    assert worksheet.get(RC381_PART_3_LINE_40).value == D("2109.38")
    assert worksheet.get(RC381_PART_3_LINE_41).value == D("390.62")
    assert worksheet.get(RC381_PART_3_LINE_42).value == D("2011.50")
    assert worksheet.get(RC381_PART_3_LINE_43).value == D("372.50")
    assert worksheet.get(RC381_PART_3_LINE_44).value == D("2384.00")
    assert worksheet.get(RC381_PART_3_LINE_46).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_49).value == D("3594.38")
    assert worksheet.get(RC381_PART_3_LINE_52).value == D("2730.66")
    assert worksheet.get(RC381_PART_3_LINE_53).value == D("863.72")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("690.62")
    assert worksheet.get(RC381_PART_3_LINE_59).value == D("517.79")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("172.83")
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("1036.55")
    assert worksheet.get(RC381_PART_3_LINE_64).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_67).value == D("84.86")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("-84.86")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("951.69")


# Part 3a and Part 3b (lines 70 to 93, "If your earnings subject to contributions are from
# employment income only and line 69 is: positive, complete Part 3a ... "0", complete Part 3b ...
# negative ... If not, complete Part 3b").

# Part 3b's lines by number ("87h" is the "result of line 68 minus line 80" inside line 87).
PART_3B_KINDS: dict[str, ArtifactKind[Decimal]] = {
    "75": RC381_PART_3_LINE_75,
    "76": RC381_PART_3_LINE_76,
    "77": RC381_PART_3_LINE_77,
    "78": RC381_PART_3_LINE_78,
    "79": RC381_PART_3_LINE_79,
    "80": RC381_PART_3_LINE_80,
    "81": RC381_PART_3_LINE_81,
    "82": RC381_PART_3_LINE_82,
    "83": RC381_PART_3_LINE_83,
    "84": RC381_PART_3_LINE_84,
    "85": RC381_PART_3_LINE_85,
    "86": RC381_PART_3_LINE_86,
    "87h": RC381_PART_3_LINE_87_DIFFERENCE,
    "87": RC381_PART_3_LINE_87,
    "88": RC381_PART_3_LINE_88,
    "89": RC381_PART_3_LINE_89,
    "90": RC381_PART_3_LINE_90,
    "91": RC381_PART_3_LINE_91,
    "92": RC381_PART_3_LINE_92,
    "93": RC381_PART_3_LINE_93,
}


def part_3b(worksheet: Worksheet) -> dict[str, Decimal]:
    """Part 3b's lines 75 to 93 of `worksheet`, by line number."""
    return {line: worksheet.get(kind).value for line, kind in PART_3B_KINDS.items()}


def results(worksheet: Worksheet) -> tuple[Decimal, Decimal, Decimal]:
    """The amounts for line 30800, line 22215 and line 44800 of the return."""
    return (
        worksheet.get(RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS).value,
        worksheet.get(RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS).value,
        worksheet.get(RC381_CPP_OVERPAYMENT).value,
    )


def test_return_bo_part_3a_matches_the_tickets_example() -> None:
    # The ticket's example: line 69 = 157.25 is positive, so Part 3a. Line 70 "Enter the amount
    # from line 52" = 3,462.75, line 71 "Enter the amount from line 59" = 665.00, line 72 "Enter the
    # amount from line 67 (if any)" = 0, line 73 "Line 71 plus line 72" = 665.00 and line 74
    # "Enter the amount from line 69" = 157.25: line 30800 = 3,462.75, line 22215 = 665.00 and
    # line 44800 = 157.25. Lines 70, 71, 72 and 74 only copy lines 52, 59, 67 and 69.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_52).value == D("3462.75")
    assert worksheet.get(RC381_PART_3_LINE_59).value == D("665.00")
    assert worksheet.get(RC381_PART_3_LINE_67).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_73).value == D("665.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("157.25")
    assert results(worksheet) == (D("3462.75"), D("665.00"), D("157.25"))


def test_return_bo_line_73_is_line_71_plus_line_72() -> None:
    # Line 1 and line 2 of 40,000 each, with box 16 of 2,380.00 and box 17 of 2,570.00: line 52 =
    # 1,678.05 + 1,830.60 = 3,508.65, line 59 = 339.00 + 339.00 = 678.00, line 67 = 174.00 +
    # 174.00 = 348.00 and line 64 = 0, so line 68 = -348.00 and line 61 = 639.79 + 123.56 =
    # 763.35: line 69 = 415.35, positive. Part 3a: line 73 = 678.00 + 348.00 = 1,026.00, so line
    # 30800 = 3,508.65, line 22215 = 1,026.00 and line 44800 = 415.35.
    worksheet = return_bo(line_1="40000", line_2="40000", line_19="2380.00", line_39="2570.00")

    assert worksheet.get(RC381_PART_3_LINE_52).value == D("3508.65")
    assert worksheet.get(RC381_PART_3_LINE_59).value == D("678.00")
    assert worksheet.get(RC381_PART_3_LINE_67).value == D("348.00")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("-348.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("415.35")
    assert worksheet.get(RC381_PART_3_LINE_73).value == D("1026.00")
    assert results(worksheet) == (D("3508.65"), D("1026.00"), D("415.35"))


def test_return_bo_part_3a_with_second_additional_contributions_paid() -> None:
    # The same T4 totals with box 16A of 200.00 and box 17A of 300.00: line 64 = 500.00, line 68 =
    # 152.00, line 69 = 763.35 + 152.00 = 915.35. Line 73 is still 678.00 + 348.00 = 1,026.00.
    worksheet = return_bo(
        line_1="40000",
        line_2="40000",
        line_19="2380.00",
        line_39="2570.00",
        line_25="200.00",
        line_45="300.00",
    )

    assert worksheet.get(RC381_PART_3_LINE_69).value == D("915.35")
    assert results(worksheet) == (D("3508.65"), D("1026.00"), D("915.35"))


def test_return_bo_part_3a_ignores_a_negative_line_53() -> None:
    # Line 1 = 68,500, line 2 = 40,000, box 16 = 4,050 and no box 17: line 53 = -99.25, line 60 =
    # 2.67, line 61 = -96.58. With box 16A of 500.00 line 64 = 500.00 and line 67 = 396.00 (lines
    # 26 and 46 are 250.01 and 145.99), so line 68 = 104.00: line 69 = -96.58 + 104.00 = 7.42,
    # positive, so Part 3a takes line 52 (3,468.58), line 59 + line 67 (678.00 + 396.00 = 1,074.00)
    # and line 69 whatever line 53 is.
    worksheet = return_bo(
        line_1="68500", line_2="40000", line_19="4050", line_39="0", line_25="500.00"
    )

    assert worksheet.get(RC381_PART_3_LINE_53).value == D("-99.25")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("7.42")
    assert results(worksheet) == (D("3468.58"), D("1074.00"), D("7.42"))


def test_return_bo_a_line_69_of_one_cent_is_positive_and_takes_part_3a() -> None:
    # Box 16 of 1,695.20 and box 17 of 2,432.56 (chosen figures): line 20 = 1,695.20 x 83.1933% =
    # 1,410.29 (1,410.2886), line 40 = 2,432.56 x 84.375% = 2,052.47 (2,052.4725); line 49 =
    # 3,462.76 against line 52 = 3,462.75, so line 53 = 0.01. Line 21 = 284.91 and line 41 =
    # 380.09: line 56 = 665.00 = line 59, line 60 = 0 and line 68 = 0, so line 69 = 0.01.
    worksheet = return_bo(line_19="1695.20", line_39="2432.56")

    assert worksheet.get(RC381_PART_3_LINE_49).value == D("3462.76")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("665.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("0.01")
    assert results(worksheet) == (D("3462.75"), D("665.00"), D("0.01"))


def test_return_bo_a_line_69_of_zero_takes_part_3b_with_lines_53_60_and_68_all_zero() -> None:
    # Box 16 of 1,695.20 and box 17 of 2,432.55 (chosen figures): line 20 = 1,410.29, line 40 =
    # 2,052.46 (2,052.4640), line 49 = 3,462.75 = line 52, line 53 = 0. Line 21 = 284.91 and line 41
    # = 380.09: line 56 = 665.00 = line 59, line 60 = 0; line 64 = line 67 = 0, line 68 = 0, so
    # line 69 = 0: Part 3b. Line 53 is "positive or 0": line 75 = line 52 = 3,462.75; line 76 = 0,
    # lines 77, 78, 80 = 0, line 79 = 3,462.75 and line 81 = 3,462.75. Line 60 is "positive or 0":
    # line 82 = line 59 = 665.00, lines 83, 84, 85, 87 = 0, line 86 = line 88 = 665.00. Line 68 is
    # "positive or 0": line 89 = line 67 = 0, lines 90, 91 = 0, line 92 = 0, line 93 = 665.00.
    # Part 3b has no overpayment, so line 44800 is 0.
    worksheet = return_bo(line_19="1695.20", line_39="2432.55")

    assert worksheet.get(RC381_PART_3_LINE_53).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("0.00")
    assert part_3b(worksheet) == {
        "75": D("3462.75"),
        "76": D("0"),
        "77": D("0"),
        "78": D("0"),
        "79": D("3462.75"),
        "80": D("0"),
        "81": D("3462.75"),
        "82": D("665.00"),
        "83": D("0"),
        "84": D("0"),
        "85": D("0"),
        "86": D("665.00"),
        "87h": D("0"),
        "87": D("0"),
        "88": D("665.00"),
        "89": D("0"),
        "90": D("0"),
        "91": D("0"),
        "92": D("0"),
        "93": D("665.00"),
    }
    assert results(worksheet) == (D("3462.75"), D("665.00"), D("0"))


def test_return_bo_part_3b_with_line_53_negative_and_line_60_positive_adds_line_77_to_line_75() -> (
    None
):
    # Box 16 of 1,750 and box 17 of 2,347.93 on a line 1 of 29,500: line 20 = 1,455.88 and line 21
    # = 294.12, line 40 = 1,981.07 and line 41 = 366.86, so line 49 = 3,436.95; line 52 = 1,386.71
    # + 2,051.22 = 3,437.93 and line 53 = 3,436.95 less 3,437.93 = -0.98; line 56 = 660.98, line 59
    # = 280.14 + 379.86 = 660.00, line 60 = 660.98 less 660.00 = 0.98. Line 61 = 0 and line 68 = 0,
    # so line 69 = 0: Part 3b. Line 53 is negative: line 75 = line 49 = 3,436.95, line 76 = 0.98.
    # Line 60 is positive: line 77 = the lesser of 0.98 and 0.98 = 0.98, line 78 = 0, line 79 =
    # 3,436.95 + 0.98 = 3,437.93, line 80 = 0 (line 68 is 0), line 81 = 3,437.93. Line 60 is
    # positive: line 82 = line 59 = 660.00 and lines 83 to 85 = 0; line 88 = 660.00; line 89 =
    # line 67 = 0 and line 93 = 660.00. The base is made up to the required base from the first
    # additional.
    worksheet = return_bo(line_19="1750", line_39="2347.93", line_1="29500")

    assert worksheet.get(RC381_PART_3_LINE_49).value == D("3436.95")
    assert worksheet.get(RC381_PART_3_LINE_53).value == D("-0.98")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("660.98")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("0.98")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("0.00")
    assert part_3b(worksheet) == {
        "75": D("3436.95"),
        "76": D("0.98"),
        "77": D("0.98"),
        "78": D("0"),
        "79": D("3437.93"),
        "80": D("0"),
        "81": D("3437.93"),
        "82": D("660.00"),
        "83": D("0"),
        "84": D("0"),
        "85": D("0"),
        "86": D("660.00"),
        "87h": D("0"),
        "87": D("0"),
        "88": D("660.00"),
        "89": D("0"),
        "90": D("0"),
        "91": D("0"),
        "92": D("0"),
        "93": D("660.00"),
    }
    assert results(worksheet) == (D("3437.93"), D("660.00"), D("0"))


def test_return_bo_part_3b_with_line_53_positive_and_line_60_negative_adds_line_84_to_line_82() -> (
    None
):
    # Box 16 of 1,557.75 and box 17 of 2,570.00, the most box 17 can be on a line 2 of 40,000 (the
    # two make the 4,127.75 required): line 20 = 1,295.94, line 21 = 261.81, line 40 = 2,168.44
    # (2,168.4375), line 41 = 401.56; line 49 = 3,464.38, line 53 = 3,464.38 less 3,462.75 = 1.63,
    # line 56 = 663.37, line 60 = 663.37 less 665.00 = -1.63, line 61 = 0, line 69 = 0: Part 3b.
    # Line 53 is positive: line 75 = line 52 = 3,462.75, lines 76 to 80 = 0, line 81 = 3,462.75.
    # Line 60 is negative: line 82 = line 56 = 663.37, line 83 = 1.63, line 84 = the lesser of 1.63
    # and 1.63 = 1.63, line 85 = 0, line 86 = 663.37 + 1.63 = 665.00, line 87 = 0, line 88 =
    # 665.00, line 93 = 665.00 + 0.
    worksheet = return_bo(line_19="1557.75", line_39="2570.00")

    assert worksheet.get(RC381_PART_3_LINE_53).value == D("1.63")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("663.37")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("-1.63")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("0.00")
    assert part_3b(worksheet) == {
        "75": D("3462.75"),
        "76": D("0"),
        "77": D("0"),
        "78": D("0"),
        "79": D("3462.75"),
        "80": D("0"),
        "81": D("3462.75"),
        "82": D("663.37"),
        "83": D("1.63"),
        "84": D("1.63"),
        "85": D("0"),
        "86": D("665.00"),
        "87h": D("0"),
        "87": D("0"),
        "88": D("665.00"),
        "89": D("0"),
        "90": D("0"),
        "91": D("0"),
        "92": D("0"),
        "93": D("665.00"),
    }
    assert results(worksheet) == (D("3462.75"), D("665.00"), D("0"))


def test_return_bo_part_3b_with_no_contributions_paid_gives_zero_for_both_results() -> None:
    # No box 16 or box 17: line 49 = 0, line 53 = -3,462.75; line 56 = 0, line 60 = -665.00; line 69
    # = -4,127.75, negative, so Part 3b ("If not, complete Part 3b"). Line 53 is negative: line 75 =
    # line 49 = 0; line 76 = 3,462.75; line 60 is negative, not positive, so line 77 = "0"; line 78
    # = 3,462.75; line 79 = 0; line 68 is 0, so line 80 = "0"; line 81 = 0. Line 60 is negative:
    # line 82 = line 56 = 0; line 83 = 665.00; line 53 is negative, not positive, so line 84 = "0";
    # line 85 = 665.00; line 86 = 0; line 87 = 0 (line 68 is 0); line 88 = 0; line 93 = 0.
    worksheet = return_bo(line_19="0", line_39="0")

    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-4127.75")
    assert part_3b(worksheet) == {
        "75": D("0"),
        "76": D("3462.75"),
        "77": D("0"),
        "78": D("3462.75"),
        "79": D("0"),
        "80": D("0"),
        "81": D("0"),
        "82": D("0"),
        "83": D("665.00"),
        "84": D("0"),
        "85": D("665.00"),
        "86": D("0"),
        "87h": D("0"),
        "87": D("0"),
        "88": D("0"),
        "89": D("0"),
        "90": D("0"),
        "91": D("0"),
        "92": D("0"),
        "93": D("0"),
    }
    assert results(worksheet) == (D("0"), D("0"), D("0"))


def test_return_bo_part_3b_with_lines_53_and_60_both_negative_gives_the_actual_contributions() -> (
    None
):
    # Box 16 of 1,430.00 and box 17 of 2,570.00 (the most box 17 can be on a line 2 of 40,000):
    # line 20 = 1,189.66, line 21 = 240.34, line 40 = 2,168.44 (2,168.4375), line 41 = 401.56; line
    # 49 = 3,358.10, line 53 = 3,358.10 less 3,462.75 = -104.65, line 56 = 641.90, line 60 =
    # 641.90 less 665.00 = -23.10, line 61 = -127.75, line 69 = -127.75. Line 75 = line 49 =
    # 3,358.10, line 76 = 104.65, line 77 = "0" (line 60 is not positive), line 78 = 104.65, line
    # 79 = 3,358.10, line 80 = "0" (line 68 is 0), line 81 = 3,358.10. Line 82 = line 56 = 641.90,
    # line 83 = 23.10, line 84 = "0" (line 53 is not positive), line 85 = 23.10, line 86 =
    # 641.90, line 87 = "0", line 88 = 641.90, line 93 = 641.90.
    worksheet = return_bo(line_19="1430.00", line_39="2570.00")

    assert worksheet.get(RC381_PART_3_LINE_53).value == D("-104.65")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("-23.10")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-127.75")
    assert part_3b(worksheet) == {
        "75": D("3358.10"),
        "76": D("104.65"),
        "77": D("0"),
        "78": D("104.65"),
        "79": D("3358.10"),
        "80": D("0"),
        "81": D("3358.10"),
        "82": D("641.90"),
        "83": D("23.10"),
        "84": D("0"),
        "85": D("23.10"),
        "86": D("641.90"),
        "87h": D("0"),
        "87": D("0"),
        "88": D("641.90"),
        "89": D("0"),
        "90": D("0"),
        "91": D("0"),
        "92": D("0"),
        "93": D("641.90"),
    }
    assert results(worksheet) == (D("3358.10"), D("641.90"), D("0"))


def test_return_bo_part_3b_line_80_is_line_68_when_line_53_is_negative_and_line_60_positive() -> (
    None
):
    # Box 16 of 1,785.00, box 17 of 2,336.75, box 16A of 3.00: line 20 = 1,485.00, line 21 =
    # 300.00, line 40 = 1,971.63 (1,971.6281), line 41 = 365.12; line 49 = 3,456.63, line 52 =
    # 3,462.75, line 53 = -6.12, line 56 = 665.12, line 60 = 665.12 less 665.00 = 0.12, line 61 =
    # -6.00; line 64 = 3.00, line 67 = 0, line 68 = 3.00, line 69 = -3.00: Part 3b. Line
    # 75 = line 49 = 3,456.63, line 76 = 6.12, line 77 = the lesser of 0.12 and 6.12 = 0.12,
    # line 78 = 6.00, line 79 = 3,456.75. Line 68 and line 78 are both positive: line 80 = the
    # lesser of 3.00 and 6.00 = 3.00, line 81 = 3,459.75. Line 60 is positive: line 82 = line 59
    # = 665.00, lines 83 to 85 = 0, line 86 = 665.00, line 87 = "0" (line 85 is 0), line 88 =
    # 665.00. Line 68 is positive: line 89 = line 67 = 0, line 92 = 0, line 93 = 665.00.
    worksheet = return_bo(line_19="1785.00", line_39="2336.75", line_25="3.00")

    assert worksheet.get(RC381_PART_3_LINE_53).value == D("-6.12")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("0.12")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("3.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-3.00")
    assert part_3b(worksheet) == {
        "75": D("3456.63"),
        "76": D("6.12"),
        "77": D("0.12"),
        "78": D("6.00"),
        "79": D("3456.75"),
        "80": D("3.00"),
        "81": D("3459.75"),
        "82": D("665.00"),
        "83": D("0"),
        "84": D("0"),
        "85": D("0"),
        "86": D("665.00"),
        "87h": D("0"),
        "87": D("0"),
        "88": D("665.00"),
        "89": D("0"),
        "90": D("0"),
        "91": D("0"),
        "92": D("0"),
        "93": D("665.00"),
    }
    assert results(worksheet) == (D("3459.75"), D("665.00"), D("0"))


def test_return_bo_part_3b_line_87_is_line_68_less_line_80_when_that_is_less_than_line_85() -> None:
    # Box 16 of 1,430.00, box 17 of 2,570.00 (lines 53 = -104.65, 60 = -23.10 as above) and box 16A
    # of 110.00: line 68 = 110.00, line 69 = -127.75 + 110.00 = -17.75: Part 3b. Line 75 =
    # 3,358.10, line 76 = 104.65, line 77 = "0", line 78 = 104.65, line 79 = 3,358.10; lines 68 and
    # 78 both positive: line 80 = the lesser of 110.00 and 104.65 = 104.65, line 81 = 3,462.75.
    # Line 82 = line 56 = 641.90, line 83 = 23.10, line 84 = "0", line 85 = 23.10, line 86 =
    # 641.90; lines 68 and 85 both positive: line 87 = the lesser of 23.10 and (110.00 less 104.65
    # = 5.35) = 5.35, line 88 = 647.25. Line 89 = line 67 = 0, line 92 = 0, line 93 = 647.25.
    worksheet = return_bo(line_19="1430.00", line_39="2570.00", line_25="110.00")

    assert worksheet.get(RC381_PART_3_LINE_68).value == D("110.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-17.75")
    assert part_3b(worksheet) == {
        "75": D("3358.10"),
        "76": D("104.65"),
        "77": D("0"),
        "78": D("104.65"),
        "79": D("3358.10"),
        "80": D("104.65"),
        "81": D("3462.75"),
        "82": D("641.90"),
        "83": D("23.10"),
        "84": D("0"),
        "85": D("23.10"),
        "86": D("641.90"),
        "87h": D("5.35"),
        "87": D("5.35"),
        "88": D("647.25"),
        "89": D("0"),
        "90": D("0"),
        "91": D("0"),
        "92": D("0"),
        "93": D("647.25"),
    }
    assert results(worksheet) == (D("3462.75"), D("647.25"), D("0"))


def test_return_bo_part_3b_line_87_is_zero_when_line_80_takes_all_of_line_68() -> None:
    # The same T4 totals with box 16A of 50.00: line 68 = 50.00, line 69 = -127.75 + 50.00 =
    # -77.75. Lines 68 and 78 (104.65) are both positive: line 80 = the lesser of 50.00 and 104.65 =
    # 50.00, line 81 = 3,358.10 + 50.00 = 3,408.10. Lines 68 and 85 (23.10) are both positive, but
    # line 68 less line 80 is 0, so the lesser of 23.10 and 0 is 0: line 87 = 0, line 88 = 641.90.
    worksheet = return_bo(line_19="1430.00", line_39="2570.00", line_25="50.00")

    assert worksheet.get(RC381_PART_3_LINE_68).value == D("50.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-77.75")
    assert part_3b(worksheet) == {
        "75": D("3358.10"),
        "76": D("104.65"),
        "77": D("0"),
        "78": D("104.65"),
        "79": D("3358.10"),
        "80": D("50.00"),
        "81": D("3408.10"),
        "82": D("641.90"),
        "83": D("23.10"),
        "84": D("0"),
        "85": D("23.10"),
        "86": D("641.90"),
        "87h": D("0"),
        "87": D("0"),
        "88": D("641.90"),
        "89": D("0"),
        "90": D("0"),
        "91": D("0"),
        "92": D("0"),
        "93": D("641.90"),
    }
    assert results(worksheet) == (D("3408.10"), D("641.90"), D("0"))


def test_return_bo_part_3b_line_87_with_line_53_positive_is_all_of_line_68() -> None:
    # Box 16 of 1,556.00, box 17 of 2,570.00 and box 16A of 1.00: line 20 = 1,294.49, line 21 =
    # 261.51, line 40 = 2,168.44 (2,168.4375), line 41 = 401.56; line 53 = 3,462.93 less 3,462.75 =
    # 0.18, line 60 = 663.07 less 665.00 = -1.93, line 61 = -1.75; line 68 = 1.00, line 69 =
    # -0.75: Part 3b. Line 53 is positive: line 75 = line 52 = 3,462.75, line 76 = 0, line 77 = 0,
    # line 78 = 0, line 79 = 3,462.75; line 78 is not positive, so line 80 = "0", line 81 =
    # 3,462.75. Line 60 is negative: line 82 = line 56 = 663.07, line 83 = 1.93, line 84 = the
    # lesser of 0.18 and 1.93 = 0.18, line 85 = 1.75, line 86 = 663.25; lines 68 and 85 both
    # positive: line 87 = the lesser of 1.75 and (1.00 less 0 = 1.00) = 1.00, line 88 = 664.25.
    # Line 89 = line 67 = 0, line 93 = 664.25.
    worksheet = return_bo(line_19="1556.00", line_39="2570.00", line_25="1.00")

    assert worksheet.get(RC381_PART_3_LINE_53).value == D("0.18")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("-1.93")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("1.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-0.75")
    assert part_3b(worksheet) == {
        "75": D("3462.75"),
        "76": D("0"),
        "77": D("0"),
        "78": D("0"),
        "79": D("3462.75"),
        "80": D("0"),
        "81": D("3462.75"),
        "82": D("663.07"),
        "83": D("1.93"),
        "84": D("0.18"),
        "85": D("1.75"),
        "86": D("663.25"),
        "87h": D("1.00"),
        "87": D("1.00"),
        "88": D("664.25"),
        "89": D("0"),
        "90": D("0"),
        "91": D("0"),
        "92": D("0"),
        "93": D("664.25"),
    }
    assert results(worksheet) == (D("3462.75"), D("664.25"), D("0"))


def test_return_bo_part_3b_with_line_68_negative_and_line_61_positive_adds_line_91() -> None:
    # Lines 1 and 2 of 40,000 (line 52 = 3,508.65, line 59 = 678.00, line 67 = 348.00), box 16 of
    # 1,630.00 and box 17 of 2,570.00: line 20 = 1,356.05, line 21 = 273.95, line 40 = 2,168.44
    # (2,168.4375), line 41 = 401.56; line 53 = 15.84, line 56 = 675.51, line 60 = 675.51 less
    # 678.00 = -2.49, line 61 = 13.35; line 64 = 0, line 68 = -348.00, line 69 = 13.35 - 348.00 =
    # -334.65: Part 3b. Line 53 is positive: line 75 = 3,508.65, lines 76 to 80 = 0, line 81 =
    # 3,508.65. Line 60 is negative: line 82 = line 56 = 675.51, line 83 = 2.49, line 84 = the
    # lesser of 15.84 and 2.49 = 2.49, line 85 = 0, line 86 = 678.00; line 68 is negative, so line
    # 87 = "0"; line 88 = 678.00. Line 68 is negative: line 89 = line 64 = 0, line 90 = 348.00, line
    # 61 is positive: line 91 = the lesser of 13.35 and 348.00 = 13.35, line 92 = 13.35, line 93 =
    # 678.00 + 13.35 = 691.35.
    worksheet = return_bo(line_1="40000", line_2="40000", line_19="1630.00", line_39="2570.00")

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("13.35")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("-348.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-334.65")
    assert part_3b(worksheet) == {
        "75": D("3508.65"),
        "76": D("0"),
        "77": D("0"),
        "78": D("0"),
        "79": D("3508.65"),
        "80": D("0"),
        "81": D("3508.65"),
        "82": D("675.51"),
        "83": D("2.49"),
        "84": D("2.49"),
        "85": D("0"),
        "86": D("678.00"),
        "87h": D("-348.00"),
        "87": D("0"),
        "88": D("678.00"),
        "89": D("0"),
        "90": D("348.00"),
        "91": D("13.35"),
        "92": D("13.35"),
        "93": D("691.35"),
    }
    assert results(worksheet) == (D("3508.65"), D("691.35"), D("0"))


def test_return_bo_part_3b_line_89_is_line_64_when_line_68_is_negative() -> None:
    # The same lines 1 and 2 with box 16 of 1,816.65, box 17 of 2,570.00 and box 16A of 100.00:
    # line 20 = 1,511.33, line 21 = 305.32, line 40 = 2,168.44, line 41 = 401.56; line 53 =
    # 171.12, line 60 = 28.88, line 61 = 200.00; line 64 =
    # 100.00, line 67 = 348.00, line 68 = -248.00, line 69 = -48.00: Part 3b. Line 75 = line 52 =
    # 3,508.65, line 81 = 3,508.65. Line 60 is positive: line 82 = line 59 = 678.00, line 88 =
    # 678.00. Line 68 is negative: line 89 = line 64 = 100.00; line 90 = 248.00; line 61 is
    # positive: line 91 = the lesser of 200.00 and 248.00 = 200.00; line 92 = 300.00; line 93 =
    # 678.00 + 300.00 = 978.00.
    worksheet = return_bo(
        line_1="40000", line_2="40000", line_19="1816.65", line_39="2570.00", line_25="100.00"
    )

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("200.00")
    assert worksheet.get(RC381_PART_3_LINE_64).value == D("100.00")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("-248.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-48.00")
    assert part_3b(worksheet) == {
        "75": D("3508.65"),
        "76": D("0"),
        "77": D("0"),
        "78": D("0"),
        "79": D("3508.65"),
        "80": D("0"),
        "81": D("3508.65"),
        "82": D("678.00"),
        "83": D("0"),
        "84": D("0"),
        "85": D("0"),
        "86": D("678.00"),
        "87h": D("-248.00"),
        "87": D("0"),
        "88": D("678.00"),
        "89": D("100.00"),
        "90": D("248.00"),
        "91": D("200.00"),
        "92": D("300.00"),
        "93": D("978.00"),
    }
    assert results(worksheet) == (D("3508.65"), D("978.00"), D("0"))


def test_return_bo_part_3a_and_3b_steps_are_the_form_capabilities() -> None:
    worksheet = return_bo()

    for kind in (
        RC381_PART_3_LINE_73,
        RC381_PART_3_LINE_79,
        RC381_PART_3_LINE_81,
        RC381_PART_3_LINE_86,
        RC381_PART_3_LINE_88,
        RC381_PART_3_LINE_92,
        RC381_PART_3_LINE_93,
    ):
        assert isinstance(worksheet.producer_of(kind), Sum), kind.identifier
    for kind in (
        RC381_PART_3_LINE_78,
        RC381_PART_3_LINE_85,
        RC381_PART_3_LINE_87_DIFFERENCE,
    ):
        assert isinstance(worksheet.producer_of(kind), Subtract), kind.identifier
    for kind in (RC381_PART_3_LINE_76, RC381_PART_3_LINE_83, RC381_PART_3_LINE_90):
        assert isinstance(worksheet.producer_of(kind), PositivePartOfNegation), kind.identifier
    for kind in (
        RC381_PART_3_LINE_77,
        RC381_PART_3_LINE_80,
        RC381_PART_3_LINE_84,
        RC381_PART_3_LINE_87,
        RC381_PART_3_LINE_91,
    ):
        assert isinstance(worksheet.producer_of(kind), LesserOfWhenPositive), kind.identifier
    for kind in (
        RC381_PART_3_LINE_75,
        RC381_PART_3_LINE_82,
        RC381_PART_3_LINE_89,
        RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS,
        RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS,
    ):
        assert isinstance(worksheet.producer_of(kind), ChooseBySign), kind.identifier
    # Line 74 "Enter the amount from line 69" is the sign's own amount, so line 44800 is line 69
    # not below zero.
    assert isinstance(worksheet.producer_of(RC381_CPP_OVERPAYMENT), SumNotBelowZero)


# Part 4, lines 1 to 27 (the CPP side before the QPP gross-up, "for residents of a province or
# territory other than Quebec"). Return BO's Part 3 gives line 61 = line 17 + line 20 of Part 4:
# lines 49 + 56 are line 19 + line 39 of Part 3 and lines 52 + 59 are its lines 24 + 44, so line
# 61 = (line 19 - line 24) + (line 39 - line 44), which are Part 4's lines 17 and 20. With Return
# BO's lines 1 and 2 (30,000 and 40,000) Part 3's lines 22, 23, 24 and 44 are 1,410.75, 285.00,
# 1,695.75 and 2,432.00, so box 16 of 1,695.75 and box 17 of 2,432.00 make line 61 "0".

# Part 4's lines by number ("13h" is the "Line 5 minus line 12" printed inside line 13; "21h17" and
# "21h20" the "enter the amount from line 17 (show in brackets)" and "enter whichever is less:
# amount from line 20 or line 17A" printed inside line 21; "23a" and "23b" the lesser and the
# product printed inside line 23; "24h" line 24's "whichever is less", before the block "If line
# 61 of Part 3 is ... negative" decides whether line 24 takes it). Line 22 is a rate.
PART_4_KINDS: dict[str, ArtifactKind[Decimal]] = {
    "8": RC381_PART_4_LINE_8,
    "11": RC381_PART_4_LINE_11,
    "12": RC381_PART_4_LINE_12,
    "13h": RC381_PART_4_LINE_13_DIFFERENCE,
    "13": RC381_PART_4_LINE_13,
    "14": RC381_PART_4_LINE_14,
    "17": RC381_PART_4_LINE_17,
    "17A": RC381_PART_4_LINE_17A,
    "20": RC381_PART_4_LINE_20,
    "21h17": RC381_PART_4_LINE_21_FROM_LINE_17,
    "21h20": RC381_PART_4_LINE_21_LESSER,
    "21": RC381_PART_4_LINE_21,
    "23a": RC381_PART_4_LINE_23_LESSER,
    "23b": RC381_PART_4_LINE_23_MULTIPLIED,
    "23": RC381_PART_4_LINE_23,
    "24h": RC381_PART_4_LINE_24_LESSER,
    "24": RC381_PART_4_LINE_24,
    "25A": RC381_PART_4_LINE_25A,
    "26": RC381_PART_4_LINE_26,
    "27": RC381_PART_4_LINE_27,
}


def part_4(worksheet: Worksheet) -> dict[str, Decimal]:
    """Part 4's lines 8 to 27 of `worksheet`, by line number (line 22 as its rate's value)."""
    lines = {line: worksheet.get(kind).value for line, kind in PART_4_KINDS.items()}
    lines["22"] = worksheet.get(RC381_PART_4_LINE_22).value.value
    return lines


def test_return_bo_part_4_line_4_adds_lines_1_to_3() -> None:
    # Line 1 (the pensionable net self-employment earnings) is 0, line 2 (50373) is 10,000 and
    # line 3 (50399) is 2,500 (chosen election figures): line 4 = 0 + 10,000 + 2,500 = 12,500.
    # Net partnership income of 300 (T1 line 12200) makes line 1 300 and line 4 = 12,800. No
    # election and no earnings: 0. Line 4 prints no floor.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_4_LINE_4).value == D("12500")
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_4), Sum)
    assert return_bo(net_partnership_income="300").get(RC381_PART_4_LINE_4).value == D("12800")
    no_election = return_bo(cpt20_earnings="0", cpt20_t4_earnings="0")
    assert no_election.get(RC381_PART_4_LINE_4).value == D("0")


def test_return_bo_part_4_line_3_cannot_be_negative() -> None:
    # Line 3 (50399) is an amount the filer enters, like line 2: below zero is refused.
    with pytest.raises(NegativeArtifactError, match="cpt20_t4_earnings"):
        return_bo(cpt20_t4_earnings="-1")


def test_return_bo_part_4_with_line_61_positive_completes_lines_6_to_13_only() -> None:
    # Line 61 of Part 3 is 157.25, positive: complete lines 6 to 13 only, continue at line 25. Line
    # 5 = line 19 of Part 3 = 1,785.00. Line 6 (the amount from line 47, Part 3's line 20) 1,485.00
    # less line 7 (line 50, Part 3's line 22) 1,410.75 = 74.25; line 9 (line 54, line 21) 300.00
    # less line 10 (line 57, line 23) 285.00 = 15.00; line 12 = 74.25 + 15.00 = 89.25; line 13 =
    # line 5 less line 12 = 1,785.00 less 89.25 = 1,695.75 (Part 3's line 24). Line 25 is line 13,
    # so line 26 = 0 + 1,695.75 + 0 = 1,695.75 and line 27 = 1,695.75 x 16.80672 = 28,499.9954...,
    # 28,500.00. Lines 14 to 24 are not completed: line 14 = 0, and lines 24 and 25A are 0. Still
    # computed, as every line is: line 17 = 1,785.00 less 1,695.75 = 89.25, so line 17A = 0; line
    # 20 = 2,500.00 less 2,432.00 = 68.00; line 21 is 0 for two positive lines (the form is silent
    # then; its helper "line 17 in brackets" is -89.25); line 22 = 0 (17A is not more than line
    # 14, which is 0); line 23 (line 69 is positive) = the lesser of line 68 (0.00) and 17A (0).
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("157.25")
    assert part_4(worksheet) == {
        "8": D("74.25"),
        "11": D("15.00"),
        "12": D("89.25"),
        "13h": D("1695.75"),
        "13": D("1695.75"),
        "14": D("0"),
        "17": D("89.25"),
        "17A": D("0"),
        "20": D("68.00"),
        "21h17": D("-89.25"),
        "21h20": D("0"),
        "21": D("0"),
        "22": D("0"),
        "23a": D("0.00"),
        "23b": D("0.00"),
        "23": D("0.00"),
        "24h": D("0"),
        "24": D("0"),
        "25A": D("0"),
        "26": D("1695.75"),
        "27": D("28500.00"),
    }


def test_return_bo_part_4_with_line_61_positive_and_line_17_negative_ignores_lines_14_to_25a() -> (
    None
):
    # Box 16 of 1,600 and box 17 of 2,570 (Part 3: line 20 = 1,331.09, line 21 = 268.91; line 61 =
    # -95.75 + 138.00 = 42.25, positive). Line 8 = 1,331.09 less 1,410.75 = -79.66, line 11 = 268.91
    # less 285.00 = -16.09, line 12 = -95.75 and line 13 = 1,600 less -95.75 = 1,695.75. Line 17 =
    # 1,600 less 1,695.75 = -95.75, so line 17A = 95.75; line 20 = 2,570 less 2,432.00 = 138.00 and
    # line 21 is the lesser of 138.00 and 95.75: 95.75, computed. Line 14 is 0, so 17A is more than
    # line 14 and line 22 is 1. But line 61 is positive: lines 24 and 25A are 0 whatever lines 21
    # and 23 are, so line 26 = line 13 = 1,695.75 and line 27 = 28,500.00.
    worksheet = return_bo(line_19="1600", line_39="2570")

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("42.25")
    assert part_4(worksheet) == {
        "8": D("-79.66"),
        "11": D("-16.09"),
        "12": D("-95.75"),
        "13h": D("1695.75"),
        "13": D("1695.75"),
        "14": D("0"),
        "17": D("-95.75"),
        "17A": D("95.75"),
        "20": D("138.00"),
        "21h17": D("0"),
        "21h20": D("95.75"),
        "21": D("95.75"),
        "22": D("1"),
        "23a": D("0.00"),
        "23b": D("0.00"),
        "23": D("0.00"),
        "24h": D("0.00"),
        "24": D("0"),
        "25A": D("0"),
        "26": D("1695.75"),
        "27": D("28500.00"),
    }


def test_return_bo_part_4_with_no_t4_contributions_lines_8_11_and_12_are_negative() -> None:
    # Line 1 of 3,700 and line 2 of 66,300 with no box 16 and box 17 of 4,253 (Part 3: lines 20 and
    # 21 are 0.00; line 52 = 3,575.18, line 59 = 665.00; line 53 = 13.29 and line 60 = -0.47, so
    # line 61 = 12.82, positive). Line 8 = 0.00 less 173.99 = -173.99, line 11 = 0.00 less 35.15 =
    # -35.15, line 12 = -209.14 (in brackets); line 13 = line 5 less line 12 = 0 less -209.14 =
    # 209.14. Line 17 = 0 less 209.14 = -209.14, so 17A = 209.14; line 20 = 4,253 less 4,031.04 =
    # 221.96; line 21 = the lesser of 221.96 and 209.14 = 209.14, computed. Line 61 is positive:
    # lines 24 and 25A are 0, line 26 = 209.14, line 27 = 209.14 x 16.80672 = 3,514.96.
    worksheet = return_bo(line_1="3700", line_2="66300", line_19="0", line_39="4253")

    assert part_4(worksheet) == {
        "8": D("-173.99"),
        "11": D("-35.15"),
        "12": D("-209.14"),
        "13h": D("209.14"),
        "13": D("209.14"),
        "14": D("0"),
        "17": D("-209.14"),
        "17A": D("209.14"),
        "20": D("221.96"),
        "21h17": D("0"),
        "21h20": D("209.14"),
        "21": D("209.14"),
        "22": D("1"),
        "23a": D("0.00"),
        "23b": D("0.00"),
        "23": D("0.00"),
        "24h": D("0.00"),
        "24": D("0"),
        "25A": D("0"),
        "26": D("209.14"),
        "27": D("3514.96"),
    }


def test_return_bo_part_4_with_line_61_positive_line_25a_stays_zero_for_a_negative_line_21() -> (
    None
):
    # Box 16 of 1,750 and box 17 of 2,350 on a line 1 of 29,500 (Part 3: line 20 = 1,750 x 83.1933%
    # = 1,455.88, line 21 = 294.12, line 24 = 1,386.71 + 280.14 = 1,666.85; line 61 = 0.76 + 1.31 =
    # 2.07, positive). Line 8 = 1,455.88 less 1,386.71 = 69.17, line 11 = 294.12 less 280.14 =
    # 13.98, line 12 = 83.15, line 13 = 1,750 less 83.15 = 1,666.85. Line 17 = 1,750 less 1,666.85
    # = 83.15 (positive), line 20 = 2,350 less 2,431.08 = -81.08: line 21 is the amount from line
    # 17 in brackets, -83.15, computed; but line 61 is positive, so line 25A is 0 and line 26 =
    # 1,666.85.
    worksheet = return_bo(line_19="1750", line_39="2350", line_1="29500")

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("2.07")
    assert part_4(worksheet) == {
        "8": D("69.17"),
        "11": D("13.98"),
        "12": D("83.15"),
        "13h": D("1666.85"),
        "13": D("1666.85"),
        "14": D("0"),
        "17": D("83.15"),
        "17A": D("0"),
        "20": D("-81.08"),
        "21h17": D("-83.15"),
        "21h20": D("0"),
        "21": D("-83.15"),
        "22": D("0"),
        "23a": D("0.00"),
        "23b": D("0.00"),
        "23": D("0.00"),
        "24h": D("0"),
        "24": D("0"),
        "25A": D("0"),
        "26": D("1666.85"),
        "27": D("28014.28"),
    }


def test_return_bo_part_4_with_line_61_positive_line_24_stays_zero_for_a_positive_line_23() -> None:
    # The same box 16 of 1,600 and box 17 of 2,570 (line 61 = 42.25, positive) with box 16A of
    # 100.00: line 68 = 100.00 less 0 = 100.00 and line 69 = 42.25 + 100.00 = 142.25, positive, so
    # line 23 is the lesser of line 68 (100.00) and line 17A (95.75): 95.75, and line 24's
    # "whichever is less" is 95.75; but line 61 is positive, so line 24 is 0 and line 26 = line 13 =
    # 1,695.75.
    worksheet = return_bo(line_19="1600", line_39="2570", line_25="100.00")

    assert worksheet.get(RC381_PART_3_LINE_69).value == D("142.25")
    lines = part_4(worksheet)
    assert lines["23"] == D("95.75")
    assert lines["24h"] == D("95.75")
    assert lines["24"] == D("0")
    assert lines["26"] == D("1695.75")


def test_return_bo_part_4_with_line_61_negative_line_17_negative_and_line_20_positive() -> None:
    # Box 16 of 1,430 and box 17 of 2,570 (Part 3: line 20 = 1,430 x 83.1933% = 1,189.66, line 21 =
    # 240.34; line 53 = -104.65 and line 60 = -23.10, so line 61 = -127.75, negative; line 68 =
    # 0.00, line 69 = -127.75). Line 61 negative: line 5 (1,430) is entered on line 13, and line 14
    # = 127.75. Line 17 = 1,430 less 1,695.75 = -265.75, so 17A = 265.75; line 20 = 2,570 less
    # 2,432.00 = 138.00. Line 21: line 20 is positive, so the lesser of 138.00 and 265.75 = 138.00.
    # Line 22: 17A (265.75) is more than line 14 (127.75): 1. Line 23: line 69 is negative, so line
    # 68 x the rate at line 22 = 0.00 x 1 = 0.00; line 24 = the lesser of 265.75 and 0.00 = 0.00;
    # line 25A = line 21 = 138.00. Line 26 = 0.00 + 1,430 + 138.00 = 1,568.00 and line 27 = 1,568.00
    # x 16.80672 = 26,352.93696, 26,352.94.
    worksheet = return_bo(line_19="1430", line_39="2570")

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("-127.75")
    assert part_4(worksheet) == {
        "8": D("-221.09"),
        "11": D("-44.66"),
        "12": D("-265.75"),
        "13h": D("1695.75"),
        "13": D("1430"),
        "14": D("127.75"),
        "17": D("-265.75"),
        "17A": D("265.75"),
        "20": D("138.00"),
        "21h17": D("0"),
        "21h20": D("138.00"),
        "21": D("138.00"),
        "22": D("1"),
        "23a": D("0.00"),
        "23b": D("0.00"),
        "23": D("0.00"),
        "24h": D("0.00"),
        "24": D("0.00"),
        "25A": D("138.00"),
        "26": D("1568.00"),
        "27": D("26352.94"),
    }


def test_return_bo_part_4_line_23_is_line_68_times_the_rate_when_line_69_is_negative() -> None:
    # The same box 16 of 1,430 and box 17 of 2,570 with box 16A of 100.00: line 68 = 100.00 and line
    # 69 = -127.75 + 100.00 = -27.75, still negative: line 23 = 100.00 x the rate at line 22 (1) =
    # 100.00. Line 24 = the lesser of line 17A (265.75) and line 23 = 100.00. Line 26 = 100.00 +
    # 1,430 + 138.00 = 1,668.00; line 27 = 1,668.00 x 16.80672 = 28,033.60896, 28,033.61.
    worksheet = return_bo(line_19="1430", line_39="2570", line_25="100.00")

    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-27.75")
    lines = part_4(worksheet)
    assert lines["23a"] == D("100.00")
    assert lines["23b"] == D("100.00")
    assert lines["23"] == D("100.00")
    assert lines["24"] == D("100.00")
    assert lines["25A"] == D("138.00")
    assert lines["26"] == D("1668.00")
    assert lines["27"] == D("28033.61")


def test_return_bo_part_4_line_23_is_the_lesser_when_line_69_is_positive() -> None:
    # Box 16A of 200.00: line 68 = 200.00 and line 69 = -127.75 + 200.00 = 72.25, positive: line 23
    # = the lesser of line 68 (200.00) and line 17A (265.75) = 200.00; line 24 = 200.00. Line 26 =
    # 200.00 + 1,430 + 138.00 = 1,768.00; line 27 = 1,768.00 x 16.80672 = 29,714.28096, 29,714.28.
    worksheet = return_bo(line_19="1430", line_39="2570", line_25="200.00")

    assert worksheet.get(RC381_PART_3_LINE_69).value == D("72.25")
    lines = part_4(worksheet)
    assert lines["23"] == D("200.00")
    assert lines["24"] == D("200.00")
    assert lines["26"] == D("1768.00")
    assert lines["27"] == D("29714.28")


def test_return_bo_part_4_line_23_takes_the_lesser_branch_when_line_69_is_zero() -> None:
    # Box 16A of 127.75: line 68 = 127.75 and line 69 = -127.75 + 127.75 = 0.00, "positive or "0"":
    # line 23 = the lesser of 127.75 and 265.75 = 127.75. Line 24 = 127.75; line 26 = 127.75 + 1,430
    # + 138.00 = 1,695.75; line 27 = 28,500.00.
    worksheet = return_bo(line_19="1430", line_39="2570", line_25="127.75")

    assert worksheet.get(RC381_PART_3_LINE_69).value == D("0.00")
    lines = part_4(worksheet)
    assert lines["23"] == D("127.75")
    assert lines["24"] == D("127.75")
    assert lines["26"] == D("1695.75")
    assert lines["27"] == D("28500.00")


def test_return_bo_part_4_line_23_is_line_17a_when_line_68_is_more_and_line_69_is_positive() -> (
    None
):
    # Box 16A of 700.00: line 68 = 700.00 and line 69 = 572.25, positive: line 23 = the lesser of
    # 700.00 and line 17A (265.75) = 265.75, not 700.00 x 1. Line 24 = the lesser of 265.75 and
    # 265.75 = 265.75; line 26 = 265.75 + 1,430 + 138.00 = 1,833.75; line 27 = 1,833.75 x 16.80672 =
    # 30,819.3228, 30,819.32.
    worksheet = return_bo(line_19="1430", line_39="2570", line_25="700.00")

    assert worksheet.get(RC381_PART_3_LINE_69).value == D("572.25")
    lines = part_4(worksheet)
    assert lines["23a"] == D("265.75")
    assert lines["23b"] == D("700.00")
    assert lines["23"] == D("265.75")
    assert lines["24"] == D("265.75")
    assert lines["26"] == D("1833.75")
    assert lines["27"] == D("30819.32")


def test_return_bo_part_4_with_line_61_negative_and_lines_17_and_20_both_negative() -> None:
    # Box 16 of 1,000 and box 17 of 2,000 (Part 3: line 20 = 831.93, line 21 = 168.07; line 61 =
    # -695.75 - 432.00 = -1,127.75, line 68 = 0.00, line 69 = -1,127.75). Line 5 (1,000) is entered
    # on line 13; line 14 = 1,127.75. Line 17 = -695.75 (17A = 695.75) and line 20 = 2,000 less
    # 2,432.00 = -432.00, both negative: line 21 = 0. Line 22 = 695.75 / 1,127.75 = 0.61693637...,
    # cut at the fifth decimal place: 0.61693 (rounding would give 0.61694). Line 23 (line 69 is
    # negative) = 0.00 x 0.61693 = 0.00, line 24 = 0.00, line 25A = 0. Line 26 = 0.00 + 1,000 + 0 =
    # 1,000.00; line 27 = 1,000.00 x 16.80672 = 16,806.72.
    worksheet = return_bo(line_19="1000", line_39="2000")

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("-1127.75")
    assert part_4(worksheet) == {
        "8": D("-578.82"),
        "11": D("-116.93"),
        "12": D("-695.75"),
        "13h": D("1695.75"),
        "13": D("1000"),
        "14": D("1127.75"),
        "17": D("-695.75"),
        "17A": D("695.75"),
        "20": D("-432.00"),
        "21h17": D("0"),
        "21h20": D("0"),
        "21": D("0"),
        "22": D("0.61693"),
        "23a": D("0.00"),
        "23b": D("0.00"),
        "23": D("0.00"),
        "24h": D("0.00"),
        "24": D("0.00"),
        "25A": D("0"),
        "26": D("1000.00"),
        "27": D("16806.72"),
    }


def test_return_bo_part_4_line_23_is_line_68_times_the_truncated_rate_to_the_cent() -> None:
    # The same with box 16A of 100.00: line 68 = 100.00, line 69 = -1,127.75 + 100.00 = -1,027.75
    # negative: line 23 = 100.00 x 0.61693 = 61.693, 61.69. Line 24 = the lesser of 695.75 and
    # 61.69 = 61.69; line 26 = 61.69 + 1,000 + 0 = 1,061.69; line 27 = 1,061.69 x 16.80672 =
    # 17,843.52656, 17,843.53.
    worksheet = return_bo(line_19="1000", line_39="2000", line_25="100.00")

    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-1027.75")
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_23_MULTIPLIED), ApplyChosenRate)
    lines = part_4(worksheet)
    assert lines["22"] == D("0.61693")
    assert lines["23b"] == D("61.69")
    assert lines["23"] == D("61.69")
    assert lines["24"] == D("61.69")
    assert lines["26"] == D("1061.69")
    assert lines["27"] == D("17843.53")


def test_return_bo_part_4_with_line_61_negative_line_17_positive_and_line_20_negative() -> None:
    # Box 16 of 1,700 and box 17 of 1,000 (Part 3: line 20 = 1,414.29, line 21 = 285.71; line 61 =
    # -1,204.71 - 223.04 = -1,427.75, negative). Line 5 (1,700) is entered on line 13; line 14 =
    # 1,427.75. Line 17 = 1,700 less 1,695.75 = 4.25 (positive), 17A = 0; line 20 = 1,000 less
    # 2,432.00 = -1,432.00. Line 21: line 17 is positive: the amount from line 17 in brackets,
    # -4.25. Line 22 = 0 / 1,427.75 = 0.00000; line 23 = 0.00 x 0 = 0.00; line 24 = the lesser of
    # 0 and 0.00 = 0; line 25A = line 21 = -4.25. Line 26 = 0 + 1,700 + -4.25 = 1,695.75 and
    # line 27 = 1,695.75 x 16.80672 = 28,500.00.
    worksheet = return_bo(line_19="1700", line_39="1000")

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("-1427.75")
    assert part_4(worksheet) == {
        "8": D("3.54"),
        "11": D("0.71"),
        "12": D("4.25"),
        "13h": D("1695.75"),
        "13": D("1700"),
        "14": D("1427.75"),
        "17": D("4.25"),
        "17A": D("0"),
        "20": D("-1432.00"),
        "21h17": D("-4.25"),
        "21h20": D("0"),
        "21": D("-4.25"),
        "22": D("0"),
        "23a": D("0.00"),
        "23b": D("0.00"),
        "23": D("0.00"),
        "24h": D("0"),
        "24": D("0"),
        "25A": D("-4.25"),
        "26": D("1695.75"),
        "27": D("28500.00"),
    }


def test_return_bo_part_4_line_22_is_1_when_line_17a_equals_line_14() -> None:
    # Box 16 of 1,000 and box 17 of 2,432.00 (Part 3's line 44, so line 20 = 0.00): line 61 =
    # -695.75 + 0.00, line 14 = 695.75 and line 17A = 695.75. 17A is not more than line 14, so
    # line 22 is 695.75 / 695.75 = 1.00000. Line 21 = 0 (line 20 is "0"); line 23 = 0.00 x 1 =
    # 0.00, line 24 = 0.00, line 25A = 0; line 26 = 1,000.00 and line 27 = 16,806.72.
    worksheet = return_bo(line_19="1000", line_39="2432.00")

    lines = part_4(worksheet)
    assert lines["14"] == D("695.75")
    assert lines["17A"] == D("695.75")
    assert lines["20"] == D("0.00")
    assert lines["21"] == D("0")
    assert lines["22"] == D("1.00000")
    assert lines["26"] == D("1000.00")
    assert lines["27"] == D("16806.72")


def test_return_bo_part_4_with_literal_line_68_negative_lines_23_and_24_are_negative() -> None:
    # Lines 1 and 2 of 40,000 each (Part 3: line 22 = 1,678.05, line 23 = 339.00, line 24 =
    # 2,017.05, line 44 = 2,169.60, line 67 = 348.00), box 16 of 1,000 and box 17 of 1,500 (line
    # 20 = 831.93, line 21 = 168.07). Line 8 = 831.93 less 1,678.05 = -846.12, line 11 = 168.07
    # less 339.00 = -170.93, line 12 = -1,017.05. Line 17 = 1,000 less 2,017.05 = -1,017.05 (17A
    # = 1,017.05); line 20 = 1,500 less 2,169.60 = -669.60. Line 61 = -1,017.05 - 669.60 =
    # -1,686.65 (line 14 = 1,686.65); line 68 = 0 less 348.00 = -348.00, line 69 = -2,034.65.
    # Line 22 = 1,017.05 / 1,686.65 = 0.6030000296, 0.60300. Line 69 is negative: line 23 = line 68
    # x 0.60300 = -209.844, -209.84. Line 24 prints "whichever is less: amount from line 17A or
    # line 23" with no floor: the lesser of 1,017.05 and -209.84, -209.84 (to be confirmed: a
    # negative line 24 reduces line 26). Line 25A = 0 (line 21 is 0). Line 26 = -209.84 + 1,000 +
    # 0 = 790.16 and line 27 = 790.16 x 16.80672 = 13,279.99788, 13,280.00.
    worksheet = return_bo(line_1="40000", line_2="40000", line_19="1000", line_39="1500")

    assert worksheet.get(RC381_PART_3_LINE_68).value == D("-348.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("-2034.65")
    assert part_4(worksheet) == {
        "8": D("-846.12"),
        "11": D("-170.93"),
        "12": D("-1017.05"),
        "13h": D("2017.05"),
        "13": D("1000"),
        "14": D("1686.65"),
        "17": D("-1017.05"),
        "17A": D("1017.05"),
        "20": D("-669.60"),
        "21h17": D("0"),
        "21h20": D("0"),
        "21": D("0"),
        "22": D("0.60300"),
        "23a": D("-348.00"),
        "23b": D("-209.84"),
        "23": D("-209.84"),
        "24h": D("-209.84"),
        "24": D("-209.84"),
        "25A": D("0"),
        "26": D("790.16"),
        "27": D("13280.00"),
    }


def test_return_bo_part_4_with_line_61_zero_enters_line_5_on_line_26() -> None:
    # Box 16 of 1,695.75 (Part 3's line 24) and box 17 of 2,432.00 (its line 44): lines 17 and 20
    # are 0.00 and line 61 = 0.00. Do not complete lines 6 to 24: "Enter the amount from line 5 on
    # line 26 and continue at line 27": line 26 = 1,695.75 and line 27 = 1,695.75 x 16.80672 =
    # 28,500.00. Line 13 (the amount carried to line 25) is line 5; lines 24 and 25A are 0.
    worksheet = return_bo(line_19="1695.75", line_39="2432.00")

    assert worksheet.get(RC381_PART_3_LINE_61).value == D("0.00")
    assert part_4(worksheet) == {
        "8": D("0.00"),
        "11": D("0.00"),
        "12": D("0.00"),
        "13h": D("1695.75"),
        "13": D("1695.75"),
        "14": D("0.00"),
        "17": D("0.00"),
        "17A": D("0.00"),
        "20": D("0.00"),
        "21h17": D("0"),
        "21h20": D("0"),
        "21": D("0"),
        "22": D("0"),
        "23a": D("0.00"),
        "23b": D("0.00"),
        "23": D("0.00"),
        "24h": D("0.00"),
        "24": D("0"),
        "25A": D("0"),
        "26": D("1695.75"),
        "27": D("28500.00"),
    }


def test_return_bo_part_4_with_line_61_zero_line_21_is_computed_but_not_entered() -> None:
    # Box 16 of 1,750 and box 17 of 2,347.93 on a line 1 of 29,500: line 17 = 1,750 less 1,666.85
    # (Part 3's line 24) = 83.15 and line 20 = 2,347.93 less 2,431.08 = -83.15, so line 61 =
    # 0.00. Line 26 is line 5 (1,750). Line 21 = the amount from line 17 in brackets, -83.15
    # (line 20 is negative), but line 25A takes line 21 only when line 61 is negative: 0. Line 27 =
    # 1,750 x 16.80672 = 29,411.76.
    worksheet = return_bo(line_19="1750", line_39="2347.93", line_1="29500")

    lines = part_4(worksheet)
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("0.00")
    assert lines["17"] == D("83.15")
    assert lines["20"] == D("-83.15")
    assert lines["21"] == D("-83.15")
    assert lines["25A"] == D("0")
    assert lines["13"] == D("1750")
    assert lines["26"] == D("1750")
    assert lines["27"] == D("29411.76")


def test_return_bo_part_4_with_line_61_zero_line_22_is_1_for_a_positive_line_17a() -> None:
    # Box 16 of 1,557.75 and box 17 of 2,570: line 17 = -138.00 (17A = 138.00), line 20 = 2,570 less
    # 2,432.00 = 138.00, line 61 = 0.00 and so line 14 = 0.00. 17A is more than line 14: line 22 = 1
    # (the test comes before any division by 0). Line 21 = the lesser of 138.00 and 138.00,
    # computed; lines 24 and 25A are 0, line 26 = line 5 = 1,557.75 and line 27 = 26,180.67.
    worksheet = return_bo(line_19="1557.75", line_39="2570")

    lines = part_4(worksheet)
    assert lines["14"] == D("0.00")
    assert lines["17A"] == D("138.00")
    assert lines["22"] == D("1")
    assert lines["21"] == D("138.00")
    assert lines["24"] == D("0")
    assert lines["25A"] == D("0")
    assert lines["26"] == D("1557.75")
    assert lines["27"] == D("26180.67")


# Part 4 line 21 "If line 17 and line 20 are both negative or either amount is "0", enter "0". If
# line 17 is positive, enter the amount from line 17 (show in brackets). If line 20 is positive,
# enter whichever is less: amount from line 20 or line 17A." (box 16, box 17, line 17, line 20,
# line 21; line 17 = box 16 less 1,695.75 and line 20 = box 17 less 2,432.00; box 17 is at most
# 2,570 on a line 2 of 40,000)
LINE_21_CASES = [
    # Line 17 negative, line 20 positive: the lesser of line 20 and line 17A (695.75 for a box 16 of
    # 1,000, 95.75 for 1,600).
    ("1000", "2570", "-695.75", "138.00", "138.00"),
    ("1600", "2570", "-95.75", "138.00", "95.75"),
    ("1000", "2500", "-695.75", "68.00", "68.00"),
    # Both negative: "0".
    ("1000", "2000", "-695.75", "-432.00", "0"),
    # Line 17 positive, line 20 negative: line 17 in brackets.
    ("1785.00", "1000", "89.25", "-1432.00", "-89.25"),
    ("1785.00", "2127.75", "89.25", "-304.25", "-89.25"),
    # Either amount "0": "0", whatever the other is.
    ("1785.00", "2432.00", "89.25", "0.00", "0"),
    ("1000", "2432.00", "-695.75", "0.00", "0"),
    ("1695.75", "2570", "0.00", "138.00", "0"),
    ("1695.75", "1000", "0.00", "-1432.00", "0"),
    ("1695.75", "2432.00", "0.00", "0.00", "0"),
    # Both positive: the form is silent; the reading is "0" (the lesser of line 20 and line 17A,
    # which is 0 for a line 17 that is not negative, and not line 17 in brackets).
    ("1785.00", "2500.00", "89.25", "68.00", "0"),
]


@pytest.mark.parametrize(("box_16", "box_17", "line_17", "line_20", "line_21"), LINE_21_CASES)
def test_return_bo_part_4_line_21_follows_the_sentences_on_lines_17_and_20(
    box_16: str, box_17: str, line_17: str, line_20: str, line_21: str
) -> None:
    worksheet = return_bo(line_19=box_16, line_39=box_17)

    assert worksheet.get(RC381_PART_4_LINE_17).value == D(line_17)
    assert worksheet.get(RC381_PART_4_LINE_20).value == D(line_20)
    assert worksheet.get(RC381_PART_4_LINE_21).value == D(line_21)


# Part 4 line 22 "If line 17A is more than line 14, enter "1". If not, enter the result of line 17A
# divided by line 14 (calculated to the fifth decimal place without rounding)." (box 16, box 17,
# line 14, line 17A, line 22)
LINE_22_CASES = [
    # More than: 1, even when line 14 is 0.
    ("1430", "2570", "127.75", "265.75", "1"),
    ("1557.75", "2570", "0.00", "138.00", "1"),
    ("1600", "2570", "0", "95.75", "1"),
    # Equal: 17A over 14 is 1.00000.
    ("1000", "2432.00", "695.75", "695.75", "1.00000"),
    # Less than: the quotient cut at the fifth decimal place (0.61693637...).
    ("1000", "2000", "1127.75", "695.75", "0.61693"),
    # Line 17A is 0: 0 over line 14.
    ("1785.00", "1000", "1342.75", "0", "0.00000"),
    # Both 0: a zero divisor gives 0.
    ("1785.00", "2500.00", "0", "0", "0"),
    ("1695.75", "2432.00", "0.00", "0.00", "0"),
]


@pytest.mark.parametrize(("box_16", "box_17", "line_14", "line_17a", "line_22"), LINE_22_CASES)
def test_return_bo_part_4_line_22_is_the_truncated_ratio_capped_at_one(
    box_16: str, box_17: str, line_14: str, line_17a: str, line_22: str
) -> None:
    worksheet = return_bo(line_19=box_16, line_39=box_17)

    assert worksheet.get(RC381_PART_4_LINE_14).value == D(line_14)
    assert worksheet.get(RC381_PART_4_LINE_17A).value == D(line_17a)
    assert worksheet.get(RC381_PART_4_LINE_22).value == Rate(D(line_22))


def test_return_bo_part_4_steps_are_the_form_capabilities() -> None:
    worksheet = return_bo()

    for kind in (RC381_PART_4_LINE_4, RC381_PART_4_LINE_12, RC381_PART_4_LINE_26):
        assert isinstance(worksheet.producer_of(kind), Sum), kind.identifier
    for kind in (
        RC381_PART_4_LINE_8,
        RC381_PART_4_LINE_11,
        RC381_PART_4_LINE_13_DIFFERENCE,
        RC381_PART_4_LINE_17,
        RC381_PART_4_LINE_20,
    ):
        assert isinstance(worksheet.producer_of(kind), Subtract), kind.identifier
    for kind in (RC381_PART_4_LINE_14, RC381_PART_4_LINE_17A):
        assert isinstance(worksheet.producer_of(kind), PositivePartOfNegation), kind.identifier
    for kind in (
        RC381_PART_4_LINE_13,
        RC381_PART_4_LINE_21,
        RC381_PART_4_LINE_23,
        RC381_PART_4_LINE_24,
        RC381_PART_4_LINE_25A,
    ):
        assert isinstance(worksheet.producer_of(kind), ChooseBySign), kind.identifier
    # Line 21's two printed results: the amount from line 17 "(show in brackets)" and "whichever is
    # less: amount from line 20 or line 17A".
    assert isinstance(
        worksheet.producer_of(RC381_PART_4_LINE_21_FROM_LINE_17), LesserOfWhenPositiveInBrackets
    )
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_21_LESSER), LesserOfWhenPositive)
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_22), RatioTruncatedAtMostOne)
    for kind in (RC381_PART_4_LINE_23_LESSER, RC381_PART_4_LINE_24_LESSER):
        assert isinstance(worksheet.producer_of(kind), LesserOf), kind.identifier
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_23_MULTIPLIED), ApplyChosenRate)
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_27), ApplyFraction)
    # Form RC381 Part 4 lines 31 to 56: the sums and differences, the signs read by "If line 61 of
    # Part 3 is ..." and "If line 68 of Part 3 is positive ...", the helpers printed inside lines
    # 31, 35A, 46 and 51, the positive parts of lines 33 and 54, the gross-up of line 41.
    for kind in (
        RC381_PART_4_LINE_35A,
        RC381_PART_4_LINE_40,
        RC381_PART_4_LINE_42,
        RC381_PART_4_LINE_53,
        RC381_PART_4_LINE_56,
    ):
        assert isinstance(worksheet.producer_of(kind), Sum), kind.identifier
    for kind in (
        RC381_PART_4_LINE_31_DIFFERENCE,
        RC381_PART_4_LINE_32,
        RC381_PART_4_LINE_35,
        RC381_PART_4_LINE_38,
        RC381_PART_4_LINE_46_DIFFERENCE,
        RC381_PART_4_LINE_47,
        RC381_PART_4_LINE_51_DIFFERENCE,
        RC381_PART_4_LINE_52,
    ):
        assert isinstance(worksheet.producer_of(kind), Subtract), kind.identifier
    for kind in (RC381_PART_4_LINE_33, RC381_PART_4_LINE_54):
        assert isinstance(worksheet.producer_of(kind), PositivePartOfNegation), kind.identifier
    for kind in (
        RC381_PART_4_LINE_31,
        RC381_PART_4_LINE_35AA,
        RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO,
        RC381_PART_4_LINE_35AB,
        RC381_PART_4_LINE_46,
        RC381_PART_4_LINE_51,
    ):
        assert isinstance(worksheet.producer_of(kind), ChooseBySign), kind.identifier
    # "Whichever is less ... when positive" (lines 34, 35A's amount from line 17 and 55) and its
    # "show in brackets" sibling (35A's amount from line 20).
    for kind in (RC381_PART_4_LINE_34, RC381_PART_4_LINE_35AA_FROM_LINE_17, RC381_PART_4_LINE_55):
        assert type(worksheet.producer_of(kind)) is LesserOfWhenPositive, kind.identifier
    assert isinstance(
        worksheet.producer_of(RC381_PART_4_LINE_35AB_FROM_LINE_20), LesserOfWhenPositiveInBrackets
    )
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_36), SumNotBelowZero)
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_39), LesserOf)
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_41), ApplyFraction)
    # Form RC381 Part 4 lines 57 to 91: the floored differences of lines 59, 61, 65, 68, 69 and 77,
    # the unfloored differences of lines 70, 80, 82 and 90, the sums of lines 74, 87 and 88, the
    # "whichever is less" of lines 62 and 83 (the latter before "If line 74 is more than line 57"),
    # line 76's division by 4%, the tiers of lines 84 to 86, the "if positive" amounts of line 89
    # and line 42100 (floored sums), line 89's "x 2", the positive amount of line 91 and its 50%.
    for kind in (
        RC381_PART_4_LINE_59,
        RC381_PART_4_LINE_61,
        RC381_PART_4_LINE_65,
        RC381_PART_4_LINE_68,
        RC381_PART_4_LINE_69,
        RC381_PART_4_LINE_77,
    ):
        assert isinstance(worksheet.producer_of(kind), SubtractNotBelowZero), kind.identifier
    for kind in (
        RC381_PART_4_LINE_70,
        RC381_PART_4_LINE_80,
        RC381_PART_4_LINE_82,
        RC381_PART_4_LINE_90,
    ):
        assert isinstance(worksheet.producer_of(kind), Subtract), kind.identifier
    for kind in (RC381_PART_4_LINE_74, RC381_PART_4_LINE_87, RC381_PART_4_LINE_88):
        assert isinstance(worksheet.producer_of(kind), Sum), kind.identifier
    for kind in (RC381_PART_4_LINE_62, RC381_PART_4_LINE_83_LESSER):
        assert isinstance(worksheet.producer_of(kind), LesserOf), kind.identifier
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_83), AmountWhenMore)
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_76), DividedByRate)
    for kind in (RC381_PART_4_LINE_84, RC381_PART_4_LINE_85, RC381_PART_4_LINE_86):
        assert isinstance(worksheet.producer_of(kind), TieredContribution), kind.identifier
    for kind in (RC381_PART_4_LINE_89_FROM_LINE_69, RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS):
        assert isinstance(worksheet.producer_of(kind), SumNotBelowZero), kind.identifier
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_89), ApplyFraction)
    assert isinstance(
        worksheet.producer_of(RC381_PART_4_LINE_91_FROM_LINE_90), PositivePartOfNegation
    )
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_91), ApplyRate)
    # Form RC381 Part 4 lines 92 to 110: the choices by the sign of line 53, 60 and 68 of Part 3
    # (lines 92, 99 and 106), the positive amounts of lines 93, 100 and 107, the "whichever is
    # less" of lines 94, 97, 101, 104 and 108 when the lines are positive, the differences of
    # lines 95 and 102 and the one printed inside line 104, and the sums of lines 96, 98, 103, 105,
    # 109 and 110.
    for kind in (RC381_PART_4_LINE_92, RC381_PART_4_LINE_99, RC381_PART_4_LINE_106):
        assert isinstance(worksheet.producer_of(kind), ChooseBySign), kind.identifier
    for kind in (RC381_PART_4_LINE_93, RC381_PART_4_LINE_100, RC381_PART_4_LINE_107):
        assert isinstance(worksheet.producer_of(kind), PositivePartOfNegation), kind.identifier
    for kind in (
        RC381_PART_4_LINE_94,
        RC381_PART_4_LINE_97,
        RC381_PART_4_LINE_101,
        RC381_PART_4_LINE_104,
        RC381_PART_4_LINE_108,
    ):
        assert isinstance(worksheet.producer_of(kind), LesserOfWhenPositive), kind.identifier
    for kind in (
        RC381_PART_4_LINE_95,
        RC381_PART_4_LINE_102,
        RC381_PART_4_LINE_104_DIFFERENCE,
    ):
        assert isinstance(worksheet.producer_of(kind), Subtract), kind.identifier
    for kind in (
        RC381_PART_4_LINE_96,
        RC381_PART_4_LINE_98,
        RC381_PART_4_LINE_103,
        RC381_PART_4_LINE_105,
        RC381_PART_4_LINE_109,
        RC381_PART_4_LINE_110,
    ):
        assert isinstance(worksheet.producer_of(kind), Sum), kind.identifier
    # Form RC381 Part 4 lines 111 to 129: lines 111, 112, 125 "× 50%" and line 116 "A × 83.1933%"
    # are rates of an amount, line 114 is line 69 of Part 3 not below zero, line 113 and line 129
    # are sums, lines 115, 118, 121 and 124 differences, A the lesser of lines 113 and 114, line
    # 127 the positive amount of a negative line 115 and line 128 a difference not below zero.
    for kind in (
        RC381_PART_4_LINE_111,
        RC381_PART_4_LINE_112,
        RC381_PART_4_LINE_116,
        RC381_PART_4_LINE_125,
    ):
        assert isinstance(worksheet.producer_of(kind), ApplyRate), kind.identifier
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_114), SumNotBelowZero)
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_116_LESSER), LesserOf)
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_127), PositivePartOfNegation)
    assert isinstance(worksheet.producer_of(RC381_PART_4_LINE_128), SubtractNotBelowZero)
    for kind in (
        RC381_PART_4_LINE_115,
        RC381_PART_4_LINE_118,
        RC381_PART_4_LINE_121,
        RC381_PART_4_LINE_124,
    ):
        assert isinstance(worksheet.producer_of(kind), Subtract), kind.identifier
    for kind in (
        RC381_PART_4_LINE_113,
        RC381_PART_4_LINE_129,
        RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
    ):
        assert isinstance(worksheet.producer_of(kind), Sum), kind.identifier
    # The final selection: the sign of lines 70 and 83 added chooses each result.
    for kind in (
        RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
        RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
        RC381_CPP_OVERPAYMENT_ON_RETURN,
        RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
        RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    ):
        assert isinstance(worksheet.producer_of(kind), ChooseBySign), kind.identifier


def test_return_bo_the_cpt20_election_reaches_the_t1_lines() -> None:
    # Part 4 line 4 is read by lines 62, 68, 74 and 80, and the final selection's six results are
    # the T1 lines (the return carries Form RC381, not Schedule 8): the same return with and
    # without lines 2 and 3 (50373 and 50399) gives different net income and total payable, and
    # the T1 lines 42100, 31000 and 22200 are "0" without the election.
    with_election = return_bo()
    without_election = return_bo(cpt20_earnings="0", cpt20_t4_earnings="0")

    t1_with_election = return_bo(form="ca-on/return")
    t1_without_election = return_bo(form="ca-on/return", cpt20_earnings="0", cpt20_t4_earnings="0")
    assert t1_with_election.get(NET_INCOME).value == D("68609.90")
    assert t1_with_election.get(TOTAL_PAYABLE).value == D("11868.30")
    assert t1_without_election.get(NET_INCOME).value == D("69335.00")
    assert t1_without_election.get(TOTAL_PAYABLE).value == D("11463.66")
    assert t1_with_election.get(CPP_OVERPAYMENT).value == D("0.00")
    assert t1_without_election.get(CPP_OVERPAYMENT).value == D("157.25")
    for kind in (
        CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    ):
        assert t1_without_election.get(kind).value == D("0"), kind.identifier
    # Part 4 lines 5 to 56 do not read line 4, so they are the same too; lines 62 and onward do:
    # line 4 of 12,500 against 0 changes line 62 (1,300.00 against 0), line 74 and the lines after
    # them, down to line 90 and line 91.
    assert part_4(with_election) == part_4(without_election)
    assert part_4_qpp(with_election) == part_4_qpp(without_election)
    assert part_4_earnings(with_election) != part_4_earnings(without_election)
    assert with_election.get(RC381_PART_4_LINE_62).value == D("1300.00")
    assert without_election.get(RC381_PART_4_LINE_62).value == D("0")
    # The final selection's six results differ with the election (lines 42100, 31000 and 22200 are
    # "0" without it), and so do the T1 lines that carry them.
    assert final_selection(with_election) != final_selection(without_election)
    assert with_election.get(
        RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS
    ).value == D("64.35")
    assert without_election.get(
        RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS
    ).value == D("0")


# Part 4, lines 31 to 56 (the QPP side before its gross-up, line 42 and the second additional
# contributions and the totals). Line 61 of Part 3 decides lines 31 to 40 ("If line 61 of Part 3 is:
# "0", do not complete lines 29 to 39. Complete line 28 and enter the amount on line 40 and continue
# at line 41. positive, complete lines 28 to 32 only, and continue at line 40. negative, complete
# line 28 and enter "0" at line 31 and continue at line 32."); line 68 of Part 3 decides lines 44
# to 46 and 49 to 51 ("If line 68 of Part 3 is positive, complete ... If not, enter "0" ...") and,
# with line 61, lines 54 and 55. The helper lines the form prints inside a line are computed
# whatever the signs are (as line 21's are), so the dicts below list them too: "31_difference" is
# "Line 29 minus line 30", "35Aa17" the amount from line 17 (when positive) of line 35A's first
# sentence, "35Ab20" the amount from line 20 in brackets (when line 20 is positive) of its second
# sentence and "35Ab0" that amount when line 35 is "0", before line 61 is read ("35Ab");
# "46_difference" and "51_difference" are lines 46 and 51's differences before line 68 is read.
PART_4_QPP_KINDS: dict[str, ArtifactKind[Decimal]] = {
    "31_difference": RC381_PART_4_LINE_31_DIFFERENCE,
    "31": RC381_PART_4_LINE_31,
    "32": RC381_PART_4_LINE_32,
    "33": RC381_PART_4_LINE_33,
    "34": RC381_PART_4_LINE_34,
    "35": RC381_PART_4_LINE_35,
    "35Aa17": RC381_PART_4_LINE_35AA_FROM_LINE_17,
    "35Aa": RC381_PART_4_LINE_35AA,
    "35Ab20": RC381_PART_4_LINE_35AB_FROM_LINE_20,
    "35Ab0": RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO,
    "35Ab": RC381_PART_4_LINE_35AB,
    "35A": RC381_PART_4_LINE_35A,
    "36": RC381_PART_4_LINE_36,
    "38": RC381_PART_4_LINE_38,
    "39": RC381_PART_4_LINE_39,
    "40": RC381_PART_4_LINE_40,
    "41": RC381_PART_4_LINE_41,
    "42": RC381_PART_4_LINE_42,
    "46_difference": RC381_PART_4_LINE_46_DIFFERENCE,
    "46": RC381_PART_4_LINE_46,
    "47": RC381_PART_4_LINE_47,
    "51_difference": RC381_PART_4_LINE_51_DIFFERENCE,
    "51": RC381_PART_4_LINE_51,
    "52": RC381_PART_4_LINE_52,
    "53": RC381_PART_4_LINE_53,
    "54": RC381_PART_4_LINE_54,
    "55": RC381_PART_4_LINE_55,
    "56": RC381_PART_4_LINE_56,
}


def part_4_qpp(worksheet: Worksheet) -> dict[str, Decimal]:
    """Part 4's lines 31 to 56 of `worksheet`, by line number (see `PART_4_QPP_KINDS`)."""
    return {line: worksheet.get(kind).value for line, kind in PART_4_QPP_KINDS.items()}


# Each case: box 26 outside and in Quebec (lines 1 and 2 of Part 3), box 16, box 17, box 16A and box
# 17A (lines 19, 39, 25 and 45), then lines 61 and 68 of Part 3, and Part 4's lines 31 to 56. The
# figures are proved by an independent Decimal model of the printed form (not by this engine).
# Part 4's line 17 = box 16 less 1,695.75 and line 20 = box 17 less 2,432.00 when lines 1 and 2 are
# 30,000 and 40,000 (Part 3's lines 24 and 44). With line 2 of 80,000 line 3 is 110,000, more than
# lines C and G, so Part 3's required second additional contributions are 108.00 (line 26) and
# 288.00 (line 46) and line 68 is -396.00 while boxes 16A and 17A are blank; Part 3's lines 24 and
# 44 are then 1,100.18 and 3,155.82.
PART_4_QPP_CASES = [
    # The ticket's example: line 61 of Part 3 is positive, so the form completes lines 28 to 32
    # only and continues at line 40.
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "157.25",
        "0.00",
        {
            "31_difference": "68.00",
            "31": "68.00",
            "32": "2432.00",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "89.25",
            "35Aa": "0",
            "35Ab20": "-68.00",
            "35Ab0": "-68.00",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "2432.00",
            "41": "38000.00",
            "42": "66500.00",
            "46_difference": "0.00",
            "46": "0",
            "47": "0",
            "51_difference": "0.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "0",
            "55": "0",
            "56": "0",
        },
        id="ticket_example_line_61_positive",
    ),
    # Line 61 positive with box 16 below line 24 of Part 3 (line 17 is negative).
    pytest.param(
        "30000",
        "40000",
        "1600",
        "2570",
        "0",
        "0",
        "42.25",
        "0.00",
        {
            "31_difference": "138.00",
            "31": "138.00",
            "32": "2432.00",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "0",
            "35Aa": "0",
            "35Ab20": "-138.00",
            "35Ab0": "-138.00",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "2432.00",
            "41": "38000.00",
            "42": "66500.00",
            "46_difference": "0.00",
            "46": "0",
            "47": "0",
            "51_difference": "0.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "0",
            "55": "0",
            "56": "0",
        },
        id="line_61_positive_line_17_negative",
    ),
    # Line 61 positive and line 68 negative: lines 54 and 55 are completed.
    pytest.param(
        "30000",
        "80000",
        "1785.00",
        "2500",
        "0",
        "0",
        "29.00",
        "-396.00",
        {
            "31_difference": "-655.82",
            "31": "-655.82",
            "32": "3155.82",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "684.82",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "3155.82",
            "41": "49309.69",
            "42": "67800.11",
            "46_difference": "-108.00",
            "46": "0",
            "47": "0",
            "51_difference": "-396.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "396.00",
            "55": "29.00",
            "56": "29.00",
        },
        id="line_61_positive_line_68_negative",
    ),
    # Line 61 positive and line 68 negative but less than line 61: line 55 is line 54.
    pytest.param(
        "30000",
        "80000",
        "1785.00",
        "2500",
        "380",
        "0",
        "29.00",
        "-16.00",
        {
            "31_difference": "-655.82",
            "31": "-655.82",
            "32": "3155.82",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "684.82",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "3155.82",
            "41": "49309.69",
            "42": "67800.11",
            "46_difference": "272.00",
            "46": "0",
            "47": "380",
            "51_difference": "-16.00",
            "51": "0",
            "52": "0",
            "53": "380",
            "54": "16.00",
            "55": "16.00",
            "56": "396.00",
        },
        id="line_61_positive_line_68_negative_small",
    ),
    # Line 61 positive and line 68 positive: lines 44 to 46 and 49 to 51 are completed.
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500",
        "50",
        "50",
        "157.25",
        "100.00",
        {
            "31_difference": "68.00",
            "31": "68.00",
            "32": "2432.00",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "89.25",
            "35Aa": "0",
            "35Ab20": "-68.00",
            "35Ab0": "-68.00",
            "35Ab": "0",
            "35A": "0",
            "36": "100.00",
            "38": "100.00",
            "39": "0",
            "40": "2432.00",
            "41": "38000.00",
            "42": "66500.00",
            "46_difference": "50.00",
            "46": "50.00",
            "47": "0.00",
            "51_difference": "50.00",
            "51": "50.00",
            "52": "0.00",
            "53": "0.00",
            "54": "0",
            "55": "0",
            "56": "0.00",
        },
        id="line_61_positive_line_68_positive",
    ),
    # Line 46 is negative (box 16A of 100.00 less line 26 of Part 3).
    pytest.param(
        "30000",
        "80000",
        "1785.00",
        "2500",
        "100",
        "300",
        "29.00",
        "4.00",
        {
            "31_difference": "-655.82",
            "31": "-655.82",
            "32": "3155.82",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "684.82",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "4.00",
            "38": "4.00",
            "39": "0",
            "40": "3155.82",
            "41": "49309.69",
            "42": "67800.11",
            "46_difference": "-8.00",
            "46": "-8.00",
            "47": "108.00",
            "51_difference": "12.00",
            "51": "12.00",
            "52": "288.00",
            "53": "396.00",
            "54": "0",
            "55": "0",
            "56": "396.00",
        },
        id="line_61_positive_line_46_negative",
    ),
    # Line 51 is negative (line 68 less a line 46 that is more).
    pytest.param(
        "30000",
        "80000",
        "1785.00",
        "3500",
        "500",
        "0",
        "1029.00",
        "104.00",
        {
            "31_difference": "344.18",
            "31": "344.18",
            "32": "3155.82",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "684.82",
            "35Aa": "0",
            "35Ab20": "-344.18",
            "35Ab0": "-344.18",
            "35Ab": "0",
            "35A": "0",
            "36": "104.00",
            "38": "104.00",
            "39": "0",
            "40": "3155.82",
            "41": "49309.69",
            "42": "67800.11",
            "46_difference": "392.00",
            "46": "392.00",
            "47": "108.00",
            "51_difference": "-288.00",
            "51": "-288.00",
            "52": "288.00",
            "53": "396.00",
            "54": "0",
            "55": "0",
            "56": "396.00",
        },
        id="line_61_positive_line_51_negative",
    ),
    # Line 68 is exactly 0, not positive: lines 44 to 46 and 49 to 51 are not completed.
    pytest.param(
        "30000",
        "80000",
        "1785.00",
        "2500",
        "396",
        "0",
        "29.00",
        "0.00",
        {
            "31_difference": "-655.82",
            "31": "-655.82",
            "32": "3155.82",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "684.82",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "3155.82",
            "41": "49309.69",
            "42": "67800.11",
            "46_difference": "288.00",
            "46": "0",
            "47": "396",
            "51_difference": "0.00",
            "51": "0",
            "52": "0",
            "53": "396",
            "54": "0",
            "55": "0",
            "56": "396",
        },
        id="line_68_zero_with_a_line_46_difference",
    ),
    # Line 61 is 0: do not complete lines 29 to 39, complete line 28 and enter it on line 40.
    pytest.param(
        "30000",
        "40000",
        "1695.75",
        "2432",
        "0",
        "0",
        "0.00",
        "0.00",
        {
            "31_difference": "0.00",
            "31": "0",
            "32": "2432",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "0",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "2432",
            "41": "38000.00",
            "42": "66500.00",
            "46_difference": "0.00",
            "46": "0",
            "47": "0",
            "51_difference": "0.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "0",
            "55": "0",
            "56": "0",
        },
        id="line_61_zero",
    ),
    # Line 61 is 0 with line 17 positive and line 20 negative: line 31 is not entered.
    pytest.param(
        "29500",
        "40000",
        "1750",
        "2347.93",
        "0",
        "0",
        "0.00",
        "0.00",
        {
            "31_difference": "-83.15",
            "31": "0",
            "32": "2347.93",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "83.15",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "2347.93",
            "41": "36686.41",
            "42": "66098.17",
            "46_difference": "0.00",
            "46": "0",
            "47": "0",
            "51_difference": "0.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "0",
            "55": "0",
            "56": "0",
        },
        id="line_61_zero_line_17_positive_line_20_negative",
    ),
    # Line 61 is 0 and line 40 x 15.625 is not a whole number of cents.
    pytest.param(
        "30000",
        "40000",
        "1557.77",
        "2569.98",
        "0",
        "0",
        "0.00",
        "0.00",
        {
            "31_difference": "137.98",
            "31": "0",
            "32": "2569.98",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "0",
            "35Aa": "0",
            "35Ab20": "-137.98",
            "35Ab0": "-137.98",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "2569.98",
            "41": "40155.94",
            "42": "66336.94",
            "46_difference": "0.00",
            "46": "0",
            "47": "0",
            "51_difference": "0.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "0",
            "55": "0",
            "56": "0",
        },
        id="line_61_zero_line_41_rounds_up",
    ),
    # Line 61 is 0 and line 68 positive.
    pytest.param(
        "30000",
        "40000",
        "1695.75",
        "2432",
        "50",
        "50",
        "0.00",
        "100.00",
        {
            "31_difference": "0.00",
            "31": "0",
            "32": "2432",
            "33": "0",
            "34": "0",
            "35": "0",
            "35Aa17": "0",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "100.00",
            "38": "100.00",
            "39": "0",
            "40": "2432",
            "41": "38000.00",
            "42": "66500.00",
            "46_difference": "50.00",
            "46": "50.00",
            "47": "0.00",
            "51_difference": "50.00",
            "51": "50.00",
            "52": "0.00",
            "53": "0.00",
            "54": "0",
            "55": "0",
            "56": "0.00",
        },
        id="line_61_zero_line_68_positive",
    ),
    # Line 61 negative with lines 17 and 20 both negative: line 35A is 0.
    pytest.param(
        "30000",
        "40000",
        "1000",
        "2000",
        "0",
        "0",
        "-1127.75",
        "0.00",
        {
            "31_difference": "-432.00",
            "31": "0",
            "32": "2000",
            "33": "1127.75",
            "34": "695.75",
            "35": "432.00",
            "35Aa17": "0",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0.00",
            "39": "0.00",
            "40": "2000.00",
            "41": "31250.00",
            "42": "48056.72",
            "46_difference": "0.00",
            "46": "0",
            "47": "0",
            "51_difference": "0.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "0",
            "55": "0",
            "56": "0",
        },
        id="line_61_negative_lines_17_and_20_negative",
    ),
    # Line 61 negative with line 17 exactly 0: line 17A is 0, so line 34 is 0.
    pytest.param(
        "30000",
        "40000",
        "1695.75",
        "1000",
        "0",
        "0",
        "-1432.00",
        "0.00",
        {
            "31_difference": "-1432.00",
            "31": "0",
            "32": "1000",
            "33": "1432.00",
            "34": "0",
            "35": "1432.00",
            "35Aa17": "0",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "1000",
            "41": "15625.00",
            "42": "44125.00",
            "46_difference": "0.00",
            "46": "0",
            "47": "0",
            "51_difference": "0.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "0",
            "55": "0",
            "56": "0",
        },
        id="line_61_negative_line_17_zero",
    ),
    # Line 61 negative, 17A at least line 33 (line 35 is 0) and line 20 positive: line 35A takes
    # line 20 in brackets.
    pytest.param(
        "30000",
        "80000",
        "0",
        "3500",
        "0",
        "0",
        "-756.00",
        "-396.00",
        {
            "31_difference": "344.18",
            "31": "0",
            "32": "3500",
            "33": "756.00",
            "34": "756.00",
            "35": "0.00",
            "35Aa17": "0",
            "35Aa": "0",
            "35Ab20": "-344.18",
            "35Ab0": "-344.18",
            "35Ab": "-344.18",
            "35A": "-344.18",
            "36": "0",
            "38": "396.00",
            "39": "0.00",
            "40": "3155.82",
            "41": "49309.69",
            "42": "48438.77",
            "46_difference": "-108.00",
            "46": "0",
            "47": "0",
            "51_difference": "-396.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "396.00",
            "55": "0",
            "56": "0",
        },
        id="line_61_negative_line_35_zero_line_20_positive",
    ),
    # Line 61 negative, line 35 and line 17 both positive: line 35A takes line 17.
    pytest.param(
        "30000",
        "80000",
        "1785.00",
        "0",
        "0",
        "0",
        "-2471.00",
        "-396.00",
        {
            "31_difference": "-3155.82",
            "31": "0",
            "32": "0",
            "33": "2471.00",
            "34": "0",
            "35": "2471.00",
            "35Aa17": "684.82",
            "35Aa": "684.82",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "684.82",
            "36": "0",
            "38": "0",
            "39": "0",
            "40": "684.82",
            "41": "10700.31",
            "42": "29190.73",
            "46_difference": "-108.00",
            "46": "0",
            "47": "0",
            "51_difference": "-396.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "396.00",
            "55": "0",
            "56": "0",
        },
        id="line_61_negative_line_35_positive_line_17_positive",
    ),
    # Line 61 negative, line 68 positive: line 36 is line 68, line 39 is the lesser, line 35.
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2000",
        "500",
        "0",
        "-342.75",
        "500.00",
        {
            "31_difference": "-432.00",
            "31": "0",
            "32": "2000",
            "33": "342.75",
            "34": "0",
            "35": "342.75",
            "35Aa17": "89.25",
            "35Aa": "89.25",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "89.25",
            "36": "500.00",
            "38": "500.00",
            "39": "342.75",
            "40": "2432.00",
            "41": "38000.00",
            "42": "66500.00",
            "46_difference": "500.00",
            "46": "500.00",
            "47": "0.00",
            "51_difference": "0.00",
            "51": "0.00",
            "52": "0.00",
            "53": "0.00",
            "54": "0",
            "55": "0",
            "56": "0.00",
        },
        id="line_61_negative_line_68_positive_line_39_is_line_35",
    ),
    # As above with box 16A of 100.00: line 39 is the lesser, line 38.
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2000",
        "100",
        "0",
        "-342.75",
        "100.00",
        {
            "31_difference": "-432.00",
            "31": "0",
            "32": "2000",
            "33": "342.75",
            "34": "0",
            "35": "342.75",
            "35Aa17": "89.25",
            "35Aa": "89.25",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "89.25",
            "36": "100.00",
            "38": "100.00",
            "39": "100.00",
            "40": "2189.25",
            "41": "34207.03",
            "42": "62707.03",
            "46_difference": "100.00",
            "46": "100.00",
            "47": "0.00",
            "51_difference": "0.00",
            "51": "0.00",
            "52": "0.00",
            "53": "0.00",
            "54": "0",
            "55": "0",
            "56": "0.00",
        },
        id="line_61_negative_line_68_positive_line_39_is_line_38",
    ),
    # Line 61 negative, line 68 negative and line 69 negative: line 24 is negative, so line 38 is
    # positive.
    pytest.param(
        "30000",
        "80000",
        "0",
        "0",
        "0",
        "0",
        "-4256.00",
        "-396.00",
        {
            "31_difference": "-3155.82",
            "31": "0",
            "32": "0",
            "33": "4256.00",
            "34": "1100.18",
            "35": "3155.82",
            "35Aa17": "0",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "0",
            "38": "102.37",
            "39": "102.37",
            "40": "102.37",
            "41": "1599.53",
            "42": "-120.97",
            "46_difference": "-108.00",
            "46": "0",
            "47": "0",
            "51_difference": "-396.00",
            "51": "0",
            "52": "0",
            "53": "0",
            "54": "396.00",
            "55": "0",
            "56": "0",
        },
        id="line_61_negative_line_68_negative_line_24_negative",
    ),
    # Line 61 negative with the second additional contributions of both plans.
    pytest.param(
        "60000",
        "80000",
        "1695.75",
        "2432",
        "500",
        "0",
        "-80.69",
        "104.00",
        {
            "31_difference": "-47.55",
            "31": "0",
            "32": "2432",
            "33": "80.69",
            "34": "33.14",
            "35": "47.55",
            "35Aa17": "0",
            "35Aa": "0",
            "35Ab20": "0",
            "35Ab0": "0",
            "35Ab": "0",
            "35A": "0",
            "36": "104.00",
            "38": "70.86",
            "39": "47.55",
            "40": "2479.55",
            "41": "38742.97",
            "42": "67799.94",
            "46_difference": "330.29",
            "46": "330.29",
            "47": "169.71",
            "51_difference": "-226.29",
            "51": "-226.29",
            "52": "226.29",
            "53": "396.00",
            "54": "0",
            "55": "0",
            "56": "396.00",
        },
        id="line_61_negative_line_68_positive_large_totals",
    ),
]


@pytest.mark.parametrize(
    (
        "line_1",
        "line_2",
        "box_16",
        "box_17",
        "box_16a",
        "box_17a",
        "line_61",
        "line_68",
        "expected",
    ),
    PART_4_QPP_CASES,
)
def test_return_bo_part_4_lines_31_to_56(
    line_1: str,
    line_2: str,
    box_16: str,
    box_17: str,
    box_16a: str,
    box_17a: str,
    line_61: str,
    line_68: str,
    expected: dict[str, str],
) -> None:
    worksheet = return_bo(line_1, line_2, box_16, box_17, line_25=box_16a, line_45=box_17a)

    assert worksheet.get(RC381_PART_3_LINE_61).value == D(line_61)
    assert worksheet.get(RC381_PART_3_LINE_68).value == D(line_68)
    assert part_4_qpp(worksheet) == {line: D(value) for line, value in expected.items()}


# Part 4, lines 57 to 91 (the earnings subject to contributions, the contributions through
# self-employment income and other earnings, the contributions payable and the overpayment). Lines
# 57 and 58 are lines C and F of Part 2, line 60 is line 42, lines 63 and 64 are line 58 and line 3
# of Part 3, lines 66, 71, 78 and 79 are lines 4 and 65, line 67 is line 59, lines 72 and 73 are
# lines 11 and 31 of Part 3, line 75 is line D and line 81 is line 70. "If line 3 of Part 3 is less
# than line 58, complete lines 63 to 69. If not, enter "0" on line 69": line 65 "Line 63 minus line
# 64 (if negative, enter "0" on lines 65 and 69 ...)" is "0" exactly when line 3 is not less than
# line 58, and so is line 69, which the tests below pin; line 68 is still computed when the form
# does not complete it. "If line 74 is more than line 57, complete lines 75 to 83. If not, enter
# "0" on line 83": line 83 is the lesser of lines 77 and 82 only then, and "0" otherwise. The
# helpers the form prints inside a line are computed whatever the signs are, so the dict below
# lists them: "83_lesser" is "Enter whichever is less: amount from line 77 or line 82.", before
# the gate, "89_from_line_69" the "Amount from line 69 of Part 3 (if positive)" and
# "91_from_line_90" the "amount from line 90 entered as a positive amount". "42100" is line 90
# when it is positive ("enter the amount on line 42100 of your return"), else "0".
PART_4_EARNINGS_KINDS: dict[str, ArtifactKind[Decimal]] = {
    "59": RC381_PART_4_LINE_59,
    "61": RC381_PART_4_LINE_61,
    "62": RC381_PART_4_LINE_62,
    "65": RC381_PART_4_LINE_65,
    "68": RC381_PART_4_LINE_68,
    "69": RC381_PART_4_LINE_69,
    "70": RC381_PART_4_LINE_70,
    "74": RC381_PART_4_LINE_74,
    "76": RC381_PART_4_LINE_76,
    "77": RC381_PART_4_LINE_77,
    "80": RC381_PART_4_LINE_80,
    "82": RC381_PART_4_LINE_82,
    "83_lesser": RC381_PART_4_LINE_83_LESSER,
    "83": RC381_PART_4_LINE_83,
    "84": RC381_PART_4_LINE_84,
    "85": RC381_PART_4_LINE_85,
    "86": RC381_PART_4_LINE_86,
    "87": RC381_PART_4_LINE_87,
    "88": RC381_PART_4_LINE_88,
    "89_from_line_69": RC381_PART_4_LINE_89_FROM_LINE_69,
    "89": RC381_PART_4_LINE_89,
    "90": RC381_PART_4_LINE_90,
    "42100": RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS,
    "91_from_line_90": RC381_PART_4_LINE_91_FROM_LINE_90,
    "91": RC381_PART_4_LINE_91,
}


def part_4_earnings(worksheet: Worksheet) -> dict[str, Decimal]:
    """Part 4's lines 59 to 91 of `worksheet`, by line number (see `PART_4_EARNINGS_KINDS`)."""
    return {line: worksheet.get(kind).value for line, kind in PART_4_EARNINGS_KINDS.items()}


def test_return_bo_part_4_lines_59_to_91_match_the_tickets_example() -> None:
    # Return BO: line 4 = 12,500 (the election), line 42 = 66,500.00 (line 27 plus line 41), line 3
    # of Part 3 = 70,000.00 and line 69 of Part 3 = 157.25. Line 59 = line C 71,300.00 less line F
    # 3,500.00 = 67,800.00; line 61 = 67,800.00 less 66,500.00 = 1,300.00; line 62 = the lesser of
    # 12,500 and 1,300.00 = 1,300.00. Line 3 (70,000.00) is not less than line 58 (3,500.00), so
    # line 65 (3,500.00 less 70,000.00, entered as "0") and line 69 are "0" (line 68 = 12,500 less
    # 67,800.00 is "0" too); line 70 = 1,300.00. Line 74 = 12,500 + 30,000.00 + 40,000.00 =
    # 82,500.00 is more than line 57 (71,300.00), so lines 75 to 83 are completed: line 76 = 0.00 /
    # 4% = 0.00 (line 56 is 0), line 77 = 9,900.00 less 0.00 = 9,900.00, line 80 = 12,500 less 0 =
    # 12,500, line 82 = 12,500 less 1,300.00 = 11,200.00 and line 83 = the lesser of 9,900.00 and
    # 11,200.00 = 9,900.00. Line 84 = 1,300.00 x 9.9% = 128.70, line 85 = 1,300.00 x 2% = 26.00,
    # line 86 = 9,900.00 x 8% = 792.00, line 87 = 818.00 and line 88 = 946.70. Line 89 = 157.25 x
    # 2 = 314.50, line 90 = 946.70 less 314.50 = 632.20, positive: line 42100 = 632.20 and line 91
    # is "0".
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_4_LINE_4).value == D("12500")
    assert worksheet.get(RC381_PART_4_LINE_42).value == D("66500.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("157.25")
    assert part_4_earnings(worksheet) == {
        "59": D("67800.00"),
        "61": D("1300.00"),
        "62": D("1300.00"),
        "65": D("0"),
        "68": D("0"),
        "69": D("0"),
        "70": D("1300.00"),
        "74": D("82500"),
        "76": D("0.00"),
        "77": D("9900.00"),
        "80": D("12500"),
        "82": D("11200.00"),
        "83_lesser": D("9900.00"),
        "83": D("9900.00"),
        "84": D("128.70"),
        "85": D("26.00"),
        "86": D("792.00"),
        "87": D("818.00"),
        "88": D("946.70"),
        "89_from_line_69": D("157.25"),
        "89": D("314.50"),
        "90": D("632.20"),
        "42100": D("632.20"),
        "91_from_line_90": D("0"),
        "91": D("0.00"),
    }


def test_return_bo_part_4_without_the_election_line_90_is_negative_and_line_91_is_half_of_it() -> (
    None
):
    # No election and no self-employment income: line 4 = 0, so lines 62, 70, 80, 82 and 83 are 0
    # and lines 84 to 88 are 0.00. Line 69 of Part 3 (157.25) is positive: line 89 = 157.25 x 2 =
    # 314.50 and line 90 = 0.00 less 314.50 = -314.50, in brackets: line 42100 is "0" and
    # line 91 = 314.50 x 50% = 157.25.
    worksheet = return_bo(cpt20_earnings="0", cpt20_t4_earnings="0")

    assert part_4_earnings(worksheet) == {
        "59": D("67800.00"),
        "61": D("1300.00"),
        "62": D("0"),
        "65": D("0"),
        "68": D("0"),
        "69": D("0"),
        "70": D("0"),
        "74": D("70000"),
        "76": D("0.00"),
        "77": D("9900.00"),
        "80": D("0"),
        "82": D("0"),
        "83_lesser": D("0"),
        "83": D("0"),
        "84": D("0.00"),
        "85": D("0.00"),
        "86": D("0.00"),
        "87": D("0.00"),
        "88": D("0.00"),
        "89_from_line_69": D("157.25"),
        "89": D("314.50"),
        "90": D("-314.50"),
        "42100": D("0"),
        "91_from_line_90": D("314.50"),
        "91": D("157.25"),
    }


def test_return_bo_part_4_self_employment_income_and_no_t4_slips_reaches_the_printed_maximums() -> (
    None
):
    # Net partnership income of 80,000 and no T4 slip: line 3 of Part 3 is 0, less than line 58, so
    # lines 63 to 69 are completed: line 65 = 3,500.00 less 0 = 3,500.00 and line 68 = 80,000 less
    # 67,800.00 = 12,200.00, so line 69 = 3,500.00 less 12,200.00, entered as "0". Line 61 =
    # 67,800.00 (line 42 is 0) and line 62 = 67,800.00, so line 70 is the band of 67,800.00: line
    # 84 = 67,800.00 x 9.9% = 6,712.20 and line 85 = 67,800.00 x 2% = 1,356.00 (the printed
    # maximums). Line 74 = 80,000 is more than line 57: line 82 = (80,000 less 3,500.00) less
    # 67,800.00 = 8,700.00 is less than line 77 (9,900.00), so line 83 = 8,700.00 and line 86 =
    # 8,700.00 x 8% = 696.00. Line 69 of Part 3 is 0: line 90 = 8,764.20 = line 42100.
    worksheet = return_bo(
        line_1="0",
        line_2="0",
        line_19="0",
        line_39="0",
        cpt20_earnings="0",
        cpt20_t4_earnings="0",
        net_partnership_income="80000",
    )

    assert worksheet.get(RC381_PART_3_LINE_3).value == D("0")
    assert part_4_earnings(worksheet) == {
        "59": D("67800.00"),
        "61": D("67800.00"),
        "62": D("67800.00"),
        "65": D("3500.00"),
        "68": D("12200.00"),
        "69": D("0"),
        "70": D("67800.00"),
        "74": D("80000"),
        "76": D("0.00"),
        "77": D("9900.00"),
        "80": D("76500.00"),
        "82": D("8700.00"),
        "83_lesser": D("8700.00"),
        "83": D("8700.00"),
        "84": D("6712.20"),
        "85": D("1356.00"),
        "86": D("696.00"),
        "87": D("2052.00"),
        "88": D("8764.20"),
        "89_from_line_69": D("0.00"),
        "89": D("0.00"),
        "90": D("8764.20"),
        "42100": D("8764.20"),
        "91_from_line_90": D("0"),
        "91": D("0.00"),
    }


def test_return_bo_part_4_line_69_is_zero_when_line_3_is_exactly_line_58_and_not_when_less() -> (
    None
):
    # Line 3 of Part 3 = 2,000 + 1,500 = 3,500.00 is not less than line 58 (3,500.00): line 65 is
    # "0", so is line 69, and with net partnership income of 100 line 70 = line 62 = 100.00. One
    # cent less (line 2 of 1,499.99): line 65 = 0.01, line 68 = 0 (100 is not more than
    # 67,800.00), line 69 = 0.01 and line 70 = 100.00 less 0.01 = 99.99.
    at_line_58 = return_bo(
        "2000",
        "1500",
        "0",
        "0",
        net_partnership_income="100",
        cpt20_earnings="0",
        cpt20_t4_earnings="0",
    )
    below_line_58 = return_bo(
        "2000",
        "1499.99",
        "0",
        "0",
        net_partnership_income="100",
        cpt20_earnings="0",
        cpt20_t4_earnings="0",
    )

    assert at_line_58.get(RC381_PART_3_LINE_3).value == D("3500.00")
    assert at_line_58.get(RC381_PART_4_LINE_65).value == D("0")
    assert at_line_58.get(RC381_PART_4_LINE_69).value == D("0")
    assert at_line_58.get(RC381_PART_4_LINE_70).value == D("100")
    assert below_line_58.get(RC381_PART_3_LINE_3).value == D("3499.99")
    assert below_line_58.get(RC381_PART_4_LINE_65).value == D("0.01")
    assert below_line_58.get(RC381_PART_4_LINE_68).value == D("0")
    assert below_line_58.get(RC381_PART_4_LINE_69).value == D("0.01")
    assert below_line_58.get(RC381_PART_4_LINE_70).value == D("99.99")
    # Lines 84 and 85 are 9.9% and 2% of line 70: 99.99 x 9.9% = 9.89901 (9.90) and 99.99 x 2% =
    # 1.9998 (2.00).
    assert below_line_58.get(RC381_PART_4_LINE_84).value == D("9.90")
    assert below_line_58.get(RC381_PART_4_LINE_85).value == D("2.00")


def test_return_bo_part_4_line_83_needs_line_74_to_be_more_than_line_57() -> None:
    # Lines 71 to 73 are line 4 (12,500) and lines 11 and 31 of Part 3 (30,000.00 and the whole of
    # line 2): with line 2 of 28,800 line 74 = 71,300.00, which is line 57 (71,300.00), not more
    # than it: line 83 is "0" although lines 77 (9,900.00) and 82 (12,500 less line 61,
    # 12,499.94, is 0.06) give 0.06; with line 2 of 28,800.01 line 74 = 71,300.01 is more, and line
    # 83 = 0.06.
    equal = return_bo(line_2="28800")
    one_cent_more = return_bo(line_2="28800.01")

    assert equal.get(RC381_PART_4_LINE_74).value == D("71300.00")
    assert equal.get(RC381_PART_4_LINE_83_LESSER).value == D("0.06")
    assert equal.get(RC381_PART_4_LINE_83).value == D("0")
    assert equal.get(RC381_PART_4_LINE_86).value == D("0")
    assert one_cent_more.get(RC381_PART_4_LINE_74).value == D("71300.01")
    assert one_cent_more.get(RC381_PART_4_LINE_83).value == D("0.06")
    assert one_cent_more.get(RC381_PART_4_LINE_86).value == D("0.00")


def test_return_bo_part_4_a_negative_line_70_contributes_nothing_and_is_not_floored() -> None:
    # The form prints no floor on line 70 "Line 62 minus line 69": with line 3 of Part 3 of 2,500.00
    # (1,000 + 1,500) line 65 = line 69 = 1,000.00 and net partnership income of 300 gives line 62 =
    # 300, so line 70 = -700.00. Lines 84 and 85 take earnings below zero as nothing (0.00), line
    # 80 = 300 less 1,000.00 = -700.00 and line 82 = -700.00 less -700.00 = 0.00.
    worksheet = return_bo(
        "1000",
        "1500",
        "0",
        "0",
        net_partnership_income="300",
        cpt20_earnings="0",
        cpt20_t4_earnings="0",
    )

    assert worksheet.get(RC381_PART_4_LINE_70).value == D("-700.00")
    assert worksheet.get(RC381_PART_4_LINE_80).value == D("-700.00")
    assert worksheet.get(RC381_PART_4_LINE_82).value == D("0.00")
    assert worksheet.get(RC381_PART_4_LINE_84).value == D("0")
    assert worksheet.get(RC381_PART_4_LINE_85).value == D("0")
    assert worksheet.get(RC381_PART_4_LINE_90).value == D("0")


def test_return_bo_part_4_line_89_is_twice_line_69_of_part_3_only_when_that_is_positive() -> None:
    # Line 69 of Part 3 = 157.25 (positive): line 89 = 157.25 x 2 = 314.50. A negative line 69
    # (line 2 of 80,000 with no T4 contributions: line 61 = -4,256.00 and line 68 = -396.00, line
    # 69 = -4,652.00) and a line 69 of "0" give "0" ("if positive").
    positive = return_bo()
    negative = return_bo(line_2="80000", line_19="0", line_39="0")
    zero = return_bo(line_19="1695.75", line_39="2432", cpt20_earnings="0", cpt20_t4_earnings="0")

    assert positive.get(RC381_PART_4_LINE_89_FROM_LINE_69).value == D("157.25")
    assert positive.get(RC381_PART_4_LINE_89).value == D("314.50")
    assert negative.get(RC381_PART_3_LINE_69).value == D("-4652.00")
    assert negative.get(RC381_PART_4_LINE_89_FROM_LINE_69).value == D("0")
    assert negative.get(RC381_PART_4_LINE_89).value == D("0")
    assert zero.get(RC381_PART_3_LINE_69).value == D("0")
    assert zero.get(RC381_PART_4_LINE_89).value == D("0")


def test_return_bo_part_4_line_90_positive_goes_to_line_42100_and_negative_to_line_91() -> None:
    # Positive (the ticket's example): line 90 = 632.20, line 42100 = 632.20, line 91 = 0. Negative
    # (no election): line 90 = -314.50, line 42100 = 0 and line 91 = 314.50 x 50% = 157.25 ("amount
    # from line 90 entered as a positive amount"). Zero (no election, line 69 of Part 3 of 0): both
    # are 0. A tie: line 90 of -314.37 gives 157.185, up to 157.19 (half even gives 157.18).
    positive = return_bo()
    negative = return_bo(cpt20_earnings="0", cpt20_t4_earnings="0")
    zero = return_bo(line_19="1695.75", line_39="2432", cpt20_earnings="0", cpt20_t4_earnings="0")
    tie = return_bo(cpt20_earnings="0", cpt20_t4_earnings="0", net_partnership_income="1.07")

    assert positive.get(RC381_PART_4_LINE_90).value == D("632.20")
    assert positive.get(RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS).value == D("632.20")
    assert positive.get(RC381_PART_4_LINE_91_FROM_LINE_90).value == D("0")
    assert positive.get(RC381_PART_4_LINE_91).value == D("0")
    assert negative.get(RC381_PART_4_LINE_90).value == D("-314.50")
    assert negative.get(RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS).value == D("0")
    assert negative.get(RC381_PART_4_LINE_91_FROM_LINE_90).value == D("314.50")
    assert negative.get(RC381_PART_4_LINE_91).value == D("157.25")
    assert zero.get(RC381_PART_4_LINE_90).value == D("0")
    assert zero.get(RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS).value == D("0")
    assert zero.get(RC381_PART_4_LINE_91).value == D("0")
    assert tie.get(RC381_PART_4_LINE_90).value == D("-314.37")
    assert tie.get(RC381_PART_4_LINE_91).value == D("157.19")


def test_return_bo_part_4_with_6_months_lines_57_and_58_are_the_6_month_row() -> None:
    # Lines C and F for 6 months on line A are 35,650.00 and 1,750.00: line 59 = 33,900.00 (the
    # most that line 59 prints for the year is 67,800). Line D is 4,950.00, which line 77 starts
    # from (line 75): line 56 is 198.00, so line 76 = 198.00 / 4% = 4,950.00 and line 77 = 0.00.
    worksheet = return_bo(cpp_months=6, qpp_months=6)

    assert worksheet.get(RC381_PART_2_LINE_B).value == 6
    assert worksheet.get(RC381_PART_4_LINE_56).value == D("198.00")
    assert worksheet.get(RC381_PART_4_LINE_59).value == D("33900.00")
    assert worksheet.get(RC381_PART_4_LINE_76).value == D("4950.00")
    assert worksheet.get(RC381_PART_4_LINE_77).value == D("0.00")


# Each case: box 26 outside and in Quebec (lines 1 and 2 of Part 3), box 16, box 17, box 16A and
# box 17A (lines 19, 39, 25 and 45), net partnership income (T1 line 12200, Part 4 line 1) and the
# election (lines 2 and 3, 50373 and 50399), the months, then the lines of the earlier parts it
# rests on (lines 61 and 69 of Part 3, lines 4, 42 and 56 of Part 4) and Part 4's lines 59 to 91.
# The figures are proved by an independent Decimal model of the printed form (not by this engine).
PART_4_EARNINGS_CASES = [
    # The example of Return BO: employment only on the T4 slips, the CPT20 election of 10,000 and
    # 2,500 and no other self-employment income, so line 4 is 12,500; line 69 of Part 3 is
    # positive.
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "0",
        "10000",
        "2500",
        12,
        12,
        {
            "part_3_line_61": "157.25",
            "part_3_line_69": "157.25",
            "line_4": "12500",
            "line_42": "66500.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "1300.00",
            "62": "1300.00",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "1300.00",
            "74": "82500",
            "76": "0.00",
            "77": "9900.00",
            "80": "12500",
            "82": "11200.00",
            "83_lesser": "9900.00",
            "83": "9900.00",
            "84": "128.70",
            "85": "26.00",
            "86": "792.00",
            "87": "818.00",
            "88": "946.70",
            "89_from_line_69": "157.25",
            "89": "314.50",
            "90": "632.20",
            "42100": "632.20",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="ticket_example",
    ),
    # Line 4 is 0: lines 70 and 83 are 0, and line 89 (twice line 69 of Part 3) makes line 90
    # negative, so line 42100 is 0 and line 91 is half of it.
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "0",
        "0",
        "0",
        12,
        12,
        {
            "part_3_line_61": "157.25",
            "part_3_line_69": "157.25",
            "line_4": "0",
            "line_42": "66500.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "1300.00",
            "62": "0",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "0",
            "74": "70000",
            "76": "0.00",
            "77": "9900.00",
            "80": "0",
            "82": "0",
            "83_lesser": "0",
            "83": "0",
            "84": "0.00",
            "85": "0.00",
            "86": "0.00",
            "87": "0.00",
            "88": "0.00",
            "89_from_line_69": "157.25",
            "89": "314.50",
            "90": "-314.50",
            "42100": "0",
            "91_from_line_90": "314.50",
            "91": "157.25",
        },
        id="no_election_and_no_self_employment_income",
    ),
    # Line 70 is 15.00: 15.00 x 9.9% = 1.485 is a tie and rounds half up to 1.49 (half even gives
    # 1.48).
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "15",
        "0",
        "0",
        12,
        12,
        {
            "part_3_line_61": "157.25",
            "part_3_line_69": "157.25",
            "line_4": "15",
            "line_42": "66500.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "1300.00",
            "62": "15",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "15",
            "74": "70015",
            "76": "0.00",
            "77": "9900.00",
            "80": "15",
            "82": "0",
            "83_lesser": "0",
            "83": "0",
            "84": "1.49",
            "85": "0.30",
            "86": "0.00",
            "87": "0.30",
            "88": "1.79",
            "89_from_line_69": "157.25",
            "89": "314.50",
            "90": "-312.71",
            "42100": "0",
            "91_from_line_90": "312.71",
            "91": "156.36",
        },
        id="net_self_employment_income_of_15",
    ),
    # Line 88 is 0.13 and line 90 is -314.37, so line 91 = 314.37 x 50% = 157.185, up to 157.19
    # (half even gives 157.18).
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "1.07",
        "0",
        "0",
        12,
        12,
        {
            "part_3_line_61": "157.25",
            "part_3_line_69": "157.25",
            "line_4": "1.07",
            "line_42": "66500.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "1300.00",
            "62": "1.07",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "1.07",
            "74": "70001.07",
            "76": "0.00",
            "77": "9900.00",
            "80": "1.07",
            "82": "0.00",
            "83_lesser": "0.00",
            "83": "0",
            "84": "0.11",
            "85": "0.02",
            "86": "0.00",
            "87": "0.02",
            "88": "0.13",
            "89_from_line_69": "157.25",
            "89": "314.50",
            "90": "-314.37",
            "42100": "0",
            "91_from_line_90": "314.37",
            "91": "157.19",
        },
        id="line_91_rounds_half_up",
    ),
    # No T4 slips: line 3 of Part 3 is 0, less than line 58, so line 65 is 3,500.00; line 68
    # (80,000.00 less 67,800.00) takes it all, line 69 is 0 and line 70 is the line 59 maximum of
    # 67,800.00, where lines 84 and 85 stop at their printed maximums.
    pytest.param(
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "80000",
        "0",
        "0",
        12,
        12,
        {
            "part_3_line_61": "0.00",
            "part_3_line_69": "0.00",
            "line_4": "80000",
            "line_42": "0.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "67800.00",
            "62": "67800.00",
            "65": "3500.00",
            "68": "12200.00",
            "69": "0",
            "70": "67800.00",
            "74": "80000",
            "76": "0.00",
            "77": "9900.00",
            "80": "76500.00",
            "82": "8700.00",
            "83_lesser": "8700.00",
            "83": "8700.00",
            "84": "6712.20",
            "85": "1356.00",
            "86": "696.00",
            "87": "2052.00",
            "88": "8764.20",
            "89_from_line_69": "0.00",
            "89": "0.00",
            "90": "8764.20",
            "42100": "8764.20",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="self_employment_income_and_no_t4_slips",
    ),
    # Line 3 of Part 3 (2,500.00) is less than line 58 (3,500.00): line 65 = 1,000.00, line 68 =
    # 0, so line 69 = 1,000.00 and line 70 = 2,500.00 less 1,000.00 = 1,500.00.
    pytest.param(
        "1000",
        "1500",
        "0",
        "0",
        "0",
        "0",
        "2500",
        "0",
        "0",
        12,
        12,
        {
            "part_3_line_61": "0.00",
            "part_3_line_69": "0.00",
            "line_4": "2500",
            "line_42": "0.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "67800.00",
            "62": "2500",
            "65": "1000.00",
            "68": "0",
            "69": "1000.00",
            "70": "1500.00",
            "74": "5000",
            "76": "0.00",
            "77": "9900.00",
            "80": "1500.00",
            "82": "0.00",
            "83_lesser": "0.00",
            "83": "0",
            "84": "148.50",
            "85": "30.00",
            "86": "0.00",
            "87": "30.00",
            "88": "178.50",
            "89_from_line_69": "0.00",
            "89": "0.00",
            "90": "178.50",
            "42100": "178.50",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="earnings_below_the_basic_exemption",
    ),
    # As above with net self-employment income of 300: line 70 = 300.00 less 1,000.00 = -700.00
    # (the form prints no floor), which the tiers of lines 84 and 85 take as no earnings, and line
    # 82 = -700.00 less -700.00 = 0.
    pytest.param(
        "1000",
        "1500",
        "0",
        "0",
        "0",
        "0",
        "300",
        "0",
        "0",
        12,
        12,
        {
            "part_3_line_61": "0.00",
            "part_3_line_69": "0.00",
            "line_4": "300",
            "line_42": "0.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "67800.00",
            "62": "300",
            "65": "1000.00",
            "68": "0",
            "69": "1000.00",
            "70": "-700.00",
            "74": "2800",
            "76": "0.00",
            "77": "9900.00",
            "80": "-700.00",
            "82": "0.00",
            "83_lesser": "0.00",
            "83": "0",
            "84": "0.00",
            "85": "0.00",
            "86": "0.00",
            "87": "0.00",
            "88": "0.00",
            "89_from_line_69": "0.00",
            "89": "0.00",
            "90": "0.00",
            "42100": "0.00",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="self_employment_income_less_than_the_unused_exemption",
    ),
    # Line 68 is 12,200.00 (80,000.00 less 67,800.00), more than line 65 (1,000.00): line 69 is 0
    # (not below zero), and line 70 is line 62.
    pytest.param(
        "1000",
        "1500",
        "0",
        "0",
        "0",
        "0",
        "80000",
        "0",
        "0",
        12,
        12,
        {
            "part_3_line_61": "0.00",
            "part_3_line_69": "0.00",
            "line_4": "80000",
            "line_42": "0.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "67800.00",
            "62": "67800.00",
            "65": "1000.00",
            "68": "12200.00",
            "69": "0",
            "70": "67800.00",
            "74": "82500",
            "76": "0.00",
            "77": "9900.00",
            "80": "79000.00",
            "82": "11200.00",
            "83_lesser": "9900.00",
            "83": "9900.00",
            "84": "6712.20",
            "85": "1356.00",
            "86": "792.00",
            "87": "2148.00",
            "88": "8860.20",
            "89_from_line_69": "0.00",
            "89": "0.00",
            "90": "8860.20",
            "42100": "8860.20",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_68_positive_and_line_3_less_than_line_58",
    ),
    # Line 3 of Part 3 (70,000.00) is not less than line 58, so the form does not complete lines
    # 63 to 69 and line 69 is 0 (line 68 is still computed: 80,000.00 less 67,800.00 = 12,200.00).
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "80000",
        "0",
        "0",
        12,
        12,
        {
            "part_3_line_61": "157.25",
            "part_3_line_69": "157.25",
            "line_4": "80000",
            "line_42": "66500.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "1300.00",
            "62": "1300.00",
            "65": "0",
            "68": "12200.00",
            "69": "0",
            "70": "1300.00",
            "74": "150000",
            "76": "0.00",
            "77": "9900.00",
            "80": "80000",
            "82": "78700.00",
            "83_lesser": "9900.00",
            "83": "9900.00",
            "84": "128.70",
            "85": "26.00",
            "86": "792.00",
            "87": "818.00",
            "88": "946.70",
            "89_from_line_69": "157.25",
            "89": "314.50",
            "90": "632.20",
            "42100": "632.20",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_68_positive_and_line_3_not_less_than_line_58",
    ),
    # Line 74 = 12,500 + 30,000.00 + 28,800.00 = 71,300.00, not more than line 57 (71,300.00):
    # line 83 is 0 although lines 77 and 82 are positive.
    pytest.param(
        "30000",
        "28800",
        "1785.00",
        "1853",
        "0",
        "0",
        "0",
        "10000",
        "2500",
        12,
        12,
        {
            "part_3_line_61": "225.76",
            "part_3_line_69": "225.76",
            "line_4": "12500",
            "line_42": "55300.06",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "12499.94",
            "62": "12499.94",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "12499.94",
            "74": "71300",
            "76": "0.00",
            "77": "9900.00",
            "80": "12500",
            "82": "0.06",
            "83_lesser": "0.06",
            "83": "0",
            "84": "1237.49",
            "85": "250.00",
            "86": "0.00",
            "87": "250.00",
            "88": "1487.49",
            "89_from_line_69": "225.76",
            "89": "451.52",
            "90": "1035.97",
            "42100": "1035.97",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_74_equal_to_line_c",
    ),
    # Line 74 = 71,300.01 is more than line 57: line 83 is the lesser of lines 77 and 82.
    pytest.param(
        "30000",
        "28800.01",
        "1785.00",
        "1853",
        "0",
        "0",
        "0",
        "10000",
        "2500",
        12,
        12,
        {
            "part_3_line_61": "225.76",
            "part_3_line_69": "225.76",
            "line_4": "12500",
            "line_42": "55300.06",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "12499.94",
            "62": "12499.94",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "12499.94",
            "74": "71300.01",
            "76": "0.00",
            "77": "9900.00",
            "80": "12500",
            "82": "0.06",
            "83_lesser": "0.06",
            "83": "0.06",
            "84": "1237.49",
            "85": "250.00",
            "86": "0.00",
            "87": "250.00",
            "88": "1487.49",
            "89_from_line_69": "225.76",
            "89": "451.52",
            "90": "1035.97",
            "42100": "1035.97",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_74_one_cent_more_than_line_c",
    ),
    # Line 4 is 6,000, line 61 is 1,300.00: line 82 = 6,000 less 1,300.00 = 4,700.00 is less than
    # line 77 (9,900.00), so line 83 = 4,700.00.
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "0",
        "4000",
        "2000",
        12,
        12,
        {
            "part_3_line_61": "157.25",
            "part_3_line_69": "157.25",
            "line_4": "6000",
            "line_42": "66500.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "1300.00",
            "62": "1300.00",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "1300.00",
            "74": "76000",
            "76": "0.00",
            "77": "9900.00",
            "80": "6000",
            "82": "4700.00",
            "83_lesser": "4700.00",
            "83": "4700.00",
            "84": "128.70",
            "85": "26.00",
            "86": "376.00",
            "87": "402.00",
            "88": "530.70",
            "89_from_line_69": "157.25",
            "89": "314.50",
            "90": "216.20",
            "42100": "216.20",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_82_less_than_line_77",
    ),
    # Line 2 of 60,000 makes line 3 of Part 3 more than line C: line 56 = 62.50, line 76 = 62.50 /
    # 4% = 1,562.50 and line 77 = 9,900.00 less 1,562.50 = 8,337.50.
    pytest.param(
        "30000",
        "60000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "0",
        "10000",
        "2500",
        12,
        12,
        {
            "part_3_line_61": "47.50",
            "part_3_line_69": "-348.50",
            "line_4": "12500",
            "line_42": "67799.99",
            "line_56": "47.50",
        },
        {
            "59": "67800.00",
            "61": "0.01",
            "62": "0.01",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "0.01",
            "74": "93700.00",
            "76": "1187.50",
            "77": "8712.50",
            "80": "12500",
            "82": "12499.99",
            "83_lesser": "8712.50",
            "83": "8712.50",
            "84": "0.00",
            "85": "0.00",
            "86": "697.00",
            "87": "697.00",
            "88": "697.00",
            "89_from_line_69": "0",
            "89": "0",
            "90": "697.00",
            "42100": "697.00",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="second_additional_contributions_reduce_line_77",
    ),
    # Line 56 is 396.00: line 76 = 396.00 / 4% = 9,900.00 is line D, so line 77 is 0.
    pytest.param(
        "30000",
        "60000",
        "1785.00",
        "2500.00",
        "500",
        "0",
        "0",
        "10000",
        "2500",
        12,
        12,
        {
            "part_3_line_61": "47.50",
            "part_3_line_69": "151.50",
            "line_4": "12500",
            "line_42": "67799.99",
            "line_56": "396.00",
        },
        {
            "59": "67800.00",
            "61": "0.01",
            "62": "0.01",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "0.01",
            "74": "93700.00",
            "76": "9900.00",
            "77": "0.00",
            "80": "12500",
            "82": "12499.99",
            "83_lesser": "0.00",
            "83": "0.00",
            "84": "0.00",
            "85": "0.00",
            "86": "0.00",
            "87": "0.00",
            "88": "0.00",
            "89_from_line_69": "151.50",
            "89": "303.00",
            "90": "-303.00",
            "42100": "0",
            "91_from_line_90": "303.00",
            "91": "151.50",
        },
        id="line_76_equal_to_line_d",
    ),
    # 6 months on line A: line D is 4,950.00 and line 76 = 396.00 / 4% = 9,900.00 is more, so line
    # 77 is 0 (negative, entered as 0).
    pytest.param(
        "30000",
        "80000",
        "500",
        "0",
        "396",
        "0",
        "300",
        "10000",
        "2500",
        6,
        12,
        {
            "part_3_line_61": "-3797.60",
            "part_3_line_69": "-3797.60",
            "line_4": "12800",
            "line_42": "8403.36",
            "line_56": "396",
        },
        {
            "59": "33900.00",
            "61": "25496.64",
            "62": "12800",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "12800",
            "74": "94000.00",
            "76": "9900.00",
            "77": "0",
            "80": "12800",
            "82": "0",
            "83_lesser": "0",
            "83": "0",
            "84": "1267.20",
            "85": "256.00",
            "86": "0.00",
            "87": "256.00",
            "88": "1523.20",
            "89_from_line_69": "0",
            "89": "0",
            "90": "1523.20",
            "42100": "1523.20",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_76_more_than_line_d_for_6_months",
    ),
    # Line 42 = 67,800.02 is more than line 59 (67,800.00): line 61 is 0 and so is line 62.
    pytest.param(
        "30000",
        "41400",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "0",
        "10000",
        "2500",
        12,
        12,
        {
            "part_3_line_61": "73.99",
            "part_3_line_69": "69.99",
            "line_4": "12500",
            "line_42": "67800.02",
            "line_56": "4.00",
        },
        {
            "59": "67800.00",
            "61": "0",
            "62": "0",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "0",
            "74": "83900",
            "76": "100.00",
            "77": "9800.00",
            "80": "12500",
            "82": "12500",
            "83_lesser": "9800.00",
            "83": "9800.00",
            "84": "0.00",
            "85": "0.00",
            "86": "784.00",
            "87": "784.00",
            "88": "784.00",
            "89_from_line_69": "69.99",
            "89": "139.98",
            "90": "644.02",
            "42100": "644.02",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_42_more_than_line_59",
    ),
    # Line 42 is negative (line 35A takes line 20 in brackets), so line 61 is more than line 59
    # and line 70 is more than the 67,800.00 band of lines 84 and 85, which stop at their printed
    # maximums.
    pytest.param(
        "70000",
        "30000",
        "0",
        "0",
        "100",
        "0",
        "80000",
        "10000",
        "2500",
        12,
        12,
        {
            "part_3_line_61": "-4125.63",
            "part_3_line_69": "-4421.63",
            "line_4": "92500",
            "line_42": "-239.41",
            "line_56": "100",
        },
        {
            "59": "67800.00",
            "61": "68039.41",
            "62": "68039.41",
            "65": "0",
            "68": "24700.00",
            "69": "0",
            "70": "68039.41",
            "74": "173700.00",
            "76": "2500.00",
            "77": "7400.00",
            "80": "92500",
            "82": "24460.59",
            "83_lesser": "7400.00",
            "83": "7400.00",
            "84": "6712.20",
            "85": "1356.00",
            "86": "592.00",
            "87": "1948.00",
            "88": "8660.20",
            "89_from_line_69": "0",
            "89": "0",
            "90": "8660.20",
            "42100": "8660.20",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_42_negative",
    ),
    # 6 months for CPP and QPP: lines C, D and F are 35,650.00, 4,950.00 and 1,750.00.
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        "0",
        "10000",
        "2500",
        6,
        6,
        {
            "part_3_line_61": "2180.78",
            "part_3_line_69": "1982.78",
            "line_4": "12500",
            "line_42": "33899.98",
            "line_56": "198.00",
        },
        {
            "59": "33900.00",
            "61": "0.02",
            "62": "0.02",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "0.02",
            "74": "53100.00",
            "76": "4950.00",
            "77": "0.00",
            "80": "12500",
            "82": "12499.98",
            "83_lesser": "0.00",
            "83": "0.00",
            "84": "0.00",
            "85": "0.00",
            "86": "0.00",
            "87": "0.00",
            "88": "0.00",
            "89_from_line_69": "1982.78",
            "89": "3965.56",
            "90": "-3965.56",
            "42100": "0",
            "91_from_line_90": "3965.56",
            "91": "1982.78",
        },
        id="6_months_on_lines_a_and_b",
    ),
    # Line A of 6 (C = 35,650.00, D = 4,950.00, F = 1,750.00) and line B of 12 (G to J): net self-
    # employment income of 30,000, so line 83 is line D (4,950.00), the lesser of lines 77 and 82.
    pytest.param(
        "20000",
        "30000",
        "500",
        "1000",
        "0",
        "0",
        "30000",
        "0",
        "0",
        6,
        12,
        {
            "part_3_line_61": "-1047.62",
            "part_3_line_69": "-1126.82",
            "line_4": "30000",
            "line_42": "24000.94",
            "line_56": "0",
        },
        {
            "59": "33900.00",
            "61": "9899.06",
            "62": "9899.06",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "9899.06",
            "74": "76240.00",
            "76": "0.00",
            "77": "4950.00",
            "80": "30000",
            "82": "20100.94",
            "83_lesser": "4950.00",
            "83": "4950.00",
            "84": "980.01",
            "85": "197.98",
            "86": "396.00",
            "87": "593.98",
            "88": "1573.99",
            "89_from_line_69": "0",
            "89": "0",
            "90": "1573.99",
            "42100": "1573.99",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="6_months_for_cpp_and_12_for_qpp",
    ),
    # Line 69 of Part 3 is negative, so the amount of line 89 is 0 and line 90 is line 88.
    pytest.param(
        "30000",
        "80000",
        "0",
        "0",
        "0",
        "0",
        "0",
        "10000",
        "2500",
        12,
        12,
        {
            "part_3_line_61": "-4256.00",
            "part_3_line_69": "-4652.00",
            "line_4": "12500",
            "line_42": "-120.97",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "67920.97",
            "62": "12500",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "12500",
            "74": "93700.00",
            "76": "0.00",
            "77": "9900.00",
            "80": "12500",
            "82": "0",
            "83_lesser": "0",
            "83": "0",
            "84": "1237.50",
            "85": "250.00",
            "86": "0.00",
            "87": "250.00",
            "88": "1487.50",
            "89_from_line_69": "0",
            "89": "0",
            "90": "1487.50",
            "42100": "1487.50",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_69_of_part_3_negative",
    ),
    # Line 69 of Part 3 is 0 and no self-employment income: lines 88 and 89 are 0, so line 90 is
    # 0, neither positive nor negative.
    pytest.param(
        "30000",
        "40000",
        "1695.75",
        "2432",
        "0",
        "0",
        "0",
        "0",
        "0",
        12,
        12,
        {
            "part_3_line_61": "0.00",
            "part_3_line_69": "0.00",
            "line_4": "0",
            "line_42": "66500.00",
            "line_56": "0",
        },
        {
            "59": "67800.00",
            "61": "1300.00",
            "62": "0",
            "65": "0",
            "68": "0",
            "69": "0",
            "70": "0",
            "74": "70000",
            "76": "0.00",
            "77": "9900.00",
            "80": "0",
            "82": "0",
            "83_lesser": "0",
            "83": "0",
            "84": "0.00",
            "85": "0.00",
            "86": "0.00",
            "87": "0.00",
            "88": "0.00",
            "89_from_line_69": "0.00",
            "89": "0.00",
            "90": "0.00",
            "42100": "0.00",
            "91_from_line_90": "0",
            "91": "0.00",
        },
        id="line_90_zero",
    ),
]


@pytest.mark.parametrize(
    (
        "line_1",
        "line_2",
        "box_16",
        "box_17",
        "box_16a",
        "box_17a",
        "line_12200",
        "line_2_of_part_4",
        "line_3_of_part_4",
        "months_a",
        "months_b",
        "upstream",
        "expected",
    ),
    PART_4_EARNINGS_CASES,
)
def test_return_bo_part_4_lines_59_to_91(
    line_1: str,
    line_2: str,
    box_16: str,
    box_17: str,
    box_16a: str,
    box_17a: str,
    line_12200: str,
    line_2_of_part_4: str,
    line_3_of_part_4: str,
    months_a: int,
    months_b: int,
    upstream: dict[str, str],
    expected: dict[str, str],
) -> None:
    worksheet = return_bo(
        line_1,
        line_2,
        box_16,
        box_17,
        line_25=box_16a,
        line_45=box_17a,
        cpp_months=months_a,
        qpp_months=months_b,
        cpt20_earnings=line_2_of_part_4,
        cpt20_t4_earnings=line_3_of_part_4,
        net_partnership_income=line_12200,
    )

    assert worksheet.get(RC381_PART_3_LINE_61).value == D(upstream["part_3_line_61"])
    assert worksheet.get(RC381_PART_3_LINE_69).value == D(upstream["part_3_line_69"])
    assert worksheet.get(RC381_PART_4_LINE_4).value == D(upstream["line_4"])
    assert worksheet.get(RC381_PART_4_LINE_42).value == D(upstream["line_42"])
    assert worksheet.get(RC381_PART_4_LINE_56).value == D(upstream["line_56"])
    assert part_4_earnings(worksheet) == {line: D(value) for line, value in expected.items()}


# Part 4, lines 92 to 110 (the base contributions through employment income, the amount for line
# 30800 of the return, and the deduction for the enhanced contributions on employment income, the
# amount for line 22215). Lines 92, 99 and 106 choose by the sign of lines 53, 60 and 68 of Part 3
# ("If line 53 of Part 3 is positive or "0", enter the amount from line 52 of Part 3 at line 92
# and line 98, and continue at line 99. If not, enter the amount from line 49 of Part 3 and
# continue at line 93."), and the lines in between are completed only for the other sign. They are
# computed whatever the signs are (as Part 4's earlier blocks are), each giving the "0" the form
# enters where it is not completed, which the tests below pin. "104_difference" is the "result of
# line 68 of Part 3 minus line 97" printed inside line 104. Lines 92 to 110 repeat Part 3b's lines
# 75 to 93 on the same Part 3 totals ("PART_3B" maps them).
PART_4_EMPLOYMENT_KINDS: dict[str, ArtifactKind[Decimal]] = {
    "92": RC381_PART_4_LINE_92,
    "93": RC381_PART_4_LINE_93,
    "94": RC381_PART_4_LINE_94,
    "95": RC381_PART_4_LINE_95,
    "96": RC381_PART_4_LINE_96,
    "97": RC381_PART_4_LINE_97,
    "98": RC381_PART_4_LINE_98,
    "99": RC381_PART_4_LINE_99,
    "100": RC381_PART_4_LINE_100,
    "101": RC381_PART_4_LINE_101,
    "102": RC381_PART_4_LINE_102,
    "103": RC381_PART_4_LINE_103,
    "104_difference": RC381_PART_4_LINE_104_DIFFERENCE,
    "104": RC381_PART_4_LINE_104,
    "105": RC381_PART_4_LINE_105,
    "106": RC381_PART_4_LINE_106,
    "107": RC381_PART_4_LINE_107,
    "108": RC381_PART_4_LINE_108,
    "109": RC381_PART_4_LINE_109,
    "110": RC381_PART_4_LINE_110,
}

# Part 4's line, Part 3b's line.
PART_3B_OF_PART_4: dict[str, str] = {
    "92": "75",
    "93": "76",
    "94": "77",
    "95": "78",
    "96": "79",
    "97": "80",
    "98": "81",
    "99": "82",
    "100": "83",
    "101": "84",
    "102": "85",
    "103": "86",
    "104_difference": "87h",
    "104": "87",
    "105": "88",
    "106": "89",
    "107": "90",
    "108": "91",
    "109": "92",
    "110": "93",
}


def part_4_employment(worksheet: Worksheet) -> dict[str, Decimal]:
    """Part 4's lines 92 to 110 of `worksheet`, by line number (see `PART_4_EMPLOYMENT_KINDS`)."""
    return {line: worksheet.get(kind).value for line, kind in PART_4_EMPLOYMENT_KINDS.items()}


def test_return_bo_part_4_lines_92_to_110_match_the_tickets_example() -> None:
    # Return BO: line 53 of Part 3 = 131.63 and line 60 = 25.62 are positive and line 68 = 0, so
    # the form enters line 52 (3,462.75) at lines 92 and 98 and line 59 (665.00) at lines 99 and
    # 105, and line 67 (0) at lines 106 and 109. Lines 93 to 95, 97, 100 to 102, 104, 107 and 108
    # are not completed: "0". Line 98 = 3,462.75 + 0 and line 110 = 665.00 + 0.00: the ticket's
    # amounts for line 30800 and line 22215.
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_53).value == D("131.63")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("25.62")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("0")
    assert part_4_employment(worksheet) == {
        "92": D("3462.75"),
        "93": D("0"),
        "94": D("0"),
        "95": D("0"),
        "96": D("3462.75"),
        "97": D("0"),
        "98": D("3462.75"),
        "99": D("665.00"),
        "100": D("0"),
        "101": D("0"),
        "102": D("0"),
        "103": D("665.00"),
        "104_difference": D("0.00"),
        "104": D("0"),
        "105": D("665.00"),
        "106": D("0.00"),
        "107": D("0"),
        "108": D("0"),
        "109": D("0.00"),
        "110": D("665.00"),
    }
    assert worksheet.get(RC381_PART_4_LINE_98).value == worksheet.get(RC381_PART_3_LINE_52).value
    assert worksheet.get(RC381_PART_4_LINE_110).value == worksheet.get(RC381_PART_3_LINE_59).value


def test_return_bo_part_4_lines_92_to_110_with_lines_53_60_and_68_all_zero() -> None:
    # Box 16 of 1,695.20 and box 17 of 2,432.55: lines 53, 60, 61 and 68 of Part 3 are 0, "positive
    # or 0" each: line 92 = line 52 = 3,462.75, line 99 = line 59 = 665.00 and line 106 = line 67 =
    # 0. Line 98 = 3,462.75 and line 110 = 665.00.
    worksheet = return_bo(line_19="1695.20", line_39="2432.55")

    assert worksheet.get(RC381_PART_3_LINE_53).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("0")
    assert worksheet.get(RC381_PART_3_LINE_68).value == D("0")
    assert part_4_employment(worksheet) == {
        "92": D("3462.75"),
        "93": D("0"),
        "94": D("0"),
        "95": D("0"),
        "96": D("3462.75"),
        "97": D("0"),
        "98": D("3462.75"),
        "99": D("665.00"),
        "100": D("0"),
        "101": D("0"),
        "102": D("0"),
        "103": D("665.00"),
        "104_difference": D("0.00"),
        "104": D("0"),
        "105": D("665.00"),
        "106": D("0.00"),
        "107": D("0"),
        "108": D("0"),
        "109": D("0.00"),
        "110": D("665.00"),
    }


def test_return_bo_part_4_line_92_takes_line_52_at_a_line_53_of_zero_and_line_49_below_it() -> None:
    # Line 53 of Part 3 of exactly 0 is "positive or "0"": line 92 = line 52 (3,462.75), line 93 =
    # 0. A line 53 of -0.01 is negative: line 92 = line 49 (3,462.74), line 93 = 0.01, line 94 = 0
    # (line 60 is 0, not positive), line 95 = 0.01 and, with line 68 at 0, line 97 = 0, so line 98
    # = 3,462.74.
    zero = return_bo(line_19="1695", line_39="2432.73")
    negative = return_bo(line_19="1695.13", line_39="2432.61")

    assert zero.get(RC381_PART_3_LINE_53).value == D("0")
    assert zero.get(RC381_PART_4_LINE_92).value == D("3462.75")
    assert zero.get(RC381_PART_4_LINE_93).value == D("0")
    assert zero.get(RC381_PART_4_LINE_98).value == D("3462.75")
    assert negative.get(RC381_PART_3_LINE_53).value == D("-0.01")
    assert negative.get(RC381_PART_3_LINE_49).value == D("3462.74")
    assert negative.get(RC381_PART_4_LINE_92).value == D("3462.74")
    assert negative.get(RC381_PART_4_LINE_93).value == D("0.01")
    assert negative.get(RC381_PART_4_LINE_94).value == D("0")
    assert negative.get(RC381_PART_4_LINE_95).value == D("0.01")
    assert negative.get(RC381_PART_4_LINE_97).value == D("0")
    assert negative.get(RC381_PART_4_LINE_98).value == D("3462.74")


def test_return_bo_part_4_line_99_takes_line_59_at_a_line_60_of_zero_and_line_56_below_it() -> None:
    # Line 60 of Part 3 of exactly 0 (line 53 = 0.06) or of 0.01 is "positive or "0"": line 99 =
    # line 59 (665.00) and line 100 = 0. A line 60 of -0.02 (line 53 = 0) is negative: line 99 =
    # line 56 (664.98), line 100 = 0.02, line 101 = 0 (line 53 is not positive), line 102 = 0.02,
    # line 103 = 664.98 and line 105 = 664.98 + 0.
    zero = return_bo(line_19="1695", line_39="2432.81")
    cent = return_bo(line_19="1695.79", line_39="2431.97")
    negative = return_bo(line_19="1695", line_39="2432.73")

    assert zero.get(RC381_PART_3_LINE_60).value == D("0")
    assert zero.get(RC381_PART_4_LINE_99).value == D("665.00")
    assert zero.get(RC381_PART_4_LINE_100).value == D("0")
    assert zero.get(RC381_PART_4_LINE_105).value == D("665.00")
    assert cent.get(RC381_PART_3_LINE_60).value == D("0.01")
    assert cent.get(RC381_PART_4_LINE_99).value == D("665.00")
    assert cent.get(RC381_PART_4_LINE_100).value == D("0")
    assert cent.get(RC381_PART_4_LINE_105).value == D("665.00")
    assert negative.get(RC381_PART_3_LINE_60).value == D("-0.02")
    assert negative.get(RC381_PART_3_LINE_56).value == D("664.98")
    assert negative.get(RC381_PART_4_LINE_99).value == D("664.98")
    assert negative.get(RC381_PART_4_LINE_100).value == D("0.02")
    assert negative.get(RC381_PART_4_LINE_101).value == D("0")
    assert negative.get(RC381_PART_4_LINE_102).value == D("0.02")
    assert negative.get(RC381_PART_4_LINE_103).value == D("664.98")
    assert negative.get(RC381_PART_4_LINE_105).value == D("664.98")


def test_return_bo_part_4_line_106_is_line_67_for_a_line_68_of_zero_or_more_and_line_64_below() -> (
    None
):
    # Line 68 of Part 3 of 0 (the ticket's example) or positive (20.00): line 106 = line 67 (0.00
    # and 396.00) and line 107 = 0. Negative (-296.00, line 64 = 100 and line 67 = 396.00): line 106
    # = line 64 (100), line 107 = 296.00 and line 109 = 100 + line 108 (line 61 = 183.80 is the
    # lesser) = 283.80.
    zero = return_bo()
    positive = return_bo(
        line_1="60000", line_2="50000", line_19="3500", line_39="2432", line_25="396", line_45="20"
    )
    negative = return_bo(
        line_1="34000", line_2="80000", line_19="2000", line_39="2432", line_25="100"
    )

    assert zero.get(RC381_PART_3_LINE_68).value == D("0")
    assert zero.get(RC381_PART_4_LINE_106).value == D("0.00")
    assert zero.get(RC381_PART_4_LINE_107).value == D("0")
    assert positive.get(RC381_PART_3_LINE_68).value == D("20.00")
    assert positive.get(RC381_PART_3_LINE_67).value == D("396.00")
    assert positive.get(RC381_PART_4_LINE_106).value == D("396.00")
    assert positive.get(RC381_PART_4_LINE_107).value == D("0")
    assert positive.get(RC381_PART_4_LINE_108).value == D("0")
    assert negative.get(RC381_PART_3_LINE_68).value == D("-296.00")
    assert negative.get(RC381_PART_3_LINE_64).value == D("100")
    assert negative.get(RC381_PART_4_LINE_106).value == D("100")
    assert negative.get(RC381_PART_4_LINE_107).value == D("296.00")
    assert negative.get(RC381_PART_4_LINE_108).value == D("183.80")
    assert negative.get(RC381_PART_4_LINE_109).value == D("283.80")


# Each case: box 26 outside and in Quebec (lines 1 and 2 of Part 3), box 16, box 17, box 16A and
# box 17A (lines 19, 39, 25 and 45), then the lines of Part 3 that Part 4's lines 92 to 110 read
# (49, 52, 53, 56, 59, 60, 61, 64, 67 and 68) and Part 4's lines 92 to 110. The figures are proved
# by an independent Decimal model of the printed form (not by this engine). The cases vary the
# signs of lines 53, 60, 61 and 68 of Part 3 and which of the two lines each "whichever is less"
# takes. The CPT20 election and net self-employment income do not reach lines 92 to 110, so they
# stay at their defaults.
PART_4_EMPLOYMENT_CASES = [
    # The example of Return BO: lines 53 and 60 of Part 3 are positive and line 68 is 0, so lines 92
    # and 99 take lines 52 and 59 and line 106 takes line 67.
    pytest.param(
        "30000",
        "40000",
        "1785.00",
        "2500.00",
        "0",
        "0",
        {
            "part_3_line_49": "3594.38",
            "part_3_line_52": "3462.75",
            "part_3_line_53": "131.63",
            "part_3_line_56": "690.62",
            "part_3_line_59": "665.00",
            "part_3_line_60": "25.62",
            "part_3_line_61": "157.25",
            "part_3_line_64": "0",
            "part_3_line_67": "0.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "3462.75",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3462.75",
            "97": "0",
            "98": "3462.75",
            "99": "665.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "665.00",
            "104_difference": "0.00",
            "104": "0",
            "105": "665.00",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "665.00",
        },
        id="ticket_example",
    ),
    # Lines 53, 60 and 68 of Part 3 are all 0, each in the "positive or 0" branch.
    pytest.param(
        "30000",
        "40000",
        "1695.20",
        "2432.55",
        "0",
        "0",
        {
            "part_3_line_49": "3462.75",
            "part_3_line_52": "3462.75",
            "part_3_line_53": "0.00",
            "part_3_line_56": "665.00",
            "part_3_line_59": "665.00",
            "part_3_line_60": "0.00",
            "part_3_line_61": "0.00",
            "part_3_line_64": "0",
            "part_3_line_67": "0.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "3462.75",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3462.75",
            "97": "0",
            "98": "3462.75",
            "99": "665.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "665.00",
            "104_difference": "0.00",
            "104": "0",
            "105": "665.00",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "665.00",
        },
        id="lines_53_60_and_68_all_zero",
    ),
    # Line 53 of Part 3 is -28.74 and line 60 is 28.74: line 92 = line 49, line 93 = 28.74, line 94
    # = the lesser of 28.74 and 28.74, line 95 = 0, and line 98 = 3,434.01 + 28.74 = line 52.
    pytest.param(
        "29500",
        "40000",
        "1750",
        "2347.93",
        "0",
        "0",
        {
            "part_3_line_49": "3436.95",
            "part_3_line_52": "3437.93",
            "part_3_line_53": "-0.98",
            "part_3_line_56": "660.98",
            "part_3_line_59": "660.00",
            "part_3_line_60": "0.98",
            "part_3_line_61": "0.00",
            "part_3_line_64": "0",
            "part_3_line_67": "0.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "3436.95",
            "93": "0.98",
            "94": "0.98",
            "95": "0.00",
            "96": "3437.93",
            "97": "0",
            "98": "3437.93",
            "99": "660.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "660.00",
            "104_difference": "0.00",
            "104": "0",
            "105": "660.00",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "660.00",
        },
        id="lines_60_and_93_the_same_amount",
    ),
    # Line 60 of Part 3 (39.20) is more than line 93 (15.20): line 94 = line 93 and line 95 = 0.
    pytest.param(
        "7000",
        "3000",
        "395.67",
        "0",
        "0",
        "0",
        {
            "part_3_line_49": "329.17",
            "part_3_line_52": "330.53",
            "part_3_line_53": "-1.36",
            "part_3_line_56": "66.50",
            "part_3_line_59": "65.00",
            "part_3_line_60": "1.50",
            "part_3_line_61": "0.14",
            "part_3_line_64": "0",
            "part_3_line_67": "0.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "329.17",
            "93": "1.36",
            "94": "1.36",
            "95": "0.00",
            "96": "330.53",
            "97": "0",
            "98": "330.53",
            "99": "65.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "65.00",
            "104_difference": "0.00",
            "104": "0",
            "105": "65.00",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "65.00",
        },
        id="line_94_is_line_93_when_line_60_is_more",
    ),
    # Line 60 of Part 3 (17.38) is less than line 93 (53.18): line 94 = line 60, line 95 = 35.80;
    # line 68 of Part 3 (50.00, positive) is more than line 95, so line 97 = line 95.
    pytest.param(
        "15500",
        "50000",
        "900",
        "3000",
        "50",
        "0",
        {
            "part_3_line_49": "3279.99",
            "part_3_line_52": "3281.97",
            "part_3_line_53": "-1.98",
            "part_3_line_56": "620.01",
            "part_3_line_59": "620.00",
            "part_3_line_60": "0.01",
            "part_3_line_61": "-1.97",
            "part_3_line_64": "50",
            "part_3_line_67": "0.00",
            "part_3_line_68": "50.00",
        },
        {
            "92": "3279.99",
            "93": "1.98",
            "94": "0.01",
            "95": "1.97",
            "96": "3280.00",
            "97": "1.97",
            "98": "3281.97",
            "99": "620.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "620.00",
            "104_difference": "48.03",
            "104": "0",
            "105": "620.00",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "620.00",
        },
        id="line_94_is_line_60_when_that_is_less_and_line_97_is_line_95",
    ),
    # Line 53 negative, line 60 positive and line 68 positive and less than line 95 (20.76): line 97
    # = line 68.
    pytest.param(
        "50000",
        "30000",
        "2975.00",
        "1150",
        "50",
        "300",
        {
            "part_3_line_49": "3445.31",
            "part_3_line_52": "3470.51",
            "part_3_line_53": "-25.20",
            "part_3_line_56": "679.69",
            "part_3_line_59": "678.00",
            "part_3_line_60": "1.69",
            "part_3_line_61": "-23.51",
            "part_3_line_64": "350",
            "part_3_line_67": "348.00",
            "part_3_line_68": "2.00",
        },
        {
            "92": "3445.31",
            "93": "25.20",
            "94": "1.69",
            "95": "23.51",
            "96": "3447.00",
            "97": "2.00",
            "98": "3449.00",
            "99": "678.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "678.00",
            "104_difference": "0.00",
            "104": "0",
            "105": "678.00",
            "106": "348.00",
            "107": "0",
            "108": "0",
            "109": "348.00",
            "110": "1026.00",
        },
        id="line_97_is_line_68_when_that_is_the_lesser",
    ),
    # Line 60 of Part 3 is negative and line 53 positive and more than line 100: line 99 = line 56,
    # line 101 = line 100 and line 102 = 0.
    pytest.param(
        "11500",
        "28500",
        "564.92",
        "1726.76",
        "0",
        "0",
        {
            "part_3_line_49": "1926.93",
            "part_3_line_52": "1923.78",
            "part_3_line_53": "3.15",
            "part_3_line_56": "364.75",
            "part_3_line_59": "365.00",
            "part_3_line_60": "-0.25",
            "part_3_line_61": "2.90",
            "part_3_line_64": "0",
            "part_3_line_67": "0.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "1923.78",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "1923.78",
            "97": "0",
            "98": "1923.78",
            "99": "364.75",
            "100": "0.25",
            "101": "0.25",
            "102": "0.00",
            "103": "365.00",
            "104_difference": "0.00",
            "104": "0",
            "105": "365.00",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "365.00",
        },
        id="line_101_is_line_100_when_line_53_is_more",
    ),
    # Line 60 of Part 3 is negative and line 53 positive and less than line 100: line 101 = line 53,
    # and line 102 is above 0 while line 68 is 0, so line 104 = 0.
    pytest.param(
        "21000",
        "65500",
        "256.84",
        "4004.66",
        "396",
        "0",
        {
            "part_3_line_49": "3592.60",
            "part_3_line_52": "3587.13",
            "part_3_line_53": "5.47",
            "part_3_line_56": "668.90",
            "part_3_line_59": "678.00",
            "part_3_line_60": "-9.10",
            "part_3_line_61": "-3.63",
            "part_3_line_64": "396",
            "part_3_line_67": "396.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "3587.13",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3587.13",
            "97": "0",
            "98": "3587.13",
            "99": "668.90",
            "100": "9.10",
            "101": "5.47",
            "102": "3.63",
            "103": "674.37",
            "104_difference": "0.00",
            "104": "0",
            "105": "674.37",
            "106": "396.00",
            "107": "0",
            "108": "0",
            "109": "396.00",
            "110": "1070.37",
        },
        id="line_101_is_line_53_when_that_is_less",
    ),
    # Lines 53 and 60 of Part 3 negative and line 68 positive (1,099.70): line 97 = line 95
    # (910.81), so line 68 less line 97 is 188.89 and line 104 = the lesser of line 102 (187.79)
    # and that difference.
    pytest.param(
        "37500",
        "39000",
        "611.76",
        "2479.29",
        "1307.70",
        "0",
        {
            "part_3_line_49": "2600.84",
            "part_3_line_52": "3511.65",
            "part_3_line_53": "-910.81",
            "part_3_line_56": "490.21",
            "part_3_line_59": "678.00",
            "part_3_line_60": "-187.79",
            "part_3_line_61": "-1098.60",
            "part_3_line_64": "1307.70",
            "part_3_line_67": "208.00",
            "part_3_line_68": "1099.70",
        },
        {
            "92": "2600.84",
            "93": "910.81",
            "94": "0",
            "95": "910.81",
            "96": "2600.84",
            "97": "910.81",
            "98": "3511.65",
            "99": "490.21",
            "100": "187.79",
            "101": "0",
            "102": "187.79",
            "103": "490.21",
            "104_difference": "188.89",
            "104": "187.79",
            "105": "678.00",
            "106": "208.00",
            "107": "0",
            "108": "0",
            "109": "208.00",
            "110": "886.00",
        },
        id="line_104_is_line_102_when_that_is_the_lesser",
    ),
    # Line 68 of Part 3 (4.00) is positive and line 97 is 0 (line 53 is positive, 0.42): line 104 =
    # line 68 less line 97 (4.00), less than line 102 (5.80).
    pytest.param(
        "60000",
        "30000",
        "2240",
        "1890",
        "100",
        "300",
        {
            "part_3_line_49": "3458.22",
            "part_3_line_52": "3457.80",
            "part_3_line_53": "0.42",
            "part_3_line_56": "671.78",
            "part_3_line_59": "678.00",
            "part_3_line_60": "-6.22",
            "part_3_line_61": "-5.80",
            "part_3_line_64": "400",
            "part_3_line_67": "396.00",
            "part_3_line_68": "4.00",
        },
        {
            "92": "3457.80",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3457.80",
            "97": "0",
            "98": "3457.80",
            "99": "671.78",
            "100": "6.22",
            "101": "0.42",
            "102": "5.80",
            "103": "672.20",
            "104_difference": "4.00",
            "104": "4.00",
            "105": "676.20",
            "106": "396.00",
            "107": "0",
            "108": "0",
            "109": "396.00",
            "110": "1072.20",
        },
        id="line_104_is_line_68_less_line_97_when_line_53_is_positive",
    ),
    # Lines 53, 60 and 61 of Part 3 negative and line 68 positive: line 97 = line 95 (190.89, less
    # than line 68), line 104 = the lesser of line 102 (17.55) and line 68 less line 97 (213.11).
    pytest.param(
        "60000",
        "80000",
        "3000",
        "1000",
        "500",
        "300",
        {
            "part_3_line_49": "3339.55",
            "part_3_line_52": "3530.44",
            "part_3_line_53": "-190.89",
            "part_3_line_56": "660.45",
            "part_3_line_59": "678.00",
            "part_3_line_60": "-17.55",
            "part_3_line_61": "-208.44",
            "part_3_line_64": "800",
            "part_3_line_67": "396.00",
            "part_3_line_68": "404.00",
        },
        {
            "92": "3339.55",
            "93": "190.89",
            "94": "0",
            "95": "190.89",
            "96": "3339.55",
            "97": "190.89",
            "98": "3530.44",
            "99": "660.45",
            "100": "17.55",
            "101": "0",
            "102": "17.55",
            "103": "660.45",
            "104_difference": "213.11",
            "104": "17.55",
            "105": "678.00",
            "106": "396.00",
            "107": "0",
            "108": "0",
            "109": "396.00",
            "110": "1074.00",
        },
        id="lines_53_and_60_negative_and_line_104_is_line_102",
    ),
    # Lines 53 and 60 of Part 3 negative and line 68 positive (892.55): line 97 = line 95 (860.61),
    # line 104 = line 68 less line 97 (31.94), less than line 102 (175.56).
    pytest.param(
        "28000",
        "39500",
        "423.82",
        "2516.54",
        "892.55",
        "0",
        {
            "part_3_line_49": "2475.92",
            "part_3_line_52": "3336.53",
            "part_3_line_53": "-860.61",
            "part_3_line_56": "464.44",
            "part_3_line_59": "640.00",
            "part_3_line_60": "-175.56",
            "part_3_line_61": "-1036.17",
            "part_3_line_64": "892.55",
            "part_3_line_67": "0.00",
            "part_3_line_68": "892.55",
        },
        {
            "92": "2475.92",
            "93": "860.61",
            "94": "0",
            "95": "860.61",
            "96": "2475.92",
            "97": "860.61",
            "98": "3336.53",
            "99": "464.44",
            "100": "175.56",
            "101": "0",
            "102": "175.56",
            "103": "464.44",
            "104_difference": "31.94",
            "104": "31.94",
            "105": "496.38",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "496.38",
        },
        id="lines_53_and_60_negative_and_line_104_is_line_68_less_line_97",
    ),
    # Line 97 = line 68 (20.00, less than line 95): line 68 less line 97 = 0, so line 104 = 0
    # although line 102 (206.23) is above 0.
    pytest.param(
        "40000",
        "30000",
        "1800",
        "1000",
        "0",
        "20",
        {
            "part_3_line_49": "2341.23",
            "part_3_line_52": "3420.00",
            "part_3_line_53": "-1078.77",
            "part_3_line_56": "458.77",
            "part_3_line_59": "665.00",
            "part_3_line_60": "-206.23",
            "part_3_line_61": "-1285.00",
            "part_3_line_64": "20",
            "part_3_line_67": "0.00",
            "part_3_line_68": "20.00",
        },
        {
            "92": "2341.23",
            "93": "1078.77",
            "94": "0",
            "95": "1078.77",
            "96": "2341.23",
            "97": "20.00",
            "98": "2361.23",
            "99": "458.77",
            "100": "206.23",
            "101": "0",
            "102": "206.23",
            "103": "458.77",
            "104_difference": "0.00",
            "104": "0.00",
            "105": "458.77",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "458.77",
        },
        id="line_104_is_zero_when_line_97_takes_all_of_line_68",
    ),
    # Line 68 of Part 3 is negative (-279.00): line 106 = line 64, line 107 = 279.00 and line 108 =
    # the lesser of line 61 (770.21) and line 107.
    pytest.param(
        "30000",
        "50000",
        "1785.00",
        "3210",
        "49",
        "20",
        {
            "part_3_line_49": "4193.44",
            "part_3_line_52": "3546.79",
            "part_3_line_53": "646.65",
            "part_3_line_56": "801.56",
            "part_3_line_59": "678.00",
            "part_3_line_60": "123.56",
            "part_3_line_61": "770.21",
            "part_3_line_64": "69",
            "part_3_line_67": "348.00",
            "part_3_line_68": "-279.00",
        },
        {
            "92": "3546.79",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3546.79",
            "97": "0",
            "98": "3546.79",
            "99": "678.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "678.00",
            "104_difference": "-279.00",
            "104": "0",
            "105": "678.00",
            "106": "69",
            "107": "279.00",
            "108": "279.00",
            "109": "348.00",
            "110": "1026.00",
        },
        id="line_108_is_line_107_when_that_is_the_lesser",
    ),
    # Line 68 of Part 3 is negative (-296.00) and line 61 positive and less than line 107: line 108
    # = line 61 (176.00).
    pytest.param(
        "34000",
        "80000",
        "2000",
        "2432",
        "100",
        "0",
        {
            "part_3_line_49": "3715.87",
            "part_3_line_52": "3570.20",
            "part_3_line_53": "145.67",
            "part_3_line_56": "716.13",
            "part_3_line_59": "678.00",
            "part_3_line_60": "38.13",
            "part_3_line_61": "183.80",
            "part_3_line_64": "100",
            "part_3_line_67": "396.00",
            "part_3_line_68": "-296.00",
        },
        {
            "92": "3570.20",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3570.20",
            "97": "0",
            "98": "3570.20",
            "99": "678.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "678.00",
            "104_difference": "-296.00",
            "104": "0",
            "105": "678.00",
            "106": "100",
            "107": "296.00",
            "108": "183.80",
            "109": "283.80",
            "110": "961.80",
        },
        id="line_108_is_line_61_when_that_is_the_lesser",
    ),
    # Line 68 of Part 3 is negative but line 61 is not positive: line 108 = 0.
    pytest.param(
        "2000",
        "80000",
        "100",
        "0",
        "50",
        "20",
        {
            "part_3_line_49": "83.19",
            "part_3_line_52": "3653.76",
            "part_3_line_53": "-3570.57",
            "part_3_line_56": "16.81",
            "part_3_line_59": "678.00",
            "part_3_line_60": "-661.19",
            "part_3_line_61": "-4231.76",
            "part_3_line_64": "70",
            "part_3_line_67": "396.00",
            "part_3_line_68": "-326.00",
        },
        {
            "92": "83.19",
            "93": "3570.57",
            "94": "0",
            "95": "3570.57",
            "96": "83.19",
            "97": "0",
            "98": "83.19",
            "99": "16.81",
            "100": "661.19",
            "101": "0",
            "102": "661.19",
            "103": "16.81",
            "104_difference": "-326.00",
            "104": "0",
            "105": "16.81",
            "106": "70",
            "107": "326.00",
            "108": "0",
            "109": "70",
            "110": "86.81",
        },
        id="line_68_negative_and_line_61_negative",
    ),
    # Line 68 of Part 3 is positive: line 106 = line 67 and line 108 = 0.
    pytest.param(
        "60000",
        "50000",
        "3500",
        "2432",
        "396",
        "20",
        {
            "part_3_line_49": "4963.77",
            "part_3_line_52": "3494.78",
            "part_3_line_53": "1468.99",
            "part_3_line_56": "968.23",
            "part_3_line_59": "678.01",
            "part_3_line_60": "290.22",
            "part_3_line_61": "1759.21",
            "part_3_line_64": "416",
            "part_3_line_67": "396.00",
            "part_3_line_68": "20.00",
        },
        {
            "92": "3494.78",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3494.78",
            "97": "0",
            "98": "3494.78",
            "99": "678.01",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "678.01",
            "104_difference": "20.00",
            "104": "0",
            "105": "678.01",
            "106": "396.00",
            "107": "0",
            "108": "0",
            "109": "396.00",
            "110": "1074.01",
        },
        id="line_68_positive_and_lines_53_and_60_positive",
    ),
    # Line 53 of Part 3 is exactly 0 ("positive or 0": line 92 = line 52) and line 60 is -0.02
    # (negative): line 99 = line 56, line 100 = 0.02 and line 101 = 0 (line 53 is not positive).
    pytest.param(
        "30000",
        "40000",
        "1695",
        "2432.73",
        "0",
        "0",
        {
            "part_3_line_49": "3462.75",
            "part_3_line_52": "3462.75",
            "part_3_line_53": "0.00",
            "part_3_line_56": "664.98",
            "part_3_line_59": "665.00",
            "part_3_line_60": "-0.02",
            "part_3_line_61": "-0.02",
            "part_3_line_64": "0",
            "part_3_line_67": "0.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "3462.75",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3462.75",
            "97": "0",
            "98": "3462.75",
            "99": "664.98",
            "100": "0.02",
            "101": "0",
            "102": "0.02",
            "103": "664.98",
            "104_difference": "0.00",
            "104": "0",
            "105": "664.98",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "664.98",
        },
        id="line_53_zero_and_line_60_negative",
    ),
    # Line 60 of Part 3 is exactly 0 ("positive or 0": line 99 = line 59) and line 53 is 0.06.
    pytest.param(
        "30000",
        "40000",
        "1695",
        "2432.81",
        "0",
        "0",
        {
            "part_3_line_49": "3462.81",
            "part_3_line_52": "3462.75",
            "part_3_line_53": "0.06",
            "part_3_line_56": "665.00",
            "part_3_line_59": "665.00",
            "part_3_line_60": "0.00",
            "part_3_line_61": "0.06",
            "part_3_line_64": "0",
            "part_3_line_67": "0.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "3462.75",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3462.75",
            "97": "0",
            "98": "3462.75",
            "99": "665.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "665.00",
            "104_difference": "0.00",
            "104": "0",
            "105": "665.00",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "665.00",
        },
        id="line_53_positive_and_line_60_zero",
    ),
    # Line 53 of Part 3 is -0.01 (negative: line 92 = line 49, line 93 = 0.01 and line 95 = 0.01)
    # and line 60 is exactly 0: line 94 = 0 (line 60 is not positive).
    pytest.param(
        "30000",
        "40000",
        "1695.13",
        "2432.61",
        "0",
        "0",
        {
            "part_3_line_49": "3462.74",
            "part_3_line_52": "3462.75",
            "part_3_line_53": "-0.01",
            "part_3_line_56": "665.00",
            "part_3_line_59": "665.00",
            "part_3_line_60": "0.00",
            "part_3_line_61": "-0.01",
            "part_3_line_64": "0",
            "part_3_line_67": "0.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "3462.74",
            "93": "0.01",
            "94": "0",
            "95": "0.01",
            "96": "3462.74",
            "97": "0",
            "98": "3462.74",
            "99": "665.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "665.00",
            "104_difference": "0.00",
            "104": "0",
            "105": "665.00",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "665.00",
        },
        id="line_53_negative_by_a_cent_and_line_60_zero",
    ),
    # Line 53 of Part 3 is exactly 0 and line 60 is 0.01 (positive): line 92 = line 52 and line 94 =
    # 0 (line 53 is not negative).
    pytest.param(
        "30000",
        "40000",
        "1695.79",
        "2431.97",
        "0",
        "0",
        {
            "part_3_line_49": "3462.75",
            "part_3_line_52": "3462.75",
            "part_3_line_53": "0.00",
            "part_3_line_56": "665.01",
            "part_3_line_59": "665.00",
            "part_3_line_60": "0.01",
            "part_3_line_61": "0.01",
            "part_3_line_64": "0",
            "part_3_line_67": "0.00",
            "part_3_line_68": "0.00",
        },
        {
            "92": "3462.75",
            "93": "0",
            "94": "0",
            "95": "0",
            "96": "3462.75",
            "97": "0",
            "98": "3462.75",
            "99": "665.00",
            "100": "0",
            "101": "0",
            "102": "0",
            "103": "665.00",
            "104_difference": "0.00",
            "104": "0",
            "105": "665.00",
            "106": "0.00",
            "107": "0",
            "108": "0",
            "109": "0.00",
            "110": "665.00",
        },
        id="line_53_zero_and_line_60_positive_by_a_cent",
    ),
]


@pytest.mark.parametrize(
    (
        "line_1",
        "line_2",
        "box_16",
        "box_17",
        "box_16a",
        "box_17a",
        "upstream",
        "expected",
    ),
    PART_4_EMPLOYMENT_CASES,
)
def test_return_bo_part_4_lines_92_to_110(
    line_1: str,
    line_2: str,
    box_16: str,
    box_17: str,
    box_16a: str,
    box_17a: str,
    upstream: dict[str, str],
    expected: dict[str, str],
) -> None:
    worksheet = return_bo(line_1, line_2, box_16, box_17, line_25=box_16a, line_45=box_17a)

    part_3_kinds = {
        "part_3_line_49": RC381_PART_3_LINE_49,
        "part_3_line_52": RC381_PART_3_LINE_52,
        "part_3_line_53": RC381_PART_3_LINE_53,
        "part_3_line_56": RC381_PART_3_LINE_56,
        "part_3_line_59": RC381_PART_3_LINE_59,
        "part_3_line_60": RC381_PART_3_LINE_60,
        "part_3_line_61": RC381_PART_3_LINE_61,
        "part_3_line_64": RC381_PART_3_LINE_64,
        "part_3_line_67": RC381_PART_3_LINE_67,
        "part_3_line_68": RC381_PART_3_LINE_68,
    }
    assert {key: worksheet.get(kind).value for key, kind in part_3_kinds.items()} == {
        key: D(value) for key, value in upstream.items()
    }
    assert part_4_employment(worksheet) == {line: D(value) for line, value in expected.items()}


@pytest.mark.parametrize(
    ("line_1", "line_2", "box_16", "box_17", "box_16a", "box_17a", "upstream", "expected"),
    PART_4_EMPLOYMENT_CASES,
)
def test_return_bo_part_4_lines_92_to_110_are_part_3b_lines_75_to_93(
    line_1: str,
    line_2: str,
    box_16: str,
    box_17: str,
    box_16a: str,
    box_17a: str,
    upstream: dict[str, str],
    expected: dict[str, str],
) -> None:
    # Part 4's lines 92 to 110 are the same procedure as Part 3b's lines 75 to 93 on the same Part 3
    # totals (line 98 is line 81 and line 110 is line 93), whatever the sign of line 69 (Part 3b is
    # computed for every return).
    worksheet = return_bo(line_1, line_2, box_16, box_17, line_25=box_16a, line_45=box_17a)

    part_3b_lines = part_3b(worksheet)
    assert part_4_employment(worksheet) == {
        line: part_3b_lines[PART_3B_OF_PART_4[line]] for line in PART_4_EMPLOYMENT_KINDS
    }


# Part 4, lines 111 to 129 (the base contributions through self-employment income and other
# earnings, line 111 being the amount for line 31000 of the return, and the deduction for the
# enhanced contributions on them, line 129, the amount for line 22200). They read the required
# contributions of lines 84, 85 and 86 (on lines 70 and 83) and line 69 of Part 3 (line 114 "if
# positive"); lines 117, 119, 120, 122, 123 and 126 only copy another line, so they are not
# listed. "116_lesser" is the amount lettered A, "Enter whichever is less: amount from line 113 or
# line 114.", that line 116 multiplies by 83.1933% and line 118 takes line 117 from. Lines 121 and
# 124 print no floor, so a cent of rounding can make them negative.
PART_4_SELF_EMPLOYMENT_KINDS: dict[str, ArtifactKind[Decimal]] = {
    "111": RC381_PART_4_LINE_111,
    "112": RC381_PART_4_LINE_112,
    "113": RC381_PART_4_LINE_113,
    "114": RC381_PART_4_LINE_114,
    "115": RC381_PART_4_LINE_115,
    "116_lesser": RC381_PART_4_LINE_116_LESSER,
    "116": RC381_PART_4_LINE_116,
    "118": RC381_PART_4_LINE_118,
    "121": RC381_PART_4_LINE_121,
    "124": RC381_PART_4_LINE_124,
    "125": RC381_PART_4_LINE_125,
    "127": RC381_PART_4_LINE_127,
    "128": RC381_PART_4_LINE_128,
    "129": RC381_PART_4_LINE_129,
}


def part_4_self_employment(worksheet: Worksheet) -> dict[str, Decimal]:
    """Part 4's lines 111 to 129 of `worksheet`, by line number (see
    `PART_4_SELF_EMPLOYMENT_KINDS`)."""
    return {line: worksheet.get(kind).value for line, kind in PART_4_SELF_EMPLOYMENT_KINDS.items()}


# The final selection after Part 3 and Part 4: "earnings_subject_to_contributions" is lines 70 and
# 83 of Part 4 added, and the six results are the amounts RC381 gives for lines 30800, 22215,
# 44800, 42100, 31000 and 22200 of the return: Part 4's lines 98, 110, 91, 90 (when positive), 111
# and 129 when the earnings are above zero, else Part 3's results ("return to Part 3") and "0".
FINAL_SELECTION_KINDS: dict[str, ArtifactKind[Decimal]] = {
    "earnings_subject_to_contributions": RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
    "line_30800": RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    "line_22215": RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    "line_44800": RC381_CPP_OVERPAYMENT_ON_RETURN,
    "line_42100": RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    "line_31000": RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    "line_22200": RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
}


def final_selection(worksheet: Worksheet) -> dict[str, Decimal]:
    """The earnings subject to contributions and the six results of `worksheet`, by line (see
    `FINAL_SELECTION_KINDS`)."""
    return {line: worksheet.get(kind).value for line, kind in FINAL_SELECTION_KINDS.items()}


def test_return_bo_part_4_lines_111_to_129_match_the_tickets_example() -> None:
    # Return BO: lines 84, 85 and 86 are 128.70, 26.00 and 792.00 (lines 70 and 83 of 1,300.00 and
    # 9,900.00). Line 111 = 128.70 x 50% = 64.35, line 112 = 26.00 x 50% = 13.00, line 113 =
    # 77.35. Line 69 of Part 3 (157.25) is positive: line 114 = 157.25, line 115 = 77.35 less 157.25
    # = -79.90 (in brackets). A = the lesser of 77.35 and 157.25 = 77.35; line 116 = 77.35 x
    # 83.1933% = 64.349... = 64.35, line 118 = 77.35 less 64.35 = 13.00 (line 117 is line 116),
    # line 121 = 64.35 less 64.35 = 0.00 and line 124 = 13.00 less 13.00 = 0.00. Line 125 = 792.00
    # x 50% = 396.00; line 115 is negative, so line 127 = 79.90 and line 128 = 396.00 less 79.90 =
    # 316.10. Line 129 = 0.00 + 13.00 + 0.00 + 396.00 + 316.10 = 725.10 (line 122 is line 112).
    worksheet = return_bo()

    assert worksheet.get(RC381_PART_3_LINE_69).value == D("157.25")
    assert worksheet.get(RC381_PART_4_LINE_84).value == D("128.70")
    assert worksheet.get(RC381_PART_4_LINE_85).value == D("26.00")
    assert worksheet.get(RC381_PART_4_LINE_86).value == D("792.00")
    assert part_4_self_employment(worksheet) == {
        "111": D("64.35"),
        "112": D("13.00"),
        "113": D("77.35"),
        "114": D("157.25"),
        "115": D("-79.90"),
        "116_lesser": D("77.35"),
        "116": D("64.35"),
        "118": D("13.00"),
        "121": D("0.00"),
        "124": D("0.00"),
        "125": D("396.00"),
        "127": D("79.90"),
        "128": D("316.10"),
        "129": D("725.10"),
    }


def test_return_bo_part_4_lines_111_112_and_125_round_half_up_to_the_cent() -> None:
    # Lines 84, 85 and 86 of 128.77, 26.01 and 79.95 (line 69 of Part 3 is 0): 128.77 x 50% =
    # 64.385, 26.01 x 50% = 13.005 and 79.95 x 50% = 39.975 are all ties, rounded up to 64.39,
    # 13.01 and 39.98 (half even gives 64.38, 13.00 and 39.98). Net self-employment income of 15:
    # line 84 = 1.49, so line 111 = 0.745, up to 0.75 (half even gives 0.74).
    ties = return_bo(
        line_19="1695.20", line_39="2432.55", cpt20_earnings="2000", cpt20_t4_earnings="300"
    )
    fifteen = return_bo(cpt20_earnings="0", cpt20_t4_earnings="0", net_partnership_income="15")

    assert ties.get(RC381_PART_4_LINE_84).value == D("128.77")
    assert ties.get(RC381_PART_4_LINE_85).value == D("26.01")
    assert ties.get(RC381_PART_4_LINE_86).value == D("79.95")
    assert ties.get(RC381_PART_4_LINE_111).value == D("64.39")
    assert ties.get(RC381_PART_4_LINE_112).value == D("13.01")
    assert ties.get(RC381_PART_4_LINE_125).value == D("39.98")
    assert fifteen.get(RC381_PART_4_LINE_84).value == D("1.49")
    assert fifteen.get(RC381_PART_4_LINE_111).value == D("0.75")
    assert fifteen.get(RC381_PART_4_LINE_116).value == D("0.75")


def test_return_bo_part_4_line_114_is_line_69_of_part_3_only_when_that_is_positive() -> None:
    # Line 69 of Part 3 of 157.25 (the ticket's example): line 114 = 157.25. Line 69 of 0 or of
    # -1,627.75: line 114 = "0" ("Enter the amount from line 69 of Part 3 if positive. If not,
    # enter "0"."), A = 0 and line 115 = line 113 (positive).
    positive = return_bo()
    zero = return_bo(
        line_19="1695.20", line_39="2432.55", cpt20_earnings="2000", cpt20_t4_earnings="300"
    )
    negative = return_bo(
        line_1="30000",
        line_2="40000",
        line_19="0",
        line_39="2500",
        cpt20_earnings="2000",
        cpt20_t4_earnings="300",
    )

    assert positive.get(RC381_PART_3_LINE_69).value == D("157.25")
    assert positive.get(RC381_PART_4_LINE_114).value == D("157.25")
    assert zero.get(RC381_PART_3_LINE_69).value == D("0")
    assert zero.get(RC381_PART_4_LINE_114).value == D("0")
    assert zero.get(RC381_PART_4_LINE_115).value == D("77.40")
    assert negative.get(RC381_PART_3_LINE_69).value == D("-1627.75")
    assert negative.get(RC381_PART_4_LINE_114).value == D("0")
    assert negative.get(RC381_PART_4_LINE_113).value == D("136.85")
    assert negative.get(RC381_PART_4_LINE_115).value == D("136.85")
    assert negative.get(RC381_PART_4_LINE_116_LESSER).value == D("0")
    assert negative.get(RC381_PART_4_LINE_116).value == D("0.00")
    assert negative.get(RC381_PART_4_LINE_121).value == D("113.85")
    assert negative.get(RC381_PART_4_LINE_124).value == D("23.00")


def test_return_bo_part_4_a_is_the_lesser_of_line_113_and_line_114() -> None:
    # Line 113 of 77.35 (the worked example) or 0.01 is less than line 114 (157.25 and
    # 2,827.78): A = line 113, line 116 is 83.1933% of it and line 118 the rest. Line 113 of 761.60
    # is more than line 114 (0.57): A = line 114 = 0.57, line 116 = 0.57 x 83.1933% = 0.47, line
    # 118 = 0.10, and line 121 = 633.60 less 0.47 = 633.13, line 124 = 128.00 less 0.10 = 127.90.
    ticket = return_bo()
    big_line_114 = return_bo(
        line_1="70000",
        line_2="50000",
        line_19="4175",
        line_39="3210",
        net_partnership_income="30000",
        cpt20_earnings="500",
        cpt20_t4_earnings="0",
    )
    small_line_114 = return_bo(
        line_1="28500", line_2="30000", line_19="1650", line_39="1750", net_partnership_income="300"
    )

    assert ticket.get(RC381_PART_4_LINE_116_LESSER).value == ticket.get(RC381_PART_4_LINE_113).value
    assert big_line_114.get(RC381_PART_4_LINE_113).value == D("0.01")
    assert big_line_114.get(RC381_PART_4_LINE_114).value == D("2827.78")
    assert big_line_114.get(RC381_PART_4_LINE_116_LESSER).value == D("0.01")
    assert big_line_114.get(RC381_PART_4_LINE_116).value == D("0.01")
    assert big_line_114.get(RC381_PART_4_LINE_118).value == D("0.00")
    assert small_line_114.get(RC381_PART_4_LINE_113).value == D("761.60")
    assert small_line_114.get(RC381_PART_4_LINE_114).value == D("0.57")
    assert small_line_114.get(RC381_PART_4_LINE_116_LESSER).value == D("0.57")
    assert small_line_114.get(RC381_PART_4_LINE_116).value == D("0.47")
    assert small_line_114.get(RC381_PART_4_LINE_118).value == D("0.10")
    assert small_line_114.get(RC381_PART_4_LINE_121).value == D("633.13")
    assert small_line_114.get(RC381_PART_4_LINE_124).value == D("127.90")


def test_return_bo_part_4_line_121_is_negative_when_line_116_is_a_cent_more_than_line_111() -> None:
    # An election of 0.25 gives line 70 = 0.25, line 84 = 0.02 and line 85 = 0.01 (0.005 up), so
    # line 111 = 0.01, line 112 = 0.01 (0.005 up) and A = line 113 = 0.02. Line 116 = 0.02 x
    # 83.1933% = 0.0166, up to 0.02, so line 121 = 0.01 less 0.02 = -0.01: the form prints no floor
    # on lines 121 and 124 and neither does the engine. Line 118 = 0.00, line 124 = 0.01 less 0.00
    # = 0.01, and line 129 = -0.01 + 0.01 + 0.01 + 0.00 + 0.00 = 0.01 (line 121 + line 124 = line
    # 113 less A, never negative).
    worksheet = return_bo(cpt20_earnings="0.25", cpt20_t4_earnings="0")

    assert part_4_self_employment(worksheet) == {
        "111": D("0.01"),
        "112": D("0.01"),
        "113": D("0.02"),
        "114": D("157.25"),
        "115": D("-157.23"),
        "116_lesser": D("0.02"),
        "116": D("0.02"),
        "118": D("0.00"),
        "121": D("-0.01"),
        "124": D("0.01"),
        "125": D("0.00"),
        "127": D("157.23"),
        "128": D("0"),
        "129": D("0.01"),
    }


def test_return_bo_part_4_lines_127_and_128_take_a_negative_line_115_off_line_125() -> None:
    # A negative line 115 (-79.90, -2.99) is entered as a positive amount on line 127; line 128 =
    # line 125 less line 127 (396.00 less 79.90 = 316.10; 360.00 less 2.99 = 357.01). When line 127
    # (460.86) is more than line 125 (96.00) the difference is negative and line 128 is entered
    # as "0". When line 115 is "0" or positive the form enters line 126 (line 125) on line 128:
    # line 127 is 0 and line 128 = line 125 (32.00 for a line 115 of exactly 0).
    ticket = return_bo()
    only_83 = return_bo(
        line_1="70000",
        line_2="1500",
        line_19="3183.79",
        line_39="100.32",
        line_25="767.38",
        cpt20_earnings="4500",
        cpt20_t4_earnings="0",
        net_partnership_income="4500",
    )
    floored = return_bo(
        line_1="71300",
        line_2="7500",
        line_19="4034",
        line_39="490",
        line_45="300",
        net_partnership_income="1.07",
    )
    zero = return_bo(
        line_1="71300",
        line_2="80000",
        line_19="1800",
        line_39="2432",
        cpt20_earnings="500",
        cpt20_t4_earnings="0",
        net_partnership_income="300",
    )

    assert ticket.get(RC381_PART_4_LINE_115).value == D("-79.90")
    assert ticket.get(RC381_PART_4_LINE_127).value == D("79.90")
    assert ticket.get(RC381_PART_4_LINE_128).value == D("316.10")
    assert only_83.get(RC381_PART_4_LINE_115).value == D("-2.99")
    assert only_83.get(RC381_PART_4_LINE_127).value == D("2.99")
    assert only_83.get(RC381_PART_4_LINE_125).value == D("360.00")
    assert only_83.get(RC381_PART_4_LINE_128).value == D("357.01")
    assert floored.get(RC381_PART_4_LINE_125).value == D("96.00")
    assert floored.get(RC381_PART_4_LINE_127).value == D("460.86")
    assert floored.get(RC381_PART_4_LINE_128).value == D("0")
    assert floored.get(RC381_PART_4_LINE_129).value == D("96.00")
    assert zero.get(RC381_PART_4_LINE_115).value == D("0")
    assert zero.get(RC381_PART_4_LINE_127).value == D("0")
    assert zero.get(RC381_PART_4_LINE_125).value == D("32.00")
    assert zero.get(RC381_PART_4_LINE_128).value == D("32.00")


def test_return_bo_part_4_with_no_t4_slips_gives_schedule_8_part_4s_amounts() -> None:
    # Net self-employment income of 80,000 and no T4 slip: nothing is paid on employment income, so
    # line 114 and A are 0 and lines 121 and 124 are lines 111 and 112; line 129 = 111 + 2 x 112 +
    # 2 x 125 = 3,356.10 + 1,356.00 + 696.00. These are Schedule 8 Part 4's line 15 (the base
    # credit), line 17 (the deduction) and line 14 (the contributions payable) on the same income,
    # which Schedule 8 computes on its own (Part 4 of Schedule 8 is in the return, not in the form,
    # so the return's worksheet has them whichever of the two forms the return carries).
    no_t4_slips: dict[str, Any] = dict(
        line_1="0",
        line_2="0",
        line_19="0",
        line_39="0",
        cpt20_earnings="0",
        cpt20_t4_earnings="0",
        net_partnership_income="80000",
    )
    worksheet = return_bo(**no_t4_slips)
    on_return = return_bo(form="ca-on/return", **no_t4_slips)

    assert worksheet.get(RC381_PART_4_LINE_114).value == D("0")
    assert worksheet.get(RC381_PART_4_LINE_116_LESSER).value == D("0")
    assert worksheet.get(RC381_PART_4_LINE_111).value == D("3356.10")
    assert worksheet.get(RC381_PART_4_LINE_129).value == D("5408.10")
    assert (
        worksheet.get(RC381_PART_4_LINE_111).value
        == on_return.get(SELF_EMPLOYED_CPP_BASE_CREDIT).value
    )
    assert (
        worksheet.get(RC381_PART_4_LINE_129).value
        == on_return.get(SELF_EMPLOYED_CPP_DEDUCTION).value
    )
    assert (
        worksheet.get(RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS).value
        == on_return.get(SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE).value
    )


def test_return_bo_the_final_selection_takes_part_4_when_lines_70_and_83_are_above_zero() -> None:
    # Return BO: lines 70 and 83 of Part 4 (1,300.00 and 9,900.00) added are 11,200.00, above zero,
    # so each result is Part 4's: line 30800 = line 98 (3,462.75), line 22215 = line 110 (665.00),
    # line 44800 = line 91 (0.00: Part 4 sets line 69 of Part 3 against the required contributions
    # on lines 84 to 86), line 42100 = line 90 (632.20), line 31000 = line 111 (64.35) and line
    # 22200 = line 129 (725.10). Part 3a gave 3,462.75, 665.00 and 157.25 for the first three.
    worksheet = return_bo()

    assert final_selection(worksheet) == {
        "earnings_subject_to_contributions": D("11200.00"),
        "line_30800": D("3462.75"),
        "line_22215": D("665.00"),
        "line_44800": D("0.00"),
        "line_42100": D("632.20"),
        "line_31000": D("64.35"),
        "line_22200": D("725.10"),
    }
    assert results(worksheet) == (D("3462.75"), D("665.00"), D("157.25"))
    assert (
        worksheet.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value
        == worksheet.get(RC381_PART_4_LINE_98).value
    )
    assert (
        worksheet.get(RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value
        == worksheet.get(RC381_PART_4_LINE_110).value
    )
    assert (
        worksheet.get(RC381_CPP_OVERPAYMENT_ON_RETURN).value
        == worksheet.get(RC381_PART_4_LINE_91).value
    )
    assert (
        worksheet.get(RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT).value
        == worksheet.get(RC381_PART_4_LINE_90).value
    )
    assert (
        worksheet.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value
        == worksheet.get(RC381_PART_4_LINE_111).value
    )
    assert (
        worksheet.get(RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value
        == worksheet.get(RC381_PART_4_LINE_129).value
    )


def test_return_bo_the_final_selection_returns_to_part_3_when_lines_70_and_83_are_zero() -> None:
    # No election and no self-employment income: lines 70 and 83 of Part 4 are both "0" ("If lines
    # 70 and 83 are both "0", return to Part 3"), so lines 30800, 22215 and 44800 are Part 3a's
    # (3,462.75, 665.00 and 157.25, line 69 being positive) and lines 42100, 31000 and 22200 are
    # "0". Part 4's own lines 98 and 110 are 3,462.75 and 665.00 too, but its line 91 (157.25) and
    # lines 111 to 129 are not used.
    worksheet = return_bo(cpt20_earnings="0", cpt20_t4_earnings="0")

    assert final_selection(worksheet) == {
        "earnings_subject_to_contributions": D("0"),
        "line_30800": D("3462.75"),
        "line_22215": D("665.00"),
        "line_44800": D("157.25"),
        "line_42100": D("0"),
        "line_31000": D("0"),
        "line_22200": D("0"),
    }
    assert results(worksheet) == (D("3462.75"), D("665.00"), D("157.25"))
    assert (
        worksheet.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value
        == worksheet.get(RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS).value
    )
    assert (
        worksheet.get(RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value
        == worksheet.get(RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS).value
    )
    assert (
        worksheet.get(RC381_CPP_OVERPAYMENT_ON_RETURN).value
        == worksheet.get(RC381_CPP_OVERPAYMENT).value
    )


def test_return_bo_the_final_selection_takes_part_4_for_earnings_of_one_cent() -> None:
    # Net self-employment income of 0.01: line 70 = 0.01 and line 83 = 0, so the earnings subject
    # to contributions are 0.01, above zero, and Part 4 is used although every contribution on
    # them rounds to 0.00: line 42100 is "0" (line 90 is negative), lines 31000 and 22200 are 0.00,
    # and lines 30800, 22215 and 44800 are Part 4's lines 98, 110 and 91.
    worksheet = return_bo(cpt20_earnings="0", cpt20_t4_earnings="0", net_partnership_income="0.01")

    assert final_selection(worksheet) == {
        "earnings_subject_to_contributions": D("0.01"),
        "line_30800": D("3462.75"),
        "line_22215": D("665.00"),
        "line_44800": D("157.25"),
        "line_42100": D("0"),
        "line_31000": D("0.00"),
        "line_22200": D("0.00"),
    }


def test_return_bo_the_final_selection_returns_to_part_3_when_line_70_is_below_zero() -> None:
    # Line 70 prints no floor: with net self-employment income of 500 against an unused exemption of
    # 1,000.00 it is -500.00 and line 83 is 0, so the earnings subject to contributions are not
    # above zero and the form's "return to Part 3" applies (line 69 of Part 3 is positive: Part 3a,
    # whose line 70 and line 73 are 0.00 here and line 74 is 127.15). With line 69 of Part 3
    # equal to 0 (net income 5, line 70 = -995.00) Part 3b applies, which has no overpayment.
    positive = return_bo(
        line_1="1500",
        line_2="1000",
        line_19="50.18",
        line_39="4.41",
        line_25="40",
        line_45="32.56",
        net_partnership_income="500",
        cpt20_earnings="0",
        cpt20_t4_earnings="0",
    )
    zero = return_bo(
        line_1="1000",
        line_2="1500",
        line_19="0",
        line_39="0",
        net_partnership_income="5",
        cpt20_earnings="0",
        cpt20_t4_earnings="0",
    )

    assert positive.get(RC381_PART_4_LINE_70).value == D("-500.00")
    assert positive.get(RC381_PART_4_LINE_83).value == D("0")
    assert final_selection(positive) == {
        "earnings_subject_to_contributions": D("-500.00"),
        "line_30800": D("0.00"),
        "line_22215": D("0.00"),
        "line_44800": D("127.15"),
        "line_42100": D("0"),
        "line_31000": D("0"),
        "line_22200": D("0"),
    }
    assert results(positive) == (D("0.00"), D("0.00"), D("127.15"))
    assert zero.get(RC381_PART_4_LINE_70).value == D("-995.00")
    assert final_selection(zero) == {
        "earnings_subject_to_contributions": D("-995.00"),
        "line_30800": D("0.00"),
        "line_22215": D("0.00"),
        "line_44800": D("0"),
        "line_42100": D("0"),
        "line_31000": D("0"),
        "line_22200": D("0"),
    }
    assert results(zero) == (D("0.00"), D("0.00"), D("0"))


# Each case: the inputs of `return_bo` it changes, the lines of Part 3 and Part 4 that lines 111 to
# 129 read (line 69 of Part 3, lines 70, 83, 84, 85 and 86), Part 4's lines 111 to 129 and the
# final selection. The figures are proved by an independent Decimal model of the printed form (not
# by this engine). The cases vary the sign of line 69 of Part 3 and of line 115, which of lines 113
# and 114 is the lesser (A), whether line 127 is more than line 125, rounding ties and the earnings
# subject to contributions above, at and below zero.
PART_4_SELF_EMPLOYMENT_CASES = [
    # The example of Return BO: the CPT20 election gives line 4 = 12,500, line 70 = 1,300.00 and
    # line 83 = 9,900.00, so lines 70 and 83 added are 11,200.00 and Part 4 is used. Line 69 of Part
    # 3 (157.25) is positive: line 114 = 157.25 and line 115 = 77.35 less 157.25 = -79.90
    # (negative); A is line 113 (77.35), the lesser; line 116 = 77.35 x 83.1933% = 64.349... =
    # 64.35, so lines 118, 121 and 124 are 13.00, 0.00 and 0.00; line 127 = 79.90 and line 128 =
    # 396.00 less 79.90 = 316.10.
    pytest.param(
        {},
        {
            "part_3_line_69": "157.25",
            "part_4_line_70": "1300.00",
            "part_4_line_83": "9900.00",
            "part_4_line_84": "128.70",
            "part_4_line_85": "26.00",
            "part_4_line_86": "792.00",
        },
        {
            "111": "64.35",
            "112": "13.00",
            "113": "77.35",
            "114": "157.25",
            "115": "-79.90",
            "116_lesser": "77.35",
            "116": "64.35",
            "118": "13.00",
            "121": "0.00",
            "124": "0.00",
            "125": "396.00",
            "127": "79.90",
            "128": "316.10",
            "129": "725.10",
        },
        {
            "earnings_subject_to_contributions": "11200.00",
            "line_30800": "3462.75",
            "line_22215": "665.00",
            "line_44800": "0.00",
            "line_42100": "632.20",
            "line_31000": "64.35",
            "line_22200": "725.10",
        },
        id="ticket_example",
    ),
    # Line 4 is 0, so lines 70 and 83 are 0 and the form returns to Part 3: the results are Part
    # 3a's (3,462.75, 665.00 and 157.25) and "0" for lines 42100, 31000 and 22200. Part 4's lines
    # are still computed: lines 111 to 113 are 0.00, line 115 = -157.25 and line 128 = 0.00 less
    # 157.25, entered as "0".
    pytest.param(
        {"cpt20_earnings": "0", "cpt20_t4_earnings": "0"},
        {
            "part_3_line_69": "157.25",
            "part_4_line_70": "0",
            "part_4_line_83": "0",
            "part_4_line_84": "0.00",
            "part_4_line_85": "0.00",
            "part_4_line_86": "0.00",
        },
        {
            "111": "0.00",
            "112": "0.00",
            "113": "0.00",
            "114": "157.25",
            "115": "-157.25",
            "116_lesser": "0.00",
            "116": "0.00",
            "118": "0.00",
            "121": "0.00",
            "124": "0.00",
            "125": "0.00",
            "127": "157.25",
            "128": "0",
            "129": "0.00",
        },
        {
            "earnings_subject_to_contributions": "0",
            "line_30800": "3462.75",
            "line_22215": "665.00",
            "line_44800": "157.25",
            "line_42100": "0",
            "line_31000": "0",
            "line_22200": "0",
        },
        id="no_election_and_no_self_employment_income",
    ),
    # Line 70 is 0.01: lines 70 and 83 added are above zero, so Part 4 is used although every line
    # from 84 on is 0.00 (0.01 x 9.9% is 0.00 to the cent). The results are Part 4's lines 98, 110
    # and 91 (the same 3,462.75, 665.00 and 157.25 as Part 3a), 0 for line 42100 (line 90 is
    # negative) and 0.00 for lines 31000 and 22200.
    pytest.param(
        {"cpt20_earnings": "0", "cpt20_t4_earnings": "0", "net_partnership_income": "0.01"},
        {
            "part_3_line_69": "157.25",
            "part_4_line_70": "0.01",
            "part_4_line_83": "0",
            "part_4_line_84": "0.00",
            "part_4_line_85": "0.00",
            "part_4_line_86": "0.00",
        },
        {
            "111": "0.00",
            "112": "0.00",
            "113": "0.00",
            "114": "157.25",
            "115": "-157.25",
            "116_lesser": "0.00",
            "116": "0.00",
            "118": "0.00",
            "121": "0.00",
            "124": "0.00",
            "125": "0.00",
            "127": "157.25",
            "128": "0",
            "129": "0.00",
        },
        {
            "earnings_subject_to_contributions": "0.01",
            "line_30800": "3462.75",
            "line_22215": "665.00",
            "line_44800": "157.25",
            "line_42100": "0",
            "line_31000": "0.00",
            "line_22200": "0.00",
        },
        id="net_self_employment_income_of_one_cent",
    ),
    # Line 70 is 15.00: line 84 = 1.49 (15.00 x 9.9% = 1.485, up) and line 85 = 0.30. Line 111 =
    # 1.49 x 50% = 0.745, a tie, up to 0.75 (half even gives 0.74), line 112 = 0.15, line 113 =
    # 0.90; line 114 = 157.25 so A = 0.90, line 116 = 0.90 x 83.1933% = 0.7487 = 0.75 and lines 118,
    # 121 and 124 are 0.15, 0.00 and 0.00.
    pytest.param(
        {"cpt20_earnings": "0", "cpt20_t4_earnings": "0", "net_partnership_income": "15"},
        {
            "part_3_line_69": "157.25",
            "part_4_line_70": "15",
            "part_4_line_83": "0",
            "part_4_line_84": "1.49",
            "part_4_line_85": "0.30",
            "part_4_line_86": "0.00",
        },
        {
            "111": "0.75",
            "112": "0.15",
            "113": "0.90",
            "114": "157.25",
            "115": "-156.35",
            "116_lesser": "0.90",
            "116": "0.75",
            "118": "0.15",
            "121": "0.00",
            "124": "0.00",
            "125": "0.00",
            "127": "156.35",
            "128": "0",
            "129": "0.15",
        },
        {
            "earnings_subject_to_contributions": "15",
            "line_30800": "3462.75",
            "line_22215": "665.00",
            "line_44800": "156.36",
            "line_42100": "0",
            "line_31000": "0.75",
            "line_22200": "0.15",
        },
        id="net_self_employment_income_of_15",
    ),
    # Line 70 is 0.25: line 84 = 0.02 and line 85 = 0.01 (0.005 up), so line 111 = 0.01 and line 112
    # = 0.01 (0.005 up), line 113 = 0.02 and A = 0.02. Line 116 = 0.02 x 83.1933% = 0.0166 = 0.02,
    # so line 121 = 0.01 less 0.02 = -0.01 (the form prints no floor) and line 124 = 0.01 less line
    # 118 (0.00) = 0.01; line 129 = -0.01 + 0.01 + 0.01 + 0.00 + 0.00 = 0.01.
    pytest.param(
        {"cpt20_earnings": "0.25", "cpt20_t4_earnings": "0"},
        {
            "part_3_line_69": "157.25",
            "part_4_line_70": "0.25",
            "part_4_line_83": "0",
            "part_4_line_84": "0.02",
            "part_4_line_85": "0.01",
            "part_4_line_86": "0.00",
        },
        {
            "111": "0.01",
            "112": "0.01",
            "113": "0.02",
            "114": "157.25",
            "115": "-157.23",
            "116_lesser": "0.02",
            "116": "0.02",
            "118": "0.00",
            "121": "-0.01",
            "124": "0.01",
            "125": "0.00",
            "127": "157.23",
            "128": "0",
            "129": "0.01",
        },
        {
            "earnings_subject_to_contributions": "0.25",
            "line_30800": "3462.75",
            "line_22215": "665.00",
            "line_44800": "157.24",
            "line_42100": "0",
            "line_31000": "0.01",
            "line_22200": "0.01",
        },
        id="election_of_a_quarter_makes_line_121_negative",
    ),
    # Line 69 of Part 3 is 0, so line 114 is 0, A is 0 and line 115 = line 113 (77.40, positive).
    # Line 84 = 128.77, line 85 = 26.01 and line 86 = 79.95: lines 111 = 64.385, 112 = 13.005 and
    # 125 = 39.975 are ties, up to 64.39, 13.01 and 39.98 (half even gives 64.38, 13.00 and 39.98).
    # Line 127 is 0 and line 128 = line 125; line 129 = 64.39 + 13.01 + 13.01 + 39.98 + 39.98 less
    # nothing = 170.37.
    pytest.param(
        {
            "line_19": "1695.20",
            "line_39": "2432.55",
            "cpt20_earnings": "2000",
            "cpt20_t4_earnings": "300",
        },
        {
            "part_3_line_69": "0.00",
            "part_4_line_70": "1300.66",
            "part_4_line_83": "999.34",
            "part_4_line_84": "128.77",
            "part_4_line_85": "26.01",
            "part_4_line_86": "79.95",
        },
        {
            "111": "64.39",
            "112": "13.01",
            "113": "77.40",
            "114": "0",
            "115": "77.40",
            "116_lesser": "0",
            "116": "0.00",
            "118": "0.00",
            "121": "64.39",
            "124": "13.01",
            "125": "39.98",
            "127": "0",
            "128": "39.98",
            "129": "170.37",
        },
        {
            "earnings_subject_to_contributions": "2300.00",
            "line_30800": "3462.75",
            "line_22215": "665.00",
            "line_44800": "0.00",
            "line_42100": "234.73",
            "line_31000": "64.39",
            "line_22200": "170.37",
        },
        id="line_69_zero_and_the_halves_are_ties",
    ),
    # Line 69 of Part 3 is negative (-1,627.75): line 114 = 0 (only a positive line 69 counts) and
    # line 115 = line 113 (136.85), A = 0 so lines 116 and 118 are 0.00, lines 121 and 124 are lines
    # 111 and 112 and line 128 = line 125 (0.00; line 83 is 0).
    pytest.param(
        {
            "line_1": "30000",
            "line_2": "40000",
            "line_19": "0",
            "line_39": "2500",
            "cpt20_earnings": "2000",
            "cpt20_t4_earnings": "300",
        },
        {
            "part_3_line_69": "-1627.75",
            "part_4_line_70": "2300",
            "part_4_line_83": "0",
            "part_4_line_84": "227.70",
            "part_4_line_85": "46.00",
            "part_4_line_86": "0.00",
        },
        {
            "111": "113.85",
            "112": "23.00",
            "113": "136.85",
            "114": "0",
            "115": "136.85",
            "116_lesser": "0",
            "116": "0.00",
            "118": "0.00",
            "121": "113.85",
            "124": "23.00",
            "125": "0.00",
            "127": "0",
            "128": "0.00",
            "129": "159.85",
        },
        {
            "earnings_subject_to_contributions": "2300",
            "line_30800": "2109.38",
            "line_22215": "390.62",
            "line_44800": "0.00",
            "line_42100": "273.70",
            "line_31000": "113.85",
            "line_22200": "159.85",
        },
        id="line_69_negative",
    ),
    # Line 69 of Part 3 is 0.57, less than line 113 (761.60): A is line 114, line 115 = 761.03 is
    # positive, so line 127 is 0 and line 128 = line 125 (0.00; line 83 is 0). Line 116 = 0.57 x
    # 83.1933% = 0.47, line 118 = 0.10, line 121 = 633.13 and line 124 = 127.90.
    pytest.param(
        {
            "line_1": "28500",
            "line_2": "30000",
            "line_19": "1650",
            "line_39": "1750",
            "net_partnership_income": "300",
        },
        {
            "part_3_line_69": "0.57",
            "part_4_line_70": "12799.89",
            "part_4_line_83": "0",
            "part_4_line_84": "1267.19",
            "part_4_line_85": "256.00",
            "part_4_line_86": "0.00",
        },
        {
            "111": "633.60",
            "112": "128.00",
            "113": "761.60",
            "114": "0.57",
            "115": "761.03",
            "116_lesser": "0.57",
            "116": "0.47",
            "118": "0.10",
            "121": "633.13",
            "124": "127.90",
            "125": "0.00",
            "127": "0",
            "128": "0",
            "129": "889.03",
        },
        {
            "earnings_subject_to_contributions": "12799.89",
            "line_30800": "2849.43",
            "line_22215": "550.00",
            "line_44800": "0.00",
            "line_42100": "1522.05",
            "line_31000": "633.60",
            "line_22200": "889.03",
        },
        id="line_69_positive_and_line_113_more_than_line_114",
    ),
    # Net self-employment income of 30,000 on top of employment income of 120,000 with a large
    # overpayment (line 69 of Part 3 = 2,827.78): there is almost no room under the maximum, so line
    # 70 = 0.10 and line 113 = 0.01 is less than line 114, so A = line 113, line 116 = 0.01 (the
    # same as line 111) and lines 121 and 124 are 0.00. Line 115 = -2,827.77; line 125 is 0.00
    # (line 83 is 0), so line 128 is 0.00 and line 129 = 0.00.
    pytest.param(
        {
            "line_1": "70000",
            "line_2": "50000",
            "line_19": "4175",
            "line_39": "3210",
            "net_partnership_income": "30000",
            "cpt20_earnings": "500",
            "cpt20_t4_earnings": "0",
        },
        {
            "part_3_line_69": "2827.78",
            "part_4_line_70": "0.10",
            "part_4_line_83": "0",
            "part_4_line_84": "0.01",
            "part_4_line_85": "0.00",
            "part_4_line_86": "0.00",
        },
        {
            "111": "0.01",
            "112": "0.00",
            "113": "0.01",
            "114": "2827.78",
            "115": "-2827.77",
            "116_lesser": "0.01",
            "116": "0.01",
            "118": "0.00",
            "121": "0.00",
            "124": "0.00",
            "125": "0.00",
            "127": "2827.77",
            "128": "0",
            "129": "0.00",
        },
        {
            "earnings_subject_to_contributions": "0.10",
            "line_30800": "3483.22",
            "line_22215": "1074.00",
            "line_44800": "2827.78",
            "line_42100": "0",
            "line_31000": "0.01",
            "line_22200": "0.00",
        },
        id="line_113_less_than_a_large_line_114",
    ),
    # Line 70 is 0 and line 83 is 2,400.00, so line 86 = 192.00 and line 125 = 96.00, but line 69
    # of Part 3 (460.86) makes line 115 = -460.86 and line 127 = 460.86: line 126 less line 127 is
    # negative and line 128 is entered as "0". Line 129 = 96.00 (line 125 only; lines 111 to 124
    # are 0.00).
    pytest.param(
        {
            "line_1": "71300",
            "line_2": "7500",
            "line_19": "4034",
            "line_39": "490",
            "line_45": "300",
            "net_partnership_income": "1.07",
        },
        {
            "part_3_line_69": "460.86",
            "part_4_line_70": "0",
            "part_4_line_83": "2400.00",
            "part_4_line_84": "0.00",
            "part_4_line_85": "0.00",
            "part_4_line_86": "192.00",
        },
        {
            "111": "0.00",
            "112": "0.00",
            "113": "0.00",
            "114": "460.86",
            "115": "-460.86",
            "116_lesser": "0.00",
            "116": "0.00",
            "118": "0.00",
            "121": "0.00",
            "124": "0.00",
            "125": "96.00",
            "127": "460.86",
            "128": "0",
            "129": "96.00",
        },
        {
            "earnings_subject_to_contributions": "2400.00",
            "line_30800": "3385.14",
            "line_22215": "978.00",
            "line_44800": "364.86",
            "line_42100": "0",
            "line_31000": "0.00",
            "line_22200": "96.00",
        },
        id="line_128_is_zero_when_line_127_is_more_than_line_125",
    ),
    # Line 70 is 0 and line 83 is 9,000.00, so the lines added are above zero and Part 4 is used:
    # lines 84 and 85 are 0.00 (so lines 111 to 113 are 0.00 and line 31000 gets 0.00) and line 86 =
    # 720.00, line 125 = 360.00. Line 115 = -2.99 (line 114 = 2.99), line 127 = 2.99 and line 128 =
    # 360.00 less 2.99 = 357.01; line 129 = 717.01.
    pytest.param(
        {
            "line_1": "70000",
            "line_2": "1500",
            "line_19": "3183.79",
            "line_39": "100.32",
            "line_25": "767.38",
            "cpt20_earnings": "4500",
            "cpt20_t4_earnings": "0",
            "net_partnership_income": "4500",
        },
        {
            "part_3_line_69": "2.99",
            "part_4_line_70": "0",
            "part_4_line_83": "9000",
            "part_4_line_84": "0.00",
            "part_4_line_85": "0.00",
            "part_4_line_86": "720.00",
        },
        {
            "111": "0.00",
            "112": "0.00",
            "113": "0.00",
            "114": "2.99",
            "115": "-2.99",
            "116_lesser": "0.00",
            "116": "0.00",
            "118": "0.00",
            "121": "0.00",
            "124": "0.00",
            "125": "360.00",
            "127": "2.99",
            "128": "357.01",
            "129": "717.01",
        },
        {
            "earnings_subject_to_contributions": "9000",
            "line_30800": "3362.50",
            "line_22215": "686.00",
            "line_44800": "0.00",
            "line_42100": "714.02",
            "line_31000": "0.00",
            "line_22200": "717.01",
        },
        id="only_line_83_is_above_zero",
    ),
    # Line 70 is 0 and line 83 is 800.00; line 69 of Part 3 is negative so line 114 is 0, and lines
    # 111 to 113 are 0.00: line 115 is exactly 0 (positive or "0": line 127 is 0 and line 128 = line
    # 125 = 32.00). Line 129 = 64.00 less nothing... = 32.00 + 32.00 (line 125 once in line 128 and
    # once itself).
    pytest.param(
        {
            "line_1": "71300",
            "line_2": "80000",
            "line_19": "1800",
            "line_39": "2432",
            "cpt20_earnings": "500",
            "cpt20_t4_earnings": "0",
            "net_partnership_income": "300",
        },
        {
            "part_3_line_69": "-359.43",
            "part_4_line_70": "0",
            "part_4_line_83": "800",
            "part_4_line_84": "0.00",
            "part_4_line_85": "0.00",
            "part_4_line_86": "64.00",
        },
        {
            "111": "0.00",
            "112": "0.00",
            "113": "0.00",
            "114": "0",
            "115": "0.00",
            "116_lesser": "0.00",
            "116": "0.00",
            "118": "0.00",
            "121": "0.00",
            "124": "0.00",
            "125": "32.00",
            "127": "0",
            "128": "32.00",
            "129": "64.00",
        },
        {
            "earnings_subject_to_contributions": "800",
            "line_30800": "3517.43",
            "line_22215": "714.57",
            "line_44800": "0.00",
            "line_42100": "64.00",
            "line_31000": "0.00",
            "line_22200": "64.00",
        },
        id="line_115_is_zero_with_line_83_only",
    ),
    # Net self-employment income of 30,000 on top of the election with line 69 of Part 3 positive
    # (232.75): line 70 = 1,300.01 and line 83 = 9,900.00, so line 84 = 128.70 and A = line 113
    # (77.35); line 115 = -155.40, line 127 = 155.40 and line 128 = 396.00 less 155.40 = 240.60.
    pytest.param(
        {
            "line_1": "50000",
            "line_2": "20000",
            "line_19": "2975.00",
            "line_39": "1000",
            "line_45": "300",
            "net_partnership_income": "30000",
        },
        {
            "part_3_line_69": "232.75",
            "part_4_line_70": "1300.01",
            "part_4_line_83": "9900.00",
            "part_4_line_84": "128.70",
            "part_4_line_85": "26.00",
            "part_4_line_86": "792.00",
        },
        {
            "111": "64.35",
            "112": "13.00",
            "113": "77.35",
            "114": "232.75",
            "115": "-155.40",
            "116_lesser": "77.35",
            "116": "64.35",
            "118": "13.00",
            "121": "0.00",
            "124": "0.00",
            "125": "396.00",
            "127": "155.40",
            "128": "240.60",
            "129": "649.60",
        },
        {
            "earnings_subject_to_contributions": "11200.01",
            "line_30800": "3377.25",
            "line_22215": "665.00",
            "line_44800": "0.00",
            "line_42100": "481.20",
            "line_31000": "64.35",
            "line_22200": "649.60",
        },
        id="line_69_positive_and_self_employment_income_of_30000",
    ),
    # Net self-employment income of 80,000 and no T4 slip (no Part 3 figures): lines 84 and 85 stop
    # at their printed maximums (6,712.20 and 1,356.00), so line 111 = 3,356.10 and line 112 =
    # 678.00, and line 86 = 696.00 gives line 125 = 348.00. Line 114 is 0 so A = 0, and lines 121
    # and 124 are lines 111 and 112: line 129 = 3,356.10 + 678.00 + 678.00 + 348.00 + 348.00 =
    # 5,408.10, which is Schedule 8 Part 4's line 17 on the same income (3,356.10 = its line 15).
    pytest.param(
        {
            "line_1": "0",
            "line_2": "0",
            "line_19": "0",
            "line_39": "0",
            "cpt20_earnings": "0",
            "cpt20_t4_earnings": "0",
            "net_partnership_income": "80000",
        },
        {
            "part_3_line_69": "0.00",
            "part_4_line_70": "67800.00",
            "part_4_line_83": "8700.00",
            "part_4_line_84": "6712.20",
            "part_4_line_85": "1356.00",
            "part_4_line_86": "696.00",
        },
        {
            "111": "3356.10",
            "112": "678.00",
            "113": "4034.10",
            "114": "0",
            "115": "4034.10",
            "116_lesser": "0",
            "116": "0.00",
            "118": "0.00",
            "121": "3356.10",
            "124": "678.00",
            "125": "348.00",
            "127": "0",
            "128": "348.00",
            "129": "5408.10",
        },
        {
            "earnings_subject_to_contributions": "76500.00",
            "line_30800": "0.00",
            "line_22215": "0.00",
            "line_44800": "0.00",
            "line_42100": "8764.20",
            "line_31000": "3356.10",
            "line_22200": "5408.10",
        },
        id="self_employment_income_and_no_t4_slips",
    ),
    # Line 70 is -500.00 (the net income of 500 is less than the unused exemption of 1,000.00; the
    # form prints no floor) and
    # line 83 is 0: the lines added are below zero, so the form returns to Part 3 (line 69 of Part 3
    # is positive, Part 3a: 0.00, 0.00 and 127.15) and lines 42100, 31000 and 22200 are "0". Lines
    # 84 to 86 and 111 to 113 are 0.00.
    pytest.param(
        {
            "line_1": "1500",
            "line_2": "1000",
            "line_19": "50.18",
            "line_39": "4.41",
            "line_25": "40",
            "line_45": "32.56",
            "net_partnership_income": "500",
            "cpt20_earnings": "0",
            "cpt20_t4_earnings": "0",
        },
        {
            "part_3_line_69": "127.15",
            "part_4_line_70": "-500.00",
            "part_4_line_83": "0",
            "part_4_line_84": "0.00",
            "part_4_line_85": "0.00",
            "part_4_line_86": "0.00",
        },
        {
            "111": "0.00",
            "112": "0.00",
            "113": "0.00",
            "114": "127.15",
            "115": "-127.15",
            "116_lesser": "0.00",
            "116": "0.00",
            "118": "0.00",
            "121": "0.00",
            "124": "0.00",
            "125": "0.00",
            "127": "127.15",
            "128": "0",
            "129": "0.00",
        },
        {
            "earnings_subject_to_contributions": "-500.00",
            "line_30800": "0.00",
            "line_22215": "0.00",
            "line_44800": "127.15",
            "line_42100": "0",
            "line_31000": "0",
            "line_22200": "0",
        },
        id="line_70_below_zero",
    ),
    # Line 70 is -995.00 and line 83 is 0: below zero, so Part 3's results (line 69 of Part 3 is 0:
    # Part 3b, all 0.00 and no overpayment) and "0" for lines 42100, 31000 and 22200. Line 115 is
    # 0.00 and line 127 is 0.
    pytest.param(
        {
            "line_1": "1000",
            "line_2": "1500",
            "line_19": "0",
            "line_39": "0",
            "net_partnership_income": "5",
            "cpt20_earnings": "0",
            "cpt20_t4_earnings": "0",
        },
        {
            "part_3_line_69": "0.00",
            "part_4_line_70": "-995.00",
            "part_4_line_83": "0",
            "part_4_line_84": "0.00",
            "part_4_line_85": "0.00",
            "part_4_line_86": "0.00",
        },
        {
            "111": "0.00",
            "112": "0.00",
            "113": "0.00",
            "114": "0",
            "115": "0.00",
            "116_lesser": "0.00",
            "116": "0.00",
            "118": "0.00",
            "121": "0.00",
            "124": "0.00",
            "125": "0.00",
            "127": "0",
            "128": "0.00",
            "129": "0.00",
        },
        {
            "earnings_subject_to_contributions": "-995.00",
            "line_30800": "0.00",
            "line_22215": "0.00",
            "line_44800": "0",
            "line_42100": "0",
            "line_31000": "0",
            "line_22200": "0",
        },
        id="line_70_below_zero_and_line_69_zero",
    ),
    # Six months on lines A and B (line 70 = 10,961.45, line 83 = 1,538.55) with line 69 of Part 3
    # negative (-323.25): line 114 = 0 so A = 0, line 115 = 652.21 and line 116 is 0.00; lines 121
    # and 124 are lines 111 and 112 (542.59 and 109.62). Part 3b would have given 1,170.62 and
    # 229.38 for lines 30800 and 22215; with Part 4 in use the results are Part 4's lines 98 and
    # 110.
    pytest.param(
        {
            "cpp_months": 6,
            "qpp_months": 6,
            "line_1": "20000",
            "line_2": "10000",
            "line_19": "900",
            "line_39": "500",
        },
        {
            "part_3_line_69": "-323.25",
            "part_4_line_70": "10961.45",
            "part_4_line_83": "1538.55",
            "part_4_line_84": "1085.18",
            "part_4_line_85": "219.23",
            "part_4_line_86": "123.08",
        },
        {
            "111": "542.59",
            "112": "109.62",
            "113": "652.21",
            "114": "0",
            "115": "652.21",
            "116_lesser": "0",
            "116": "0.00",
            "118": "0.00",
            "121": "542.59",
            "124": "109.62",
            "125": "61.54",
            "127": "0",
            "128": "61.54",
            "129": "884.91",
        },
        {
            "earnings_subject_to_contributions": "12500.00",
            "line_30800": "1170.62",
            "line_22215": "229.38",
            "line_44800": "0.00",
            "line_42100": "1427.49",
            "line_31000": "542.59",
            "line_22200": "884.91",
        },
        id="six_months_and_line_69_negative",
    ),
    # Six months on lines A and B with line 69 of Part 3 positive (366.75) and line 70 = 3,500.00
    # (line 83 = 0): line 113 = 208.25 is less than line 114, so A = line 113, line 116 = 173.25 and
    # line 118 = 35.00; line 115 = -158.50, line 127 = 158.50 and line 128 = 0.00 less 158.50,
    # entered as "0"; line 129 = 35.00.
    pytest.param(
        {
            "cpp_months": 6,
            "qpp_months": 6,
            "line_1": "20000",
            "line_2": "10000",
            "line_19": "1190.00",
            "line_39": "650",
            "cpt20_earnings": "500",
            "cpt20_t4_earnings": "500",
        },
        {
            "part_3_line_69": "116.75",
            "part_4_line_70": "1000",
            "part_4_line_83": "0",
            "part_4_line_84": "99.00",
            "part_4_line_85": "20.00",
            "part_4_line_86": "0.00",
        },
        {
            "111": "49.50",
            "112": "10.00",
            "113": "59.50",
            "114": "116.75",
            "115": "-57.25",
            "116_lesser": "59.50",
            "116": "49.50",
            "118": "10.00",
            "121": "0.00",
            "124": "0.00",
            "125": "0.00",
            "127": "57.25",
            "128": "0",
            "129": "10.00",
        },
        {
            "earnings_subject_to_contributions": "1000",
            "line_30800": "1440.75",
            "line_22215": "282.50",
            "line_44800": "57.25",
            "line_42100": "0",
            "line_31000": "49.50",
            "line_22200": "10.00",
        },
        id="six_months_and_line_69_positive",
    ),
]


@pytest.mark.parametrize(
    ("inputs", "upstream", "expected", "selection"), PART_4_SELF_EMPLOYMENT_CASES
)
def test_return_bo_part_4_lines_111_to_129(
    inputs: dict[str, Any],
    upstream: dict[str, str],
    expected: dict[str, str],
    selection: dict[str, str],
) -> None:
    worksheet = return_bo(**inputs)

    upstream_kinds = {
        "part_3_line_69": RC381_PART_3_LINE_69,
        "part_4_line_70": RC381_PART_4_LINE_70,
        "part_4_line_83": RC381_PART_4_LINE_83,
        "part_4_line_84": RC381_PART_4_LINE_84,
        "part_4_line_85": RC381_PART_4_LINE_85,
        "part_4_line_86": RC381_PART_4_LINE_86,
    }
    assert {key: worksheet.get(kind).value for key, kind in upstream_kinds.items()} == {
        key: D(value) for key, value in upstream.items()
    }
    assert part_4_self_employment(worksheet) == {line: D(value) for line, value in expected.items()}


@pytest.mark.parametrize(
    ("inputs", "upstream", "expected", "selection"), PART_4_SELF_EMPLOYMENT_CASES
)
def test_return_bo_the_final_selection(
    inputs: dict[str, Any],
    upstream: dict[str, str],
    expected: dict[str, str],
    selection: dict[str, str],
) -> None:
    worksheet = return_bo(**inputs)

    assert final_selection(worksheet) == {line: D(value) for line, value in selection.items()}
    # The earnings subject to contributions are lines 70 and 83 of Part 4 added; above zero the
    # results are Part 4's lines, else Part 3's results and "0" ("return to Part 3").
    earnings = worksheet.get(RC381_PART_4_LINE_70).value + worksheet.get(RC381_PART_4_LINE_83).value
    assert worksheet.get(RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS).value == earnings
    if earnings > 0:
        assert (
            worksheet.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value
            == worksheet.get(RC381_PART_4_LINE_98).value
        )
        assert (
            worksheet.get(RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value
            == worksheet.get(RC381_PART_4_LINE_110).value
        )
        assert (
            worksheet.get(RC381_CPP_OVERPAYMENT_ON_RETURN).value
            == worksheet.get(RC381_PART_4_LINE_91).value
        )
        assert (
            worksheet.get(RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT).value
            == worksheet.get(RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS).value
        )
        assert (
            worksheet.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value
            == worksheet.get(RC381_PART_4_LINE_111).value
        )
        assert (
            worksheet.get(RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value
            == worksheet.get(RC381_PART_4_LINE_129).value
        )
    else:
        assert (
            worksheet.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value
            == worksheet.get(RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS).value
        )
        assert (
            worksheet.get(RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value
            == worksheet.get(RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS).value
        )
        assert (
            worksheet.get(RC381_CPP_OVERPAYMENT_ON_RETURN).value
            == worksheet.get(RC381_CPP_OVERPAYMENT).value
        )
        for kind in (
            RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
            RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
            RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        ):
            assert worksheet.get(kind).value == D("0"), kind.identifier


@pytest.mark.parametrize(
    ("inputs", "upstream", "expected", "selection"), PART_4_SELF_EMPLOYMENT_CASES
)
def test_return_bo_part_4_lines_121_and_124_add_up_to_line_113_less_a(
    inputs: dict[str, Any],
    upstream: dict[str, str],
    expected: dict[str, str],
    selection: dict[str, str],
) -> None:
    # Lines 121 and 124 are (111 less 116) and (112 less 118), and line 118 is A less line 116, so
    # together they are line 113 less A, which is never negative although each may be a cent below
    # zero.
    lines = part_4_self_employment(return_bo(**inputs))

    assert lines["121"] + lines["124"] == lines["113"] - lines["116_lesser"]
    assert lines["121"] + lines["124"] >= 0


# A return with no Quebec figures.


def test_a_return_with_no_quebec_figures_is_unchanged_and_rc381_part_3_matches_schedule_8() -> None:
    # Employment income of 60,000 and none of the Quebec figures: the T1 lines are Schedule 8's,
    # base contributions 4.95% x (60,000 less 3,500) = 2,796.75 and enhanced 1% x 56,500 = 565.00.
    # The T4 box 16 total is the Schedule 8 Part 3 line 8 input, here the required 3,361.75, on
    # the T4 box 26 of 60,000, so
    # line 20 (83.1933% of it) is the base contributions 2,796.75 and line 21 the enhanced 565.00,
    # equal to the required figures of lines 22 and 23: lines 53, 60, 61 and 69 and line 44800's
    # overpayment are 0.00. The QPP lines and the second additional contributions are 0.
    # (The return carries Schedule 8 or Form RC381, so the T1 lines are read from the return with
    # Schedule 8 and the Form RC381 lines from the same return carrying Form RC381.)
    with_schedule_8 = compute_with_schedule_8("60000", (), "0", "0", "0", "0", "0")
    worksheet = compute_form("ca/rc381", "60000", (), "0", "0", "0", "0", "0")

    assert with_schedule_8.get(CPP_BASE_CONTRIBUTIONS).value == D("2796.75")
    assert with_schedule_8.get(CPP_ENHANCED_CONTRIBUTIONS).value == D("565.00")
    assert with_schedule_8.get(NET_INCOME).value == D("59435.00")
    kinds: tuple[ArtifactKind[Any], ...] = (
        RC381_PART_3_LINE_3,
        RC381_PART_3_LINE_7,
        RC381_PART_3_LINE_8,
        RC381_PART_3_LINE_9,
        RC381_PART_3_LINE_10,
        RC381_PART_3_LINE_11,
        RC381_PART_3_LINE_14,
        RC381_PART_3_LINE_15,
        RC381_PART_3_LINE_16,
        RC381_PART_3_LINE_18,
        RC381_PART_3_LINE_22,
        RC381_PART_3_LINE_23,
        RC381_PART_3_LINE_24,
        RC381_PART_3_LINE_26,
        RC381_PART_3_LINE_31,
        RC381_PART_3_LINE_34,
        RC381_PART_3_LINE_35_LESSER,
        RC381_PART_3_LINE_35,
        RC381_PART_3_LINE_36,
        RC381_PART_3_LINE_38,
        RC381_PART_3_LINE_40,
        RC381_PART_3_LINE_41,
        RC381_PART_3_LINE_42,
        RC381_PART_3_LINE_43,
        RC381_PART_3_LINE_44,
        RC381_PART_3_LINE_46,
        RC381_PART_3_LINE_52,
        RC381_PART_3_LINE_59,
        RC381_PART_3_LINE_64,
        RC381_PART_3_LINE_67,
        RC381_PART_3_LINE_68,
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
        RC381_PART_3_LINE_87_DIFFERENCE,
        RC381_PART_3_LINE_87,
        RC381_PART_3_LINE_88,
        RC381_PART_3_LINE_89,
        RC381_PART_3_LINE_90,
        RC381_PART_3_LINE_91,
        RC381_PART_3_LINE_92,
        RC381_PART_3_LINE_93,
        RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS,
        RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS,
        RC381_PART_4_LINE_4,
        RC381_PART_4_LINE_13,
        RC381_PART_4_LINE_13_DIFFERENCE,
        RC381_PART_4_LINE_14,
        RC381_PART_4_LINE_17A,
        RC381_PART_4_LINE_20,
        RC381_PART_4_LINE_21,
        RC381_PART_4_LINE_21_LESSER,
        RC381_PART_4_LINE_23,
        RC381_PART_4_LINE_23_LESSER,
        RC381_PART_4_LINE_23_MULTIPLIED,
        RC381_PART_4_LINE_24,
        RC381_PART_4_LINE_24_LESSER,
        RC381_PART_4_LINE_25A,
        RC381_PART_4_LINE_26,
        RC381_PART_4_LINE_27,
        RC381_PART_4_LINE_31_DIFFERENCE,
        RC381_PART_4_LINE_31,
        RC381_PART_4_LINE_32,
        RC381_PART_4_LINE_33,
        RC381_PART_4_LINE_34,
        RC381_PART_4_LINE_35,
        RC381_PART_4_LINE_35AA,
        RC381_PART_4_LINE_35AB_FROM_LINE_20,
        RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO,
        RC381_PART_4_LINE_35AB,
        RC381_PART_4_LINE_35A,
        RC381_PART_4_LINE_36,
        RC381_PART_4_LINE_38,
        RC381_PART_4_LINE_39,
        RC381_PART_4_LINE_40,
        RC381_PART_4_LINE_41,
        RC381_PART_4_LINE_42,
        RC381_PART_4_LINE_46_DIFFERENCE,
        RC381_PART_4_LINE_46,
        RC381_PART_4_LINE_47,
        RC381_PART_4_LINE_51_DIFFERENCE,
        RC381_PART_4_LINE_51,
        RC381_PART_4_LINE_52,
        RC381_PART_4_LINE_53,
        RC381_PART_4_LINE_54,
        RC381_PART_4_LINE_55,
        RC381_PART_4_LINE_56,
        RC381_PART_4_LINE_92,
        RC381_PART_4_LINE_93,
        RC381_PART_4_LINE_94,
        RC381_PART_4_LINE_95,
        RC381_PART_4_LINE_96,
        RC381_PART_4_LINE_97,
        RC381_PART_4_LINE_98,
        RC381_PART_4_LINE_99,
        RC381_PART_4_LINE_100,
        RC381_PART_4_LINE_101,
        RC381_PART_4_LINE_102,
        RC381_PART_4_LINE_103,
        RC381_PART_4_LINE_104_DIFFERENCE,
        RC381_PART_4_LINE_104,
        RC381_PART_4_LINE_105,
        RC381_PART_4_LINE_106,
        RC381_PART_4_LINE_107,
        RC381_PART_4_LINE_108,
        RC381_PART_4_LINE_109,
        RC381_PART_4_LINE_110,
    )
    assert worksheet.get(RC381_PART_3_LINE_20).value == D("2796.75")
    assert worksheet.get(RC381_PART_3_LINE_21).value == D("565.00")
    assert worksheet.get(RC381_PART_3_LINE_6).value == Rate(D("1.00000"))
    assert worksheet.get(RC381_PART_3_LINE_49).value == D("2796.75")
    assert worksheet.get(RC381_PART_3_LINE_53).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_56).value == D("565.00")
    assert worksheet.get(RC381_PART_3_LINE_60).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_61).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_69).value == D("0.00")
    # Line 69 is 0.00, not positive, so Part 3b applies, which has no overpayment: line 44800 is 0;
    # the other two results are the required 2,796.75 and 565.00 that the T4 box 16 total equals.
    assert worksheet.get(RC381_CPP_OVERPAYMENT).value == D("0")
    # Part 4: lines 8 and 11 are lines 20 and 21 less the required lines 22 and 23 (2,796.75 and
    # 565.00), line 12 their sum and line 17 the T4 box 16 total less line 13 (3,361.75), so all
    # are 0.00 and line 21 (from line 17) is 0.
    assert worksheet.get(RC381_PART_4_LINE_8).value == D("0.00")
    assert worksheet.get(RC381_PART_4_LINE_11).value == D("0.00")
    assert worksheet.get(RC381_PART_4_LINE_12).value == D("0.00")
    assert worksheet.get(RC381_PART_4_LINE_17).value == D("0.00")
    assert worksheet.get(RC381_PART_4_LINE_21_FROM_LINE_17).value == D("0")
    # Part 4 line 35aa from line 17 is 0, as line 17 is 0.00.
    assert worksheet.get(RC381_PART_4_LINE_35AA_FROM_LINE_17).value == D("0")
    # Part 4 line 22 is 0 over 0: a zero divisor gives 0.
    assert worksheet.get(RC381_PART_4_LINE_22).value == Rate(D("0"))
    # Lines 27 to 30 are the QPP row of the table less lines 7 to 10 (line 6 is 1, so lines 7 to
    # 10 are the whole row): 0.00.
    assert worksheet.get(RC381_PART_3_LINE_27).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_28).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_29).value == D("0.00")
    assert worksheet.get(RC381_PART_3_LINE_30).value == D("0.00")
    # Every other line of the list is 0: the QPP lines (27 to 46, the T4 box 17 total and the
    # Quebec earnings being absent) and the second additional contributions; those below are the
    # CPP lines on the 60,000 of box 26 (60,000 less the 3,500.00 exemption is 56,500.00, 4.95% of
    # it 2,796.75 and 1% of it 565.00, the required 3,361.75 that the box 16 total is).
    on_the_earnings = {
        RC381_PART_3_LINE_3: D("60000"),
        RC381_PART_3_LINE_7: D("81200.00"),
        RC381_PART_3_LINE_8: D("71300.00"),
        RC381_PART_3_LINE_9: D("3500.00"),
        RC381_PART_3_LINE_10: D("9900.00"),
        RC381_PART_3_LINE_11: D("60000"),
        RC381_PART_3_LINE_16: D("60000"),
        RC381_PART_3_LINE_18: D("56500.00"),
        RC381_PART_3_LINE_22: D("2796.75"),
        RC381_PART_3_LINE_23: D("565.00"),
        RC381_PART_3_LINE_24: D("3361.75"),
        RC381_PART_3_LINE_52: D("2796.75"),
        RC381_PART_3_LINE_59: D("565.00"),
        RC381_PART_3_LINE_73: D("565.00"),
        RC381_PART_3_LINE_75: D("2796.75"),
        RC381_PART_3_LINE_79: D("2796.75"),
        RC381_PART_3_LINE_81: D("2796.75"),
        RC381_PART_3_LINE_82: D("565.00"),
        RC381_PART_3_LINE_86: D("565.00"),
        RC381_PART_3_LINE_88: D("565.00"),
        RC381_PART_3_LINE_93: D("565.00"),
        RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS: D("2796.75"),
        RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS: D("565.00"),
        RC381_PART_4_LINE_13: D("3361.75"),
        RC381_PART_4_LINE_13_DIFFERENCE: D("3361.75"),
        RC381_PART_4_LINE_26: D("3361.75"),
        RC381_PART_4_LINE_27: D("56499.99"),
        RC381_PART_4_LINE_42: D("56499.99"),
        RC381_PART_4_LINE_92: D("2796.75"),
        RC381_PART_4_LINE_96: D("2796.75"),
        RC381_PART_4_LINE_98: D("2796.75"),
        RC381_PART_4_LINE_99: D("565.00"),
        RC381_PART_4_LINE_103: D("565.00"),
        RC381_PART_4_LINE_105: D("565.00"),
        RC381_PART_4_LINE_110: D("565.00"),
    }
    for kind in kinds:
        assert worksheet.get(kind).value == on_the_earnings.get(kind, D("0")), kind.identifier
    # Part 4 lines 57 to 91 are computed for every return: line 59 = 71,300.00 less 3,500.00 =
    # 67,800.00 and line 61 = line 59 less line 42 (56,499.99) = 11,300.01. Line 4 is 0, so line 62
    # = 0; line 3 of Part 3 (60,000) is not less than line 58, so lines 65, 68 and 69 are "0" and
    # line 70 = line 62 less line 69 = 0. Lines 80 and 82 follow (0 and 0.00), line 77 = line D
    # 9,900.00 less line 76 (0.00), and lines 84 to 88 are 0.00; line 89 = 2 x line 69 (0) = 0.00,
    # so line 90 = 0.00 (line 42100 is 0.00) and line 91 = 0.00.
    assert part_4_earnings(worksheet) == {
        "59": D("67800.00"),
        "61": D("11300.01"),
        "62": D("0"),
        "65": D("0"),
        "68": D("0"),
        "69": D("0"),
        "70": D("0"),
        "74": D("60000"),
        "76": D("0.00"),
        "77": D("9900.00"),
        "80": D("0"),
        "82": D("0.00"),
        "83_lesser": D("0.00"),
        "83": D("0"),
        "84": D("0.00"),
        "85": D("0.00"),
        "86": D("0.00"),
        "87": D("0.00"),
        "88": D("0.00"),
        "89_from_line_69": D("0"),
        "89": D("0.00"),
        "90": D("0.00"),
        "42100": D("0.00"),
        "91_from_line_90": D("0"),
        "91": D("0.00"),
    }
    # Part 4 lines 111 to 129 are computed for every return: lines 84 to 86 are 0.00 and line 69 of
    # Part 3 is 0.00, so line 114 is "0", line 115 = line 113 = 0.00 and every other line is 0.00.
    # The earnings subject to contributions are lines 70 and 83 added, 0 + 0: not above zero, so
    # the form returns to Part 3 and the six results are Part 3's (2,796.75 and 565.00 for lines
    # 30800 and 22215, "0" for the overpayment of line 44800) and "0" for the others.
    assert part_4_self_employment(worksheet) == {
        "111": D("0.00"),
        "112": D("0.00"),
        "113": D("0.00"),
        "114": D("0"),
        "115": D("0.00"),
        "116_lesser": D("0.00"),
        "116": D("0.00"),
        "118": D("0.00"),
        "121": D("0.00"),
        "124": D("0.00"),
        "125": D("0.00"),
        "127": D("0"),
        "128": D("0.00"),
        "129": D("0.00"),
    }
    assert final_selection(worksheet) == {
        "earnings_subject_to_contributions": D("0"),
        "line_30800": D("2796.75"),
        "line_22215": D("565.00"),
        "line_44800": D("0"),
        "line_42100": D("0"),
        "line_31000": D("0"),
        "line_22200": D("0"),
    }


def test_the_rc381_results_are_the_t1_lines() -> None:
    # Each of the six results of the form is the T1 line it is entered on, the return carrying
    # Form RC381 and no Schedule 8: lines 30800 and 22215 (3,462.75 and 665.00), 44800 (0.00),
    # 42100 (632.20), 31000 (64.35) and 22200 (725.10) of return BO.
    form = return_bo()
    on_return = return_bo(form="ca-on/return")

    for result, line in (
        (RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN, CPP_BASE_CONTRIBUTIONS_ON_RETURN),
        (RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN, CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN),
        (RC381_CPP_OVERPAYMENT_ON_RETURN, CPP_OVERPAYMENT),
        (RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT, CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS),
        (
            RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        ),
        (
            RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        ),
    ):
        assert on_return.get(line).value == form.get(result).value, line.identifier
    assert on_return.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3462.75")
    assert on_return.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("665.00")
    assert on_return.get(NET_INCOME).value == D("68609.90")
    assert on_return.get(TOTAL_PAYABLE).value == D("11868.30")
    assert on_return.get(REFUND_OR_BALANCE_OWING).value == D("-131.70")


def test_the_t1_lines_follow_the_rc381_totals_not_the_pensionable_earnings_totals_alone() -> None:
    # Without the Quebec pensionable earnings and the T4 box 17 total (lines 2 and 39) the form
    # gives other results, and the T1 lines follow them.
    without_totals = return_bo(form="ca-on/return", line_2="0", line_39="0")
    form = return_bo(line_2="0", line_39="0")

    assert (
        without_totals.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value
        == form.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value
    )
    assert (
        without_totals.get(CPP_OVERPAYMENT).value == form.get(RC381_CPP_OVERPAYMENT_ON_RETURN).value
    )


# Parts 4 and 5 completed on a return that carries Form RC381. Schedule 8 is not on the return, so
# the Part 4 and Part 5 amounts are the form's alone: a filer's Part 4 or Part 5 flag counted on top
# of the form's result would double count (the guard `ca/count_without_records`).


def test_return_bo_line_42100_is_the_form_rc381_result_of_632_20_with_both_parts_at_0() -> None:
    # With Parts 4 and 5 both at 0, line 42100 is Form RC381's own result, 632.20, and nothing else
    # is added to it.
    on_return = return_bo(form="ca-on/return")

    assert on_return.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("632.20")


def test_return_bo_with_part_4_completed_is_refused_naming_the_input_and_the_form() -> None:
    # Part 4 completed as 1 on a return with a copy of Form RC381 is an input error, naming the
    # input (`ca/cpp_part_4_completed`) and the form's records (`ca/rc381_instances`); it is not
    # counted on top of the form's result.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bo(form="ca-on/return", cpp_part_4_completed=1)

    assert "ca/cpp_part_4_completed" in str(raised.value)
    assert "ca/rc381_instances" in str(raised.value)


def test_return_bo_with_part_5_completed_is_refused_naming_the_input_and_the_form() -> None:
    # The same for Part 5 completed as 1: refused, not counted on top of the form's result.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bo(form="ca-on/return", cpp_part_5_completed=1)

    assert "ca/cpp_part_5_completed" in str(raised.value)
    assert "ca/rc381_instances" in str(raised.value)


def test_a_schedule_8_return_with_part_5_completed_still_computes_line_42100() -> None:
    # The Part 5 case of `test_return_schedule_8.py`, with one copy of Schedule 8 and no Form RC381:
    # with no record of the form the guard passes the input on, and line 42100 is 1,764.20.
    result = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_part_5_completed=1,
    )

    assert result.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1764.20")
