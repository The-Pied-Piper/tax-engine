"""CA-ON 2025 end to end, Return A carrying Form RC381: the form's structured trace 4."""

from __future__ import annotations

from tax_calculator.domain.parameters.contribution_tier import ContributionTier
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.trace import (
    AmountByCountLine,
    ContributionTierLine,
    LesserOfLine,
    SubtractedNotBelowZeroLine,
    SumNotBelowZeroLine,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_BASIC_EXEMPTION,
    CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM,
    RC381_CPP_OVERPAYMENT,
    RC381_PART_2_LINE_B,
    RC381_PART_2_LINE_G,
    RC381_PART_2_LINE_H,
    RC381_PART_2_LINE_I,
    RC381_PART_2_LINE_J,
    RC381_PART_3_LINE_3,
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
    RC381_PART_3_LINE_22,
    RC381_PART_3_LINE_23,
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
    RC381_PART_3_LINE_42,
    RC381_PART_3_LINE_43,
    RC381_PART_3_LINE_46,
    RC381_PART_3_LINE_68,
    RC381_PART_3_LINE_69,
    RC381_PART_4_LINE_4,
    RC381_PART_4_LINE_17A,
    RC381_PART_4_LINE_23,
    RC381_PART_4_LINE_23_LESSER,
    RC381_PART_4_LINE_24_LESSER,
    RC381_PART_4_LINE_35,
    RC381_PART_4_LINE_36,
    RC381_PART_4_LINE_38,
    RC381_PART_4_LINE_39,
    RC381_PART_4_LINE_42,
    RC381_PART_4_LINE_59,
    RC381_PART_4_LINE_61,
    RC381_PART_4_LINE_62,
    RC381_PART_4_LINE_65,
    RC381_PART_4_LINE_68,
    RC381_PART_4_LINE_69,
    RC381_PART_4_LINE_70,
    RC381_PART_4_LINE_76,
    RC381_PART_4_LINE_77,
    RC381_PART_4_LINE_82,
    RC381_PART_4_LINE_83,
    RC381_PART_4_LINE_83_LESSER,
    RC381_PART_4_LINE_84,
    RC381_PART_4_LINE_85,
    RC381_PART_4_LINE_86,
    RC381_PART_4_LINE_89_FROM_LINE_69,
    RC381_PART_4_LINE_90,
    RC381_PART_4_LINE_113,
    RC381_PART_4_LINE_114,
    RC381_PART_4_LINE_116_LESSER,
    RC381_PART_4_LINE_125,
    RC381_PART_4_LINE_127,
    RC381_PART_4_LINE_128,
    RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS,
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
    T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, rc381_own_trace, run_a


def test_the_trace_records_each_total_as_a_structured_line() -> None:
    # The lines of Form RC381's own steps on Return A's inputs, the return carrying one copy of the
    # form instead of its Schedule 8.
    # Return A's T4 box 26 is its 110000 of employment income.
    result = run_a(schedule_8_copies=0, rc381_copies=1)
    trace = rc381_own_trace(result["ca/rc381"][0])
    floored = {line.output: line for line in trace if isinstance(line, SubtractedNotBelowZeroLine)}
    summed_floored = {line.output: line for line in trace if isinstance(line, SumNotBelowZeroLine)}
    by_count = {line.output: line for line in trace if isinstance(line, AmountByCountLine)}
    tiers = {line.output: line for line in trace if isinstance(line, ContributionTierLine)}
    lesser = {line.output: line for line in trace if isinstance(line, LesserOfLine)}
    assert lesser == {
        # Form RC381 Part 4 the amount lettered A, "Enter whichever is less: amount from line 113 or
        # line 114.": both are 0 for Return A.
        RC381_PART_4_LINE_116_LESSER: LesserOfLine(
            output=RC381_PART_4_LINE_116_LESSER,
            parts=((RC381_PART_4_LINE_113, D("0.00")), (RC381_PART_4_LINE_114, D("0"))),
            result=D("0.00"),
        ),
        # Form RC381 Part 4 line 62 "Enter whichever is less: amount from line 4 or line 61." and
        # line 83 "Enter whichever is less: amount from line 77 or line 82." (before the gate
        # "If line 74 is more than line 57"): Return A's line 4 and line 82 are 0.
        RC381_PART_4_LINE_62: LesserOfLine(
            output=RC381_PART_4_LINE_62,
            parts=((RC381_PART_4_LINE_4, D("0")), (RC381_PART_4_LINE_61, D("0.01"))),
            result=D("0"),
        ),
        RC381_PART_4_LINE_83_LESSER: LesserOfLine(
            output=RC381_PART_4_LINE_83_LESSER,
            parts=((RC381_PART_4_LINE_77, D("9900.00")), (RC381_PART_4_LINE_82, D("0.00"))),
            result=D("0.00"),
        ),
        # Form RC381 Part 4 line 39 "Enter whichever is less: amount from line 35 or line 38.":
        # both are 0 for Return A.
        RC381_PART_4_LINE_39: LesserOfLine(
            output=RC381_PART_4_LINE_39,
            parts=((RC381_PART_4_LINE_35, D("0")), (RC381_PART_4_LINE_38, D("0"))),
            result=D("0"),
        ),
        # Form RC381 Part 4 line 23 "enter whichever is less: amount from line 68 of Part 3 or
        # line 17A" and line 24 "Enter whichever is less: amount from line 17A or line 23.":
        # every part is 0 for Return A.
        RC381_PART_4_LINE_23_LESSER: LesserOfLine(
            output=RC381_PART_4_LINE_23_LESSER,
            parts=((RC381_PART_3_LINE_68, D("-396.00")), (RC381_PART_4_LINE_17A, D("0"))),
            result=D("-396.00"),
        ),
        RC381_PART_4_LINE_24_LESSER: LesserOfLine(
            output=RC381_PART_4_LINE_24_LESSER,
            parts=((RC381_PART_4_LINE_17A, D("0")), (RC381_PART_4_LINE_23, D("0"))),
            result=D("0"),
        ),
        # Form RC381 Part 3 line 31 "Enter whichever is less: amount from line 2 or line 27.":
        # line 2 is 0.
        RC381_PART_3_LINE_31: LesserOfLine(
            output=RC381_PART_3_LINE_31,
            parts=(
                (T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC, D("0")),
                (RC381_PART_3_LINE_27, D("0.00")),
            ),
            result=D("0"),
        ),
        # Form RC381 Part 3 line 35 "Enter whichever is less: amount from line 30 or line 34.":
        # line 34 is 0.
        RC381_PART_3_LINE_35_LESSER: LesserOfLine(
            output=RC381_PART_3_LINE_35_LESSER,
            parts=((RC381_PART_3_LINE_30, D("0.00")), (RC381_PART_3_LINE_34, D("0"))),
            result=D("0.00"),
        ),
        # Form RC381 Part 3 line 11 "Enter whichever is less: amount from line 1 or line 7.": line
        # 1 is 0.
        RC381_PART_3_LINE_11: LesserOfLine(
            output=RC381_PART_3_LINE_11,
            parts=(
                (T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC, D("110000")),
                (RC381_PART_3_LINE_7, D("81200.00")),
            ),
            result=D("81200.00"),
        ),
        # Form RC381 Part 3 line 15 "Enter whichever is less: amount from line 10 or line 14.":
        # both are 0.
        RC381_PART_3_LINE_15_LESSER: LesserOfLine(
            output=RC381_PART_3_LINE_15_LESSER,
            parts=((RC381_PART_3_LINE_10, D("9900.00")), (RC381_PART_3_LINE_14, D("9900.00"))),
            result=D("9900.00"),
        ),
    }
    assert tiers == {
        # Form RC381 Part 4 line 84 "amount from line 70 × 9.9% = (maximum $6,712.20)", line 85
        # "amount from line 70 × 2% = (maximum $1,356.00)" and line 86 "amount from line 83 × 8% =
        # (maximum $792.00)": line 70 is 0 for Return A, which has no earnings in the band, and
        # line 83 is 0.
        RC381_PART_4_LINE_84: ContributionTierLine(
            RC381_PART_4_LINE_84,
            RC381_PART_4_LINE_70,
            D("0"),
            ContributionTier(Rate(D("0.099")), D("0"), D("67800"), D("6712.20")),
            CENT,
            D("0"),
            D("0.00"),
        ),
        RC381_PART_4_LINE_85: ContributionTierLine(
            RC381_PART_4_LINE_85,
            RC381_PART_4_LINE_70,
            D("0"),
            ContributionTier(Rate(D("0.02")), D("0"), D("67800"), D("1356.00")),
            CENT,
            D("0"),
            D("0.00"),
        ),
        RC381_PART_4_LINE_86: ContributionTierLine(
            RC381_PART_4_LINE_86,
            RC381_PART_4_LINE_83,
            D("0"),
            ContributionTier(Rate(D("0.08")), D("0"), D("9900"), D("792.00")),
            CENT,
            D("0"),
            D("0.00"),
        ),
        # Form RC381 Part 3 line 42 "amount from line 38 x 5.4% = (maximum $3,661.20)", line 43
        # "amount from line 38 x 1% = (maximum $678.00)" and line 46 "amount from line 35 x 4% =
        # (maximum $396.00)": line 38 and line 35 are 0.
        RC381_PART_3_LINE_42: ContributionTierLine(
            RC381_PART_3_LINE_42,
            RC381_PART_3_LINE_38,
            D("0"),
            ContributionTier(Rate(D("0.054")), D("0"), D("67800"), D("3661.20")),
            CENT,
            D("0"),
            D("0.00"),
        ),
        RC381_PART_3_LINE_43: ContributionTierLine(
            RC381_PART_3_LINE_43,
            RC381_PART_3_LINE_38,
            D("0"),
            ContributionTier(Rate(D("0.01")), D("0"), D("67800"), D("678.00")),
            CENT,
            D("0"),
            D("0.00"),
        ),
        RC381_PART_3_LINE_46: ContributionTierLine(
            RC381_PART_3_LINE_46,
            RC381_PART_3_LINE_35,
            D("0"),
            ContributionTier(Rate(D("0.04")), D("0"), D("9900"), D("396.00")),
            CENT,
            D("0"),
            D("0.00"),
        ),
        # Form RC381 Part 3 line 22 "amount from line 18 x 4.95% = (maximum $3,356.10)", line 23
        # "amount from line 18 x 1% = (maximum $678.00)" and line 26 "amount from line 15 x 4% =
        # (maximum $396.00)": line 18 and line 15 are 0.
        RC381_PART_3_LINE_22: ContributionTierLine(
            RC381_PART_3_LINE_22,
            RC381_PART_3_LINE_18,
            D("67800.00"),
            ContributionTier(Rate(D("0.0495")), D("0"), D("67800"), D("3356.10")),
            CENT,
            D("67800.00"),
            D("3356.10"),
        ),
        RC381_PART_3_LINE_23: ContributionTierLine(
            RC381_PART_3_LINE_23,
            RC381_PART_3_LINE_18,
            D("67800.00"),
            ContributionTier(Rate(D("0.01")), D("0"), D("67800"), D("678.00")),
            CENT,
            D("67800.00"),
            D("678.00"),
        ),
        RC381_PART_3_LINE_26: ContributionTierLine(
            RC381_PART_3_LINE_26,
            RC381_PART_3_LINE_15,
            D("9900.00"),
            ContributionTier(Rate(D("0.04")), D("0"), D("9900"), D("396.00")),
            CENT,
            D("9900.00"),
            D("396.00"),
        ),
    }
    assert floored == {
        # Form RC381 Part 4 line 128 "Line 126 minus line 127 (if negative, enter "0")", line 126
        # being the amount from line 125: both are 0 for Return A.
        RC381_PART_4_LINE_128: SubtractedNotBelowZeroLine(
            output=RC381_PART_4_LINE_128,
            minuend=RC381_PART_4_LINE_125,
            minuend_amount=D("0.00"),
            subtrahend=RC381_PART_4_LINE_127,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        # Form RC381 Part 4 line 59 "Line 57 minus line 58 (if negative, enter "0")" (the table's
        # amounts of lines C and F: 71,300.00 less 3,500.00), line 61 "Line 59 minus line 60" (line
        # 60 being line 42, 67,799.99 for Return A), line 65 "Line 63 minus line 64" (line 58 less
        # line 3 of Part 3, which is 110000 for Return A: negative, entered as "0"), line 68 "Line
        # 66 minus line 67" (line 4, 0, less line 59), line 69 "Line 65 minus line 68" and line 77
        # "Line 75 minus line 76" (line D less line 76, which is 0).
        RC381_PART_4_LINE_59: SubtractedNotBelowZeroLine(
            output=RC381_PART_4_LINE_59,
            minuend=CPP_MAXIMUM_PENSIONABLE_EARNINGS,
            minuend_amount=D("71300.00"),
            subtrahend=CPP_BASIC_EXEMPTION,
            subtrahend_amount=D("3500.00"),
            result=D("67800.00"),
        ),
        RC381_PART_4_LINE_61: SubtractedNotBelowZeroLine(
            output=RC381_PART_4_LINE_61,
            minuend=RC381_PART_4_LINE_59,
            minuend_amount=D("67800.00"),
            subtrahend=RC381_PART_4_LINE_42,
            subtrahend_amount=D("67799.99"),
            result=D("0.01"),
        ),
        RC381_PART_4_LINE_65: SubtractedNotBelowZeroLine(
            output=RC381_PART_4_LINE_65,
            minuend=CPP_BASIC_EXEMPTION,
            minuend_amount=D("3500.00"),
            subtrahend=RC381_PART_3_LINE_3,
            subtrahend_amount=D("110000"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_68: SubtractedNotBelowZeroLine(
            output=RC381_PART_4_LINE_68,
            minuend=RC381_PART_4_LINE_4,
            minuend_amount=D("0.00"),
            subtrahend=RC381_PART_4_LINE_59,
            subtrahend_amount=D("67800.00"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_69: SubtractedNotBelowZeroLine(
            output=RC381_PART_4_LINE_69,
            minuend=RC381_PART_4_LINE_65,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_68,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_77: SubtractedNotBelowZeroLine(
            output=RC381_PART_4_LINE_77,
            minuend=CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM,
            minuend_amount=D("9900.00"),
            subtrahend=RC381_PART_4_LINE_76,
            subtrahend_amount=D("0.00"),
            result=D("9900.00"),
        ),
        # Form RC381 Part 3 line 34 "Line 32 minus line 33 (if negative, enter "0")": line 32 is
        # line 31 (0) and line 33 is line 28 (71,300.00).
        RC381_PART_3_LINE_34: SubtractedNotBelowZeroLine(
            output=RC381_PART_3_LINE_34,
            minuend=RC381_PART_3_LINE_31,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_3_LINE_28,
            subtrahend_amount=D("0.00"),
            result=D("0"),
        ),
        # Form RC381 Part 3 line 38 "Line 36 minus line 37 (if negative, enter "0")": line 37 is
        # line 29 (0.00 for Return A).
        RC381_PART_3_LINE_38: SubtractedNotBelowZeroLine(
            output=RC381_PART_3_LINE_38,
            minuend=RC381_PART_3_LINE_36,
            minuend_amount=D("0.00"),
            subtrahend=RC381_PART_3_LINE_29,
            subtrahend_amount=D("0.00"),
            result=D("0"),
        ),
        # Form RC381 Part 3 line 14 "Line 12 minus line 13 (if negative, enter "0")": line 12 is
        # line 11 (81,200.00) and line 13 is line 8 (71,300.00).
        RC381_PART_3_LINE_14: SubtractedNotBelowZeroLine(
            output=RC381_PART_3_LINE_14,
            minuend=RC381_PART_3_LINE_11,
            minuend_amount=D("81200.00"),
            subtrahend=RC381_PART_3_LINE_8,
            subtrahend_amount=D("71300.00"),
            result=D("9900.00"),
        ),
        # Form RC381 Part 3 line 18 "Line 16 minus line 17 (if negative, enter "0")": line 17 is
        # line 9 (3,500.00).
        RC381_PART_3_LINE_18: SubtractedNotBelowZeroLine(
            output=RC381_PART_3_LINE_18,
            minuend=RC381_PART_3_LINE_16,
            minuend_amount=D("71300.00"),
            subtrahend=RC381_PART_3_LINE_9,
            subtrahend_amount=D("3500.00"),
            result=D("67800.00"),
        ),
    }
    # Schedule 8 Part 4 line 3 "Line 1 plus line 2 (if negative, enter "0")" and Schedule 13 line 1
    # "(if negative, enter "0")", on no self-employment income and no partnership income, and the
    # rental CCA limit, and the Form T1206 lines floored in Part 1 (the TOSI-adjusted net income)
    # and Part 2 (line 24, on line 22 alone) for a return without split income.
    assert summed_floored == {
        # Form RC381 Part 4 line 114 "Enter the amount from line 69 of Part 3 if positive. If not,
        # enter "0"." (Return A's line 69 is -396.00, so line 114 is "0").
        RC381_PART_4_LINE_114: SumNotBelowZeroLine(
            output=RC381_PART_4_LINE_114,
            parts=((RC381_PART_3_LINE_69, D("-396.00")),),
            total=D("0"),
        ),
        # Form RC381 Part 4 line 89 "Amount from line 69 of Part 3 (if positive)" (Return A's
        # line 69 is -396.00, so it is "0") and line 90 "If positive, enter the amount ... on line
        # 42100 of your return" (Return A's line 90 is 0).
        RC381_PART_4_LINE_89_FROM_LINE_69: SumNotBelowZeroLine(
            output=RC381_PART_4_LINE_89_FROM_LINE_69,
            parts=((RC381_PART_3_LINE_69, D("-396.00")),),
            total=D("0"),
        ),
        RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS: SumNotBelowZeroLine(
            output=RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS,
            parts=((RC381_PART_4_LINE_90, D("0.00")),),
            total=D("0"),
        ),
        # Form RC381 Part 4 line 36 "Enter the amount from line 68 of Part 3 if positive. If not,
        # enter "0".": Return A's line 68 is -396.00, so line 36 is "0".
        RC381_PART_4_LINE_36: SumNotBelowZeroLine(
            output=RC381_PART_4_LINE_36,
            parts=((RC381_PART_3_LINE_68, D("-396.00")),),
            total=D("0"),
        ),
        # Form RC381 Part 3a line 74 "Overpayment: Enter the amount from line 69." for line 44800,
        # when line 69 is positive: Return A's line 69 is -396.00, so line 44800 is "0".
        RC381_CPP_OVERPAYMENT: SumNotBelowZeroLine(
            output=RC381_CPP_OVERPAYMENT,
            parts=((RC381_PART_3_LINE_69, D("-396.00")),),
            total=D("0"),
        ),
    }
    # Schedule 8 Part 2 lines B, C, D and E: the row of the monthly proration table for box A's 12
    # months, each as printed.
    assert by_count == {
        # Form RC381 Part 2 lines G, H, I and J: the row of the monthly proration table for line B's
        # 12 months.
        RC381_PART_2_LINE_G: AmountByCountLine(
            RC381_PART_2_LINE_G, RC381_PART_2_LINE_B, 12, D("71300.00"), CENT, D("71300.00")
        ),
        RC381_PART_2_LINE_H: AmountByCountLine(
            RC381_PART_2_LINE_H, RC381_PART_2_LINE_B, 12, D("9900.00"), CENT, D("9900.00")
        ),
        RC381_PART_2_LINE_I: AmountByCountLine(
            RC381_PART_2_LINE_I, RC381_PART_2_LINE_B, 12, D("81200.00"), CENT, D("81200.00")
        ),
        RC381_PART_2_LINE_J: AmountByCountLine(
            RC381_PART_2_LINE_J, RC381_PART_2_LINE_B, 12, D("3500.00"), CENT, D("3500.00")
        ),
    }
