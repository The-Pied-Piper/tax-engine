"""CA-ON 2025 end to end, Return A carrying Form RC381: the form's structured trace 3."""

from __future__ import annotations

from tax_engine.domain.parameters.fraction import Fraction
from tax_engine.domain.trace import (
    FractionAppliedLine,
    SubtractedLine,
)
from tax_engine.jurisdictions.ca.catalog import (
    CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    RC381_PART_2_LINE_G,
    RC381_PART_2_LINE_H,
    RC381_PART_2_LINE_I,
    RC381_PART_2_LINE_J,
    RC381_PART_3_LINE_7,
    RC381_PART_3_LINE_8,
    RC381_PART_3_LINE_9,
    RC381_PART_3_LINE_10,
    RC381_PART_3_LINE_11,
    RC381_PART_3_LINE_15,
    RC381_PART_3_LINE_16,
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
    RC381_PART_3_LINE_35,
    RC381_PART_3_LINE_36,
    RC381_PART_3_LINE_40,
    RC381_PART_3_LINE_41,
    RC381_PART_3_LINE_44,
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
    RC381_PART_3_LINE_76,
    RC381_PART_3_LINE_77,
    RC381_PART_3_LINE_78,
    RC381_PART_3_LINE_80,
    RC381_PART_3_LINE_83,
    RC381_PART_3_LINE_84,
    RC381_PART_3_LINE_85,
    RC381_PART_3_LINE_87_DIFFERENCE,
    RC381_PART_4_LINE_4,
    RC381_PART_4_LINE_8,
    RC381_PART_4_LINE_11,
    RC381_PART_4_LINE_12,
    RC381_PART_4_LINE_13_DIFFERENCE,
    RC381_PART_4_LINE_17,
    RC381_PART_4_LINE_20,
    RC381_PART_4_LINE_24,
    RC381_PART_4_LINE_26,
    RC381_PART_4_LINE_27,
    RC381_PART_4_LINE_31,
    RC381_PART_4_LINE_31_DIFFERENCE,
    RC381_PART_4_LINE_32,
    RC381_PART_4_LINE_33,
    RC381_PART_4_LINE_34,
    RC381_PART_4_LINE_35,
    RC381_PART_4_LINE_36,
    RC381_PART_4_LINE_38,
    RC381_PART_4_LINE_40,
    RC381_PART_4_LINE_41,
    RC381_PART_4_LINE_46,
    RC381_PART_4_LINE_46_DIFFERENCE,
    RC381_PART_4_LINE_47,
    RC381_PART_4_LINE_51,
    RC381_PART_4_LINE_51_DIFFERENCE,
    RC381_PART_4_LINE_52,
    RC381_PART_4_LINE_62,
    RC381_PART_4_LINE_65,
    RC381_PART_4_LINE_69,
    RC381_PART_4_LINE_70,
    RC381_PART_4_LINE_80,
    RC381_PART_4_LINE_82,
    RC381_PART_4_LINE_88,
    RC381_PART_4_LINE_89,
    RC381_PART_4_LINE_89_FROM_LINE_69,
    RC381_PART_4_LINE_90,
    RC381_PART_4_LINE_93,
    RC381_PART_4_LINE_94,
    RC381_PART_4_LINE_95,
    RC381_PART_4_LINE_97,
    RC381_PART_4_LINE_100,
    RC381_PART_4_LINE_101,
    RC381_PART_4_LINE_102,
    RC381_PART_4_LINE_104_DIFFERENCE,
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
    T4_CPP_SECOND_ADDITIONAL_BOX_16A,
    T4_QPP_CONTRIBUTIONS_BOX_17,
    T4_QPP_SECOND_ADDITIONAL_BOX_17A,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, rc381_own_trace, run_a


def test_the_trace_records_each_total_as_a_structured_line() -> None:
    # The lines of Form RC381's own steps on Return A's inputs, the return carrying one copy of the
    # form instead of its Schedule 8.
    # Return A's T4 box 26 is its 110000 of employment income.
    result = run_a(schedule_8_copies=0, rc381_copies=1)
    trace = rc381_own_trace(result["ca/rc381"][0])
    subtracted = {line.output: line for line in trace if isinstance(line, SubtractedLine)}
    fractions = {line.output: line for line in trace if isinstance(line, FractionAppliedLine)}
    assert subtracted == {
        # Form RC381 Part 4 line 115 "Line 113 minus line 114", line 118 "Amount A minus line 117"
        # (line 117 being the amount from line 116), line 121 "Line 119 minus line 120" (the
        # amounts from lines 111 and 116) and line 124 "Line 122 minus line 123" (the amounts from
        # lines 112 and 118): every amount is 0 for Return A.
        RC381_PART_4_LINE_115: SubtractedLine(
            output=RC381_PART_4_LINE_115,
            minuend=RC381_PART_4_LINE_113,
            minuend_amount=D("0.00"),
            subtrahend=RC381_PART_4_LINE_114,
            subtrahend_amount=D("0"),
            result=D("0.00"),
        ),
        RC381_PART_4_LINE_118: SubtractedLine(
            output=RC381_PART_4_LINE_118,
            minuend=RC381_PART_4_LINE_116_LESSER,
            minuend_amount=D("0.00"),
            subtrahend=RC381_PART_4_LINE_116,
            subtrahend_amount=D("0.00"),
            result=D("0.00"),
        ),
        RC381_PART_4_LINE_121: SubtractedLine(
            output=RC381_PART_4_LINE_121,
            minuend=RC381_PART_4_LINE_111,
            minuend_amount=D("0.00"),
            subtrahend=RC381_PART_4_LINE_116,
            subtrahend_amount=D("0.00"),
            result=D("0.00"),
        ),
        RC381_PART_4_LINE_124: SubtractedLine(
            output=RC381_PART_4_LINE_124,
            minuend=RC381_PART_4_LINE_112,
            minuend_amount=D("0.00"),
            subtrahend=RC381_PART_4_LINE_118,
            subtrahend_amount=D("0.00"),
            result=D("0.00"),
        ),
        # Form RC381 Part 4 line 95 "Line 93 minus line 94", line 102 "Line 100 minus line 101" and
        # the result printed inside line 104, "the result of line 68 of Part 3 minus line 97":
        # Return A's lines 93, 94, 97, 100 and 101 are 0 and its line 68 of Part 3 is -396.00 (no
        # box 16A against the required 396.00 of line 67), so that result is -396.00.
        RC381_PART_4_LINE_95: SubtractedLine(
            output=RC381_PART_4_LINE_95,
            minuend=RC381_PART_4_LINE_93,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_94,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_102: SubtractedLine(
            output=RC381_PART_4_LINE_102,
            minuend=RC381_PART_4_LINE_100,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_101,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_104_DIFFERENCE: SubtractedLine(
            output=RC381_PART_4_LINE_104_DIFFERENCE,
            minuend=RC381_PART_3_LINE_68,
            minuend_amount=D("-396.00"),
            subtrahend=RC381_PART_4_LINE_97,
            subtrahend_amount=D("0"),
            result=D("-396.00"),
        ),
        # Form RC381 Part 4 line 70 "Line 62 minus line 69", line 80 "Line 78 minus line 79" (the
        # amount from line 4 less the amount from line 65), line 82 "Line 80 minus line 81" (line 81
        # being line 70) and line 90 "Line 88 minus 89.": Return A's line 3 of Part 3 (110000)
        # is not less than line 58 (3,500.00), so lines 65 and 69 are 0; line 4 is 0, so lines 70,
        # 80 and 82 are 0 and lines 88 and 89 are 0.
        RC381_PART_4_LINE_70: SubtractedLine(
            output=RC381_PART_4_LINE_70,
            minuend=RC381_PART_4_LINE_62,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_69,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_80: SubtractedLine(
            output=RC381_PART_4_LINE_80,
            minuend=RC381_PART_4_LINE_4,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_65,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_82: SubtractedLine(
            output=RC381_PART_4_LINE_82,
            minuend=RC381_PART_4_LINE_80,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_70,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_90: SubtractedLine(
            output=RC381_PART_4_LINE_90,
            minuend=RC381_PART_4_LINE_88,
            minuend_amount=D("0.00"),
            subtrahend=RC381_PART_4_LINE_89,
            subtrahend_amount=D("0.00"),
            result=D("0.00"),
        ),
        # Form RC381 Part 4 lines 31 "Line 29 minus line 30" (the amount from line 61 of Part 3 less
        # the amount from line 12), 32 "Line 28 minus line 31" (the QPP T4 contributions less line
        # 31), 35 "Line 33 minus line 34", 38 "Line 36 minus line 37" (line 37 being line 24), 46
        # "Line 44 minus line 45" (the second additional CPP contributions less line 26 of Part 3),
        # 47 "Line 43 minus line 46", 51 "Line 49 minus line 50" (line 68 of Part 3 less line 46)
        # and 52 "Line 48 minus line 51": 0 for Return A; line 31's difference is its line 61
        # (0.00) less line 12 (0.00).
        RC381_PART_4_LINE_31_DIFFERENCE: SubtractedLine(
            output=RC381_PART_4_LINE_31_DIFFERENCE,
            minuend=RC381_PART_3_LINE_61,
            minuend_amount=D("0.00"),
            subtrahend=RC381_PART_4_LINE_12,
            subtrahend_amount=D("0.00"),
            result=D("0.00"),
        ),
        RC381_PART_4_LINE_32: SubtractedLine(
            output=RC381_PART_4_LINE_32,
            minuend=T4_QPP_CONTRIBUTIONS_BOX_17,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_31,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_35: SubtractedLine(
            output=RC381_PART_4_LINE_35,
            minuend=RC381_PART_4_LINE_33,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_34,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_38: SubtractedLine(
            output=RC381_PART_4_LINE_38,
            minuend=RC381_PART_4_LINE_36,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_24,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_46_DIFFERENCE: SubtractedLine(
            output=RC381_PART_4_LINE_46_DIFFERENCE,
            minuend=T4_CPP_SECOND_ADDITIONAL_BOX_16A,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_3_LINE_26,
            subtrahend_amount=D("396.00"),
            result=D("-396.00"),
        ),
        RC381_PART_4_LINE_47: SubtractedLine(
            output=RC381_PART_4_LINE_47,
            minuend=T4_CPP_SECOND_ADDITIONAL_BOX_16A,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_46,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_4_LINE_51_DIFFERENCE: SubtractedLine(
            output=RC381_PART_4_LINE_51_DIFFERENCE,
            minuend=RC381_PART_3_LINE_68,
            minuend_amount=D("-396.00"),
            subtrahend=RC381_PART_4_LINE_46,
            subtrahend_amount=D("0"),
            result=D("-396.00"),
        ),
        RC381_PART_4_LINE_52: SubtractedLine(
            output=RC381_PART_4_LINE_52,
            minuend=T4_QPP_SECOND_ADDITIONAL_BOX_17A,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_4_LINE_51,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        # Form RC381 Part 4 lines 8 "Line 6 minus line 7" (the amounts from lines 20 and 22 of
        # Part 3), 11 "Line 9 minus line 10" (lines 21 and 23), 17 "Line 15 minus line 16" (the T4
        # contributions less line 24) and 20 "Line 18 minus line 19" (the QPP T4 contributions
        # less line 44), and the result printed inside line 13, "Line 5 minus line 12": Return A's
        # box 16 total is 4034.10 (lines 20 and 21 of Part 3 being 3356.10 and 678.00), so lines 8,
        # 11, 12 and 17 carry those and line 13's result is 0; the QPP side is 0.
        RC381_PART_4_LINE_8: SubtractedLine(
            output=RC381_PART_4_LINE_8,
            minuend=RC381_PART_3_LINE_20,
            minuend_amount=D("3356.10"),
            subtrahend=RC381_PART_3_LINE_22,
            subtrahend_amount=D("3356.10"),
            result=D("0.00"),
        ),
        RC381_PART_4_LINE_11: SubtractedLine(
            output=RC381_PART_4_LINE_11,
            minuend=RC381_PART_3_LINE_21,
            minuend_amount=D("678.00"),
            subtrahend=RC381_PART_3_LINE_23,
            subtrahend_amount=D("678.00"),
            result=D("0.00"),
        ),
        RC381_PART_4_LINE_13_DIFFERENCE: SubtractedLine(
            output=RC381_PART_4_LINE_13_DIFFERENCE,
            minuend=CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
            minuend_amount=D("4034.10"),
            subtrahend=RC381_PART_4_LINE_12,
            subtrahend_amount=D("0.00"),
            result=D("4034.10"),
        ),
        RC381_PART_4_LINE_17: SubtractedLine(
            output=RC381_PART_4_LINE_17,
            minuend=CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
            minuend_amount=D("4034.10"),
            subtrahend=RC381_PART_3_LINE_24,
            subtrahend_amount=D("4034.10"),
            result=D("0.00"),
        ),
        RC381_PART_4_LINE_20: SubtractedLine(
            output=RC381_PART_4_LINE_20,
            minuend=T4_QPP_CONTRIBUTIONS_BOX_17,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_3_LINE_44,
            subtrahend_amount=D("0.00"),
            result=D("0.00"),
        ),
        # Form RC381 Part 3 lines 27 to 30 "Amount from line I of Part 2 minus the amount from
        # line 7" (and G less 8, J less 9, H less 10): the QPP row of the table less the CPP
        # shares; Return A's line 6 is 1, so the shares are the whole row and each is 0.00.
        RC381_PART_3_LINE_27: SubtractedLine(
            output=RC381_PART_3_LINE_27,
            minuend=RC381_PART_2_LINE_I,
            minuend_amount=D("81200.00"),
            subtrahend=RC381_PART_3_LINE_7,
            subtrahend_amount=D("81200.00"),
            result=D("0.00"),
        ),
        RC381_PART_3_LINE_28: SubtractedLine(
            output=RC381_PART_3_LINE_28,
            minuend=RC381_PART_2_LINE_G,
            minuend_amount=D("71300.00"),
            subtrahend=RC381_PART_3_LINE_8,
            subtrahend_amount=D("71300.00"),
            result=D("0.00"),
        ),
        RC381_PART_3_LINE_29: SubtractedLine(
            output=RC381_PART_3_LINE_29,
            minuend=RC381_PART_2_LINE_J,
            minuend_amount=D("3500.00"),
            subtrahend=RC381_PART_3_LINE_9,
            subtrahend_amount=D("3500.00"),
            result=D("0.00"),
        ),
        RC381_PART_3_LINE_30: SubtractedLine(
            output=RC381_PART_3_LINE_30,
            minuend=RC381_PART_2_LINE_H,
            minuend_amount=D("9900.00"),
            subtrahend=RC381_PART_3_LINE_10,
            subtrahend_amount=D("9900.00"),
            result=D("0.00"),
        ),
        # Form RC381 Part 3 line 36 "Line 31 minus line 35": both are 0.
        RC381_PART_3_LINE_36: SubtractedLine(
            output=RC381_PART_3_LINE_36,
            minuend=RC381_PART_3_LINE_31,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_3_LINE_35,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        # Form RC381 Part 3 line 41 "Line 39 minus line 40": both are 0.
        RC381_PART_3_LINE_41: SubtractedLine(
            output=RC381_PART_3_LINE_41,
            minuend=T4_QPP_CONTRIBUTIONS_BOX_17,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_3_LINE_40,
            subtrahend_amount=D("0.00"),
            result=D("0.00"),
        ),
        # Form RC381 Part 3 lines 53, 60 and 68 "Line 49 minus line 52", "Line 56 minus line 59"
        # and "Line 64 minus line 67": Return A's actual base (3356.10) and first additional
        # (678.00) contributions from its T4 box 16 total, equal to the required contributions of
        # lines 52 and 59 on its 110000 of T4 box 26, so lines 53 and 60 are 0.00; line 68 is
        # -396.00 (no box 16A against the required 396.00 of line 67).
        RC381_PART_3_LINE_53: SubtractedLine(
            output=RC381_PART_3_LINE_53,
            minuend=RC381_PART_3_LINE_49,
            minuend_amount=D("3356.10"),
            subtrahend=RC381_PART_3_LINE_52,
            subtrahend_amount=D("3356.10"),
            result=D("0.00"),
        ),
        RC381_PART_3_LINE_60: SubtractedLine(
            output=RC381_PART_3_LINE_60,
            minuend=RC381_PART_3_LINE_56,
            minuend_amount=D("678.00"),
            subtrahend=RC381_PART_3_LINE_59,
            subtrahend_amount=D("678.00"),
            result=D("0.00"),
        ),
        RC381_PART_3_LINE_68: SubtractedLine(
            output=RC381_PART_3_LINE_68,
            minuend=RC381_PART_3_LINE_64,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_3_LINE_67,
            subtrahend_amount=D("396.00"),
            result=D("-396.00"),
        ),
        # Form RC381 Part 3b lines 78 "Line 76 minus line 77" and 85 "Line 83 minus line 84", and
        # the result printed inside line 87, "the result of line 68 minus line 80": all 0 for
        # Return A.
        RC381_PART_3_LINE_78: SubtractedLine(
            output=RC381_PART_3_LINE_78,
            minuend=RC381_PART_3_LINE_76,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_3_LINE_77,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_3_LINE_85: SubtractedLine(
            output=RC381_PART_3_LINE_85,
            minuend=RC381_PART_3_LINE_83,
            minuend_amount=D("0"),
            subtrahend=RC381_PART_3_LINE_84,
            subtrahend_amount=D("0"),
            result=D("0"),
        ),
        RC381_PART_3_LINE_87_DIFFERENCE: SubtractedLine(
            output=RC381_PART_3_LINE_87_DIFFERENCE,
            minuend=RC381_PART_3_LINE_68,
            minuend_amount=D("-396.00"),
            subtrahend=RC381_PART_3_LINE_80,
            subtrahend_amount=D("0"),
            result=D("-396.00"),
        ),
        # Form RC381 Part 3 line 16 "Line 11 minus line 15": both are 0.
        RC381_PART_3_LINE_16: SubtractedLine(
            output=RC381_PART_3_LINE_16,
            minuend=RC381_PART_3_LINE_11,
            minuend_amount=D("81200.00"),
            subtrahend=RC381_PART_3_LINE_15,
            subtrahend_amount=D("9900.00"),
            result=D("71300.00"),
        ),
        # Form RC381 Part 3 line 21 "Line 19 minus line 20": the T4 box 16 total of 4034.10 less
        # line 20, 3356.10, 678.00.
        RC381_PART_3_LINE_21: SubtractedLine(
            output=RC381_PART_3_LINE_21,
            minuend=CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
            minuend_amount=D("4034.10"),
            subtrahend=RC381_PART_3_LINE_20,
            subtrahend_amount=D("3356.10"),
            result=D("678.00"),
        ),
    }
    assert fractions == {
        # Form RC381 Part 4 line 89 "Amount from line 69 of Part 3 (if positive) × 2": the amount
        # is 0 for Return A.
        RC381_PART_4_LINE_89: FractionAppliedLine(
            output=RC381_PART_4_LINE_89,
            base=RC381_PART_4_LINE_89_FROM_LINE_69,
            base_amount=D("0"),
            fraction=Fraction(2, 1),
            rounding=CENT,
            result=D("0.00"),
        ),
        # Form RC381 Part 4 line 41 "Amount from line 40 × 15.625": line 40 is 0.
        RC381_PART_4_LINE_41: FractionAppliedLine(
            output=RC381_PART_4_LINE_41,
            base=RC381_PART_4_LINE_40,
            base_amount=D("0"),
            fraction=Fraction(15625, 1000),
            rounding=CENT,
            result=D("0"),
        ),
        # Form RC381 Part 4 line 27 "Amount from line 26 × 16.80672": line 26 is 0.
        RC381_PART_4_LINE_27: FractionAppliedLine(
            output=RC381_PART_4_LINE_27,
            base=RC381_PART_4_LINE_26,
            base_amount=D("4034.10"),
            fraction=Fraction(1680672, 100000),
            rounding=CENT,
            result=D("67799.99"),
        ),
    }
