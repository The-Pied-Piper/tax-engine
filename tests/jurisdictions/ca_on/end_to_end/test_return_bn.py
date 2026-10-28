"""CA-ON 2025 end to end: return bn."""

from __future__ import annotations

import re
from collections.abc import Mapping
from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.errors import InputOutOfRangeError
from tax_calculator.domain.parameters.fraction import Fraction
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.trace import (
    ChosenByCountLine,
    ContributionTierLine,
    DividedByRateLine,
    FractionAppliedLine,
    LesserOfLine,
    RateAppliedLine,
    SubtractedLine,
    SumLine,
    TimesCountLine,
)
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_DEDUCTIONS_TOTAL,
    CPP_ACTUAL_BASE_CONTRIBUTIONS,
    CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_BASE_CONTRIBUTIONS,
    CPP_BASE_CONTRIBUTIONS_DIFFERENCE,
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_CONTRIBUTIONS_DIFFERENCE,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ENHANCED_CONTRIBUTIONS,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE,
    CPP_LINE_16_NOT_NEGATIVE,
    CPP_LINE_16_POSITIVE,
    CPP_LINE_19_NOT_NEGATIVE,
    CPP_LINE_20_POSITIVE,
    CPP_LINE_23_AND_LINE_33_POSITIVE,
    CPP_LINE_23_AND_LINE_40_POSITIVE,
    CPP_LINE_23_NOT_NEGATIVE,
    CPP_LINE_24_POSITIVE,
    CPP_OVERPAYMENT,
    CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_PART_3_OVERPAYMENT,
    CPP_PART_3B_LINE_30,
    CPP_PART_3B_LINE_31,
    CPP_PART_3B_LINE_32,
    CPP_PART_3B_LINE_33,
    CPP_PART_3B_LINE_34,
    CPP_PART_3B_LINE_35,
    CPP_PART_3B_LINE_36,
    CPP_PART_3B_LINE_37,
    CPP_PART_3B_LINE_38,
    CPP_PART_3B_LINE_39,
    CPP_PART_3B_LINE_40,
    CPP_PART_3B_LINE_41,
    CPP_PART_3B_LINE_42,
    CPP_PART_3B_LINE_43,
    CPP_PART_3B_LINE_44,
    CPP_PART_3B_LINE_45,
    CPP_PART_3B_LINE_46,
    CPP_PART_3B_LINE_47,
    CPP_PART_3B_LINE_48,
    CPP_PART_5_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
    CPP_PART_5_COMPLETED,
    CPP_PART_5_COMPLETED_CHECKED,
    CPP_PART_5_DEDUCTION_ON_SELF_EMPLOYMENT,
    CPP_PART_5_LINE_4,
    CPP_PART_5_LINE_6,
    CPP_PART_5_LINE_7,
    CPP_PART_5_LINE_8,
    CPP_PART_5_LINE_9,
    CPP_PART_5_LINE_9_LESSER,
    CPP_PART_5_LINE_10,
    CPP_PART_5_LINE_12,
    CPP_PART_5_LINE_13,
    CPP_PART_5_LINE_14,
    CPP_PART_5_LINE_15,
    CPP_PART_5_LINE_15_LESSER,
    CPP_PART_5_LINE_16,
    CPP_PART_5_LINE_19,
    CPP_PART_5_LINE_20,
    CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE,
    CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE,
    CPP_PART_5_LINE_21,
    CPP_PART_5_LINE_22,
    CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE,
    CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE,
    CPP_PART_5_LINE_23_LESS_LINE_56,
    CPP_PART_5_LINE_25,
    CPP_PART_5_LINE_28,
    CPP_PART_5_LINE_29,
    CPP_PART_5_LINE_30,
    CPP_PART_5_LINE_33,
    CPP_PART_5_LINE_33_MORE_THAN_LINE_17,
    CPP_PART_5_LINE_35,
    CPP_PART_5_LINE_36,
    CPP_PART_5_LINE_39,
    CPP_PART_5_LINE_41,
    CPP_PART_5_LINE_42,
    CPP_PART_5_LINE_42_LESSER,
    CPP_PART_5_LINE_43,
    CPP_PART_5_LINE_44,
    CPP_PART_5_LINE_45,
    CPP_PART_5_LINE_46,
    CPP_PART_5_LINE_47,
    CPP_PART_5_LINE_48,
    CPP_PART_5_LINE_48_LINE_24_IF_POSITIVE,
    CPP_PART_5_LINE_49,
    CPP_PART_5_LINE_49_IF_POSITIVE,
    CPP_PART_5_LINE_50,
    CPP_PART_5_LINE_50_LINE_49_POSITIVE,
    CPP_PART_5_LINE_51,
    CPP_PART_5_LINE_52,
    CPP_PART_5_LINE_53,
    CPP_PART_5_LINE_54,
    CPP_PART_5_LINE_55,
    CPP_PART_5_LINE_56,
    CPP_PART_5_LINE_56_LESSER,
    CPP_PART_5_LINE_57,
    CPP_PART_5_LINE_58,
    CPP_PART_5_LINE_59,
    CPP_PART_5_LINE_60,
    CPP_PART_5_LINE_61,
    CPP_PART_5_LINE_62,
    CPP_PART_5_LINE_63,
    CPP_PART_5_LINE_63_LESSER,
    CPP_PART_5_LINE_64,
    CPP_PART_5_LINE_65,
    CPP_PART_5_LINE_66,
    CPP_PART_5_LINE_67,
    CPP_PART_5_LINE_67_LESSER,
    CPP_PART_5_LINE_68,
    CPP_PART_5_LINE_69,
    CPP_PART_5_LINE_70,
    CPP_PART_5_LINE_71,
    CPP_PART_5_LINE_72,
    CPP_PART_5_LINE_73,
    CPP_PART_5_LINE_74,
    CPP_PART_5_LINE_75,
    CPP_PART_5_LINE_75_BASE,
    CPP_PART_5_LINE_77,
    CPP_PART_5_LINE_80,
    CPP_PART_5_LINE_83,
    CPP_PART_5_LINE_84,
    CPP_PART_5_LINE_86,
    CPP_PART_5_LINE_87,
    CPP_PART_5_LINE_88,
    CPP_PART_5_PAYABLE_ON_SELF_EMPLOYMENT,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CPP_ZERO,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    EI_PAYABLE_ON_SELF_EMPLOYMENT,
    NET_FEDERAL_TAX,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    REFUND_OR_BALANCE_OWING,
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_OVERPAYMENT,
    SOCIAL_BENEFITS_REPAYMENT_PAYABLE,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    ReturnAndSchedule8,
    compute_with_schedule_8,
    routed_statement,
)

CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Return BN: employment income of $60,000, the T4 box 16 total of $3,500.00 (Schedule 8 line 8)
# and box 16A of $0 (line 21), so line 24 is positive. The required amounts are base 4.95% x
# 56,500 = 2,796.75 (line 11), first additional 1% x 56,500 = 565.00 (line 12) and so line 13 is
# 3,361.75 and line 22 is 0. Line 9 is 2,911.7655 rounded to 2,911.77, line 10 is 588.23, line 16
# is 115.02, line 19 is 23.23, line 20 is 138.25 and line 24 is 138.25. The other cases of the
# same employment income: box 16 of $3,300.00 gives line 24 of -61.75 (in brackets), and box 16
# equal to the required $3,361.75 gives 0.


def test_t4_contributions_above_the_required_ones_give_a_positive_line_24() -> None:
    # Return BN as filed: box 16 of $3,500.00 is 138.25 more than line 13.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_t4_second_additional_contributions="0",
    )

    assert worksheet.get(CPP_BASE_CONTRIBUTIONS).value == D("2796.75")
    assert worksheet.get(CPP_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("565.00")
    assert worksheet.get(CPP_SECOND_ADDITIONAL_CONTRIBUTIONS).value == D("0.00")
    # Line 9: 83.1933% of 3,500.00, 2,911.7655, rounded half-up to the cent.
    assert worksheet.get(CPP_ACTUAL_BASE_CONTRIBUTIONS).value == D("2911.77")
    # Line 10: line 8 minus line 9.
    assert worksheet.get(CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("588.23")
    # Line 13: line 11 plus line 12.
    assert worksheet.get(CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("3361.75")
    # Line 16: line 14 (line 9) minus line 15 (line 11); line 19: line 17 (line 10) minus line 18
    # (line 12); line 20: line 16 plus line 19.
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_DIFFERENCE).value == D("115.02")
    assert worksheet.get(CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D("23.23")
    assert worksheet.get(CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D(
        "138.25"
    )
    # Line 23: line 21 ($0) minus line 22 ($0); line 24: line 20 plus line 23.
    assert worksheet.get(CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D("0.00")
    assert worksheet.get(CPP_CONTRIBUTIONS_DIFFERENCE).value == D("138.25")


def test_t4_contributions_below_the_required_ones_give_a_negative_line_24_in_brackets() -> None:
    # Box 16 of $3,300.00: line 9 is 2,745.38, line 16 is -51.37, line 10 is 554.62, line 19 is
    # -10.38, line 20 is -61.75 and line 24 is -61.75 (shown in brackets on the form).
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3300.00",
        cpp_t4_second_additional_contributions="0",
    )

    assert worksheet.get(CPP_ACTUAL_BASE_CONTRIBUTIONS).value == D("2745.38")
    assert worksheet.get(CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("554.62")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_DIFFERENCE).value == D("-51.37")
    assert worksheet.get(CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D("-10.38")
    assert worksheet.get(CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D(
        "-61.75"
    )
    assert worksheet.get(CPP_CONTRIBUTIONS_DIFFERENCE).value == D("-61.75")


def test_t4_contributions_equal_to_the_required_ones_give_line_24_zero() -> None:
    # Box 16 of $3,361.75 is line 13: line 9 is 2,796.75 (equal to line 11) and line 24 is 0.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3361.75",
        cpp_t4_second_additional_contributions="0",
    )

    assert worksheet.get(CPP_ACTUAL_BASE_CONTRIBUTIONS).value == D("2796.75")
    assert worksheet.get(CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("565.00")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_DIFFERENCE).value == D("0.00")
    assert worksheet.get(CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D("0.00")
    assert worksheet.get(CPP_CONTRIBUTIONS_DIFFERENCE).value == D("0.00")


def test_without_t4_inputs_the_required_contributions_are_the_default_so_line_24_is_zero() -> None:
    # The helper's default is the required amount for the employment income: box 16 of
    # $3,361.75 and box 16A of $0 at $60,000, so line 24 is 0 with no T4 input given.
    worksheet = compute_with_schedule_8("60000", (), "0", "0", "0", "0", "0")

    assert worksheet.get(CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("3361.75")
    assert worksheet.get(CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS).value == D("0")
    assert worksheet.get(CPP_CONTRIBUTIONS_DIFFERENCE).value == D("0.00")


def test_a_second_additional_contribution_above_the_required_one_is_a_positive_line_23() -> None:
    # Employment income of $90,000: line 22 is 4% of 9,900 = 396.00. Box 16A of $500.00 is 104.00
    # more, so line 23 and line 24 are 104.00 (the base and first parts are the required ones).
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="4034.10",
        cpp_t4_second_additional_contributions="500",
    )

    assert worksheet.get(CPP_SECOND_ADDITIONAL_CONTRIBUTIONS).value == D("396.00")
    assert worksheet.get(CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D("104.00")
    assert worksheet.get(CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D("0.00")
    assert worksheet.get(CPP_CONTRIBUTIONS_DIFFERENCE).value == D("104.00")


def test_form_rounding_moves_lines_16_and_19_a_cent_each_way_but_line_24_stays_zero() -> None:
    # Employment income of $6,900.50: the required base is 168.32 and first additional 34.01, so
    # line 13 is 202.33. Line 9 of 202.33 is 168.33, a cent above line 11, so line 16 is 0.01;
    # line 10 is 34.00, a cent below line 12, so line 19 is -0.01. Line 20 is 0.00 and line 24
    # is 0.00: line 20 is line 8 less line 13, whatever line 9 rounds to.
    worksheet = compute_with_schedule_8("6900.50", (), "0", "0", "0", "0", "0")

    assert worksheet.get(CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS).value == D("202.33")
    assert worksheet.get(CPP_ACTUAL_BASE_CONTRIBUTIONS).value == D("168.33")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_DIFFERENCE).value == D("0.01")
    assert worksheet.get(CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D("-0.01")
    assert worksheet.get(CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE).value == D("0.00")
    assert worksheet.get(CPP_CONTRIBUTIONS_DIFFERENCE).value == D("0.00")


def assert_values(
    worksheet: ReturnAndSchedule8, expected: Mapping[ArtifactKind[Any], Decimal | int]
) -> None:
    for kind, value in expected.items():
        assert worksheet.get(kind).value == value, kind.identifier


# Schedule 8 Part 3a and Part 3b (T1 lines 30800, 22215 and 44800). Every figure below is derived
# by hand from the form's lines, in order, from the employment income and the two T4 totals:
# line 7 is employment income less 3,500 (to 67,800), line 11 is 4.95% of it (maximum 3,356.10),
# line 12 is 1% of it (maximum 678.00), line 4 is employment income over 71,300 (to 9,900) and
# line 22 is 4% of that (maximum 396.00). Line 9 is box 16 times 83.1933% to the cent. The cases:
# line 24 positive (Part 3a, three cases); line 24 "0" (the helper's default, and two cases where
# the cent rounding of line 9 splits lines 16 and 19); line 24 negative (both differences
# negative; line 23 positive with line 33 positive; line 20 positive with line 23 negative).


def test_part_3a_routes_lines_25_28_and_29_to_lines_30800_22215_and_44800() -> None:
    # Return BN as filed (box 16 of $3,500.00, 138.25 more than line 13): line 24 is positive,
    # so Part 3a applies.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_t4_second_additional_contributions="0",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("115.02"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("23.23"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("138.25"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("138.25"),
            CPP_LINE_24_POSITIVE: 1,
            CPP_BASE_CONTRIBUTIONS: D("2796.75"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS: D("565.00"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS: D("0.00"),
            CPP_ENHANCED_CONTRIBUTIONS: D("565.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2796.75"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("565.00"),
            CPP_OVERPAYMENT: D("138.25"),
        },
    )


def test_part_3a_with_a_positive_line_23_adds_line_22_to_the_enhanced_deduction() -> None:
    # Employment income of $90,000 and box 16A of $500.00, 104.00 more than line 22: box 16 is
    # the required $4,034.10, so line 24 is line 23, 104.00, and Part 3a applies with line 27
    # (line 22) of 396.00.
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="4034.10",
        cpp_t4_second_additional_contributions="500",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("104.00"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("104.00"),
            CPP_LINE_24_POSITIVE: 1,
            CPP_BASE_CONTRIBUTIONS: D("3356.10"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS: D("678.00"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS: D("396.00"),
            CPP_ENHANCED_CONTRIBUTIONS: D("1074.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("3356.10"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("1074.00"),
            CPP_OVERPAYMENT: D("104.00"),
        },
    )


def test_part_3a_applies_when_a_larger_line_20_outweighs_a_negative_line_23() -> None:
    # Box 16 of $4,300.00 is 265.90 over line 13 and box 16A of $300.00 is 96.00 under line 22,
    # so line 24 is positive (169.90) and Part 3a applies.
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="4300.00",
        cpp_t4_second_additional_contributions="300",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("221.21"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("44.69"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("265.90"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-96.00"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("169.90"),
            CPP_LINE_24_POSITIVE: 1,
            CPP_BASE_CONTRIBUTIONS: D("3356.10"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS: D("678.00"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS: D("396.00"),
            CPP_ENHANCED_CONTRIBUTIONS: D("1074.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("3356.10"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("1074.00"),
            CPP_OVERPAYMENT: D("169.90"),
        },
    )


def test_part_3b_with_line_24_zero_takes_the_required_lines_11_12_and_22() -> None:
    # Box 16 equal to line 13 (the helper's default): lines 16, 19, 23 and 24 are 0, so Part 3b
    # applies and every count that asks for a positive amount is 0.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_LINE_24_POSITIVE: 0,
            CPP_LINE_16_NOT_NEGATIVE: 1,
            CPP_LINE_19_NOT_NEGATIVE: 1,
            CPP_LINE_23_NOT_NEGATIVE: 1,
            CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_33_POSITIVE: 0,
            CPP_LINE_16_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_40_POSITIVE: 0,
            CPP_LINE_20_POSITIVE: 0,
            CPP_PART_3B_LINE_30: D("2796.75"),
            CPP_PART_3B_LINE_31: D("0"),
            CPP_PART_3B_LINE_32: D("0"),
            CPP_PART_3B_LINE_33: D("0"),
            CPP_PART_3B_LINE_34: D("2796.75"),
            CPP_PART_3B_LINE_35: D("0"),
            CPP_PART_3B_LINE_36: D("2796.75"),
            CPP_PART_3B_LINE_37: D("565.00"),
            CPP_PART_3B_LINE_38: D("0"),
            CPP_PART_3B_LINE_39: D("0"),
            CPP_PART_3B_LINE_40: D("0"),
            CPP_PART_3B_LINE_41: D("565.00"),
            CPP_PART_3B_LINE_42: D("0"),
            CPP_PART_3B_LINE_43: D("565.00"),
            CPP_PART_3B_LINE_44: D("0.00"),
            CPP_PART_3B_LINE_45: D("0"),
            CPP_PART_3B_LINE_46: D("0"),
            CPP_PART_3B_LINE_47: D("0.00"),
            CPP_PART_3B_LINE_48: D("565.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2796.75"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("565.00"),
            CPP_OVERPAYMENT: D("0"),
        },
    )


def test_part_3b_a_cent_split_between_lines_16_and_19_is_added_back_on_line_39() -> None:
    # Employment income of $6,900.50, box 16 equal to line 13 (202.33): line 9 rounds a cent
    # over line 11 and line 10 a cent under line 12, so line 16 is positive (0.01) and line 19
    # negative (-0.01); line 39 takes the lesser of line 16 and line 38, 0.01, and line 41 adds
    # it to line 37.
    worksheet = compute_with_schedule_8(
        "6900.50",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("0.01"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-0.01"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_LINE_24_POSITIVE: 0,
            CPP_LINE_16_NOT_NEGATIVE: 1,
            CPP_LINE_19_NOT_NEGATIVE: 0,
            CPP_LINE_23_NOT_NEGATIVE: 1,
            CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_33_POSITIVE: 0,
            CPP_LINE_16_POSITIVE: 1,
            CPP_LINE_23_AND_LINE_40_POSITIVE: 0,
            CPP_LINE_20_POSITIVE: 0,
            CPP_PART_3B_LINE_30: D("168.32"),
            CPP_PART_3B_LINE_31: D("0"),
            CPP_PART_3B_LINE_32: D("0"),
            CPP_PART_3B_LINE_33: D("0"),
            CPP_PART_3B_LINE_34: D("168.32"),
            CPP_PART_3B_LINE_35: D("0"),
            CPP_PART_3B_LINE_36: D("168.32"),
            CPP_PART_3B_LINE_37: D("34.00"),
            CPP_PART_3B_LINE_38: D("0.01"),
            CPP_PART_3B_LINE_39: D("0.01"),
            CPP_PART_3B_LINE_40: D("0.00"),
            CPP_PART_3B_LINE_41: D("34.01"),
            CPP_PART_3B_LINE_42: D("0"),
            CPP_PART_3B_LINE_43: D("34.01"),
            CPP_PART_3B_LINE_44: D("0.00"),
            CPP_PART_3B_LINE_45: D("0"),
            CPP_PART_3B_LINE_46: D("0"),
            CPP_PART_3B_LINE_47: D("0.00"),
            CPP_PART_3B_LINE_48: D("34.01"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("168.32"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("34.01"),
            CPP_OVERPAYMENT: D("0"),
        },
    )


def test_part_3b_with_a_cent_over_on_line_16_and_a_cent_under_on_line_23() -> None:
    # Box 16 of $4,034.11 is a cent over line 13 and box 16A of $395.99 a cent under line 22:
    # line 24 is 0.00, so Part 3b applies; line 16 is positive but line 19 is 0, so line 39 is
    # the lesser of 0.01 and 0 (line 38); line 20 is positive and line 23 negative, so line 46
    # is the lesser of 0.01 (line 20) and 0.01 (line 45).
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="4034.11",
        cpp_t4_second_additional_contributions="395.99",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("0.01"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.01"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-0.01"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_LINE_24_POSITIVE: 0,
            CPP_LINE_16_NOT_NEGATIVE: 1,
            CPP_LINE_19_NOT_NEGATIVE: 1,
            CPP_LINE_23_NOT_NEGATIVE: 0,
            CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_33_POSITIVE: 0,
            CPP_LINE_16_POSITIVE: 1,
            CPP_LINE_23_AND_LINE_40_POSITIVE: 0,
            CPP_LINE_20_POSITIVE: 1,
            CPP_PART_3B_LINE_30: D("3356.10"),
            CPP_PART_3B_LINE_31: D("0"),
            CPP_PART_3B_LINE_32: D("0"),
            CPP_PART_3B_LINE_33: D("0"),
            CPP_PART_3B_LINE_34: D("3356.10"),
            CPP_PART_3B_LINE_35: D("0"),
            CPP_PART_3B_LINE_36: D("3356.10"),
            CPP_PART_3B_LINE_37: D("678.00"),
            CPP_PART_3B_LINE_38: D("0"),
            CPP_PART_3B_LINE_39: D("0"),
            CPP_PART_3B_LINE_40: D("0"),
            CPP_PART_3B_LINE_41: D("678.00"),
            CPP_PART_3B_LINE_42: D("0"),
            CPP_PART_3B_LINE_43: D("678.00"),
            CPP_PART_3B_LINE_44: D("395.99"),
            CPP_PART_3B_LINE_45: D("0.01"),
            CPP_PART_3B_LINE_46: D("0.01"),
            CPP_PART_3B_LINE_47: D("396.00"),
            CPP_PART_3B_LINE_48: D("1074.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("3356.10"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("1074.00"),
            CPP_OVERPAYMENT: D("0"),
        },
    )


def test_part_3b_with_both_differences_negative_adds_back_lines_31_and_38() -> None:
    # Box 16 of $3,300.00 is 61.75 under line 13: line 16 and line 19 are both negative, line 23
    # is 0, so lines 32, 35, 39, 42 and 46 are all 0 and lines 31 and 38 are the shortfalls as
    # positive amounts.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3300.00",
        cpp_t4_second_additional_contributions="0",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("-51.37"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-10.38"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-61.75"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("0.00"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("-61.75"),
            CPP_LINE_24_POSITIVE: 0,
            CPP_LINE_16_NOT_NEGATIVE: 0,
            CPP_LINE_19_NOT_NEGATIVE: 0,
            CPP_LINE_23_NOT_NEGATIVE: 1,
            CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_33_POSITIVE: 0,
            CPP_LINE_16_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_40_POSITIVE: 0,
            CPP_LINE_20_POSITIVE: 0,
            CPP_PART_3B_LINE_30: D("2745.38"),
            CPP_PART_3B_LINE_31: D("51.37"),
            CPP_PART_3B_LINE_32: D("0"),
            CPP_PART_3B_LINE_33: D("51.37"),
            CPP_PART_3B_LINE_34: D("2745.38"),
            CPP_PART_3B_LINE_35: D("0"),
            CPP_PART_3B_LINE_36: D("2745.38"),
            CPP_PART_3B_LINE_37: D("554.62"),
            CPP_PART_3B_LINE_38: D("10.38"),
            CPP_PART_3B_LINE_39: D("0"),
            CPP_PART_3B_LINE_40: D("10.38"),
            CPP_PART_3B_LINE_41: D("554.62"),
            CPP_PART_3B_LINE_42: D("0"),
            CPP_PART_3B_LINE_43: D("554.62"),
            CPP_PART_3B_LINE_44: D("0.00"),
            CPP_PART_3B_LINE_45: D("0"),
            CPP_PART_3B_LINE_46: D("0"),
            CPP_PART_3B_LINE_47: D("0.00"),
            CPP_PART_3B_LINE_48: D("554.62"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2745.38"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("554.62"),
            CPP_OVERPAYMENT: D("0"),
        },
    )


def test_part_3b_line_35_takes_line_23_when_it_is_less_than_line_33() -> None:
    # Box 16 of $3,434.10 (600.00 under line 13) and box 16A of $401.00 (5.00 over line 22):
    # line 24 is -595.00, line 23 and line 33 are both positive and line 23 is the lesser, so
    # line 35 is 5.00; line 42 is then the lesser of line 40 and line 23 minus line 35, which is
    # 0.
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3434.10",
        cpp_t4_second_additional_contributions="401.00",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("-499.16"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-100.84"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-600.00"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("5.00"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("-595.00"),
            CPP_LINE_24_POSITIVE: 0,
            CPP_LINE_16_NOT_NEGATIVE: 0,
            CPP_LINE_19_NOT_NEGATIVE: 0,
            CPP_LINE_23_NOT_NEGATIVE: 1,
            CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_33_POSITIVE: 1,
            CPP_LINE_16_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_40_POSITIVE: 1,
            CPP_LINE_20_POSITIVE: 0,
            CPP_PART_3B_LINE_30: D("2856.94"),
            CPP_PART_3B_LINE_31: D("499.16"),
            CPP_PART_3B_LINE_32: D("0"),
            CPP_PART_3B_LINE_33: D("499.16"),
            CPP_PART_3B_LINE_34: D("2856.94"),
            CPP_PART_3B_LINE_35: D("5.00"),
            CPP_PART_3B_LINE_36: D("2861.94"),
            CPP_PART_3B_LINE_37: D("577.16"),
            CPP_PART_3B_LINE_38: D("100.84"),
            CPP_PART_3B_LINE_39: D("0"),
            CPP_PART_3B_LINE_40: D("100.84"),
            CPP_PART_3B_LINE_41: D("577.16"),
            CPP_PART_3B_LINE_42: D("0.00"),
            CPP_PART_3B_LINE_43: D("577.16"),
            CPP_PART_3B_LINE_44: D("396.00"),
            CPP_PART_3B_LINE_45: D("0"),
            CPP_PART_3B_LINE_46: D("0"),
            CPP_PART_3B_LINE_47: D("396.00"),
            CPP_PART_3B_LINE_48: D("973.16"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2861.94"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("973.16"),
            CPP_OVERPAYMENT: D("0"),
        },
    )


def test_part_3b_line_35_takes_line_33_and_line_42_the_rest_of_line_23() -> None:
    # Box 16 of $3,564.10 (470.00 under line 13) and box 16A of $791.00 (395.00 over line 22):
    # line 24 is -75.00. Line 33 (391.01) is less than line 23, so line 35 is 391.01 and line 42
    # is the lesser of line 40 (78.99) and line 23 minus line 35 (3.99), 3.99.
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3564.10",
        cpp_t4_second_additional_contributions="791.00",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("-391.01"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-78.99"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-470.00"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("395.00"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("-75.00"),
            CPP_LINE_24_POSITIVE: 0,
            CPP_LINE_16_NOT_NEGATIVE: 0,
            CPP_LINE_19_NOT_NEGATIVE: 0,
            CPP_LINE_23_NOT_NEGATIVE: 1,
            CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_33_POSITIVE: 1,
            CPP_LINE_16_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_40_POSITIVE: 1,
            CPP_LINE_20_POSITIVE: 0,
            CPP_PART_3B_LINE_30: D("2965.09"),
            CPP_PART_3B_LINE_31: D("391.01"),
            CPP_PART_3B_LINE_32: D("0"),
            CPP_PART_3B_LINE_33: D("391.01"),
            CPP_PART_3B_LINE_34: D("2965.09"),
            CPP_PART_3B_LINE_35: D("391.01"),
            CPP_PART_3B_LINE_36: D("3356.10"),
            CPP_PART_3B_LINE_37: D("599.01"),
            CPP_PART_3B_LINE_38: D("78.99"),
            CPP_PART_3B_LINE_39: D("0"),
            CPP_PART_3B_LINE_40: D("78.99"),
            CPP_PART_3B_LINE_41: D("599.01"),
            CPP_PART_3B_LINE_42: D("3.99"),
            CPP_PART_3B_LINE_43: D("603.00"),
            CPP_PART_3B_LINE_44: D("396.00"),
            CPP_PART_3B_LINE_45: D("0"),
            CPP_PART_3B_LINE_46: D("0"),
            CPP_PART_3B_LINE_47: D("396.00"),
            CPP_PART_3B_LINE_48: D("999.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("3356.10"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("999.00"),
            CPP_OVERPAYMENT: D("0"),
        },
    )


def test_part_3b_line_46_takes_line_20_when_line_23_is_negative_and_line_24_is_not_positive() -> (
    None
):
    # Box 16 of $4,100.00 (65.90 over line 13) and box 16A of $300.00 (96.00 under line 22):
    # line 24 is -30.10, so Part 3b applies; line 20 is positive and line 23 negative, so line
    # 46 is the lesser of line 20 (65.90) and line 45 (96.00), 65.90, and line 44 is line 21
    # (300.00).
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="4100.00",
        cpp_t4_second_additional_contributions="300",
    )

    assert_values(
        worksheet,
        {
            CPP_BASE_CONTRIBUTIONS_DIFFERENCE: D("54.83"),
            CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("11.07"),
            CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("65.90"),
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE: D("-96.00"),
            CPP_CONTRIBUTIONS_DIFFERENCE: D("-30.10"),
            CPP_LINE_24_POSITIVE: 0,
            CPP_LINE_16_NOT_NEGATIVE: 1,
            CPP_LINE_19_NOT_NEGATIVE: 1,
            CPP_LINE_23_NOT_NEGATIVE: 0,
            CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE: 0,
            CPP_LINE_23_AND_LINE_33_POSITIVE: 0,
            CPP_LINE_16_POSITIVE: 1,
            CPP_LINE_23_AND_LINE_40_POSITIVE: 0,
            CPP_LINE_20_POSITIVE: 1,
            CPP_PART_3B_LINE_30: D("3356.10"),
            CPP_PART_3B_LINE_31: D("0"),
            CPP_PART_3B_LINE_32: D("0"),
            CPP_PART_3B_LINE_33: D("0"),
            CPP_PART_3B_LINE_34: D("3356.10"),
            CPP_PART_3B_LINE_35: D("0"),
            CPP_PART_3B_LINE_36: D("3356.10"),
            CPP_PART_3B_LINE_37: D("678.00"),
            CPP_PART_3B_LINE_38: D("0"),
            CPP_PART_3B_LINE_39: D("0"),
            CPP_PART_3B_LINE_40: D("0"),
            CPP_PART_3B_LINE_41: D("678.00"),
            CPP_PART_3B_LINE_42: D("0"),
            CPP_PART_3B_LINE_43: D("678.00"),
            CPP_PART_3B_LINE_44: D("300"),
            CPP_PART_3B_LINE_45: D("96.00"),
            CPP_PART_3B_LINE_46: D("65.90"),
            CPP_PART_3B_LINE_47: D("365.90"),
            CPP_PART_3B_LINE_48: D("1043.90"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("3356.10"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("1043.90"),
            CPP_OVERPAYMENT: D("0"),
        },
    )


def test_part_3a_adds_the_overpayment_to_total_credits_and_changes_nothing_else() -> None:
    # Return BN as filed against the same return with box 16 equal to line 13: lines 30800 and
    # 22215 are the required 2,796.75 and 565.00 in both, so the only difference is line 44800,
    # 138.25, which joins total credits (T1 line 166) and lowers the balance owing by as much.
    base = compute_with_schedule_8("60000", (), "0", "0", "0", "0", "0", income_tax_deducted="5000")
    over = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        income_tax_deducted="5000",
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_t4_second_additional_contributions="0",
    )

    assert base.get(CPP_OVERPAYMENT).value == D("0")
    assert over.get(CPP_OVERPAYMENT).value == D("138.25")
    assert over.get(TOTAL_CREDITS).value - base.get(TOTAL_CREDITS).value == D("138.25")
    assert base.get(REFUND_OR_BALANCE_OWING).value - over.get(REFUND_OR_BALANCE_OWING).value == D(
        "138.25"
    )
    assert (
        over.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value
        == base.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value
    )
    assert (
        over.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == base.get(DEDUCTIONS_FROM_TOTAL_INCOME).value
    )


def test_part_3b_lines_36_and_48_feed_the_credit_and_the_deductions() -> None:
    # Box 16 of $3,300.00 against the required 3,361.75: line 30800 is line 36, 2,745.38, that is
    # 51.37 less than line 11, and line 22215 is line 48, 554.62, that is 10.38 less than line 12.
    # Each reader of line 30800 (the federal and Ontario credit amounts, ON428 line 58240) and of
    # line 22215 (the deductions and the minimum tax deductions) moves by exactly those amounts.
    base = compute_with_schedule_8("60000", (), "0", "0", "0", "0", "0")
    short = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3300.00",
        cpp_t4_second_additional_contributions="0",
    )

    assert base.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2796.75")
    assert short.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2745.38")
    assert short.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value - base.get(
        NON_REFUNDABLE_CREDIT_AMOUNTS
    ).value == D("-51.37")
    assert short.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value - base.get(
        ontario.NON_REFUNDABLE_CREDIT_AMOUNTS
    ).value == D("-51.37")
    assert base.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("565.00")
    assert short.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("554.62")
    assert short.get(DEDUCTIONS_FROM_TOTAL_INCOME).value - base.get(
        DEDUCTIONS_FROM_TOTAL_INCOME
    ).value == D("-10.38")
    assert short.get(AMT_DEDUCTIONS_TOTAL).value - base.get(AMT_DEDUCTIONS_TOTAL).value == D(
        "-10.38"
    )
    # The required lines 11, 12 and 22 are unchanged: only the routing differs.
    assert short.get(CPP_BASE_CONTRIBUTIONS).value == base.get(CPP_BASE_CONTRIBUTIONS).value
    assert short.get(CPP_ENHANCED_CONTRIBUTIONS).value == base.get(CPP_ENHANCED_CONTRIBUTIONS).value


def chosen_lines(worksheet: ReturnAndSchedule8) -> dict[ArtifactKind[Any], ChosenByCountLine]:
    return {line.output: line for line in worksheet.trace if isinstance(line, ChosenByCountLine)}


def test_the_trace_names_the_part_the_three_return_lines_were_taken_from() -> None:
    # Line 24 positive: Part 3a line 25 (line 15, the amount from line 11), line 28 and line 29,
    # the Part 3 route that Part 5 replaces when it is completed.
    positive = chosen_lines(
        compute_with_schedule_8(
            "60000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            cpp_t4_base_and_first_additional_contributions="3500.00",
            cpp_t4_second_additional_contributions="0",
        )
    )
    assert positive[CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN] == ChosenByCountLine(
        output=CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN,
        count_kind=CPP_LINE_24_POSITIVE,
        count=1,
        chosen_kind=CPP_BASE_CONTRIBUTIONS,
        chosen_value=D("2796.75"),
    )
    assert positive[CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN] == ChosenByCountLine(
        output=CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN,
        count_kind=CPP_LINE_24_POSITIVE,
        count=1,
        chosen_kind=CPP_ENHANCED_CONTRIBUTIONS,
        chosen_value=D("565.00"),
    )
    assert positive[CPP_PART_3_OVERPAYMENT] == ChosenByCountLine(
        output=CPP_PART_3_OVERPAYMENT,
        count_kind=CPP_LINE_24_POSITIVE,
        count=1,
        chosen_kind=CPP_CONTRIBUTIONS_DIFFERENCE,
        chosen_value=D("138.25"),
    )
    # Line 24 "0" or negative: Part 3b line 36 and line 48, and "0" for the overpayment.
    zero = chosen_lines(compute_with_schedule_8("60000", (), "0", "0", "0", "0", "0"))
    assert zero[CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN] == ChosenByCountLine(
        output=CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN,
        count_kind=CPP_LINE_24_POSITIVE,
        count=0,
        chosen_kind=CPP_PART_3B_LINE_36,
        chosen_value=D("2796.75"),
    )
    assert zero[CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN] == ChosenByCountLine(
        output=CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN,
        count_kind=CPP_LINE_24_POSITIVE,
        count=0,
        chosen_kind=CPP_PART_3B_LINE_48,
        chosen_value=D("565.00"),
    )
    assert zero[CPP_PART_3_OVERPAYMENT] == ChosenByCountLine(
        output=CPP_PART_3_OVERPAYMENT,
        count_kind=CPP_LINE_24_POSITIVE,
        count=0,
        chosen_kind=CPP_ZERO,
        chosen_value=D("0"),
    )
    # Line 30 of Part 3b chooses between line 9 ("amount from line 14") and line 11, by line 16.
    short = chosen_lines(
        compute_with_schedule_8(
            "60000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            cpp_t4_base_and_first_additional_contributions="3300.00",
            cpp_t4_second_additional_contributions="0",
        )
    )
    assert short[CPP_PART_3B_LINE_30] == ChosenByCountLine(
        output=CPP_PART_3B_LINE_30,
        count_kind=CPP_LINE_16_NOT_NEGATIVE,
        count=0,
        chosen_kind=CPP_ACTUAL_BASE_CONTRIBUTIONS,
        chosen_value=D("2745.38"),
    )
    assert zero[CPP_PART_3B_LINE_30] == ChosenByCountLine(
        output=CPP_PART_3B_LINE_30,
        count_kind=CPP_LINE_16_NOT_NEGATIVE,
        count=1,
        chosen_kind=CPP_BASE_CONTRIBUTIONS,
        chosen_value=D("2796.75"),
    )


# Schedule 8 Part 5 lines 1 to 42 (lines 30 and 42 are read by lines 43 to 45 and declared outputs
# as well). Every figure below is derived by hand from the form's
# lines, in order, from the employment income, the self-employment income (T1 line 23, which is
# line 27 of the return), the two T4 totals and the two CPT20 amounts. Without a T4 total given, box
# 16 and 16A are the required contributions (see `required_cpp_contributions`), so lines 20 and 23
# of Part 3 are 0. The cases: (a) the worked example, employment income 60,000 and line 27 of
# 20,000; (b) employment income above 71,300; (c) T4 contributions above and below the required
# ones, hitting lines 6, 15, 8 and 9; (d) CPT20 earnings; (e) employment income below the
# exemption, hitting lines 25 and 29; no self-employment income; and a loss.


def test_part_5_with_employment_income_of_60000_and_line_27_of_20000_prints_the_form() -> None:
    # Case (a), the worked example. Part 3 for employment income of $60,000: line 11 is 4.95%
    # x 56,500 = 2,796.75, line 12 is 1% x 56,500 = 565.00, line 13 is 3,361.75 and line 22 is
    # 0. The T4 box 16 total is the required 3,361.75, so Part 3 line 9 is 2,796.75 and line 10
    # is 565.00; lines 16, 19, 20 and 23 are 0. Part 5: line 1 is 20,000 (line 12200 of 0 plus
    # line 27 of 20,000), lines 2 and 3 are 0, line 4 is 20,000. Line 5 is 3,361.75, line 6 is 0
    # (line 20 of Part 3 is not positive) and line 7 is 3,361.75; lines 8 and 9 are 0 (line 20
    # of Part 3 is not negative) and line 10 is 3,361.75. Lines 11 to 16 are 0 (box 16A of 0,
    # line 23 of 0). Line 17 is 71,300 and line 18 is 3,500, so line 19 is 67,800. Line 20 is
    # 3,361.75 x 16.80672 = 56,499.99096, to the cent 56,499.99 (not 56,500.00), line 21 is
    # 67,800 - 56,499.99 = 11,300.01 and line 22, the lesser of line 4 (20,000) and line 21, is
    # 11,300.01. Employment income of 60,000 is not less than line 18, so line 25 is 0 and so is
    # line 29 (line 28 is 20,000 - 67,800, below zero, so 0); line 30 is 11,300.01. Line 32 is
    # the lesser of 81,200 and 60,000, 60,000, and line 33 is 80,000, more than 71,300, so lines
    # 34 to 42 are computed: line 34 is 9,900, line 35 is 0 / 4% = 0, line 36 is 9,900, line 37
    # is 20,000, line 38 is 0, line 39 is 20,000, line 40 is 11,300.01, line 41 is 8,699.99 and
    # line 42, the lesser of lines 36 and 41, is 8,699.99.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("20000"),
            CPP_PART_5_LINE_6: D("0"),
            CPP_PART_5_LINE_7: D("3361.75"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("3361.75"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("0"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("0"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("56499.99"),
            CPP_PART_5_LINE_21: D("11300.01"),
            CPP_PART_5_LINE_22: D("11300.01"),
            CPP_PART_5_LINE_25: D("0"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("0"),
            CPP_PART_5_LINE_30: D("11300.01"),
            CPP_PART_5_LINE_33: D("80000"),
            CPP_PART_5_LINE_35: D("0"),
            CPP_PART_5_LINE_36: D("9900"),
            CPP_PART_5_LINE_39: D("20000"),
            CPP_PART_5_LINE_41: D("8699.99"),
            CPP_PART_5_LINE_42: D("8699.99"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 1,
        },
    )


def test_part_5_lines_34_to_42_use_line_16_when_employment_income_is_above_71300() -> None:
    # Case (b). Employment income of $80,000 and line 27 of 15,000. Part 3: line 11 is 4.95% x
    # 67,800 = 3,356.10 (the maximum), line 12 is 678.00, line 13 is 4,034.10 and line 22 is 4%
    # x (80,000 - 71,300) = 348.00; the T4 totals are the required 4,034.10 and 348.00, so lines
    # 16, 19, 20 and 23 of Part 3 are 0. Part 5: line 4 is 15,000, line 7 is 4,034.10 and line
    # 10 is 4,034.10; line 11 is 348.00, line 12 is 0, line 13 is 348.00 and line 16 is 348.00.
    # Line 19 is 67,800 and line 20 is 4,034.10 x 16.80672 = 67,799.989152, to the cent
    # 67,799.99, so line 21 is 0.01 and line 22, the lesser of 15,000 and 0.01, is 0.01; lines
    # 25, 28 and 29 are 0 and line 30 is 0.01. Line 32 is 80,000 and line 33 is 95,000, more
    # than 71,300: line 34 is 9,900, line 35 is 348.00 / 4% = 8,700.00, line 36 is 1,200.00,
    # line 37 is 15,000, line 38 is 0, line 39 is 15,000, line 40 is 0.01, line 41 is 14,999.99
    # and line 42, the lesser of 1,200.00 and 14,999.99, is 1,200.00.
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("15000"),
            CPP_PART_5_LINE_6: D("0"),
            CPP_PART_5_LINE_7: D("4034.1"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("4034.1"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("348"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("348"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("67799.99"),
            CPP_PART_5_LINE_21: D("0.01"),
            CPP_PART_5_LINE_22: D("0.01"),
            CPP_PART_5_LINE_25: D("0"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("0"),
            CPP_PART_5_LINE_30: D("0.01"),
            CPP_PART_5_LINE_33: D("95000"),
            CPP_PART_5_LINE_35: D("8700"),
            CPP_PART_5_LINE_36: D("1200"),
            CPP_PART_5_LINE_39: D("15000"),
            CPP_PART_5_LINE_41: D("14999.99"),
            CPP_PART_5_LINE_42: D("1200"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 1,
        },
    )


def test_part_5_line_6_takes_the_overpaid_line_20_of_part_3_off_line_5() -> None:
    # Case (c), contributions above the required ones: Return BN as filed, employment income of
    # $60,000 with the T4 box 16 total of 3,500.00 (138.25 more than line 13) and line 27 of
    # 20,000. Part 3: line 9 is 2,911.77, line 10 is 588.23, line 16 is 115.02, line 19 is
    # 23.23, line 20 is 138.25 and line 23 is 0. Part 5: line 5 is 3,500.00, line 6 is 138.25
    # (line 20 of Part 3, positive) and line 7 is 3,500.00 - 138.25 = 3,361.75, so line 10 is
    # 3,361.75 as in case (a) (line 20 of Part 3 is not negative, so lines 8 and 9 are 0) and
    # lines 19 to 42 are the same as in case (a).
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3500.00",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("20000"),
            CPP_PART_5_LINE_6: D("138.25"),
            CPP_PART_5_LINE_7: D("3361.75"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("3361.75"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("0"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("0"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("56499.99"),
            CPP_PART_5_LINE_21: D("11300.01"),
            CPP_PART_5_LINE_22: D("11300.01"),
            CPP_PART_5_LINE_25: D("0"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("0"),
            CPP_PART_5_LINE_30: D("11300.01"),
            CPP_PART_5_LINE_33: D("80000"),
            CPP_PART_5_LINE_35: D("0"),
            CPP_PART_5_LINE_36: D("9900"),
            CPP_PART_5_LINE_39: D("20000"),
            CPP_PART_5_LINE_41: D("8699.99"),
            CPP_PART_5_LINE_42: D("8699.99"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 1,
        },
    )


def test_part_5_line_15_is_the_lesser_of_line_20_of_part_3_and_line_14() -> None:
    # Case (c), line 20 of Part 3 positive and line 23 negative. Employment income of $80,000
    # and line 27 of 15,000, with box 16 of 4,100.00 and box 16A of 300.00 (required 4,034.10
    # and 348.00). Part 3: line 9 is 3,410.9253, to the cent 3,410.93, line 10 is 689.07, line
    # 16 is 3,410.93 - 3,356.10 = 54.83, line 19 is 689.07 - 678.00 = 11.07, line 20 is 65.90
    # and line 23 is 300.00 - 348.00 = -48.00. Part 5: line 6 is 65.90 and line 7 is 4,100.00 -
    # 65.90 = 4,034.10; line 8 is 0 (line 20 is not negative), line 9 is 0 and line 10 is
    # 4,034.10. Line 11 is 300.00, line 12 is 0 (line 23 is negative) and line 13 is 300.00;
    # line 14 is 48.00 and line 15, the lesser of line 20 of Part 3 (65.90) and line 14 (48.00),
    # is 48.00; line 16 is 300.00 + 48.00 = 348.00. Lines 17 to 42 are those of case (b).
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_t4_base_and_first_additional_contributions="4100.00",
        cpp_t4_second_additional_contributions="300.00",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("15000"),
            CPP_PART_5_LINE_6: D("65.90"),
            CPP_PART_5_LINE_7: D("4034.10"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("4034.10"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("300.00"),
            CPP_PART_5_LINE_14: D("48.00"),
            CPP_PART_5_LINE_15: D("48.00"),
            CPP_PART_5_LINE_16: D("348.00"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("67799.99"),
            CPP_PART_5_LINE_21: D("0.01"),
            CPP_PART_5_LINE_22: D("0.01"),
            CPP_PART_5_LINE_25: D("0"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("0"),
            CPP_PART_5_LINE_30: D("0.01"),
            CPP_PART_5_LINE_33: D("95000"),
            CPP_PART_5_LINE_35: D("8700"),
            CPP_PART_5_LINE_36: D("1200"),
            CPP_PART_5_LINE_39: D("15000"),
            CPP_PART_5_LINE_41: D("14999.99"),
            CPP_PART_5_LINE_42: D("1200"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 1,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 1,
        },
    )


def test_part_5_line_9_is_the_lesser_of_line_23_of_part_3_and_line_8() -> None:
    # Case (c), line 20 of Part 3 negative and line 23 positive. Employment income of $80,000
    # and line 27 of 15,000, with box 16 of 4,000.00 and box 16A of 400.00. Part 3: line 9 is
    # 3,327.732, to the cent 3,327.73, line 10 is 672.27, line 16 is 3,327.73 - 3,356.10 =
    # -28.37, line 19 is 672.27 - 678.00 = -5.73, line 20 is -34.10 and line 23 is 400.00 -
    # 348.00 = 52.00. Part 5: line 6 is 0 (line 20 is negative) and line 7 is 4,000.00; line 8
    # is 34.10 and line 9, the lesser of line 23 of Part 3 (52.00) and line 8 (34.10), is 34.10;
    # line 10 is 4,034.10. Line 11 is 400.00, line 12 is 52.00 and line 13 is 348.00; line 14
    # and line 15 are 0 (line 20 is not positive) and line 16 is 348.00. Lines 17 to 42 are
    # those of case (b).
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_t4_base_and_first_additional_contributions="4000.00",
        cpp_t4_second_additional_contributions="400.00",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("15000"),
            CPP_PART_5_LINE_6: D("0"),
            CPP_PART_5_LINE_7: D("4000.00"),
            CPP_PART_5_LINE_8: D("34.10"),
            CPP_PART_5_LINE_9: D("34.10"),
            CPP_PART_5_LINE_10: D("4034.10"),
            CPP_PART_5_LINE_12: D("52.00"),
            CPP_PART_5_LINE_13: D("348.00"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("348.00"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("67799.99"),
            CPP_PART_5_LINE_21: D("0.01"),
            CPP_PART_5_LINE_22: D("0.01"),
            CPP_PART_5_LINE_25: D("0"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("0"),
            CPP_PART_5_LINE_30: D("0.01"),
            CPP_PART_5_LINE_33: D("95000"),
            CPP_PART_5_LINE_35: D("8700"),
            CPP_PART_5_LINE_36: D("1200"),
            CPP_PART_5_LINE_39: D("15000"),
            CPP_PART_5_LINE_41: D("14999.99"),
            CPP_PART_5_LINE_42: D("1200"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 1,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 1,
        },
    )


def test_part_5_line_3_adds_the_cpt20_earnings_shown_on_a_t4_slip() -> None:
    # Case (d). Employment income of $60,000, line 27 of 20,000, CPT20 earnings not on a T4 slip
    # (line 2) of 3,000 and on a T4 slip (line 3) of 5,000, with box 16 the required 3,361.75.
    # Part 3 and lines 5 to 21 are those of case (a). Line 4 is 20,000 + 3,000 + 5,000 = 28,000,
    # so line 22 is the lesser of 28,000 and 11,300.01, 11,300.01, and line 30 is 11,300.01.
    # Line 33 is 28,000 + 60,000 = 88,000: line 36 is 9,900, line 39 is 28,000, line 41 is
    # 28,000 - 11,300.01 = 16,699.99 and line 42, the lesser of 9,900 and 16,699.99, is 9,900.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpt20_earnings="3000",
        cpt20_t4_earnings="5000",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("28000"),
            CPP_PART_5_LINE_6: D("0"),
            CPP_PART_5_LINE_7: D("3361.75"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("3361.75"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("0"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("0"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("56499.99"),
            CPP_PART_5_LINE_21: D("11300.01"),
            CPP_PART_5_LINE_22: D("11300.01"),
            CPP_PART_5_LINE_25: D("0"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("0"),
            CPP_PART_5_LINE_30: D("11300.01"),
            CPP_PART_5_LINE_33: D("88000"),
            CPP_PART_5_LINE_35: D("0"),
            CPP_PART_5_LINE_36: D("9900"),
            CPP_PART_5_LINE_39: D("28000"),
            CPP_PART_5_LINE_41: D("16699.99"),
            CPP_PART_5_LINE_42: D("9900"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 1,
        },
    )


def test_part_5_lines_25_and_29_when_employment_income_is_below_the_exemption() -> None:
    # Case (e). Employment income of $2,000, below the 3,500 of line 18, and line 27 of 40,000;
    # no T4 contributions are required (Part 3 lines 7 to 24 are 0). Part 5: line 4 is 40,000,
    # lines 5 to 18 are 0 or the limits (line 19 is 67,800) and line 20 is 0, so line 21 is
    # 67,800 and line 22 is 40,000. Line 24 (employment income) is 2,000, less than line 23
    # (3,500): line 25 is 1,500. Line 28 is 40,000 - 67,800, below zero, so 0, and line 29 is
    # 1,500 - 0 = 1,500; line 30 is 40,000 - 1,500 = 38,500. Line 32 is 2,000 and line 33 is
    # 42,000, not more than 71,300, so line 42 is 0 (lines 34 to 41 are still computed: line 36
    # is 9,900, line 39 is 40,000 - 1,500 = 38,500 and line 41 is 38,500 - 38,500 = 0).
    worksheet = compute_with_schedule_8(
        "2000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("40000", 2),),
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("40000"),
            CPP_PART_5_LINE_6: D("0"),
            CPP_PART_5_LINE_7: D("0"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("0"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("0"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("0"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("0"),
            CPP_PART_5_LINE_21: D("67800"),
            CPP_PART_5_LINE_22: D("40000"),
            CPP_PART_5_LINE_25: D("1500"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("1500"),
            CPP_PART_5_LINE_30: D("38500"),
            CPP_PART_5_LINE_33: D("42000"),
            CPP_PART_5_LINE_35: D("0"),
            CPP_PART_5_LINE_36: D("9900"),
            CPP_PART_5_LINE_39: D("38500"),
            CPP_PART_5_LINE_41: D("0"),
            CPP_PART_5_LINE_42: D("0"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 0,
        },
    )


def test_part_5_line_28_takes_what_line_4_has_over_line_19_off_line_29() -> None:
    # Case (e), with line 27 of 68,800. Employment income of $2,000, so line 25 is 1,500. Line 4
    # is 68,800, line 21 is 67,800 and line 22, the lesser of the two, is 67,800. Line 28 is
    # 68,800 - 67,800 = 1,000, so line 29 is 1,500 - 1,000 = 500 and line 30 is 67,800 - 500 =
    # 67,300. Line 33 is 68,800 + 2,000 = 70,800, not more than 71,300, so line 42 is 0 (line 39
    # is 68,800 - 1,500 = 67,300 and line 41 is 67,300 - 67,300 = 0).
    worksheet = compute_with_schedule_8(
        "2000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("68800", 2),),
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("68800"),
            CPP_PART_5_LINE_6: D("0"),
            CPP_PART_5_LINE_7: D("0"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("0"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("0"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("0"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("0"),
            CPP_PART_5_LINE_21: D("67800"),
            CPP_PART_5_LINE_22: D("67800"),
            CPP_PART_5_LINE_25: D("1500"),
            CPP_PART_5_LINE_28: D("1000"),
            CPP_PART_5_LINE_29: D("500"),
            CPP_PART_5_LINE_30: D("67300"),
            CPP_PART_5_LINE_33: D("70800"),
            CPP_PART_5_LINE_35: D("0"),
            CPP_PART_5_LINE_36: D("9900"),
            CPP_PART_5_LINE_39: D("67300"),
            CPP_PART_5_LINE_41: D("0"),
            CPP_PART_5_LINE_42: D("0"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 0,
        },
    )


def test_part_5_without_self_employment_income_only_the_part_3_lines_are_not_zero() -> None:
    # No self-employment income and no CPT20 earnings: employment income of $60,000 with box 16
    # the required 3,361.75. Lines 1 to 4, 22, 30, 39, 41 and 42 are 0; lines 7 and 10 are the
    # T4 box 16 total, 3,361.75 (lines 5 and 20 of Part 3 are not positive, so lines 6 and 8 are
    # 0), lines 19, 20 and 21 are 67,800, 56,499.99 and 11,300.01 as in case (a), and line 36 is
    # 9,900; line 33 is the 60,000 of Part 3 line 2, not more than 71,300.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("0"),
            CPP_PART_5_LINE_6: D("0"),
            CPP_PART_5_LINE_7: D("3361.75"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("3361.75"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("0"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("0"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("56499.99"),
            CPP_PART_5_LINE_21: D("11300.01"),
            CPP_PART_5_LINE_22: D("0"),
            CPP_PART_5_LINE_25: D("0"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("0"),
            CPP_PART_5_LINE_30: D("0"),
            CPP_PART_5_LINE_33: D("60000"),
            CPP_PART_5_LINE_35: D("0"),
            CPP_PART_5_LINE_36: D("9900"),
            CPP_PART_5_LINE_39: D("0"),
            CPP_PART_5_LINE_41: D("0"),
            CPP_PART_5_LINE_42: D("0"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 0,
        },
    )


def test_part_5_without_self_employment_income_lines_13_16_and_35_come_from_box_16a() -> None:
    # No self-employment income and employment income of $80,000: box 16A is the required
    # 348.00, so line 13 and line 16 are 348.00 and line 35 is 348.00 / 4% = 8,700.00, line 36
    # is 1,200.00. Line 33 is 80,000, more than 71,300, so line 42 is the lesser of 1,200.00 and
    # line 41 (0 - 0 = 0), 0. Line 20 is 4,034.10 x 16.80672 = 67,799.99 and line 21 is 0.01.
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("0"),
            CPP_PART_5_LINE_6: D("0"),
            CPP_PART_5_LINE_7: D("4034.1"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("4034.1"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("348"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("348"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("67799.99"),
            CPP_PART_5_LINE_21: D("0.01"),
            CPP_PART_5_LINE_22: D("0"),
            CPP_PART_5_LINE_25: D("0"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("0"),
            CPP_PART_5_LINE_30: D("0"),
            CPP_PART_5_LINE_33: D("80000"),
            CPP_PART_5_LINE_35: D("8700"),
            CPP_PART_5_LINE_36: D("1200"),
            CPP_PART_5_LINE_39: D("0"),
            CPP_PART_5_LINE_41: D("0"),
            CPP_PART_5_LINE_42: D("0"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 1,
        },
    )


def test_part_5_line_42_is_negative_when_line_4_is_a_loss_and_line_33_is_above_71300() -> None:
    # A loss: employment income of $80,000 and line 27 of -5,000 (professional income). Line 4
    # prints no floor, so it is -5,000, line 22 is the lesser of -5,000 and 0.01, -5,000, and
    # lines 25, 28, 29 and 30 are 0 (line 30 is -5,000 - 0, below zero, so 0). Line 33 is -5,000
    # + 80,000 = 75,000, more than 71,300: line 36 is 9,900 - 8,700.00 = 1,200.00, line 39 is
    # -5,000, line 40 is 0, line 41 is -5,000 and line 42, the lesser of 1,200.00 and -5,000, is
    # -5,000: the form prints no floor on lines 36 to 42, so line 42 is signed (a later change
    # decides what lines 45 and 46 do with it).
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("-5000", 2),),
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_4: D("-5000"),
            CPP_PART_5_LINE_6: D("0"),
            CPP_PART_5_LINE_7: D("4034.1"),
            CPP_PART_5_LINE_8: D("0"),
            CPP_PART_5_LINE_9: D("0"),
            CPP_PART_5_LINE_10: D("4034.1"),
            CPP_PART_5_LINE_12: D("0"),
            CPP_PART_5_LINE_13: D("348"),
            CPP_PART_5_LINE_14: D("0"),
            CPP_PART_5_LINE_15: D("0"),
            CPP_PART_5_LINE_16: D("348"),
            CPP_PART_5_LINE_19: D("67800"),
            CPP_PART_5_LINE_20: D("67799.99"),
            CPP_PART_5_LINE_21: D("0.01"),
            CPP_PART_5_LINE_22: D("-5000"),
            CPP_PART_5_LINE_25: D("0"),
            CPP_PART_5_LINE_28: D("0"),
            CPP_PART_5_LINE_29: D("0"),
            CPP_PART_5_LINE_30: D("0"),
            CPP_PART_5_LINE_33: D("75000"),
            CPP_PART_5_LINE_35: D("8700"),
            CPP_PART_5_LINE_36: D("1200"),
            CPP_PART_5_LINE_39: D("-5000"),
            CPP_PART_5_LINE_41: D("-5000"),
            CPP_PART_5_LINE_42: D("-5000"),
            CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE: 0,
            CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE: 0,
            CPP_PART_5_LINE_33_MORE_THAN_LINE_17: 1,
        },
    )


def test_part_5_changes_no_other_line_of_the_return() -> None:
    # Part 5 is not completed, so none of its lines is routed to the return: the CPT20 earnings
    # shown on a T4 slip (line 3) feed Part 5 alone, so the deductions, the credits and the balance
    # owing do not move.
    without = compute_with_schedule_8(
        "60000", (), "0", "0", "0", "0", "0", business_statements=(routed_statement("20000", 2),)
    )
    with_cpt20 = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpt20_t4_earnings="5000",
    )

    assert with_cpt20.get(CPP_PART_5_LINE_4).value == D("25000")
    assert without.get(CPP_PART_5_LINE_4).value == D("20000")
    for kind in (DEDUCTIONS_FROM_TOTAL_INCOME, TOTAL_CREDITS, REFUND_OR_BALANCE_OWING):
        assert with_cpt20.get(kind).value == without.get(kind).value, kind.identifier


def part_5_trace(worksheet: ReturnAndSchedule8, line_type: type) -> dict[ArtifactKind[Any], Any]:
    lines: list[Any] = [line for line in worksheet.trace if isinstance(line, line_type)]
    return {line.output: line for line in lines}


def test_the_trace_records_line_20_as_a_fraction_and_line_35_as_a_division() -> None:
    # Case (a): line 20 is line 10 of 3,361.75 times 16.80672 (a fraction, 1,680,672 / 100,000, to
    # the cent: 56,499.99096 is 56,499.99).
    case_a = compute_with_schedule_8(
        "60000", (), "0", "0", "0", "0", "0", business_statements=(routed_statement("20000", 2),)
    )
    assert part_5_trace(case_a, FractionAppliedLine)[CPP_PART_5_LINE_20] == FractionAppliedLine(
        output=CPP_PART_5_LINE_20,
        base=CPP_PART_5_LINE_10,
        base_amount=D("3361.75"),
        fraction=Fraction(1680672, 100000),
        rounding=CENT,
        result=D("56499.99"),
    )
    # Case (b): line 35 is line 16 of 348.00 divided by 4%, 8,700.00.
    case_b = compute_with_schedule_8(
        "80000", (), "0", "0", "0", "0", "0", business_statements=(routed_statement("15000", 2),)
    )
    assert part_5_trace(case_b, DividedByRateLine)[CPP_PART_5_LINE_35] == DividedByRateLine(
        output=CPP_PART_5_LINE_35,
        dividend=CPP_PART_5_LINE_16,
        dividend_amount=D("348.00"),
        rate=Rate(D("0.04")),
        rounding=CENT,
        result=D("8700.00"),
    )


def test_the_trace_names_the_candidate_lines_9_15_and_42_took_or_the_zero() -> None:
    # Line 9 takes its lesser (34.10) when line 20 of Part 3 is negative and line 23 positive.
    case_c3 = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_t4_base_and_first_additional_contributions="4000.00",
        cpp_t4_second_additional_contributions="400.00",
    )
    chosen = part_5_trace(case_c3, ChosenByCountLine)
    assert chosen[CPP_PART_5_LINE_9] == ChosenByCountLine(
        output=CPP_PART_5_LINE_9,
        count_kind=CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE,
        count=1,
        chosen_kind=CPP_PART_5_LINE_9_LESSER,
        chosen_value=D("34.10"),
    )
    assert chosen[CPP_PART_5_LINE_15] == ChosenByCountLine(
        output=CPP_PART_5_LINE_15,
        count_kind=CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE,
        count=0,
        chosen_kind=CPP_ZERO,
        chosen_value=D("0"),
    )
    # Line 15 takes its lesser (48.00) when line 20 of Part 3 is positive and line 23 negative.
    case_c2 = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_t4_base_and_first_additional_contributions="4100.00",
        cpp_t4_second_additional_contributions="300.00",
    )
    chosen = part_5_trace(case_c2, ChosenByCountLine)
    assert chosen[CPP_PART_5_LINE_15] == ChosenByCountLine(
        output=CPP_PART_5_LINE_15,
        count_kind=CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE,
        count=1,
        chosen_kind=CPP_PART_5_LINE_15_LESSER,
        chosen_value=D("48.00"),
    )
    # Line 42 takes its lesser (8,699.99) when line 33 is more than line 17, else "0".
    case_a = compute_with_schedule_8(
        "60000", (), "0", "0", "0", "0", "0", business_statements=(routed_statement("20000", 2),)
    )
    assert part_5_trace(case_a, ChosenByCountLine)[CPP_PART_5_LINE_42] == ChosenByCountLine(
        output=CPP_PART_5_LINE_42,
        count_kind=CPP_PART_5_LINE_33_MORE_THAN_LINE_17,
        count=1,
        chosen_kind=CPP_PART_5_LINE_42_LESSER,
        chosen_value=D("8699.99"),
    )
    below = compute_with_schedule_8(
        "2000", (), "0", "0", "0", "0", "0", business_statements=(routed_statement("40000", 2),)
    )
    assert part_5_trace(below, ChosenByCountLine)[CPP_PART_5_LINE_42] == ChosenByCountLine(
        output=CPP_PART_5_LINE_42,
        count_kind=CPP_PART_5_LINE_33_MORE_THAN_LINE_17,
        count=0,
        chosen_kind=CPP_ZERO,
        chosen_value=D("0"),
    )


# Schedule 8 Part 5 lines 43 to 69 (lines 49, 50, 57 and 69 are routed to lines 42100, 44800,
# 30800 and 22215 by the cases at the end of this file). Every figure below is derived
# by hand from the form's lines, in order, from the employment income, the self-employment income
# (T1 line 23, which is line 27 of the return) and the two T4 totals; the Part 3 lines and Part 5
# lines 1 to 42 are those of the cases above. Lines 51 to 69 repeat Part 3b lines 30 to 48 with the
# same formulas (line 51 is 3b line 30, line 57 is 3b line 36, line 69 is 3b line 48), so for the
# same Part 3 figures they equal 3b's. Without a T4 total given, box 16 and 16A are the required
# contributions, so lines 16, 19, 20, 23 and 24 of Part 3 are 0. The cases: (a) the ticket's
# example, employment income 60,000 and line 27 of 20,000; (b) employment income above 71,300 (line
# 45 not 0); (c) T4 contributions above the required ones (line 24 positive: line 48, and lines 66
# and 67); (d) line 24 positive and line 49 negative, in brackets, with line 50; (e) the lines 51
# to 69 branches for T4 contributions below the required ones (lines 16 and 19 negative, line 23
# positive or negative); (f) no self-employment income; and a loss with employment income above
# 71,300 (line 45 is 0). No case reaches line 16 negative with line 19 positive: line 19 is box 16
# less line 13 minus line 16, and for every line 7 from 0 to 67,800.00 and box 16 from a cent
# under line 13 to three cents over it, line 16 and line 19 are both negative, both non-negative,
# or line 16 positive and line 19 negative, so line 53 is always 0 (the count
# `ca/cpp_line_16_negative_line_19_positive` is 0 and line 54 is line 52); line 60 takes line 59
# over line 16 only as a tie (0.01 each).


def test_part_5_lines_43_to_69_for_employment_income_of_60000_and_line_27_of_20000() -> None:
    # Case (a), the ticket's example. Part 3 for employment income of $60,000 with box 16 the
    # required 3,361.75 and box 16A of 0: line 11 is 4.95% x 56,500 = 2,796.75, line 12 is 1% x
    # 56,500 = 565.00, line 22 is 0, lines 16, 19, 20, 23 and 24 are 0 and line 9 is 2,796.75
    # and line 10 565.00. Part 5 lines 1 to 42 (line 4 = 20,000): line 30 is 11,300.01 and line
    # 42 is 8,699.99. Line 43 is 9.9% x 11,300.01 = 1,118.70099, to the cent 1,118.70; line 44
    # is 2% x 11,300.01 = 226.0002, 226.00; line 45 is 8% x 8,699.99 = 695.9992, 696.00. Line 46
    # is 226.00 + 696.00 = 922.00 and line 47 is 1,118.70 + 922.00 = 2,040.70. Line 48 is 2 x
    # line 24 if positive, and line 24 is 0, so 0. Line 49 is 2,040.70 - 0 = 2,040.70, positive
    # (line 42100 later), so line 50 (line 49 as a positive amount x 50%, and a positive line 49
    # is not negative) is 0. Line 16 of Part 3 is 0, positive or "0", so line 51 is line 11,
    # 2,796.75; line 52 is 0 and so are lines 53 and 54; line 55 is 2,796.75. Line 23 is 0, so
    # line 56 is 0 and line 57 is 2,796.75. Line 19 is 0, so line 58 is line 12, 565.00; lines
    # 59 to 61 are 0 (line 16 is not positive, so line 60 is 0), line 62 is 565.00, line 63 is 0
    # and line 64 is 565.00. Line 23 is 0, so line 65 is line 22, 0; lines 66 to 68 are 0 and
    # line 69 is 565.00 + 0 = 565.00.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("11300.01"),
            CPP_PART_5_LINE_42: D("8699.99"),
            CPP_PART_5_LINE_43: D("1118.70"),
            CPP_PART_5_LINE_44: D("226.00"),
            CPP_PART_5_LINE_45: D("696.00"),
            CPP_PART_5_LINE_46: D("922.00"),
            CPP_PART_5_LINE_47: D("2040.70"),
            CPP_PART_5_LINE_48: D("0.00"),
            CPP_PART_5_LINE_49: D("2040.70"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("2796.75"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("2796.75"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_58: D("565.00"),
            CPP_PART_5_LINE_59: D("0.00"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("565.00"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("565.00"),
            CPP_PART_5_LINE_65: D("0.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("0.00"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
        },
    )


def test_part_5_line_45_is_8_percent_of_line_42_when_employment_income_is_above_71300() -> None:
    # Case (b). Employment income of $80,000 and line 27 of 15,000, the T4 totals the required
    # ones. Part 3: line 11 is 4.95% x 67,800 = 3,356.10 (the maximum), line 12 is 678.00 and
    # line 22 is 4% x (80,000 - 71,300) = 348.00, so box 16A is 348.00 (line 45 reads line 42,
    # not box 16A). Part 5 lines 1 to 42: line 30 is 0.01 and line 42 is 1,200.00. Line 43 is
    # 9.9% x 0.01 = 0.00099, 0.00; line 44 is 2% x 0.01 = 0.0002, 0.00; line 45 is 8% x 1,200.00
    # = 96.00; lines 46 and 47 are 96.00. Line 48 is 0 (line 24 is 0), line 49 is 96.00 and line
    # 50 is 0. Line 51 is 3,356.10 and line 57 is 3,356.10 (lines 52 to 56 are 0); line 58 is
    # 678.00 and line 64 is 678.00 (lines 59 to 63 are 0); line 65 is line 22, 348.00, so line
    # 68 is 348.00 (lines 66 and 67 are 0) and line 69 is 678.00 + 348.00 = 1,026.00.
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("0.01"),
            CPP_PART_5_LINE_42: D("1200.00"),
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("96.00"),
            CPP_PART_5_LINE_46: D("96.00"),
            CPP_PART_5_LINE_47: D("96.00"),
            CPP_PART_5_LINE_48: D("0.00"),
            CPP_PART_5_LINE_49: D("96.00"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("3356.10"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("3356.10"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_58: D("678.00"),
            CPP_PART_5_LINE_59: D("0.00"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("678.00"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("678.00"),
            CPP_PART_5_LINE_65: D("348.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("348.00"),
            CPP_PART_5_LINE_69: D("1026.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
        },
    )


def test_part_5_line_48_doubles_a_positive_line_24_and_line_49_is_what_line_47_has_over_it() -> (
    None
):
    # Case (c), contributions above the required ones: employment income of $60,000, line 27 of
    # 20,000 and box 16 of 3,500.00 (138.25 more than line 13), as Return BN. Part 3: line 9 is
    # 2,911.77, line 10 is 588.23, line 16 is 115.02, line 19 is 23.23, line 20 is 138.25, line
    # 23 is 0 and line 24 is 138.25. Part 5 lines 30 and 42 are those of case (a) (line 5 less
    # line 6 leaves the required 3,361.75 on line 10), so lines 43 to 47 are those of case (a):
    # 1,118.70, 226.00, 696.00, 922.00 and 2,040.70. Line 48 is line 24 (138.25, positive) x 2 =
    # 276.50 and line 49 is 2,040.70 - 276.50 = 1,764.20, positive, so line 50 is 0. Line 16 is
    # positive, so line 51 is line 11, 2,796.75 (lines 52 to 56 are 0); line 19 is positive, so
    # line 58 is line 12, 565.00. Line 60 counts line 16 as positive and takes the lesser of
    # line 16 (115.02) and line 59 (0), 0, and line 67 counts line 20 as positive and takes the
    # lesser of 138.25 and line 66 (0), 0. Lines 57, 64 and 69 are 2,796.75, 565.00 and 565.00
    # as in case (a).
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3500.00",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("11300.01"),
            CPP_PART_5_LINE_42: D("8699.99"),
            CPP_PART_5_LINE_43: D("1118.70"),
            CPP_PART_5_LINE_44: D("226.00"),
            CPP_PART_5_LINE_45: D("696.00"),
            CPP_PART_5_LINE_46: D("922.00"),
            CPP_PART_5_LINE_47: D("2040.70"),
            CPP_PART_5_LINE_48: D("276.50"),
            CPP_PART_5_LINE_49: D("1764.20"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("2796.75"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("2796.75"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_58: D("565.00"),
            CPP_PART_5_LINE_59: D("0.00"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("565.00"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("565.00"),
            CPP_PART_5_LINE_65: D("0.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("0.00"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
            CPP_PART_5_LINE_48_LINE_24_IF_POSITIVE: D("138.25"),
        },
    )


def test_part_5_line_67_takes_line_66_when_line_23_is_negative_and_line_20_positive() -> None:
    # Case (c), line 20 of Part 3 positive and line 23 negative. Employment income of $80,000
    # and line 27 of 15,000, with box 16 of 4,100.00 and box 16A of 300.00 (required 4,034.10
    # and 348.00). Part 3: line 9 is 3,410.93, line 10 is 689.07, line 16 is 3,410.93 - 3,356.10
    # = 54.83, line 19 is 689.07 - 678.00 = 11.07, line 20 is 65.90, line 23 is 300.00 - 348.00
    # = -48.00 and line 24 is 65.90 - 48.00 = 17.90. Part 5: lines 30 and 42 are those of case
    # (b) (0.01 and 1,200.00), so lines 43 to 47 are 0.00, 0.00, 96.00, 96.00 and 96.00. Line 48
    # is 17.90 x 2 = 35.80, line 49 is 96.00 - 35.80 = 60.20 and line 50 is 0. Lines 51 to 62
    # are those of case (b) except line 60: line 16 is positive, so line 60 is the lesser of
    # 54.83 and line 59 (0), 0; line 58 is line 12, 678.00 and line 64 is 678.00. Line 23 is
    # negative, so line 65 is line 21, the box 16A of 300.00; line 66 is 48.00 and line 67, with
    # line 20 positive, is the lesser of line 20 (65.90) and line 66 (48.00), 48.00; line 68 is
    # 300.00 + 48.00 = 348.00 and line 69 is 678.00 + 348.00 = 1,026.00.
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_t4_base_and_first_additional_contributions="4100.00",
        cpp_t4_second_additional_contributions="300.00",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("0.01"),
            CPP_PART_5_LINE_42: D("1200.00"),
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("96.00"),
            CPP_PART_5_LINE_46: D("96.00"),
            CPP_PART_5_LINE_47: D("96.00"),
            CPP_PART_5_LINE_48: D("35.80"),
            CPP_PART_5_LINE_49: D("60.20"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("3356.10"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("3356.10"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_58: D("678.00"),
            CPP_PART_5_LINE_59: D("0.00"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("678.00"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("678.00"),
            CPP_PART_5_LINE_65: D("300.00"),
            CPP_PART_5_LINE_66: D("48.00"),
            CPP_PART_5_LINE_67: D("48.00"),
            CPP_PART_5_LINE_68: D("348.00"),
            CPP_PART_5_LINE_69: D("1026.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
        },
    )


def test_part_5_line_49_is_negative_when_line_48_is_more_than_line_47_and_line_50_halves_it() -> (
    None
):
    # Case (d). Employment income of $90,000 and line 27 of 20,000, with box 16 the required
    # 4,034.10 and box 16A of 500.00, which is 104.00 more than line 22 (4% x 9,900 = 396.00,
    # the maximum). Part 3: line 16, 19 and 20 are 0, line 23 is 104.00 and line 24 is 104.00.
    # Part 5: line 20 is 67,799.99 and line 21 is 0.01, so line 30 is 0.01; line 13 is 500.00 -
    # 104.00 = 396.00 (line 12 is the 104.00 of line 23), so line 35 is 396.00 / 4% = 9,900.00,
    # line 36 is 0.00 and line 42 is 0. Lines 43, 44 and 45 are 0.00 (9.9% and 2% of 0.01 round
    # down, and line 42 is 0), so lines 46 and 47 are 0. Line 48 is 104.00 x 2 = 208.00, so line
    # 49 is 0.00 - 208.00 = -208.00, in brackets (negative, continue at line 50), and line 50 is
    # line 49 as a positive amount, 208.00, x 50% = 104.00 (the line 44800 overpayment of the
    # self-employment lines, the same as line 24 here). Line 51 is line 11, 3,356.10, and line
    # 58 is line 12, 678.00, as lines 16 and 19 are 0. Line 23 is positive but line 54 is 0, so
    # line 56 is 0 (the count is 0) and line 57 is 3,356.10; line 61 is 0, so line 63 is 0 and
    # line 64 is 678.00. Line 65 is line 22, 396.00 (line 23 positive), line 67 is 0 (line 20 is
    # not positive), line 68 is 396.00 and line 69 is 678.00 + 396.00 = 1,074.00.
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="4034.10",
        cpp_t4_second_additional_contributions="500",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("0.01"),
            CPP_PART_5_LINE_42: D("0.00"),
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_46: D("0.00"),
            CPP_PART_5_LINE_47: D("0.00"),
            CPP_PART_5_LINE_48: D("208.00"),
            CPP_PART_5_LINE_49: D("-208.00"),
            CPP_PART_5_LINE_50: D("104.00"),
            CPP_PART_5_LINE_51: D("3356.10"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("3356.10"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_58: D("678.00"),
            CPP_PART_5_LINE_59: D("0.00"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("678.00"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("678.00"),
            CPP_PART_5_LINE_65: D("396.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("396.00"),
            CPP_PART_5_LINE_69: D("1074.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
            CPP_PART_5_LINE_48_LINE_24_IF_POSITIVE: D("104.00"),
            CPP_PART_5_LINE_50_LINE_49_POSITIVE: D("208.00"),
        },
    )


def test_part_5_line_67_takes_line_20_when_it_is_less_than_line_66() -> None:
    # Case (e), line 20 of Part 3 positive and less than line 66. Employment income of $75,000
    # and line 27 of 20,000, with box 16 of 4,034.11 (a cent over the required 4,034.10) and box
    # 16A of 0 (148.00 under line 22, 4% x (75,000 - 71,300)). Part 3: line 9 is 4,034.11 x
    # 83.1933% = 3,356.10923, to the cent 3,356.11, line 10 is 678.00, line 16 is 0.01, line 19
    # is 0.00, line 20 is 0.01, line 23 is -148.00 and line 24 is -147.99. Part 5: line 20 is
    # 4,034.10 x 16.80672 = 67,799.99 (line 10 is 4,034.10 as line 5 less line 6), so line 30 is
    # 0.01; line 35 is 0.01 / 4% = 0.25, line 36 is 9,900.00 - 0.25 = 9,899.75 and line 42 is
    # the lesser of line 36 and line 41 (19,999.99), 9,899.75. Lines 43 and 44 are 0.00; line 45
    # is 8% x 9,899.75 = 791.98, so lines 46 and 47 are 791.98. Line 24 is negative, so line 48
    # is 0 and line 49 is 791.98 (positive). Line 16 is 0.01, positive, so line 51 is line 11
    # (3,356.10); line 60 is the lesser of 0.01 and line 59 (0), 0; line 19 is 0.00, so line 58
    # is line 12 (678.00). Line 23 is negative, so line 65 is line 21, 0.00; line 66 is 148.00
    # and line 67, with line 20 (0.01) positive, is the lesser of 0.01 and 148.00, 0.01. Line 68
    # is 0.01 and line 69 is 678.00 + 0.01 = 678.01.
    worksheet = compute_with_schedule_8(
        "75000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="4034.11",
        cpp_t4_second_additional_contributions="0",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("0.01"),
            CPP_PART_5_LINE_42: D("9899.75"),
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("791.98"),
            CPP_PART_5_LINE_46: D("791.98"),
            CPP_PART_5_LINE_47: D("791.98"),
            CPP_PART_5_LINE_48: D("0.00"),
            CPP_PART_5_LINE_49: D("791.98"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("3356.10"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("3356.10"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_58: D("678.00"),
            CPP_PART_5_LINE_59: D("0.00"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("678.00"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("678.00"),
            CPP_PART_5_LINE_65: D("0.00"),
            CPP_PART_5_LINE_66: D("148.00"),
            CPP_PART_5_LINE_67: D("0.01"),
            CPP_PART_5_LINE_68: D("0.01"),
            CPP_PART_5_LINE_69: D("678.01"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
        },
    )


def test_part_5_lines_52_to_64_when_lines_16_and_19_are_negative_and_line_23_positive() -> None:
    # Case (e), lines 16 and 19 negative, line 23 positive. Employment income of $80,000 and
    # line 27 of 15,000, with box 16 of 4,000.00 and box 16A of 400.00. Part 3: line 9 is
    # 4,000.00 x 83.1933% = 3,327.732, to the cent 3,327.73, line 10 is 672.27, line 16 is
    # 3,327.73 - 3,356.10 = -28.37, line 19 is 672.27 - 678.00 = -5.73, line 20 is -34.10, line
    # 23 is 400.00 - 348.00 = 52.00 and line 24 is -34.10 + 52.00 = 17.90. Part 5: lines 30 and
    # 42 are 0.01 and 1,200.00, so lines 43 to 47 are 0.00, 0.00, 96.00, 96.00 and 96.00; line
    # 48 is 17.90 x 2 = 35.80 and line 49 is 96.00 - 35.80 = 60.20. Line 16 is negative, so line
    # 51 is line 9, 3,327.73; line 52 is 28.37; line 19 is not positive, so line 53 is 0 and
    # line 54 is 28.37; line 55 is 3,327.73. Line 23 (52.00) and line 54 (28.37) are both
    # positive, so line 56 is the lesser, 28.37, and line 57 is 3,327.73 + 28.37 = 3,356.10, the
    # maximum of line 11. Line 19 is negative, so line 58 is line 10, 672.27; line 59 is 5.73;
    # line 16 is not positive, so line 60 is 0 and line 61 is 5.73; line 62 is 672.27. Line 23
    # (52.00) and line 61 (5.73) are both positive, so line 63 is the lesser of line 61 (5.73)
    # and line 23 less line 56 (52.00 - 28.37 = 23.63), 5.73, and line 64 is 672.27 + 5.73 =
    # 678.00, the line 12 maximum. Line 23 is positive, so line 65 is line 22, 348.00; lines 66
    # and 67 are 0 (line 20 is negative), line 68 is 348.00 and line 69 is 678.00 + 348.00 =
    # 1,026.00.
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_t4_base_and_first_additional_contributions="4000.00",
        cpp_t4_second_additional_contributions="400.00",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("0.01"),
            CPP_PART_5_LINE_42: D("1200.00"),
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("96.00"),
            CPP_PART_5_LINE_46: D("96.00"),
            CPP_PART_5_LINE_47: D("96.00"),
            CPP_PART_5_LINE_48: D("35.80"),
            CPP_PART_5_LINE_49: D("60.20"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("3327.73"),
            CPP_PART_5_LINE_52: D("28.37"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("28.37"),
            CPP_PART_5_LINE_55: D("3327.73"),
            CPP_PART_5_LINE_56: D("28.37"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_58: D("672.27"),
            CPP_PART_5_LINE_59: D("5.73"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("5.73"),
            CPP_PART_5_LINE_62: D("672.27"),
            CPP_PART_5_LINE_63: D("5.73"),
            CPP_PART_5_LINE_64: D("678.00"),
            CPP_PART_5_LINE_65: D("348.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("348.00"),
            CPP_PART_5_LINE_69: D("1026.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 1,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 1,
            CPP_PART_5_LINE_23_LESS_LINE_56: D("23.63"),
        },
    )


def test_part_5_line_56_takes_line_23_when_it_is_less_than_line_54_and_line_63_is_then_0() -> None:
    # Case (e), line 23 less than line 54. Employment income of $90,000 and line 27 of 20,000,
    # with box 16 of 3,434.10 (600.00 under line 13) and box 16A of 401.00 (5.00 over line 22 of
    # 396.00). Part 3: line 9 is 2,856.94 (2,856.9411), line 10 is 577.16, line 16 is 2,856.94 -
    # 3,356.10 = -499.16, line 19 is 577.16 - 678.00 = -100.84, line 20 is -600.00, line 23 is
    # 5.00 and line 24 is -595.00. Part 5: line 6 is 0 (line 20 is not positive), line 7 is
    # 3,434.10, line 8 is 600.00 and line 9, the lesser of line 23 of Part 3 (5.00) and line 8,
    # is 5.00, so line 10 is 3,439.10 and line 20 is 3,439.10 x 16.80672 = 57,799.99; line 21
    # and line 30 are 10,000.01. Line 13 is 396.00 (box 16A less line 12, 5.00), so line 35 is
    # 9,900.00, line 36 is 0.00 and line 42 is 0. Line 43 is 9.9% x 10,000.01 = 990.00099,
    # 990.00; line 44 is 2% x 10,000.01 = 200.0002, 200.00; line 45 is 0.00; line 46 is 200.00
    # and line 47 is 1,190.00. Line 24 is negative, so line 48 is 0 and line 49 is 1,190.00.
    # Line 16 is negative, so line 51 is line 9, 2,856.94; line 52 is 499.16; line 53 is 0 (line
    # 19 is negative); line 54 is 499.16; line 55 is 2,856.94. Line 56 is the lesser of line 23
    # (5.00) and line 54 (499.16), 5.00; line 57 is 2,861.94. Line 58 is line 10, 577.16; line
    # 59 is 100.84; line 60 is 0 (line 16 not positive); line 61 is 100.84; line 62 is 577.16.
    # Line 23 and line 61 are positive: line 63 is the lesser of line 61 (100.84) and line 23
    # less line 56 (5.00 - 5.00 = 0.00), 0.00; line 64 is 577.16. Line 65 is line 22, 396.00;
    # lines 66 to 67 are 0 and line 69 is 577.16 + 396.00 = 973.16.
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3434.10",
        cpp_t4_second_additional_contributions="401.00",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("10000.01"),
            CPP_PART_5_LINE_42: D("0.00"),
            CPP_PART_5_LINE_43: D("990.00"),
            CPP_PART_5_LINE_44: D("200.00"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_46: D("200.00"),
            CPP_PART_5_LINE_47: D("1190.00"),
            CPP_PART_5_LINE_48: D("0.00"),
            CPP_PART_5_LINE_49: D("1190.00"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("2856.94"),
            CPP_PART_5_LINE_52: D("499.16"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("499.16"),
            CPP_PART_5_LINE_55: D("2856.94"),
            CPP_PART_5_LINE_56: D("5.00"),
            CPP_PART_5_LINE_57: D("2861.94"),
            CPP_PART_5_LINE_58: D("577.16"),
            CPP_PART_5_LINE_59: D("100.84"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("100.84"),
            CPP_PART_5_LINE_62: D("577.16"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("577.16"),
            CPP_PART_5_LINE_65: D("396.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("396.00"),
            CPP_PART_5_LINE_69: D("973.16"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 1,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 1,
        },
    )


def test_part_5_line_56_takes_line_54_and_line_63_takes_what_is_left_of_line_23() -> None:
    # Case (e), line 23 more than line 54. Employment income of $90,000 and line 27 of 20,000,
    # with box 16 of 3,564.10 (470.00 under line 13) and box 16A of 791.00 (395.00 over line
    # 22). Part 3: line 9 is 2,965.09 (2,965.0924), line 10 is 599.01, line 16 is -391.01, line
    # 19 is 599.01 - 678.00 = -78.99, line 20 is -470.00, line 23 is 395.00 and line 24 is
    # -75.00. Part 5: line 8 is 470.00, line 9 is the lesser of 395.00 and 470.00, 395.00, line
    # 10 is 3,959.10 and line 20 is 3,959.10 x 16.80672 = 66,539.49; line 21 and line 30 are
    # 1,260.51. Line 13 is 396.00 (791.00 - 395.00), so line 36 is 0.00 and line 42 is 0. Line
    # 43 is 9.9% x 1,260.51 = 124.79049, 124.79; line 44 is 2% x 1,260.51 = 25.2102, 25.21; line
    # 45 is 0.00; line 46 is 25.21 and line 47 is 150.00. Line 24 is negative, so line 48 is 0
    # and line 49 is 150.00. Line 51 is line 9, 2,965.09; line 52 is 391.01; line 53 is 0; line
    # 54 is 391.01; line 55 is 2,965.09. Line 56 is the lesser of line 23 (395.00) and line 54
    # (391.01), 391.01, and line 57 is 3,356.10. Line 58 is line 10, 599.01; line 59 is 78.99;
    # line 60 is 0; line 61 is 78.99; line 62 is 599.01. Line 63 is the lesser of line 61
    # (78.99) and line 23 less line 56 (395.00 - 391.01 = 3.99), 3.99, and line 64 is 599.01 +
    # 3.99 = 603.00. Line 65 is line 22, 396.00, and line 69 is 603.00 + 396.00 = 999.00.
    worksheet = compute_with_schedule_8(
        "90000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3564.10",
        cpp_t4_second_additional_contributions="791.00",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("1260.51"),
            CPP_PART_5_LINE_42: D("0.00"),
            CPP_PART_5_LINE_43: D("124.79"),
            CPP_PART_5_LINE_44: D("25.21"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_46: D("25.21"),
            CPP_PART_5_LINE_47: D("150.00"),
            CPP_PART_5_LINE_48: D("0.00"),
            CPP_PART_5_LINE_49: D("150.00"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("2965.09"),
            CPP_PART_5_LINE_52: D("391.01"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("391.01"),
            CPP_PART_5_LINE_55: D("2965.09"),
            CPP_PART_5_LINE_56: D("391.01"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_58: D("599.01"),
            CPP_PART_5_LINE_59: D("78.99"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("78.99"),
            CPP_PART_5_LINE_62: D("599.01"),
            CPP_PART_5_LINE_63: D("3.99"),
            CPP_PART_5_LINE_64: D("603.00"),
            CPP_PART_5_LINE_65: D("396.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("396.00"),
            CPP_PART_5_LINE_69: D("999.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 1,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 1,
            CPP_PART_5_LINE_23_LESS_LINE_56: D("3.99"),
        },
    )


def test_part_5_line_60_adds_back_the_cent_line_16_is_over_when_line_19_is_a_cent_under() -> None:
    # Case (e), a cent split between lines 16 and 19. Employment income of $6,900.50 and line 27
    # of 3,000, box 16 the required 202.33: line 7 is 3,400.50, line 11 is 4.95% x 3,400.50 =
    # 168.32 (168.31975), line 12 is 1% x 3,400.50 = 34.01 (34.005), line 13 is 202.33 and line
    # 22 is 0. Part 3: line 9 is 202.33 x 83.1933% = 168.325..., to the cent 168.33, line 10 is
    # 34.00, line 16 is 0.01, line 19 is 34.00 - 34.01 = -0.01, line 20 is 0.00, line 23 is 0
    # and line 24 is 0.00. Part 5: line 30 is 3,000.00 and line 42 is 0 (line 33 is 3,000 +
    # 6,900.50, not more than 71,300). Line 43 is 9.9% x 3,000 = 297.00, line 44 is 2% x 3,000 =
    # 60.00, line 45 is 0.00, line 46 is 60.00, line 47 is 357.00; line 48 is 0 and line 49 is
    # 357.00. Line 16 is positive, so line 51 is line 11, 168.32; lines 52 to 56 are 0 and line
    # 57 is 168.32. Line 19 is negative, so line 58 is line 10, 34.00; line 59 is 0.01; line 16
    # is positive, so line 60 is the lesser of line 16 (0.01) and line 59 (0.01), 0.01; line 61
    # is 0.00 and line 62 is 34.01. Line 23 is 0, so line 63 is 0.00, line 64 is 34.01 (the
    # required line 12), line 65 is line 22, 0, and line 69 is 34.01.
    worksheet = compute_with_schedule_8(
        "6900.50",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("3000", 2),),
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("3000.00"),
            CPP_PART_5_LINE_42: D("0.00"),
            CPP_PART_5_LINE_43: D("297.00"),
            CPP_PART_5_LINE_44: D("60.00"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_46: D("60.00"),
            CPP_PART_5_LINE_47: D("357.00"),
            CPP_PART_5_LINE_48: D("0.00"),
            CPP_PART_5_LINE_49: D("357.00"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("168.32"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("168.32"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("168.32"),
            CPP_PART_5_LINE_58: D("34.00"),
            CPP_PART_5_LINE_59: D("0.01"),
            CPP_PART_5_LINE_60: D("0.01"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("34.01"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("34.01"),
            CPP_PART_5_LINE_65: D("0.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("0.00"),
            CPP_PART_5_LINE_69: D("34.01"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
        },
    )


def test_part_5_line_45_is_0_when_line_42_is_negative() -> None:
    # A loss with employment income above $71,300: employment income of $80,000 and line 27 of
    # -5,000 (professional income), the T4 totals the required ones (4,034.10 and 348.00). Part
    # 5: line 4 is -5,000 (no floor) and line 30 is 0.00; line 33 is -5,000 + 80,000 = 75,000,
    # more than 71,300, so line 42 is the lesser of 1,200.00 and line 41 (-5,000), -5,000.00.
    # Line 43 and line 44 are 0.00 (0 of earnings), and line 45 is 8% of a negative line 42: a
    # negative amount is below the band, so 0.00, not -400.00. Lines 46 and 47 are 0.00, line 48
    # is 0 (line 24 is 0) and line 49 is 0.00. Lines 51 to 69 are those of case (b): 3,356.10,
    # 3,356.10, 678.00, 678.00, 348.00 and 1,026.00 on lines 51, 57, 58, 64, 65 and 69.
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("-5000", 2),),
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("0.00"),
            CPP_PART_5_LINE_42: D("-5000.00"),
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_46: D("0.00"),
            CPP_PART_5_LINE_47: D("0.00"),
            CPP_PART_5_LINE_48: D("0.00"),
            CPP_PART_5_LINE_49: D("0.00"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("3356.10"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("3356.10"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_58: D("678.00"),
            CPP_PART_5_LINE_59: D("0.00"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("678.00"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("678.00"),
            CPP_PART_5_LINE_65: D("348.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("348.00"),
            CPP_PART_5_LINE_69: D("1026.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
        },
    )


def test_part_5_without_self_employment_income_lines_43_to_47_are_0() -> None:
    # No self-employment income and no CPT20 earnings: employment income of $60,000 with box 16
    # the required 3,361.75. Lines 4, 22, 30 and 42 are 0, so lines 43 to 47 are 0.00; line 48
    # is 0 (line 24 is 0), line 49 is 0.00 and line 50 is 0. Lines 51 to 69 are those of case
    # (a): 2,796.75, 2,796.75, 565.00, 565.00, 0.00 and 565.00 on lines 51, 57, 58, 64, 65 and
    # 69.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("0.00"),
            CPP_PART_5_LINE_42: D("0.00"),
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_46: D("0.00"),
            CPP_PART_5_LINE_47: D("0.00"),
            CPP_PART_5_LINE_48: D("0.00"),
            CPP_PART_5_LINE_49: D("0.00"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_51: D("2796.75"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("2796.75"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_58: D("565.00"),
            CPP_PART_5_LINE_59: D("0.00"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("565.00"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("565.00"),
            CPP_PART_5_LINE_65: D("0.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("0.00"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
        },
    )


def test_part_5_without_self_employment_income_line_49_is_minus_line_48() -> None:
    # Return BN as filed: employment income of $60,000, no self-employment income and box 16 of
    # 3,500.00 (138.25 more than line 13). Part 3 line 24 is 138.25 (lines 16 and 19 are 115.02
    # and 23.23, line 20 138.25, line 23 0). Lines 4, 22, 30 and 42 are 0, so lines 43 to 47 are
    # 0.00. Line 48 is 138.25 x 2 = 276.50 and line 49 is 0.00 - 276.50 = -276.50, in brackets,
    # so line 50 is 276.50 x 50% = 138.25, the same as the 138.25 of line 44800 on the return
    # (line 29 of Part 3a). Lines 51 to 69 are those of case (c): 2,796.75, 2,796.75, 565.00,
    # 565.00, 0 and 565.00 on lines 51, 57, 58, 64, 65 and 69.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3500.00",
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_30: D("0.00"),
            CPP_PART_5_LINE_42: D("0.00"),
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_46: D("0.00"),
            CPP_PART_5_LINE_47: D("0.00"),
            CPP_PART_5_LINE_48: D("276.50"),
            CPP_PART_5_LINE_49: D("-276.50"),
            CPP_PART_5_LINE_50: D("138.25"),
            CPP_PART_5_LINE_51: D("2796.75"),
            CPP_PART_5_LINE_52: D("0.00"),
            CPP_PART_5_LINE_53: D("0.00"),
            CPP_PART_5_LINE_54: D("0.00"),
            CPP_PART_5_LINE_55: D("2796.75"),
            CPP_PART_5_LINE_56: D("0.00"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_58: D("565.00"),
            CPP_PART_5_LINE_59: D("0.00"),
            CPP_PART_5_LINE_60: D("0.00"),
            CPP_PART_5_LINE_61: D("0.00"),
            CPP_PART_5_LINE_62: D("565.00"),
            CPP_PART_5_LINE_63: D("0.00"),
            CPP_PART_5_LINE_64: D("565.00"),
            CPP_PART_5_LINE_65: D("0.00"),
            CPP_PART_5_LINE_66: D("0.00"),
            CPP_PART_5_LINE_67: D("0.00"),
            CPP_PART_5_LINE_68: D("0.00"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE: 0,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE: 0,
            CPP_PART_5_LINE_48_LINE_24_IF_POSITIVE: D("138.25"),
            CPP_PART_5_LINE_50_LINE_49_POSITIVE: D("276.50"),
        },
    )


def test_the_trace_records_line_48_as_a_fraction_and_line_50_as_a_rate() -> None:
    # Return BN as filed: line 24 of Part 3 is 138.25, so line 48 is 138.25 x 2 = 276.50 (a
    # fraction, 2 / 1, to the cent), line 49 is 0.00 - 276.50 = -276.50 and line 50 is line 49 as a
    # positive amount, 276.50, x 50% = 138.25.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3500.00",
    )
    assert part_5_trace(worksheet, FractionAppliedLine)[CPP_PART_5_LINE_48] == FractionAppliedLine(
        output=CPP_PART_5_LINE_48,
        base=CPP_PART_5_LINE_48_LINE_24_IF_POSITIVE,
        base_amount=D("138.25"),
        fraction=Fraction(2, 1),
        rounding=CENT,
        result=D("276.50"),
    )
    assert part_5_trace(worksheet, RateAppliedLine)[CPP_PART_5_LINE_50] == RateAppliedLine(
        output=CPP_PART_5_LINE_50,
        base=CPP_PART_5_LINE_50_LINE_49_POSITIVE,
        base_amount=D("276.50"),
        rate=Rate(D("0.5")),
        rounding=CENT,
        result=D("138.25"),
    )


def test_the_trace_records_lines_43_to_45_as_the_tier_on_the_earnings_of_their_line() -> None:
    # Case (a): line 43 is the tier on line 30 (11,300.01), line 44 the tier on line 30 and line 45
    # the tier on line 42 (8,699.99); the contributory earnings are the earnings themselves.
    case_a = compute_with_schedule_8(
        "60000", (), "0", "0", "0", "0", "0", business_statements=(routed_statement("20000", 2),)
    )
    tiers = part_5_trace(case_a, ContributionTierLine)
    for line, earnings, earnings_amount, result in (
        (CPP_PART_5_LINE_43, CPP_PART_5_LINE_30, "11300.01", "1118.70"),
        (CPP_PART_5_LINE_44, CPP_PART_5_LINE_30, "11300.01", "226.00"),
        (CPP_PART_5_LINE_45, CPP_PART_5_LINE_42, "8699.99", "696.00"),
    ):
        assert tiers[line].earnings is earnings, line.identifier
        assert tiers[line].earnings_amount == D(earnings_amount), line.identifier
        assert tiers[line].contributory == D(earnings_amount), line.identifier
        assert tiers[line].result == D(result), line.identifier
    # A loss with employment income above 71,300: line 42 is -5,000.00, which the tier floors to
    # contributory earnings of 0, so line 45 is 0.00.
    loss = compute_with_schedule_8(
        "80000", (), "0", "0", "0", "0", "0", business_statements=(routed_statement("-5000", 2),)
    )
    tier = part_5_trace(loss, ContributionTierLine)[CPP_PART_5_LINE_45]
    assert tier.earnings is CPP_PART_5_LINE_42
    assert tier.earnings_amount == D("-5000.00")
    assert tier.contributory == D("0")
    assert tier.result == D("0.00")


def test_the_trace_names_the_candidate_lines_51_to_67_took_or_the_zero() -> None:
    # Case (e) with lines 16 and 19 negative and line 23 positive (box 16 of 4,000.00, box 16A of
    # 400.00): lines 51 and 58 take the actual amounts (lines 9 and 10 of Part 3), line 53 and line
    # 60 take "0", line 56 takes its lesser (28.37), line 63 takes its lesser (5.73), line 65 takes
    # line 22 and line 67 takes "0".
    case_e = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_t4_base_and_first_additional_contributions="4000.00",
        cpp_t4_second_additional_contributions="400.00",
    )
    chosen = part_5_trace(case_e, ChosenByCountLine)
    for line, count_kind, count, chosen_kind, chosen_value in (
        (CPP_PART_5_LINE_51, CPP_LINE_16_NOT_NEGATIVE, 0, CPP_ACTUAL_BASE_CONTRIBUTIONS, "3327.73"),
        (
            CPP_PART_5_LINE_53,
            CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE,
            0,
            CPP_ZERO,
            "0",
        ),
        (
            CPP_PART_5_LINE_56,
            CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE,
            1,
            CPP_PART_5_LINE_56_LESSER,
            "28.37",
        ),
        (
            CPP_PART_5_LINE_58,
            CPP_LINE_19_NOT_NEGATIVE,
            0,
            CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS,
            "672.27",
        ),
        (CPP_PART_5_LINE_60, CPP_LINE_16_POSITIVE, 0, CPP_ZERO, "0"),
        (
            CPP_PART_5_LINE_63,
            CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE,
            1,
            CPP_PART_5_LINE_63_LESSER,
            "5.73",
        ),
        (
            CPP_PART_5_LINE_65,
            CPP_LINE_23_NOT_NEGATIVE,
            1,
            CPP_SECOND_ADDITIONAL_CONTRIBUTIONS,
            "348.00",
        ),
        (CPP_PART_5_LINE_67, CPP_LINE_20_POSITIVE, 0, CPP_ZERO, "0"),
    ):
        assert chosen[line] == ChosenByCountLine(
            output=line,
            count_kind=count_kind,
            count=count,
            chosen_kind=chosen_kind,
            chosen_value=D(chosen_value),
        ), line.identifier
    # Line 65 takes line 21 (box 16A, 300.00) when line 23 is negative, and line 67 then takes its
    # lesser (48.00): box 16 of 4,100.00 and box 16A of 300.00 on employment income of 80,000.
    case_c = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_t4_base_and_first_additional_contributions="4100.00",
        cpp_t4_second_additional_contributions="300.00",
    )
    chosen = part_5_trace(case_c, ChosenByCountLine)
    assert chosen[CPP_PART_5_LINE_65] == ChosenByCountLine(
        output=CPP_PART_5_LINE_65,
        count_kind=CPP_LINE_23_NOT_NEGATIVE,
        count=0,
        chosen_kind=CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS,
        chosen_value=D("300.00"),
    )
    assert chosen[CPP_PART_5_LINE_67] == ChosenByCountLine(
        output=CPP_PART_5_LINE_67,
        count_kind=CPP_LINE_20_POSITIVE,
        count=1,
        chosen_kind=CPP_PART_5_LINE_67_LESSER,
        chosen_value=D("48.00"),
    )


@pytest.mark.parametrize(
    ("employment", "box_16", "box_16a", "line_30800", "line_22215"),
    [
        # Cases (a) to (e) above: the Part 5 lines 57 and 69 repeat Part 3a and Part 3b's lines for
        # the same Part 3 figures, so they equal the base and enhanced contributions on the return.
        ("60000", None, None, "2796.75", "565.00"),
        ("80000", None, None, "3356.10", "1026.00"),
        ("60000", "3500.00", "0", "2796.75", "565.00"),
        ("90000", "4034.10", "500", "3356.10", "1074.00"),
        ("75000", "4034.11", "0", "3356.10", "678.01"),
        ("90000", "3434.10", "401.00", "2861.94", "973.16"),
        ("90000", "3564.10", "791.00", "3356.10", "999.00"),
    ],
)
def test_part_5_lines_57_and_69_equal_the_base_and_enhanced_contributions_on_the_return(
    employment: str,
    box_16: str | None,
    box_16a: str | None,
    line_30800: str,
    line_22215: str,
) -> None:
    worksheet = compute_with_schedule_8(
        employment,
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions=box_16,
        cpp_t4_second_additional_contributions=box_16a,
    )

    assert worksheet.get(CPP_PART_5_LINE_57).value == D(line_30800)
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D(line_30800)
    assert worksheet.get(CPP_PART_5_LINE_69).value == D(line_22215)
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D(line_22215)


# Schedule 8 Part 5 lines 70 to 88 and the final routing of lines 30800, 22215, 44800, 22200, 31000
# and 42100. Every figure below is derived by hand from the form's lines, in order, from the
# employment income, line 27 and the two T4 totals; Part 3, Part 5 lines 1 to 42 and lines 43 to
# 69 are those of the cases above. Line 70 is 50% of line 43 and line 71 50% of line 44 (line
# 31000 is line 70); line 73 is line 24 of Part 3 if positive; line A is the lesser of lines 72 and
# 73; line 75 is A x 83.1933%; line 84 is 50% of line 45; line 86 is line 74 as a positive amount;
# line 87 is line 84 less line 86 (if negative, "0"); and line 88 (line 22200) adds lines 80, 81,
# 83, 84 and 87 as printed, so line 71 (as line 81) and line 84 (as lines 84 and 87) are counted
# twice when line 74 is not negative: with no employment income that is Part 4's line 17, as the
# test of Part 4's lines 14, 15 and 17 below shows. With Part 5 completed the return takes line
# 30800 from line 57, line 22215 from line 69, line 44800 from line 50, line 42100 from line 49
# (if positive), line 31000 from line 70 and line 22200 from line 88, each replacing Part 3a and
# Part 3b (30800, 22215 and 44800) or added to Part 4's line (42100, 31000 and 22200). The cases:
# (a) the ticket's example; (b) employment income above 71,300 (line 84 not 0); (c) Return BN as
# filed with line 27 of 20,000 (line A is line 73); (d) line 72 less than line 73 (line A is line
# 72, line 74 negative); (e) line 86 more than line 84 (line 87 is 0) and line 49 negative (line 50
# is line 44800); (f) line 73 equal to line 72; (h) line 80 a cent negative; (i) no self-employment
# income; (j) a loss; (k) line 24 negative; (l) line 24 positive with line 23 negative. Line 83
# is never negative (line 77 never exceeds line 71 for any line 30 from 0 to 67,800.00, checked cent
# by cent), so no case reaches it. Lines 70 to 88 do not depend on the Part 5 completed count; only
# the routing does, and the cases below it show the count at 0, Part 4 alone and both counts at 1
# refused.


def test_part_5_lines_70_to_88_for_employment_income_of_60000_and_line_27_of_20000() -> None:
    # Case (a), the ticket's example: employment income of $60,000, line 27 of 20,000 and the T4
    # totals the required ones (box 16 of 3,361.75 and box 16A of 0), Part 5 completed. Part 3
    # line 24 is 0.00; Part 5 lines 30 and 42 are 11,300.01 and 8,699.99, so lines 43 to 47 are
    # 1,118.70, 226.00, 696.00, 922.00 and 2,040.70, line 48 is 0.00, line 49 is 2,040.70 and
    # line 50 is 0.00, and lines 57 and 69 are 2,796.75 and 565.00 (see the cases above for
    # lines 1 to 69). Line 70 is line 43 (1,118.70) x 50% = 559.35 and line 71 is line 44
    # (226.00) x 50% = 113.00; line 72 is 559.35 + 113.00 = 672.35. Line 73 is "0" (line 24 of
    # Part 3, 0.00, is not positive). Line 74 is 672.35 - 0.00 = 672.35. Line A is the lesser of
    # line 72 (672.35) and line 73 (0.00): 0.00 (line 73). Line 75 is A x 83.1933% = 0.00 x
    # 0.831933 = 0, to the cent 0.00; line 77 is A - line 76 (the amount from line 75) = 0.00 -
    # 0.00 = 0.00. Line 80 is line 78 (the amount from line 70) less line 79 (the amount from
    # line 75) = 559.35 - 0.00 = 559.35; line 83 is line 81 (the amount from line 71) less line
    # 82 (the amount from line 77) = 113.00 - 0.00 = 113.00. Line 84 is line 45 (696.00) x 50% =
    # 348, to the cent 348.00. Line 74 is positive or "0", so line 86 is "0" and line 85 (the
    # amount from line 84) goes on line 87. Line 87 is line 85 (the amount from line 84) less
    # line 86 = 348.00 - 0.00 = 348.00. Line 88 adds lines 80, 81 (the amount from line 71), 83,
    # 84 and 87 as printed: 559.35 + 113.00 + 113.00 + 348.00 + 348.00 = 1,481.35. With Part 5
    # completed the return takes line 30800 from line 57 (2,796.75), line 22215 from line 69
    # (565.00), line 44800 from line 50 (0.00), line 42100 from line 49 if positive (2,040.70),
    # line 31000 from line 70 (559.35) and line 22200 from line 88 (1,481.35).
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("1118.70"),
            CPP_PART_5_LINE_44: D("226.00"),
            CPP_PART_5_LINE_45: D("696.00"),
            CPP_PART_5_LINE_49: D("2040.70"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_70: D("559.35"),
            CPP_PART_5_LINE_71: D("113.00"),
            CPP_PART_5_LINE_72: D("672.35"),
            CPP_PART_5_LINE_73: D("0.00"),
            CPP_PART_5_LINE_74: D("672.35"),
            CPP_PART_5_LINE_75_BASE: D("0.00"),
            CPP_PART_5_LINE_75: D("0.00"),
            CPP_PART_5_LINE_77: D("0.00"),
            CPP_PART_5_LINE_80: D("559.35"),
            CPP_PART_5_LINE_83: D("113.00"),
            CPP_PART_5_LINE_84: D("348.00"),
            CPP_PART_5_LINE_86: D("0.00"),
            CPP_PART_5_LINE_87: D("348.00"),
            CPP_PART_5_LINE_88: D("1481.35"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("2040.70"),
            CPP_PART_3_OVERPAYMENT: D("0.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2796.75"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("565.00"),
            CPP_OVERPAYMENT: D("0.00"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("2040.70"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("559.35"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("1481.35"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_line_84_halves_line_45_when_employment_income_is_above_71300() -> None:
    # Case (b): employment income of $80,000 and line 27 of 15,000, the T4 totals the required
    # ones (4,034.10 and 348.00), Part 5 completed. Part 3 line 24 is 0.00; Part 5 lines 30 and
    # 42 are 0.01 and 1,200.00, so lines 43 to 47 are 0.00, 0.00, 96.00, 96.00 and 96.00, line
    # 48 is 0.00, line 49 is 96.00 and line 50 is 0.00, and lines 57 and 69 are 3,356.10 and
    # 1,026.00 (see the cases above for lines 1 to 69). Line 70 is line 43 (0.00) x 50% = 0.00
    # and line 71 is line 44 (0.00) x 50% = 0.00; line 72 is 0.00 + 0.00 = 0.00. Line 73 is "0"
    # (line 24 of Part 3, 0.00, is not positive). Line 74 is 0.00 - 0.00 = 0.00. Line A is the
    # lesser of line 72 (0.00) and line 73 (0.00): 0.00 (equal, so either). Line 75 is A x
    # 83.1933% = 0.00 x 0.831933 = 0, to the cent 0.00; line 77 is A - line 76 (the amount from
    # line 75) = 0.00 - 0.00 = 0.00. Line 80 is line 78 (the amount from line 70) less line 79
    # (the amount from line 75) = 0.00 - 0.00 = 0.00; line 83 is line 81 (the amount from line
    # 71) less line 82 (the amount from line 77) = 0.00 - 0.00 = 0.00. Line 84 is line 45
    # (96.00) x 50% = 48, to the cent 48.00. Line 74 is positive or "0", so line 86 is "0" and
    # line 85 (the amount from line 84) goes on line 87. Line 87 is line 85 (the amount from
    # line 84) less line 86 = 48.00 - 0.00 = 48.00. Line 88 adds lines 80, 81 (the amount from
    # line 71), 83, 84 and 87 as printed: 0.00 + 0.00 + 0.00 + 48.00 + 48.00 = 96.00. With Part
    # 5 completed the return takes line 30800 from line 57 (3,356.10), line 22215 from line 69
    # (1,026.00), line 44800 from line 50 (0.00), line 42100 from line 49 if positive (96.00),
    # line 31000 from line 70 (0.00) and line 22200 from line 88 (96.00).
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("96.00"),
            CPP_PART_5_LINE_49: D("96.00"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_69: D("1026.00"),
            CPP_PART_5_LINE_70: D("0.00"),
            CPP_PART_5_LINE_71: D("0.00"),
            CPP_PART_5_LINE_72: D("0.00"),
            CPP_PART_5_LINE_73: D("0.00"),
            CPP_PART_5_LINE_74: D("0.00"),
            CPP_PART_5_LINE_75_BASE: D("0.00"),
            CPP_PART_5_LINE_75: D("0.00"),
            CPP_PART_5_LINE_77: D("0.00"),
            CPP_PART_5_LINE_80: D("0.00"),
            CPP_PART_5_LINE_83: D("0.00"),
            CPP_PART_5_LINE_84: D("48.00"),
            CPP_PART_5_LINE_86: D("0.00"),
            CPP_PART_5_LINE_87: D("48.00"),
            CPP_PART_5_LINE_88: D("96.00"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("96.00"),
            CPP_PART_3_OVERPAYMENT: D("0.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("3356.10"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("1026.00"),
            CPP_OVERPAYMENT: D("0.00"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("96.00"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("96.00"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_line_a_is_line_73_when_line_24_of_part_3_is_less_than_line_72() -> None:
    # Case (c): Return BN as filed with line 27 of 20,000, employment income of $60,000 and box
    # 16 of 3,500.00 (138.25 more than line 13), Part 5 completed. Part 3 line 24 is 138.25;
    # Part 5 lines 30 and 42 are 11,300.01 and 8,699.99, so lines 43 to 47 are 1,118.70, 226.00,
    # 696.00, 922.00 and 2,040.70, line 48 is 276.50, line 49 is 1,764.20 and line 50 is 0.00,
    # and lines 57 and 69 are 2,796.75 and 565.00 (see the cases above for lines 1 to 69). Line
    # 70 is line 43 (1,118.70) x 50% = 559.35 and line 71 is line 44 (226.00) x 50% = 113.00;
    # line 72 is 559.35 + 113.00 = 672.35. Line 73 is line 24 of Part 3, positive, 138.25. Line
    # 74 is 672.35 - 138.25 = 534.10. Line A is the lesser of line 72 (672.35) and line 73
    # (138.25): 138.25 (line 73). Line 75 is A x 83.1933% = 138.25 x 0.831933 = 115.01473725, to
    # the cent 115.01; line 77 is A - line 76 (the amount from line 75) = 138.25 - 115.01 =
    # 23.24. Line 80 is line 78 (the amount from line 70) less line 79 (the amount from line 75)
    # = 559.35 - 115.01 = 444.34; line 83 is line 81 (the amount from line 71) less line 82 (the
    # amount from line 77) = 113.00 - 23.24 = 89.76. Line 84 is line 45 (696.00) x 50% = 348, to
    # the cent 348.00. Line 74 is positive or "0", so line 86 is "0" and line 85 (the amount
    # from line 84) goes on line 87. Line 87 is line 85 (the amount from line 84) less line 86 =
    # 348.00 - 0.00 = 348.00. Line 88 adds lines 80, 81 (the amount from line 71), 83, 84 and 87
    # as printed: 444.34 + 113.00 + 89.76 + 348.00 + 348.00 = 1,343.10. With Part 5 completed
    # the return takes line 30800 from line 57 (2,796.75), line 22215 from line 69 (565.00),
    # line 44800 from line 50 (0.00), line 42100 from line 49 if positive (1,764.20), line 31000
    # from line 70 (559.35) and line 22200 from line 88 (1,343.10); Part 3a's line 29 would be
    # 138.25.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_t4_second_additional_contributions="0",
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("1118.70"),
            CPP_PART_5_LINE_44: D("226.00"),
            CPP_PART_5_LINE_45: D("696.00"),
            CPP_PART_5_LINE_49: D("1764.20"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_70: D("559.35"),
            CPP_PART_5_LINE_71: D("113.00"),
            CPP_PART_5_LINE_72: D("672.35"),
            CPP_PART_5_LINE_73: D("138.25"),
            CPP_PART_5_LINE_74: D("534.10"),
            CPP_PART_5_LINE_75_BASE: D("138.25"),
            CPP_PART_5_LINE_75: D("115.01"),
            CPP_PART_5_LINE_77: D("23.24"),
            CPP_PART_5_LINE_80: D("444.34"),
            CPP_PART_5_LINE_83: D("89.76"),
            CPP_PART_5_LINE_84: D("348.00"),
            CPP_PART_5_LINE_86: D("0.00"),
            CPP_PART_5_LINE_87: D("348.00"),
            CPP_PART_5_LINE_88: D("1343.10"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("1764.20"),
            CPP_PART_3_OVERPAYMENT: D("138.25"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2796.75"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("565.00"),
            CPP_OVERPAYMENT: D("0.00"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("1764.20"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("559.35"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("1343.10"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_line_a_is_line_72_and_line_86_comes_off_line_84_when_line_74_is_negative() -> None:
    # Case (d): employment income of $60,000, line 27 of 20,000, box 16 of 3,361.75 (line 13) and
    # box 16A of 738.25 (no second additional contributions are required), Part 5 completed. Part 3
    # line 24 is 738.25 (line 23 is the box 16A); Part 5 lines 30 and 42 are
    # 11,300.01 and 8,699.99, so lines 43 to 47 are 1,118.70, 226.00, 696.00, 922.00 and
    # 2,040.70, line 48 is 1,476.50, line 49 is 564.20 and line 50 is 0.00, and lines 57 and 69
    # are 2,796.75 and 565.00 (see the cases above for lines 1 to 69). Line 70 is line 43
    # (1,118.70) x 50% = 559.35 and line 71 is line 44 (226.00) x 50% = 113.00; line 72 is
    # 559.35 + 113.00 = 672.35. Line 73 is line 24 of Part 3, positive, 738.25. Line 74 is
    # 672.35 - 738.25 = -65.90, in brackets. Line A is the lesser of line 72 (672.35) and line
    # 73 (738.25): 672.35 (line 72). Line 75 is A x 83.1933% = 672.35 x 0.831933 = 559.35015255,
    # to the cent 559.35; line 77 is A - line 76 (the amount from line 75) = 672.35 - 559.35 =
    # 113.00. Line 80 is line 78 (the amount from line 70) less line 79 (the amount from line
    # 75) = 559.35 - 559.35 = 0.00; line 83 is line 81 (the amount from line 71) less line 82
    # (the amount from line 77) = 113.00 - 113.00 = 0.00. Line 84 is line 45 (696.00) x 50% =
    # 348, to the cent 348.00. Line 74 is negative, so line 86 is 65.90 (line 74 as a positive
    # amount). Line 87 is line 85 (the amount from line 84) less line 86 = 348.00 - 65.90 =
    # 282.10. Line 88 adds lines 80, 81 (the amount from line 71), 83, 84 and 87 as printed:
    # 0.00 + 113.00 + 0.00 + 348.00 + 282.10 = 743.10. With Part 5 completed the return takes
    # line 30800 from line 57 (2,796.75), line 22215 from line 69 (565.00), line 44800 from line
    # 50 (0.00), line 42100 from line 49 if positive (564.20), line 31000 from line 70 (559.35)
    # and line 22200 from line 88 (743.10); Part 3a's line 29 would be 738.25.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3361.75",
        cpp_t4_second_additional_contributions="738.25",
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("1118.70"),
            CPP_PART_5_LINE_44: D("226.00"),
            CPP_PART_5_LINE_45: D("696.00"),
            CPP_PART_5_LINE_49: D("564.20"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_70: D("559.35"),
            CPP_PART_5_LINE_71: D("113.00"),
            CPP_PART_5_LINE_72: D("672.35"),
            CPP_PART_5_LINE_73: D("738.25"),
            CPP_PART_5_LINE_74: D("-65.90"),
            CPP_PART_5_LINE_75_BASE: D("672.35"),
            CPP_PART_5_LINE_75: D("559.35"),
            CPP_PART_5_LINE_77: D("113.00"),
            CPP_PART_5_LINE_80: D("0.00"),
            CPP_PART_5_LINE_83: D("0.00"),
            CPP_PART_5_LINE_84: D("348.00"),
            CPP_PART_5_LINE_86: D("65.90"),
            CPP_PART_5_LINE_87: D("282.10"),
            CPP_PART_5_LINE_88: D("743.10"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("564.20"),
            CPP_PART_3_OVERPAYMENT: D("738.25"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2796.75"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("565.00"),
            CPP_OVERPAYMENT: D("0.00"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("564.20"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("559.35"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("743.10"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_line_87_is_0_when_line_86_is_more_than_line_84_and_line_49_is_negative() -> None:
    # Case (e): employment income of $60,000, line 27 of 20,000, box 16 of 3,361.75 (line 13) and
    # box 16A of 1,238.25 (no second additional contributions are required), Part 5 completed. Part
    # 3 line 24 is 1,238.25 (line 23 is the box 16A); Part 5 lines 30 and 42
    # are 11,300.01 and 8,699.99, so lines 43 to 47 are 1,118.70, 226.00, 696.00, 922.00 and
    # 2,040.70, line 48 is 2,476.50, line 49 is -435.80, in brackets, and line 50 is 217.90, and
    # lines 57 and 69 are 2,796.75 and 565.00 (see the cases above for lines 1 to 69). Line 70
    # is line 43 (1,118.70) x 50% = 559.35 and line 71 is line 44 (226.00) x 50% = 113.00; line
    # 72 is 559.35 + 113.00 = 672.35. Line 73 is line 24 of Part 3, positive, 1,238.25. Line 74
    # is 672.35 - 1,238.25 = -565.90, in brackets. Line A is the lesser of line 72 (672.35) and
    # line 73 (1,238.25): 672.35 (line 72). Line 75 is A x 83.1933% = 672.35 x 0.831933 =
    # 559.35015255, to the cent 559.35; line 77 is A - line 76 (the amount from line 75) =
    # 672.35 - 559.35 = 113.00. Line 80 is line 78 (the amount from line 70) less line 79 (the
    # amount from line 75) = 559.35 - 559.35 = 0.00; line 83 is line 81 (the amount from line
    # 71) less line 82 (the amount from line 77) = 113.00 - 113.00 = 0.00. Line 84 is line 45
    # (696.00) x 50% = 348, to the cent 348.00. Line 74 is negative, so line 86 is 565.90 (line
    # 74 as a positive amount). Line 87 is line 85 (the amount from line 84) less line 86 =
    # 348.00 - 565.90 = -217.90, negative, so 0. Line 88 adds lines 80, 81 (the amount from line
    # 71), 83, 84 and 87 as printed: 0.00 + 113.00 + 0.00 + 348.00 + 0.00 = 461.00. With Part 5
    # completed the return takes line 30800 from line 57 (2,796.75), line 22215 from line 69
    # (565.00), line 44800 from line 50 (217.90), line 42100 from line 49 if positive (0.00),
    # line 31000 from line 70 (559.35) and line 22200 from line 88 (461.00); Part 3a's line 29
    # would be 1,238.25.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3361.75",
        cpp_t4_second_additional_contributions="1238.25",
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("1118.70"),
            CPP_PART_5_LINE_44: D("226.00"),
            CPP_PART_5_LINE_45: D("696.00"),
            CPP_PART_5_LINE_49: D("-435.80"),
            CPP_PART_5_LINE_50: D("217.90"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_70: D("559.35"),
            CPP_PART_5_LINE_71: D("113.00"),
            CPP_PART_5_LINE_72: D("672.35"),
            CPP_PART_5_LINE_73: D("1238.25"),
            CPP_PART_5_LINE_74: D("-565.90"),
            CPP_PART_5_LINE_75_BASE: D("672.35"),
            CPP_PART_5_LINE_75: D("559.35"),
            CPP_PART_5_LINE_77: D("113.00"),
            CPP_PART_5_LINE_80: D("0.00"),
            CPP_PART_5_LINE_83: D("0.00"),
            CPP_PART_5_LINE_84: D("348.00"),
            CPP_PART_5_LINE_86: D("565.90"),
            CPP_PART_5_LINE_87: D("0.00"),
            CPP_PART_5_LINE_88: D("461.00"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("0.00"),
            CPP_PART_3_OVERPAYMENT: D("1238.25"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2796.75"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("565.00"),
            CPP_OVERPAYMENT: D("217.90"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("559.35"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("461.00"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_line_74_is_0_and_line_86_is_0_when_line_73_equals_line_72() -> None:
    # Case (f): employment income of $60,000, line 27 of 20,000, box 16 of 3,361.75 (line 13) and
    # box 16A of 672.35 (the same as line 72), Part 5 completed. Part 3 line 24 is 672.35; Part
    # 5 lines 30 and 42 are 11,300.01 and 8,699.99, so lines 43 to 47 are 1,118.70, 226.00,
    # 696.00, 922.00 and 2,040.70, line 48 is 1,344.70, line 49 is 696.00 and line 50 is 0.00,
    # and lines 57 and 69 are 2,796.75 and 565.00 (see the cases above for lines 1 to 69). Line
    # 70 is line 43 (1,118.70) x 50% = 559.35 and line 71 is line 44 (226.00) x 50% = 113.00;
    # line 72 is 559.35 + 113.00 = 672.35. Line 73 is line 24 of Part 3, positive, 672.35. Line
    # 74 is 672.35 - 672.35 = 0.00. Line A is the lesser of line 72 (672.35) and line 73
    # (672.35): 672.35 (equal, so either). Line 75 is A x 83.1933% = 672.35 x 0.831933 =
    # 559.35015255, to the cent 559.35; line 77 is A - line 76 (the amount from line 75) =
    # 672.35 - 559.35 = 113.00. Line 80 is line 78 (the amount from line 70) less line 79 (the
    # amount from line 75) = 559.35 - 559.35 = 0.00; line 83 is line 81 (the amount from line
    # 71) less line 82 (the amount from line 77) = 113.00 - 113.00 = 0.00. Line 84 is line 45
    # (696.00) x 50% = 348, to the cent 348.00. Line 74 is positive or "0", so line 86 is "0"
    # and line 85 (the amount from line 84) goes on line 87. Line 87 is line 85 (the amount from
    # line 84) less line 86 = 348.00 - 0.00 = 348.00. Line 88 adds lines 80, 81 (the amount from
    # line 71), 83, 84 and 87 as printed: 0.00 + 113.00 + 0.00 + 348.00 + 348.00 = 809.00. With
    # Part 5 completed the return takes line 30800 from line 57 (2,796.75), line 22215 from line
    # 69 (565.00), line 44800 from line 50 (0.00), line 42100 from line 49 if positive (696.00),
    # line 31000 from line 70 (559.35) and line 22200 from line 88 (809.00); Part 3a's line 29
    # would be 672.35.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3361.75",
        cpp_t4_second_additional_contributions="672.35",
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("1118.70"),
            CPP_PART_5_LINE_44: D("226.00"),
            CPP_PART_5_LINE_45: D("696.00"),
            CPP_PART_5_LINE_49: D("696.00"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_70: D("559.35"),
            CPP_PART_5_LINE_71: D("113.00"),
            CPP_PART_5_LINE_72: D("672.35"),
            CPP_PART_5_LINE_73: D("672.35"),
            CPP_PART_5_LINE_74: D("0.00"),
            CPP_PART_5_LINE_75_BASE: D("672.35"),
            CPP_PART_5_LINE_75: D("559.35"),
            CPP_PART_5_LINE_77: D("113.00"),
            CPP_PART_5_LINE_80: D("0.00"),
            CPP_PART_5_LINE_83: D("0.00"),
            CPP_PART_5_LINE_84: D("348.00"),
            CPP_PART_5_LINE_86: D("0.00"),
            CPP_PART_5_LINE_87: D("348.00"),
            CPP_PART_5_LINE_88: D("809.00"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("696.00"),
            CPP_PART_3_OVERPAYMENT: D("672.35"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2796.75"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("565.00"),
            CPP_OVERPAYMENT: D("0.00"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("696.00"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("559.35"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("809.00"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_line_80_is_a_cent_negative_when_line_75_is_a_cent_more_than_line_70() -> None:
    # Case (h): employment income of $60,000, line 27 of 100.25 and box 16 of 3,500.00, Part 5
    # completed. Part 3 line 24 is 138.25; Part 5 lines 30 and 42 are 100.25 and 0.00, so lines
    # 43 to 47 are 9.92, 2.01, 0.00, 2.01 and 11.93, line 48 is 276.50, line 49 is -264.57, in
    # brackets, and line 50 is 132.29, and lines 57 and 69 are 2,796.75 and 565.00 (see the
    # cases above for lines 1 to 69). Line 70 is line 43 (9.92) x 50% = 4.96 and line 71 is line
    # 44 (2.01) x 50% = 1.01; line 72 is 4.96 + 1.01 = 5.97. Line 73 is line 24 of Part 3,
    # positive, 138.25. Line 74 is 5.97 - 138.25 = -132.28, in brackets. Line A is the lesser of
    # line 72 (5.97) and line 73 (138.25): 5.97 (line 72). Line 75 is A x 83.1933% = 5.97 x
    # 0.831933 = 4.96664001, to the cent 4.97; line 77 is A - line 76 (the amount from line 75)
    # = 5.97 - 4.97 = 1.00. Line 80 is line 78 (the amount from line 70) less line 79 (the
    # amount from line 75) = 4.96 - 4.97 = -0.01, a cent negative since line 75 rounds a cent
    # over line 70; line 83 is line 81 (the amount from line 71) less line 82 (the amount from
    # line 77) = 1.01 - 1.00 = 0.01. Line 84 is line 45 (0.00) x 50% = 0, to the cent 0.00. Line
    # 74 is negative, so line 86 is 132.28 (line 74 as a positive amount). Line 87 is line 85
    # (the amount from line 84) less line 86 = 0.00 - 132.28 = -132.28, negative, so 0. Line 88
    # adds lines 80, 81 (the amount from line 71), 83, 84 and 87 as printed: -0.01 + 1.01 + 0.01
    # + 0.00 + 0.00 = 1.01. With Part 5 completed the return takes line 30800 from line 57
    # (2,796.75), line 22215 from line 69 (565.00), line 44800 from line 50 (132.29), line 42100
    # from line 49 if positive (0.00), line 31000 from line 70 (4.96) and line 22200 from line
    # 88 (1.01); Part 3a's line 29 would be 138.25.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("100.25", 2),),
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("9.92"),
            CPP_PART_5_LINE_44: D("2.01"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_49: D("-264.57"),
            CPP_PART_5_LINE_50: D("132.29"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_70: D("4.96"),
            CPP_PART_5_LINE_71: D("1.01"),
            CPP_PART_5_LINE_72: D("5.97"),
            CPP_PART_5_LINE_73: D("138.25"),
            CPP_PART_5_LINE_74: D("-132.28"),
            CPP_PART_5_LINE_75_BASE: D("5.97"),
            CPP_PART_5_LINE_75: D("4.97"),
            CPP_PART_5_LINE_77: D("1.00"),
            CPP_PART_5_LINE_80: D("-0.01"),
            CPP_PART_5_LINE_83: D("0.01"),
            CPP_PART_5_LINE_84: D("0.00"),
            CPP_PART_5_LINE_86: D("132.28"),
            CPP_PART_5_LINE_87: D("0.00"),
            CPP_PART_5_LINE_88: D("1.01"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("0.00"),
            CPP_PART_3_OVERPAYMENT: D("138.25"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2796.75"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("565.00"),
            CPP_OVERPAYMENT: D("132.29"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("4.96"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("1.01"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_without_self_employment_income_only_lines_73_74_and_86_are_not_0() -> None:
    # Case (i): employment income of $60,000, no self-employment income and box 16 of 3,500.00,
    # Part 5 completed. Part 3 line 24 is 138.25; Part 5 lines 30 and 42 are 0.00 and 0.00, so
    # lines 43 to 47 are 0.00, 0.00, 0.00, 0.00 and 0.00, line 48 is 276.50, line 49 is -276.50,
    # in brackets, and line 50 is 138.25, and lines 57 and 69 are 2,796.75 and 565.00 (see the
    # cases above for lines 1 to 69). Line 70 is line 43 (0.00) x 50% = 0.00 and line 71 is line
    # 44 (0.00) x 50% = 0.00; line 72 is 0.00 + 0.00 = 0.00. Line 73 is line 24 of Part 3,
    # positive, 138.25. Line 74 is 0.00 - 138.25 = -138.25, in brackets. Line A is the lesser of
    # line 72 (0.00) and line 73 (138.25): 0.00 (line 72). Line 75 is A x 83.1933% = 0.00 x
    # 0.831933 = 0, to the cent 0.00; line 77 is A - line 76 (the amount from line 75) = 0.00 -
    # 0.00 = 0.00. Line 80 is line 78 (the amount from line 70) less line 79 (the amount from
    # line 75) = 0.00 - 0.00 = 0.00; line 83 is line 81 (the amount from line 71) less line 82
    # (the amount from line 77) = 0.00 - 0.00 = 0.00. Line 84 is line 45 (0.00) x 50% = 0, to
    # the cent 0.00. Line 74 is negative, so line 86 is 138.25 (line 74 as a positive amount).
    # Line 87 is line 85 (the amount from line 84) less line 86 = 0.00 - 138.25 = -138.25,
    # negative, so 0. Line 88 adds lines 80, 81 (the amount from line 71), 83, 84 and 87 as
    # printed: 0.00 + 0.00 + 0.00 + 0.00 + 0.00 = 0.00. With Part 5 completed the return takes
    # line 30800 from line 57 (2,796.75), line 22215 from line 69 (565.00), line 44800 from line
    # 50 (138.25), line 42100 from line 49 if positive (0.00), line 31000 from line 70 (0.00)
    # and line 22200 from line 88 (0.00); Part 3a's line 29 would be 138.25.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_49: D("-276.50"),
            CPP_PART_5_LINE_50: D("138.25"),
            CPP_PART_5_LINE_57: D("2796.75"),
            CPP_PART_5_LINE_69: D("565.00"),
            CPP_PART_5_LINE_70: D("0.00"),
            CPP_PART_5_LINE_71: D("0.00"),
            CPP_PART_5_LINE_72: D("0.00"),
            CPP_PART_5_LINE_73: D("138.25"),
            CPP_PART_5_LINE_74: D("-138.25"),
            CPP_PART_5_LINE_75_BASE: D("0.00"),
            CPP_PART_5_LINE_75: D("0.00"),
            CPP_PART_5_LINE_77: D("0.00"),
            CPP_PART_5_LINE_80: D("0.00"),
            CPP_PART_5_LINE_83: D("0.00"),
            CPP_PART_5_LINE_84: D("0.00"),
            CPP_PART_5_LINE_86: D("138.25"),
            CPP_PART_5_LINE_87: D("0.00"),
            CPP_PART_5_LINE_88: D("0.00"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("0.00"),
            CPP_PART_3_OVERPAYMENT: D("138.25"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("2796.75"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("565.00"),
            CPP_OVERPAYMENT: D("138.25"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_lines_70_to_88_are_0_for_a_loss_with_employment_income_above_71300() -> None:
    # Case (j): employment income of $80,000 and line 27 of -5,000 (a loss), the T4 totals the
    # required ones, Part 5 completed. Part 3 line 24 is 0.00; Part 5 lines 30 and 42 are 0.00
    # and -5,000.00, so lines 43 to 47 are 0.00, 0.00, 0.00, 0.00 and 0.00, line 48 is 0.00,
    # line 49 is 0.00 and line 50 is 0.00, and lines 57 and 69 are 3,356.10 and 1,026.00 (see
    # the cases above for lines 1 to 69). Line 70 is line 43 (0.00) x 50% = 0.00 and line 71 is
    # line 44 (0.00) x 50% = 0.00; line 72 is 0.00 + 0.00 = 0.00. Line 73 is "0" (line 24 of
    # Part 3, 0.00, is not positive). Line 74 is 0.00 - 0.00 = 0.00. Line A is the lesser of
    # line 72 (0.00) and line 73 (0.00): 0.00 (equal, so either). Line 75 is A x 83.1933% = 0.00
    # x 0.831933 = 0, to the cent 0.00; line 77 is A - line 76 (the amount from line 75) = 0.00
    # - 0.00 = 0.00. Line 80 is line 78 (the amount from line 70) less line 79 (the amount from
    # line 75) = 0.00 - 0.00 = 0.00; line 83 is line 81 (the amount from line 71) less line 82
    # (the amount from line 77) = 0.00 - 0.00 = 0.00. Line 84 is line 45 (0.00) x 50% = 0, to
    # the cent 0.00. Line 74 is positive or "0", so line 86 is "0" and line 85 (the amount from
    # line 84) goes on line 87. Line 87 is line 85 (the amount from line 84) less line 86 = 0.00
    # - 0.00 = 0.00. Line 88 adds lines 80, 81 (the amount from line 71), 83, 84 and 87 as
    # printed: 0.00 + 0.00 + 0.00 + 0.00 + 0.00 = 0.00. With Part 5 completed the return takes
    # line 30800 from line 57 (3,356.10), line 22215 from line 69 (1,026.00), line 44800 from
    # line 50 (0.00), line 42100 from line 49 if positive (0.00), line 31000 from line 70 (0.00)
    # and line 22200 from line 88 (0.00).
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("-5000", 2),),
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("0.00"),
            CPP_PART_5_LINE_49: D("0.00"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_69: D("1026.00"),
            CPP_PART_5_LINE_70: D("0.00"),
            CPP_PART_5_LINE_71: D("0.00"),
            CPP_PART_5_LINE_72: D("0.00"),
            CPP_PART_5_LINE_73: D("0.00"),
            CPP_PART_5_LINE_74: D("0.00"),
            CPP_PART_5_LINE_75_BASE: D("0.00"),
            CPP_PART_5_LINE_75: D("0.00"),
            CPP_PART_5_LINE_77: D("0.00"),
            CPP_PART_5_LINE_80: D("0.00"),
            CPP_PART_5_LINE_83: D("0.00"),
            CPP_PART_5_LINE_84: D("0.00"),
            CPP_PART_5_LINE_86: D("0.00"),
            CPP_PART_5_LINE_87: D("0.00"),
            CPP_PART_5_LINE_88: D("0.00"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("0.00"),
            CPP_PART_3_OVERPAYMENT: D("0.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("3356.10"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("1026.00"),
            CPP_OVERPAYMENT: D("0.00"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_line_84_is_the_only_one_of_lines_70_to_88_not_0_when_line_24_is_negative() -> None:
    # Case (k): employment income of $75,000, line 27 of 20,000, box 16 of 4,034.11 (a cent over
    # the required 4,034.10) and box 16A of 0 (148.00 under line 22), Part 5 completed. Part 3
    # line 24 is -147.99; Part 5 lines 30 and 42 are 0.01 and 9,899.75, so lines 43 to 47 are
    # 0.00, 0.00, 791.98, 791.98 and 791.98, line 48 is 0.00, line 49 is 791.98 and line 50 is
    # 0.00, and lines 57 and 69 are 3,356.10 and 678.01 (see the cases above for lines 1 to 69).
    # Line 70 is line 43 (0.00) x 50% = 0.00 and line 71 is line 44 (0.00) x 50% = 0.00; line 72
    # is 0.00 + 0.00 = 0.00. Line 73 is "0" (line 24 of Part 3, -147.99, is not positive). Line
    # 74 is 0.00 - 0.00 = 0.00. Line A is the lesser of line 72 (0.00) and line 73 (0.00): 0.00
    # (equal, so either). Line 75 is A x 83.1933% = 0.00 x 0.831933 = 0, to the cent 0.00; line
    # 77 is A - line 76 (the amount from line 75) = 0.00 - 0.00 = 0.00. Line 80 is line 78 (the
    # amount from line 70) less line 79 (the amount from line 75) = 0.00 - 0.00 = 0.00; line 83
    # is line 81 (the amount from line 71) less line 82 (the amount from line 77) = 0.00 - 0.00
    # = 0.00. Line 84 is line 45 (791.98) x 50% = 395.99, to the cent 395.99. Line 74 is
    # positive or "0", so line 86 is "0" and line 85 (the amount from line 84) goes on line 87.
    # Line 87 is line 85 (the amount from line 84) less line 86 = 395.99 - 0.00 = 395.99. Line
    # 88 adds lines 80, 81 (the amount from line 71), 83, 84 and 87 as printed: 0.00 + 0.00 +
    # 0.00 + 395.99 + 395.99 = 791.98. With Part 5 completed the return takes line 30800 from
    # line 57 (3,356.10), line 22215 from line 69 (678.01), line 44800 from line 50 (0.00), line
    # 42100 from line 49 if positive (791.98), line 31000 from line 70 (0.00) and line 22200
    # from line 88 (791.98).
    worksheet = compute_with_schedule_8(
        "75000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="4034.11",
        cpp_t4_second_additional_contributions="0",
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("791.98"),
            CPP_PART_5_LINE_49: D("791.98"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_69: D("678.01"),
            CPP_PART_5_LINE_70: D("0.00"),
            CPP_PART_5_LINE_71: D("0.00"),
            CPP_PART_5_LINE_72: D("0.00"),
            CPP_PART_5_LINE_73: D("0.00"),
            CPP_PART_5_LINE_74: D("0.00"),
            CPP_PART_5_LINE_75_BASE: D("0.00"),
            CPP_PART_5_LINE_75: D("0.00"),
            CPP_PART_5_LINE_77: D("0.00"),
            CPP_PART_5_LINE_80: D("0.00"),
            CPP_PART_5_LINE_83: D("0.00"),
            CPP_PART_5_LINE_84: D("395.99"),
            CPP_PART_5_LINE_86: D("0.00"),
            CPP_PART_5_LINE_87: D("395.99"),
            CPP_PART_5_LINE_88: D("791.98"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("791.98"),
            CPP_PART_3_OVERPAYMENT: D("0.00"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("3356.10"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("678.01"),
            CPP_OVERPAYMENT: D("0.00"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("791.98"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("791.98"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


def test_part_5_line_87_is_30_10_when_line_24_is_positive_and_line_23_negative() -> None:
    # Case (l): employment income of $80,000, line 27 of 15,000, box 16 of 4,100.00 and box 16A
    # of 300.00 (required 4,034.10 and 348.00), Part 5 completed. Part 3 line 24 is 17.90; Part
    # 5 lines 30 and 42 are 0.01 and 1,200.00, so lines 43 to 47 are 0.00, 0.00, 96.00, 96.00
    # and 96.00, line 48 is 35.80, line 49 is 60.20 and line 50 is 0.00, and lines 57 and 69 are
    # 3,356.10 and 1,026.00 (see the cases above for lines 1 to 69). Line 70 is line 43 (0.00) x
    # 50% = 0.00 and line 71 is line 44 (0.00) x 50% = 0.00; line 72 is 0.00 + 0.00 = 0.00. Line
    # 73 is line 24 of Part 3, positive, 17.90. Line 74 is 0.00 - 17.90 = -17.90, in brackets.
    # Line A is the lesser of line 72 (0.00) and line 73 (17.90): 0.00 (line 72). Line 75 is A x
    # 83.1933% = 0.00 x 0.831933 = 0, to the cent 0.00; line 77 is A - line 76 (the amount from
    # line 75) = 0.00 - 0.00 = 0.00. Line 80 is line 78 (the amount from line 70) less line 79
    # (the amount from line 75) = 0.00 - 0.00 = 0.00; line 83 is line 81 (the amount from line
    # 71) less line 82 (the amount from line 77) = 0.00 - 0.00 = 0.00. Line 84 is line 45
    # (96.00) x 50% = 48, to the cent 48.00. Line 74 is negative, so line 86 is 17.90 (line 74
    # as a positive amount). Line 87 is line 85 (the amount from line 84) less line 86 = 48.00 -
    # 17.90 = 30.10. Line 88 adds lines 80, 81 (the amount from line 71), 83, 84 and 87 as
    # printed: 0.00 + 0.00 + 0.00 + 48.00 + 30.10 = 78.10. With Part 5 completed the return
    # takes line 30800 from line 57 (3,356.10), line 22215 from line 69 (1,026.00), line 44800
    # from line 50 (0.00), line 42100 from line 49 if positive (60.20), line 31000 from line 70
    # (0.00) and line 22200 from line 88 (78.10); Part 3a's line 29 would be 17.90.
    worksheet = compute_with_schedule_8(
        "80000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("15000", 2),),
        cpp_t4_base_and_first_additional_contributions="4100.00",
        cpp_t4_second_additional_contributions="300.00",
        cpp_part_5_completed=1,
    )

    assert_values(
        worksheet,
        {
            CPP_PART_5_LINE_43: D("0.00"),
            CPP_PART_5_LINE_44: D("0.00"),
            CPP_PART_5_LINE_45: D("96.00"),
            CPP_PART_5_LINE_49: D("60.20"),
            CPP_PART_5_LINE_50: D("0.00"),
            CPP_PART_5_LINE_57: D("3356.10"),
            CPP_PART_5_LINE_69: D("1026.00"),
            CPP_PART_5_LINE_70: D("0.00"),
            CPP_PART_5_LINE_71: D("0.00"),
            CPP_PART_5_LINE_72: D("0.00"),
            CPP_PART_5_LINE_73: D("17.90"),
            CPP_PART_5_LINE_74: D("-17.90"),
            CPP_PART_5_LINE_75_BASE: D("0.00"),
            CPP_PART_5_LINE_75: D("0.00"),
            CPP_PART_5_LINE_77: D("0.00"),
            CPP_PART_5_LINE_80: D("0.00"),
            CPP_PART_5_LINE_83: D("0.00"),
            CPP_PART_5_LINE_84: D("48.00"),
            CPP_PART_5_LINE_86: D("17.90"),
            CPP_PART_5_LINE_87: D("30.10"),
            CPP_PART_5_LINE_88: D("78.10"),
            CPP_PART_5_LINE_49_IF_POSITIVE: D("60.20"),
            CPP_PART_3_OVERPAYMENT: D("17.90"),
            CPP_BASE_CONTRIBUTIONS_ON_RETURN: D("3356.10"),
            CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: D("1026.00"),
            CPP_OVERPAYMENT: D("0.00"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("60.20"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("0.00"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("78.10"),
            CPP_PART_5_COMPLETED: 1,
        },
    )


@pytest.mark.parametrize(
    ("employment", "line_27", "box_16", "overpayment"),
    [
        # Cases (a), (c), (e), (h) and (i): Part 5 is not completed, so lines 30800, 22215 and 44800
        # are Part 3a's and Part 3b's (line 29 is the 138.25, 208.25 or 138.25 of line 24), and
        # lines 42100, 31000 and 22200 are Part 4's, which is not completed either: 0.
        ("60000", "20000", None, "0.00"),
        ("60000", "20000", "3500.00", "138.25"),
        ("60000", "20000", "3570.00", "208.25"),
        ("60000", "100.25", "3500.00", "138.25"),
        ("60000", "0", "3500.00", "138.25"),
    ],
)
def test_without_part_5_completed_the_return_lines_are_part_3s_and_part_4s_which_is_0(
    employment: str, line_27: str, box_16: str | None, overpayment: str
) -> None:
    worksheet = compute_with_schedule_8(
        employment,
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement(line_27, 2),),
        cpp_t4_base_and_first_additional_contributions=box_16,
    )

    assert worksheet.get(CPP_PART_5_COMPLETED).value == 0
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2796.75")
    assert worksheet.get(CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2796.75")
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("565.00")
    assert worksheet.get(CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("565.00")
    assert worksheet.get(CPP_OVERPAYMENT).value == D(overpayment)
    assert worksheet.get(CPP_PART_3_OVERPAYMENT).value == D(overpayment)
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("0")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D(
        "0"
    )
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("0")


def test_part_5_without_employment_income_gives_part_4s_lines_14_15_and_17() -> None:
    # No employment income and line 27 of 20,000. Part 4: line 9 is 20,000 - 3,500 = 16,500, line 10
    # is 9.9% x 16,500 = 1,633.50, line 11 is 2% x 16,500 = 330.00, line 12 is 0, line 13 is
    # 330.00, line 14 is 1,633.50 + 330.00 = 1,963.50 (line 42100), line 15 is 1,633.50 x 50% =
    # 816.75 (line 31000), line 16 is 330.00 and line 17 is 816.75 + 330.00 = 1,146.75 (line
    # 22200). Part 5 with no employment income: Part 3 lines 1 to 24 are 0, line 30 is 16,500.00,
    # line 42 is 0 (line 33 is 20,000.00, not more than 71,300), lines 43 and 44 are those of
    # Part 4 lines 10 and 11, line 49 is 1,963.50 (line 48 is 0), line 70 is 1,633.50 x 50% =
    # 816.75, line 71 is 330.00 x 50% = 165.00, line 73 is "0" so line A and lines 75 and 77 are
    # 0.00, line 80 is 816.75, line 83 is 165.00, line 84 is 0.00 and line 87 is 0.00, so line
    # 88 is 816.75 + 165.00 + 165.00 + 0.00 + 0.00 = 1,146.75: the form's lines 49, 70 and 88
    # are Part 4's lines 14, 15 and 17.
    part_5 = compute_with_schedule_8(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_part_5_completed=1,
    )
    part_4 = compute_with_schedule_8(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_part_4_completed=1,
    )

    assert_values(
        part_5,
        {
            CPP_PART_5_LINE_43: D("1633.50"),
            CPP_PART_5_LINE_44: D("330.00"),
            CPP_PART_5_LINE_70: D("816.75"),
            CPP_PART_5_LINE_71: D("165.00"),
            CPP_PART_5_LINE_80: D("816.75"),
            CPP_PART_5_LINE_83: D("165.00"),
            CPP_PART_5_LINE_88: D("1146.75"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("1963.50"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("816.75"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("1146.75"),
        },
    )
    assert_values(
        part_4,
        {
            CPP_PAYABLE_ON_SELF_EMPLOYMENT: D("1963.50"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT: D("816.75"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT: D("1146.75"),
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("1963.50"),
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("816.75"),
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: D("1146.75"),
            # Part 5 is computed but not routed when only Part 4 is completed.
            CPP_PART_5_PAYABLE_ON_SELF_EMPLOYMENT: D("0"),
            CPP_PART_5_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT: D("0"),
            CPP_PART_5_DEDUCTION_ON_SELF_EMPLOYMENT: D("0"),
            CPP_PART_5_LINE_49: D("1963.50"),
            CPP_PART_5_LINE_70: D("816.75"),
            CPP_PART_5_LINE_88: D("1146.75"),
        },
    )


def test_with_both_parts_completed_the_return_is_refused_not_added_twice() -> None:
    # The form's headings make Part 4 (only self-employment income) and Part 5 (both employment and
    # self-employment income) alternatives, so both counts at 1 are refused as an input error naming
    # both parts, not added: adding them would count the same contributions twice on lines 42100,
    # 31000 and 22200. The case of the two parts above, employment income of $60,000 and line 27 of
    # 20,000. The refusal is the check of `ca/cpp_part_4_and_part_5_both`; see
    # `test_return_iz.py`. No T4 pensionable earnings are given, so the check of Part 4 beside
    # employment earnings (`test_return_jc.py`) does not speak first.
    with pytest.raises(
        InputOutOfRangeError,
        match=re.escape(
            "ca/cpp_part_4_and_part_5_both 1 is refused: Part 4 and Part 5 of Schedule 8 are both "
            "completed, but Part 4 is for self-employment income only and Part 5 for employment "
            "income as well"
        ),
    ):
        compute_with_schedule_8(
            "60000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            business_statements=(routed_statement("20000", 2),),
            t4_cpp_pensionable_earnings_outside_quebec="0",
            cpp_part_4_completed=1,
            cpp_part_5_completed=1,
        )


def test_part_5_completed_moves_the_credit_the_deductions_and_the_totals_by_the_routed_lines() -> (
    None
):
    # Return BN as filed with line 27 of 20,000 (case (c)), without and with Part 5 completed: line
    # 31000 (559.35) joins the federal and Ontario credit amounts (T1 line 87, ON428 line 58280),
    # line 22200 (1,343.10) joins the deductions from total income (line 23300) and the minimum
    # tax deductions (Form T691 Part 1), line 42100 (1,764.20) joins the total payable (line 148)
    # and line 44800 is line 50, 0.00, not Part 3a's line 29, 138.25, so the total credits (line
    # 166) are 138.25 less. Lines 30800 and 22215 are line 57 and line 69, which equal Part 3a's
    # line 25 and line 28 here.
    without = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        income_tax_deducted="5000",
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_t4_second_additional_contributions="0",
    )
    routed = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        income_tax_deducted="5000",
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_t4_second_additional_contributions="0",
        cpp_part_5_completed=1,
    )

    assert routed.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value - without.get(
        NON_REFUNDABLE_CREDIT_AMOUNTS
    ).value == D("559.35")
    assert routed.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value - without.get(
        ontario.NON_REFUNDABLE_CREDIT_AMOUNTS
    ).value == D("559.35")
    assert routed.get(DEDUCTIONS_FROM_TOTAL_INCOME).value - without.get(
        DEDUCTIONS_FROM_TOTAL_INCOME
    ).value == D("1343.10")
    assert routed.get(AMT_DEDUCTIONS_TOTAL).value - without.get(AMT_DEDUCTIONS_TOTAL).value == D(
        "1343.10"
    )
    assert without.get(CPP_OVERPAYMENT).value == D("138.25")
    assert routed.get(CPP_OVERPAYMENT).value == D("0.00")
    assert routed.get(TOTAL_CREDITS).value - without.get(TOTAL_CREDITS).value == D("-138.25")
    assert without.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("0")
    assert routed.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1764.20")
    # Line 148 "Add lines 143 to 147": line 143 (net federal tax), line 144 (42100), line 145
    # (42120), line 146 (42200) and line 147 (Ontario tax).
    assert routed.get(TOTAL_PAYABLE).value == (
        routed.get(NET_FEDERAL_TAX).value
        + routed.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value
        + routed.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value
        + routed.get(SOCIAL_BENEFITS_REPAYMENT_PAYABLE).value
        + routed.get(ontario.ONTARIO_TAX).value
    )
    assert routed.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2796.75")
    assert routed.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("565.00")


def test_the_trace_names_part_5_or_part_3_for_lines_30800_22215_and_44800() -> None:
    # Case (c) (Return BN as filed with line 27 of 20,000). Part 5 completed: Schedule 8's line
    # 30800 takes line 57 (2,796.75), line 22215 line 69 (565.00) and line 44800 line 50 (0.00);
    # the Part 3 route (line 24 positive: lines 15, 18 plus 22 and 24) is kept under its own
    # kinds. Part 5 not completed: they take the Part 3 route.
    arguments: dict[str, Any] = {
        "business_statements": (routed_statement("20000", 2),),
        "cpp_t4_base_and_first_additional_contributions": "3500.00",
        "cpp_t4_second_additional_contributions": "0",
    }
    routed = chosen_lines(
        compute_with_schedule_8(
            "60000", (), "0", "0", "0", "0", "0", cpp_part_5_completed=1, **arguments
        )
    )
    for line, chosen_kind, chosen_value in (
        (SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN, CPP_PART_5_LINE_57, "2796.75"),
        (SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN, CPP_PART_5_LINE_69, "565.00"),
        (SCHEDULE_8_CPP_OVERPAYMENT, CPP_PART_5_LINE_50, "0.00"),
    ):
        assert routed[line] == ChosenByCountLine(
            output=line,
            count_kind=CPP_PART_5_COMPLETED,
            count=1,
            chosen_kind=chosen_kind,
            chosen_value=D(chosen_value),
        ), line.identifier
    for line, chosen_kind, chosen_value in (
        (CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN, CPP_BASE_CONTRIBUTIONS, "2796.75"),
        (CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN, CPP_ENHANCED_CONTRIBUTIONS, "565.00"),
        (CPP_PART_3_OVERPAYMENT, CPP_CONTRIBUTIONS_DIFFERENCE, "138.25"),
    ):
        assert routed[line] == ChosenByCountLine(
            output=line,
            count_kind=CPP_LINE_24_POSITIVE,
            count=1,
            chosen_kind=chosen_kind,
            chosen_value=D(chosen_value),
        ), line.identifier
    kept = chosen_lines(compute_with_schedule_8("60000", (), "0", "0", "0", "0", "0", **arguments))
    for line, chosen_kind, chosen_value in (
        (
            SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
            CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN,
            "2796.75",
        ),
        (
            SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
            CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN,
            "565.00",
        ),
        (SCHEDULE_8_CPP_OVERPAYMENT, CPP_PART_3_OVERPAYMENT, "138.25"),
    ):
        assert kept[line] == ChosenByCountLine(
            output=line,
            count_kind=CPP_PART_5_COMPLETED,
            count=0,
            chosen_kind=chosen_kind,
            chosen_value=D(chosen_value),
        ), line.identifier


def test_the_trace_counts_part_5_lines_49_70_and_88_once_for_each_part_5_completed() -> None:
    # Case (c) with Part 5 completed: line 49 if positive (1,764.20), line 70 (559.35) and line 88
    # (1,343.10) are each counted once, then added to the Part 4 route (0 here) and Form RC381's
    # amount (0, the return carries Schedule 8).
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_t4_second_additional_contributions="0",
        cpp_part_5_completed=1,
    )
    times = part_5_trace(worksheet, TimesCountLine)
    sums = part_5_trace(worksheet, SumLine)
    for line, amount_kind, amount, part_4, rc381, total in (
        (
            CPP_PART_5_PAYABLE_ON_SELF_EMPLOYMENT,
            CPP_PART_5_LINE_49_IF_POSITIVE,
            "1764.20",
            CPP_PAYABLE_ON_SELF_EMPLOYMENT,
            RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
            CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        ),
        (
            CPP_PART_5_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
            CPP_PART_5_LINE_70,
            "559.35",
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
            RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
            CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        ),
        (
            CPP_PART_5_DEDUCTION_ON_SELF_EMPLOYMENT,
            CPP_PART_5_LINE_88,
            "1343.10",
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT,
            RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
            CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        ),
    ):
        assert times[line] == TimesCountLine(
            output=line,
            amount_kind=amount_kind,
            amount_value=D(amount),
            count_kind=CPP_PART_5_COMPLETED_CHECKED,
            count=1,
            result=D(amount),
        ), line.identifier
        assert sums[total] == SumLine(
            output=total,
            parts=((part_4, D("0")), (line, D(amount)), (rc381, D("0"))),
            total=D(amount),
        ), total.identifier


def test_the_trace_records_lines_70_to_88_as_rates_differences_and_a_lesser() -> None:
    # Case (c): line 70 is 50% of 1,118.70, line 75 is line A (138.25, line 73) x 83.1933% =
    # 115.0147, 115.01, line 77 is 138.25 - 115.01 = 23.24, line 80 is 559.35 - 115.01 = 444.34
    # and line 83 is 113.00 - 23.24 = 89.76; line 74 is 672.35 - 138.25 = 534.10.
    worksheet = compute_with_schedule_8(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        cpp_t4_base_and_first_additional_contributions="3500.00",
        cpp_t4_second_additional_contributions="0",
    )
    rates = part_5_trace(worksheet, RateAppliedLine)
    for line, base, base_amount, rate, result in (
        (CPP_PART_5_LINE_70, CPP_PART_5_LINE_43, "1118.70", "0.5", "559.35"),
        (CPP_PART_5_LINE_71, CPP_PART_5_LINE_44, "226.00", "0.5", "113.00"),
        (CPP_PART_5_LINE_75, CPP_PART_5_LINE_75_BASE, "138.25", "0.831933", "115.01"),
        (CPP_PART_5_LINE_84, CPP_PART_5_LINE_45, "696.00", "0.5", "348.00"),
    ):
        assert rates[line] == RateAppliedLine(
            output=line,
            base=base,
            base_amount=D(base_amount),
            rate=Rate(D(rate)),
            rounding=CENT,
            result=D(result),
        ), line.identifier
    differences = part_5_trace(worksheet, SubtractedLine)
    for line, minuend, minuend_amount, subtrahend, subtrahend_amount, result in (
        (CPP_PART_5_LINE_74, CPP_PART_5_LINE_72, "672.35", CPP_PART_5_LINE_73, "138.25", "534.10"),
        (
            CPP_PART_5_LINE_77,
            CPP_PART_5_LINE_75_BASE,
            "138.25",
            CPP_PART_5_LINE_75,
            "115.01",
            "23.24",
        ),
        (CPP_PART_5_LINE_80, CPP_PART_5_LINE_70, "559.35", CPP_PART_5_LINE_75, "115.01", "444.34"),
        (CPP_PART_5_LINE_83, CPP_PART_5_LINE_71, "113.00", CPP_PART_5_LINE_77, "23.24", "89.76"),
    ):
        assert differences[line] == SubtractedLine(
            output=line,
            minuend=minuend,
            minuend_amount=D(minuend_amount),
            subtrahend=subtrahend,
            subtrahend_amount=D(subtrahend_amount),
            result=D(result),
        ), line.identifier
    lesser = part_5_trace(worksheet, LesserOfLine)[CPP_PART_5_LINE_75_BASE]
    assert lesser == LesserOfLine(
        output=CPP_PART_5_LINE_75_BASE,
        parts=((CPP_PART_5_LINE_72, D("672.35")), (CPP_PART_5_LINE_73, D("138.25"))),
        result=D("138.25"),
    )
    assert part_5_trace(worksheet, SumLine)[CPP_PART_5_LINE_88] == SumLine(
        output=CPP_PART_5_LINE_88,
        parts=(
            (CPP_PART_5_LINE_80, D("444.34")),
            (CPP_PART_5_LINE_71, D("113.00")),
            (CPP_PART_5_LINE_83, D("89.76")),
            (CPP_PART_5_LINE_84, D("348.00")),
            (CPP_PART_5_LINE_87, D("348.00")),
        ),
        total=D("1343.10"),
    )
