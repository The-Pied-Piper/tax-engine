"""CA-ON 2025 end to end, Return A carrying Form RC381: the form's structured trace 5."""

from __future__ import annotations

from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.trace import (
    AmountWhenMoreLine,
    ChosenBySignLine,
    CountAtLeastLine,
    DividedByRateLine,
    LesserOfWhenPositiveLine,
    PositivePartOfNegationLine,
    RatioTruncatedLine,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_MONTHS,
    CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    QPP_MONTHS,
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
    RC381_PART_3_LINE_3,
    RC381_PART_3_LINE_6,
    RC381_PART_3_LINE_15,
    RC381_PART_3_LINE_15_LESSER,
    RC381_PART_3_LINE_35,
    RC381_PART_3_LINE_35_LESSER,
    RC381_PART_3_LINE_52,
    RC381_PART_3_LINE_53,
    RC381_PART_3_LINE_59,
    RC381_PART_3_LINE_60,
    RC381_PART_3_LINE_61,
    RC381_PART_3_LINE_64,
    RC381_PART_3_LINE_68,
    RC381_PART_3_LINE_69,
    RC381_PART_3_LINE_75,
    RC381_PART_3_LINE_76,
    RC381_PART_3_LINE_77,
    RC381_PART_3_LINE_78,
    RC381_PART_3_LINE_80,
    RC381_PART_3_LINE_81,
    RC381_PART_3_LINE_82,
    RC381_PART_3_LINE_83,
    RC381_PART_3_LINE_84,
    RC381_PART_3_LINE_85,
    RC381_PART_3_LINE_87,
    RC381_PART_3_LINE_87_DIFFERENCE,
    RC381_PART_3_LINE_89,
    RC381_PART_3_LINE_90,
    RC381_PART_3_LINE_91,
    RC381_PART_3_LINE_93,
    RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
    RC381_PART_4_LINE_13,
    RC381_PART_4_LINE_14,
    RC381_PART_4_LINE_17,
    RC381_PART_4_LINE_17A,
    RC381_PART_4_LINE_20,
    RC381_PART_4_LINE_21,
    RC381_PART_4_LINE_21_FROM_LINE_17,
    RC381_PART_4_LINE_21_LESSER,
    RC381_PART_4_LINE_22,
    RC381_PART_4_LINE_23,
    RC381_PART_4_LINE_23_MULTIPLIED,
    RC381_PART_4_LINE_24,
    RC381_PART_4_LINE_25A,
    RC381_PART_4_LINE_31,
    RC381_PART_4_LINE_33,
    RC381_PART_4_LINE_34,
    RC381_PART_4_LINE_35,
    RC381_PART_4_LINE_35AA,
    RC381_PART_4_LINE_35AA_FROM_LINE_17,
    RC381_PART_4_LINE_35AB,
    RC381_PART_4_LINE_35AB_FROM_LINE_20,
    RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO,
    RC381_PART_4_LINE_46,
    RC381_PART_4_LINE_51,
    RC381_PART_4_LINE_54,
    RC381_PART_4_LINE_55,
    RC381_PART_4_LINE_56,
    RC381_PART_4_LINE_74,
    RC381_PART_4_LINE_76,
    RC381_PART_4_LINE_83,
    RC381_PART_4_LINE_83_LESSER,
    RC381_PART_4_LINE_90,
    RC381_PART_4_LINE_91_FROM_LINE_90,
    RC381_PART_4_LINE_92,
    RC381_PART_4_LINE_93,
    RC381_PART_4_LINE_94,
    RC381_PART_4_LINE_95,
    RC381_PART_4_LINE_97,
    RC381_PART_4_LINE_99,
    RC381_PART_4_LINE_100,
    RC381_PART_4_LINE_101,
    RC381_PART_4_LINE_102,
    RC381_PART_4_LINE_104,
    RC381_PART_4_LINE_104_DIFFERENCE,
    RC381_PART_4_LINE_106,
    RC381_PART_4_LINE_107,
    RC381_PART_4_LINE_108,
    RC381_PART_4_LINE_115,
    RC381_PART_4_LINE_127,
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, rc381_own_trace, run_a


def test_the_trace_records_each_total_as_a_structured_line() -> None:
    # The lines of Form RC381's own steps on Return A's inputs, the return carrying one copy of the
    # form instead of its Schedule 8.
    # Return A's T4 box 26 is its 110000 of employment income.
    result = run_a(schedule_8_copies=0, rc381_copies=1)
    trace = rc381_own_trace(result["ca/rc381"][0])
    counts_at_least = {line.output: line for line in trace if isinstance(line, CountAtLeastLine)}
    truncated = {line.output: line for line in trace if isinstance(line, RatioTruncatedLine)}
    when_more = {line.output: line for line in trace if isinstance(line, AmountWhenMoreLine)}
    chosen_by_sign = {line.output: line for line in trace if isinstance(line, ChosenBySignLine)}
    positive_parts = {
        line.output: line for line in trace if isinstance(line, PositivePartOfNegationLine)
    }
    lesser_when_positive = {
        line.output: line for line in trace if isinstance(line, LesserOfWhenPositiveLine)
    }
    # Form RC381 Part 3b lines 75 "If line 53 is positive or "0", enter the amount from line 52",
    # 82 "If line 60 is positive or "0", enter the amount from line 59" and 89 "If line 68 is
    # positive or "0", enter the amount from line 67", and the three results of Part 3a and Part
    # 3b, chosen by the sign of line 69: Return A's lines 53 and 60 are 0.00 ("positive or 0")
    # and its line 68 is -396.00, so lines 75 and 82 take lines 52 and 59 and line 89 has none; its
    # line 69 (-396.00) is negative, so Part 3b's results apply, 3356.10 and 678.00. The
    # overpayment of line 44800 is line 69 not below zero, a floored sum of line 69.
    assert chosen_by_sign == {
        # The final selection, by the sign of lines 70 and 83 of Part 4 added ("If lines 70 and
        # 83 are both "0", return to Part 3"): Return A's are 0, not above zero, so lines 30800,
        # 22215 and 44800 are Part 3's results (3356.10, 678.00 and "0", its line 69 being
        # negative) and lines 42100, 31000 and 22200 are "0".
        RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN: ChosenBySignLine(
            output=RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
            sign_kind=RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
            sign=D("0"),
            chosen_kind=RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS,
            chosen_value=D("3356.10"),
        ),
        RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN: ChosenBySignLine(
            output=RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
            sign_kind=RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
            sign=D("0"),
            chosen_kind=RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS,
            chosen_value=D("678.00"),
        ),
        RC381_CPP_OVERPAYMENT_ON_RETURN: ChosenBySignLine(
            output=RC381_CPP_OVERPAYMENT_ON_RETURN,
            sign_kind=RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
            sign=D("0"),
            chosen_kind=RC381_CPP_OVERPAYMENT,
            chosen_value=D("0"),
        ),
        RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT: ChosenBySignLine(
            output=RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
            sign_kind=RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
            sign=D("0"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: ChosenBySignLine(
            output=RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
            sign_kind=RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
            sign=D("0"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS: ChosenBySignLine(
            output=RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
            sign_kind=RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
            sign=D("0"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        # Form RC381 Part 4 line 92 "If line 53 of Part 3 is positive or "0", enter the amount from
        # line 52", line 99 "If line 60 of Part 3 is positive or "0", enter the amount from line 59"
        # and line 106 "If line 68 of Part 3 is positive or "0", enter the amount from line 67":
        # Return A's lines 53 and 60 are 0.00, "positive or 0", so lines 92 and 99 take lines 52
        # (3356.10) and 59 (678.00); its line 68 is -396.00, negative, so line 106 takes line 64
        # (0).
        RC381_PART_4_LINE_92: ChosenBySignLine(
            output=RC381_PART_4_LINE_92,
            sign_kind=RC381_PART_3_LINE_53,
            sign=D("0.00"),
            chosen_kind=RC381_PART_3_LINE_52,
            chosen_value=D("3356.10"),
        ),
        RC381_PART_4_LINE_99: ChosenBySignLine(
            output=RC381_PART_4_LINE_99,
            sign_kind=RC381_PART_3_LINE_60,
            sign=D("0.00"),
            chosen_kind=RC381_PART_3_LINE_59,
            chosen_value=D("678.00"),
        ),
        RC381_PART_4_LINE_106: ChosenBySignLine(
            output=RC381_PART_4_LINE_106,
            sign_kind=RC381_PART_3_LINE_68,
            sign=D("-396.00"),
            chosen_kind=RC381_PART_3_LINE_64,
            chosen_value=D("0"),
        ),
        # Form RC381 Part 4 line 31 (the difference "Line 29 minus line 30" when line 61 of Part 3
        # is positive), line 35A's two sentences (line 35A takes line 17 when line 35 is positive,
        # and line 20 in brackets when line 35 is "0" and then only when line 61 is negative) and
        # lines 46 and 51 (the differences, when line 68 of Part 3 is positive): Return A's line 61
        # is 0.00, not positive, and its lines 35 and 20 are 0 and its line 68 is negative, so line
        # 31 has no candidate, line 35aa and line 35ab at "0" have no candidate, line 35ab's choice
        # for line 35 at "0" takes the amount from line 20 in brackets (0), and lines 46 and 51
        # have none.
        RC381_PART_4_LINE_31: ChosenBySignLine(
            output=RC381_PART_4_LINE_31,
            sign_kind=RC381_PART_3_LINE_61,
            sign=D("0.00"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        RC381_PART_4_LINE_35AA: ChosenBySignLine(
            output=RC381_PART_4_LINE_35AA,
            sign_kind=RC381_PART_4_LINE_35,
            sign=D("0"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO: ChosenBySignLine(
            output=RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO,
            sign_kind=RC381_PART_4_LINE_35,
            sign=D("0"),
            chosen_kind=RC381_PART_4_LINE_35AB_FROM_LINE_20,
            chosen_value=D("0"),
        ),
        RC381_PART_4_LINE_35AB: ChosenBySignLine(
            output=RC381_PART_4_LINE_35AB,
            sign_kind=RC381_PART_3_LINE_61,
            sign=D("0.00"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        RC381_PART_4_LINE_46: ChosenBySignLine(
            output=RC381_PART_4_LINE_46,
            sign_kind=RC381_PART_3_LINE_68,
            sign=D("-396.00"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        RC381_PART_4_LINE_51: ChosenBySignLine(
            output=RC381_PART_4_LINE_51,
            sign_kind=RC381_PART_3_LINE_68,
            sign=D("-396.00"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        # Form RC381 Part 4 line 13 "Line 5 minus line 12" (line 61 of Part 3 positive; else line
        # 5), line 21 (by the sign of line 20), line 23 (by the sign of line 69 of Part 3), line
        # 24 and line 25A (line 61 negative): Return A's line 61 is 0.00 and line 20 is 0, so line
        # 13 takes line 5, its T4 box 16 total of 4034.10 (line 61 is not positive), line 21 has no
        # candidate for "0", and lines 24 and 25A have none; its line 69 is -396.00 (negative), so
        # line 23 takes line 68 times the rate, 0.00.
        RC381_PART_4_LINE_13: ChosenBySignLine(
            output=RC381_PART_4_LINE_13,
            sign_kind=RC381_PART_3_LINE_61,
            sign=D("0.00"),
            chosen_kind=CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
            chosen_value=D("4034.10"),
        ),
        RC381_PART_4_LINE_21: ChosenBySignLine(
            output=RC381_PART_4_LINE_21,
            sign_kind=RC381_PART_4_LINE_20,
            sign=D("0"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        RC381_PART_4_LINE_23: ChosenBySignLine(
            output=RC381_PART_4_LINE_23,
            sign_kind=RC381_PART_3_LINE_69,
            sign=D("-396.00"),
            chosen_kind=RC381_PART_4_LINE_23_MULTIPLIED,
            chosen_value=D("0.00"),
        ),
        RC381_PART_4_LINE_24: ChosenBySignLine(
            output=RC381_PART_4_LINE_24,
            sign_kind=RC381_PART_3_LINE_61,
            sign=D("0.00"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        RC381_PART_4_LINE_25A: ChosenBySignLine(
            output=RC381_PART_4_LINE_25A,
            sign_kind=RC381_PART_3_LINE_61,
            sign=D("0.00"),
            chosen_kind=None,
            chosen_value=D("0"),
        ),
        RC381_PART_3_LINE_75: ChosenBySignLine(
            output=RC381_PART_3_LINE_75,
            sign_kind=RC381_PART_3_LINE_53,
            sign=D("0.00"),
            chosen_kind=RC381_PART_3_LINE_52,
            chosen_value=D("3356.10"),
        ),
        RC381_PART_3_LINE_82: ChosenBySignLine(
            output=RC381_PART_3_LINE_82,
            sign_kind=RC381_PART_3_LINE_60,
            sign=D("0.00"),
            chosen_kind=RC381_PART_3_LINE_59,
            chosen_value=D("678.00"),
        ),
        RC381_PART_3_LINE_89: ChosenBySignLine(
            output=RC381_PART_3_LINE_89,
            sign_kind=RC381_PART_3_LINE_68,
            sign=D("-396.00"),
            chosen_kind=RC381_PART_3_LINE_64,
            chosen_value=D("0"),
        ),
        RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS: ChosenBySignLine(
            output=RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS,
            sign_kind=RC381_PART_3_LINE_69,
            sign=D("-396.00"),
            chosen_kind=RC381_PART_3_LINE_81,
            chosen_value=D("3356.10"),
        ),
        RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS: ChosenBySignLine(
            output=RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS,
            sign_kind=RC381_PART_3_LINE_69,
            sign=D("-396.00"),
            chosen_kind=RC381_PART_3_LINE_93,
            chosen_value=D("678.00"),
        ),
    }
    # Form RC381 Part 3b lines 76, 83 and 90 "Enter the amount from line 53 (60, 68) as a positive
    # amount": lines 53 and 60 are not negative for Return A, and line 68 (-396.00) is.
    assert positive_parts == {
        # Form RC381 Part 4 line 127 "If line 115 is negative, enter it as a positive amount.":
        # Return A's line 115 is 0.00.
        RC381_PART_4_LINE_127: PositivePartOfNegationLine(
            output=RC381_PART_4_LINE_127,
            amount_kind=RC381_PART_4_LINE_115,
            amount_value=D("0.00"),
            result=D("0"),
        ),
        # Form RC381 Part 4 lines 93, 100 and 107 "Enter the amount from line 53 (60, 68) of Part 3
        # as a positive amount": none is negative for Return A.
        RC381_PART_4_LINE_93: PositivePartOfNegationLine(
            output=RC381_PART_4_LINE_93,
            amount_kind=RC381_PART_3_LINE_53,
            amount_value=D("0.00"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_100: PositivePartOfNegationLine(
            output=RC381_PART_4_LINE_100,
            amount_kind=RC381_PART_3_LINE_60,
            amount_value=D("0.00"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_107: PositivePartOfNegationLine(
            output=RC381_PART_4_LINE_107,
            amount_kind=RC381_PART_3_LINE_68,
            amount_value=D("-396.00"),
            result=D("396.00"),
        ),
        # Form RC381 Part 4 line 91 "amount from line 90 entered as a positive amount": Return A's
        # line 90 is 0.00, not negative.
        RC381_PART_4_LINE_91_FROM_LINE_90: PositivePartOfNegationLine(
            output=RC381_PART_4_LINE_91_FROM_LINE_90,
            amount_kind=RC381_PART_4_LINE_90,
            amount_value=D("0.00"),
            result=D("0"),
        ),
        # Form RC381 Part 4 line 33 "Enter the amount from line 61 of Part 3 as a positive amount."
        # and line 54 "Enter the amount from line 68 of Part 3 as a positive amount.": neither is
        # negative for Return A except line 68, which is -396.00.
        RC381_PART_4_LINE_33: PositivePartOfNegationLine(
            output=RC381_PART_4_LINE_33,
            amount_kind=RC381_PART_3_LINE_61,
            amount_value=D("0.00"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_54: PositivePartOfNegationLine(
            output=RC381_PART_4_LINE_54,
            amount_kind=RC381_PART_3_LINE_68,
            amount_value=D("-396.00"),
            result=D("396.00"),
        ),
        # Form RC381 Part 4 line 14 "Enter the amount from line 61 of Part 3 as a positive
        # amount." and line 17A "If line 17 is negative, enter it as a positive amount.": neither
        # is negative for Return A.
        RC381_PART_4_LINE_14: PositivePartOfNegationLine(
            output=RC381_PART_4_LINE_14,
            amount_kind=RC381_PART_3_LINE_61,
            amount_value=D("0.00"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_17A: PositivePartOfNegationLine(
            output=RC381_PART_4_LINE_17A,
            amount_kind=RC381_PART_4_LINE_17,
            amount_value=D("0.00"),
            result=D("0"),
        ),
        RC381_PART_3_LINE_76: PositivePartOfNegationLine(
            output=RC381_PART_3_LINE_76,
            amount_kind=RC381_PART_3_LINE_53,
            amount_value=D("0.00"),
            result=D("0"),
        ),
        RC381_PART_3_LINE_83: PositivePartOfNegationLine(
            output=RC381_PART_3_LINE_83,
            amount_kind=RC381_PART_3_LINE_60,
            amount_value=D("0.00"),
            result=D("0"),
        ),
        RC381_PART_3_LINE_90: PositivePartOfNegationLine(
            output=RC381_PART_3_LINE_90,
            amount_kind=RC381_PART_3_LINE_68,
            amount_value=D("-396.00"),
            result=D("396.00"),
        ),
    }
    # Form RC381 Part 3b lines 77, 80, 84, 87 and 91, "whichever is less" when the lines are
    # positive: none is positive for Return A, so each is "0".
    assert lesser_when_positive == {
        # Form RC381 Part 4 line 94 "If line 53 of Part 3 is negative and line 60 of Part 3 is
        # positive, enter whichever is less", line 97 "If line 68 of Part 3 and line 95 are both
        # positive, enter whichever is less", line 101 "If line 53 of Part 3 is positive, enter
        # whichever is less", line 104 "If line 68 of Part 3 and line 102 are both positive, enter
        # whichever is less" (with the result of line 68 minus line 97) and line 108 "If line 61 of
        # Part 3 is positive and line 68 of Part 3 is negative, enter whichever is less": none is
        # chosen for Return A (lines 53, 60 and 61 are 0.00, not positive, although its line 68
        # is negative), so each is "0".
        RC381_PART_4_LINE_94: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_94,
            parts=((RC381_PART_3_LINE_60, D("0.00")), (RC381_PART_4_LINE_93, D("0"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_4_LINE_97: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_97,
            parts=((RC381_PART_3_LINE_68, D("-396.00")), (RC381_PART_4_LINE_95, D("0"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_4_LINE_101: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_101,
            parts=((RC381_PART_3_LINE_53, D("0.00")), (RC381_PART_4_LINE_100, D("0"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_4_LINE_104: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_104,
            parts=(
                (RC381_PART_4_LINE_102, D("0")),
                (RC381_PART_4_LINE_104_DIFFERENCE, D("-396.00")),
            ),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_4_LINE_108: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_108,
            parts=((RC381_PART_3_LINE_61, D("0.00")), (RC381_PART_4_LINE_107, D("396.00"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        # Form RC381 Part 4 line 34 "If line 17A is positive, enter whichever is less: amount from
        # line 17A or line 33.", line 35A's amounts from line 17 and (in brackets) from line 20 and
        # line 55 "If line 61 of Part 3 is positive, enter whichever is less: amount from line 61
        # of Part 3 or line 54.": none is positive for Return A, so each is "0".
        RC381_PART_4_LINE_34: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_34,
            parts=((RC381_PART_4_LINE_17A, D("0")), (RC381_PART_4_LINE_33, D("0"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_4_LINE_35AA_FROM_LINE_17: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_35AA_FROM_LINE_17,
            parts=((RC381_PART_4_LINE_17, D("0.00")),),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_4_LINE_35AB_FROM_LINE_20: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_35AB_FROM_LINE_20,
            parts=((RC381_PART_4_LINE_20, D("0")),),
            all_positive=False,
            bracket=True,
            result=D("0"),
        ),
        RC381_PART_4_LINE_55: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_55,
            parts=((RC381_PART_3_LINE_61, D("0.00")), (RC381_PART_4_LINE_54, D("396.00"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        # Form RC381 Part 4 line 21, "If line 17 is positive, enter the amount from line 17 (show
        # in brackets)" and "If line 20 is positive, enter whichever is less: amount from line 20
        # or line 17A": none is positive for Return A, so each is "0".
        RC381_PART_4_LINE_21_FROM_LINE_17: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_21_FROM_LINE_17,
            parts=((RC381_PART_4_LINE_17, D("0.00")),),
            all_positive=False,
            bracket=True,
            result=D("0"),
        ),
        RC381_PART_4_LINE_21_LESSER: LesserOfWhenPositiveLine(
            output=RC381_PART_4_LINE_21_LESSER,
            parts=((RC381_PART_4_LINE_20, D("0")), (RC381_PART_4_LINE_17A, D("0"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_3_LINE_77: LesserOfWhenPositiveLine(
            output=RC381_PART_3_LINE_77,
            parts=((RC381_PART_3_LINE_60, D("0.00")), (RC381_PART_3_LINE_76, D("0"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_3_LINE_80: LesserOfWhenPositiveLine(
            output=RC381_PART_3_LINE_80,
            parts=((RC381_PART_3_LINE_68, D("-396.00")), (RC381_PART_3_LINE_78, D("0"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_3_LINE_84: LesserOfWhenPositiveLine(
            output=RC381_PART_3_LINE_84,
            parts=((RC381_PART_3_LINE_53, D("0.00")), (RC381_PART_3_LINE_83, D("0"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_3_LINE_87: LesserOfWhenPositiveLine(
            output=RC381_PART_3_LINE_87,
            parts=((RC381_PART_3_LINE_85, D("0")), (RC381_PART_3_LINE_87_DIFFERENCE, D("-396.00"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
        RC381_PART_3_LINE_91: LesserOfWhenPositiveLine(
            output=RC381_PART_3_LINE_91,
            parts=((RC381_PART_3_LINE_61, D("0.00")), (RC381_PART_3_LINE_90, D("396.00"))),
            all_positive=False,
            bracket=False,
            result=D("0"),
        ),
    }
    # Form RC381 Part 2 "The number you enter on line A cannot be more than the number you enter on
    # line B.": Return A's lines A and B are both 12.
    assert counts_at_least == {
        RC381_PART_2_LINE_B: CountAtLeastLine(
            output=RC381_PART_2_LINE_B,
            count_kind=QPP_MONTHS,
            count=12,
            minimum_kind=CPP_MONTHS,
            minimum=12,
        )
    }
    # Form RC381 Part 3 line 6 "Line 4 divided by line 5 (calculated to the fifth decimal place
    # without rounding)": Return A's line 3 is 110000, not less than line 5, so line 6 is 1.
    assert truncated == {
        # Form RC381 Part 4 line 22 "If line 17A is more than line 14, enter "1". If not, enter
        # the result of line 17A divided by line 14 (calculated to the fifth decimal place
        # without rounding).": lines 17A and 14 are both 0, so line 17A is not more and line 22 is
        # 0 (a zero divisor gives 0).
        RC381_PART_4_LINE_22: RatioTruncatedLine(
            output=RC381_PART_4_LINE_22,
            dividend=RC381_PART_4_LINE_17A,
            dividend_amount=D("0"),
            divisor=RC381_PART_4_LINE_14,
            divisor_amount=D("0"),
            rounding=RoundTo(D("0.00001"), RoundingMode.DOWN),
            cap_at_one=True,
            result=D("0"),
        ),
        RC381_PART_3_LINE_6: RatioTruncatedLine(
            output=RC381_PART_3_LINE_6,
            dividend=T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
            dividend_amount=D("110000"),
            divisor=RC381_PART_3_LINE_3,
            divisor_amount=D("110000"),
            rounding=RoundTo(D("0.00001"), RoundingMode.DOWN),
            cap_at_one=False,
            result=D("1.00000"),
        ),
    }
    # Form RC381 Part 3 line 15, when "the amount from line 3 is more than the amount from line C
    # of Part 2": line 3 is 110000, more than line C (71,300.00), so line 15 is the lesser of
    # line 10 and line 14.
    assert when_more == {
        # Form RC381 Part 4 line 83, "If line 74 is more than line 57, complete lines 75 to 83. If
        # not, enter "0" on line 83": Return A's line 74 is 81,200.00, more than line 57
        # (71,300.00), but line 82 is 0.00, so line 83 is 0.
        RC381_PART_4_LINE_83: AmountWhenMoreLine(
            output=RC381_PART_4_LINE_83,
            amount_kind=RC381_PART_4_LINE_83_LESSER,
            amount_value=D("0"),
            more_kind=RC381_PART_4_LINE_74,
            more_value=D("81200.00"),
            than_kind=CPP_MAXIMUM_PENSIONABLE_EARNINGS,
            than_value=D("71300.00"),
            result=D("0"),
        ),
        # Form RC381 Part 3 line 35, when "the amount from line 3 is more than the amount from line
        # G of Part 2": line 3 is 0, not more than line G (71,300.00), so line 35 is 0.
        RC381_PART_3_LINE_35: AmountWhenMoreLine(
            output=RC381_PART_3_LINE_35,
            amount_kind=RC381_PART_3_LINE_35_LESSER,
            amount_value=D("0.00"),
            more_kind=RC381_PART_3_LINE_3,
            more_value=D("110000"),
            than_kind=RC381_PART_2_LINE_G,
            than_value=D("71300.00"),
            result=D("0.00"),
        ),
        RC381_PART_3_LINE_15: AmountWhenMoreLine(
            output=RC381_PART_3_LINE_15,
            amount_kind=RC381_PART_3_LINE_15_LESSER,
            amount_value=D("9900.00"),
            more_kind=RC381_PART_3_LINE_3,
            more_value=D("110000"),
            than_kind=CPP_MAXIMUM_PENSIONABLE_EARNINGS,
            than_value=D("71300.00"),
            result=D("9900.00"),
        ),
    }
    # Form RC381 Part 4 line 76 "Amount from line 56 ÷ 4% =": Return A's line 56 is 0, so the
    # quotient is 0.00.
    assert [
        line
        for line in trace
        if isinstance(line, DividedByRateLine) and line.output == RC381_PART_4_LINE_76
    ] == [
        DividedByRateLine(
            RC381_PART_4_LINE_76,
            RC381_PART_4_LINE_56,
            D("0"),
            Rate(D("0.04")),
            CENT,
            D("0.00"),
        )
    ]
