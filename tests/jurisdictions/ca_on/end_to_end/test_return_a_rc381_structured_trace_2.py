"""CA-ON 2025 end to end, Return A carrying Form RC381: the form's structured trace 2."""

from __future__ import annotations

from tax_calculator.domain.trace import (
    SumLine,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CPT20_EARNINGS,
    CPT20_T4_EARNINGS,
    PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS,
    RC381_PART_3_LINE_3,
    RC381_PART_3_LINE_11,
    RC381_PART_3_LINE_20,
    RC381_PART_3_LINE_21,
    RC381_PART_3_LINE_22,
    RC381_PART_3_LINE_23,
    RC381_PART_3_LINE_24,
    RC381_PART_3_LINE_26,
    RC381_PART_3_LINE_31,
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
    RC381_PART_3_LINE_77,
    RC381_PART_3_LINE_79,
    RC381_PART_3_LINE_80,
    RC381_PART_3_LINE_81,
    RC381_PART_3_LINE_82,
    RC381_PART_3_LINE_84,
    RC381_PART_3_LINE_86,
    RC381_PART_3_LINE_87,
    RC381_PART_3_LINE_88,
    RC381_PART_3_LINE_89,
    RC381_PART_3_LINE_91,
    RC381_PART_3_LINE_92,
    RC381_PART_3_LINE_93,
    RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
    RC381_PART_4_LINE_4,
    RC381_PART_4_LINE_8,
    RC381_PART_4_LINE_11,
    RC381_PART_4_LINE_12,
    RC381_PART_4_LINE_13,
    RC381_PART_4_LINE_24,
    RC381_PART_4_LINE_25A,
    RC381_PART_4_LINE_26,
    RC381_PART_4_LINE_27,
    RC381_PART_4_LINE_32,
    RC381_PART_4_LINE_35A,
    RC381_PART_4_LINE_35AA,
    RC381_PART_4_LINE_35AB,
    RC381_PART_4_LINE_39,
    RC381_PART_4_LINE_40,
    RC381_PART_4_LINE_41,
    RC381_PART_4_LINE_42,
    RC381_PART_4_LINE_47,
    RC381_PART_4_LINE_52,
    RC381_PART_4_LINE_53,
    RC381_PART_4_LINE_55,
    RC381_PART_4_LINE_56,
    RC381_PART_4_LINE_70,
    RC381_PART_4_LINE_74,
    RC381_PART_4_LINE_83,
    RC381_PART_4_LINE_84,
    RC381_PART_4_LINE_85,
    RC381_PART_4_LINE_86,
    RC381_PART_4_LINE_87,
    RC381_PART_4_LINE_88,
    RC381_PART_4_LINE_92,
    RC381_PART_4_LINE_94,
    RC381_PART_4_LINE_96,
    RC381_PART_4_LINE_97,
    RC381_PART_4_LINE_98,
    RC381_PART_4_LINE_99,
    RC381_PART_4_LINE_101,
    RC381_PART_4_LINE_103,
    RC381_PART_4_LINE_104,
    RC381_PART_4_LINE_105,
    RC381_PART_4_LINE_106,
    RC381_PART_4_LINE_108,
    RC381_PART_4_LINE_109,
    RC381_PART_4_LINE_110,
    RC381_PART_4_LINE_111,
    RC381_PART_4_LINE_112,
    RC381_PART_4_LINE_113,
    RC381_PART_4_LINE_121,
    RC381_PART_4_LINE_124,
    RC381_PART_4_LINE_125,
    RC381_PART_4_LINE_128,
    RC381_PART_4_LINE_129,
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
    T4_CPP_SECOND_ADDITIONAL_BOX_16A,
    T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC,
    T4_QPP_SECOND_ADDITIONAL_BOX_17A,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, rc381_own_trace, run_a


def test_the_trace_records_each_total_as_a_structured_line() -> None:
    # The lines of Form RC381's own steps on Return A's inputs, the return carrying one copy of the
    # form instead of its Schedule 8.
    # Return A's T4 box 26 is its 110000 of employment income.
    result = run_a(schedule_8_copies=0, rc381_copies=1)
    trace = rc381_own_trace(result["ca/rc381"][0])
    sums = {line.output: line for line in trace if isinstance(line, SumLine)}
    assert sums == {
        # Form RC381 Part 4 line 113 "Line 111 plus line 112", line 129 "Add lines 121, 122, 124,
        # 125, and 128." (the amount for line 22200; line 122 is the amount from line 112) and the
        # earnings subject to contributions, lines 70 and 83 added: every contribution is 0.00 for
        # Return A, whose line 70 is 0 (no election, and its 110000 of T4 box 26 is not less than
        # line 58, so line 69 is "0").
        RC381_PART_4_LINE_113: SumLine(
            RC381_PART_4_LINE_113,
            ((RC381_PART_4_LINE_111, D("0.00")), (RC381_PART_4_LINE_112, D("0.00"))),
            D("0.00"),
        ),
        RC381_PART_4_LINE_129: SumLine(
            RC381_PART_4_LINE_129,
            (
                (RC381_PART_4_LINE_121, D("0.00")),
                (RC381_PART_4_LINE_112, D("0.00")),
                (RC381_PART_4_LINE_124, D("0.00")),
                (RC381_PART_4_LINE_125, D("0.00")),
                (RC381_PART_4_LINE_128, D("0")),
            ),
            D("0.00"),
        ),
        RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS: SumLine(
            RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
            ((RC381_PART_4_LINE_70, D("0")), (RC381_PART_4_LINE_83, D("0"))),
            D("0"),
        ),
        # Form RC381 Part 4 line 96 "Line 92 plus line 94", line 98 "Line 96 plus line 97", line 103
        # "Line 99 plus line 101", line 105 "Line 103 plus line 104", line 109 "Line 106 plus line
        # 108" and line 110 "Line 105 plus line 109": Return A's lines 92 (3356.10) and 99 (678.00)
        # carry lines 52 and 59 of Part 3 and every other part is 0 (lines 53, 60 and 61 of Part 3
        # are 0.00, as its T4 box 16 total equals the required contributions).
        RC381_PART_4_LINE_96: SumLine(
            RC381_PART_4_LINE_96,
            ((RC381_PART_4_LINE_92, D("3356.10")), (RC381_PART_4_LINE_94, D("0"))),
            D("3356.10"),
        ),
        RC381_PART_4_LINE_98: SumLine(
            RC381_PART_4_LINE_98,
            ((RC381_PART_4_LINE_96, D("3356.10")), (RC381_PART_4_LINE_97, D("0"))),
            D("3356.10"),
        ),
        RC381_PART_4_LINE_103: SumLine(
            RC381_PART_4_LINE_103,
            ((RC381_PART_4_LINE_99, D("678.00")), (RC381_PART_4_LINE_101, D("0"))),
            D("678.00"),
        ),
        RC381_PART_4_LINE_105: SumLine(
            RC381_PART_4_LINE_105,
            ((RC381_PART_4_LINE_103, D("678.00")), (RC381_PART_4_LINE_104, D("0"))),
            D("678.00"),
        ),
        RC381_PART_4_LINE_109: SumLine(
            RC381_PART_4_LINE_109,
            ((RC381_PART_4_LINE_106, D("0.00")), (RC381_PART_4_LINE_108, D("0"))),
            D("0.00"),
        ),
        RC381_PART_4_LINE_110: SumLine(
            RC381_PART_4_LINE_110,
            ((RC381_PART_4_LINE_105, D("678.00")), (RC381_PART_4_LINE_109, D("0"))),
            D("678.00"),
        ),
        # Form RC381 Part 4 line 74 "Add lines 71 to 73." (the amounts from line 4 and from lines
        # 11 and 31 of Part 3), line 87 "Line 85 plus line 86" and line 88
        # "Line 84 plus line 87": Return A has no election (line 4 is 0), line 11 of Part 3 is
        # 81,200.00 and line 31 is 0, so line 74 is 81,200.00; every part of lines 87 and 88 is
        # 0.00.
        RC381_PART_4_LINE_74: SumLine(
            RC381_PART_4_LINE_74,
            (
                (RC381_PART_4_LINE_4, D("0")),
                (RC381_PART_3_LINE_11, D("81200.00")),
                (RC381_PART_3_LINE_31, D("0")),
            ),
            D("81200.00"),
        ),
        RC381_PART_4_LINE_87: SumLine(
            RC381_PART_4_LINE_87,
            ((RC381_PART_4_LINE_85, D("0.00")), (RC381_PART_4_LINE_86, D("0.00"))),
            D("0.00"),
        ),
        RC381_PART_4_LINE_88: SumLine(
            RC381_PART_4_LINE_88,
            ((RC381_PART_4_LINE_84, D("0.00")), (RC381_PART_4_LINE_87, D("0.00"))),
            D("0.00"),
        ),
        # Form RC381 Part 4 line 35A "If line 35 and line 17 are both positive, enter the amount
        # from line 17. If line 35 is "0" and line 20 is positive, enter the amount from line 20
        # (show in brackets)." (the two sentences added), line 40 "Add lines 32, 35A, and 39.",
        # line 42 "Line 27 plus line 41", line 53 "Line 47 plus line 52" and line 56 "Line 53 plus
        # line 55": every part is 0 for Return A, whose lines 17 and 20 are 0.00, except line 42:
        # line 27 is 67799.99 (the QPP row less lines 7 to 10 of Part 3) and line 41 is 0.00.
        RC381_PART_4_LINE_35A: SumLine(
            RC381_PART_4_LINE_35A,
            ((RC381_PART_4_LINE_35AA, D("0")), (RC381_PART_4_LINE_35AB, D("0"))),
            D("0"),
        ),
        RC381_PART_4_LINE_40: SumLine(
            RC381_PART_4_LINE_40,
            (
                (RC381_PART_4_LINE_32, D("0")),
                (RC381_PART_4_LINE_35A, D("0")),
                (RC381_PART_4_LINE_39, D("0")),
            ),
            D("0"),
        ),
        RC381_PART_4_LINE_42: SumLine(
            RC381_PART_4_LINE_42,
            ((RC381_PART_4_LINE_27, D("67799.99")), (RC381_PART_4_LINE_41, D("0.00"))),
            D("67799.99"),
        ),
        RC381_PART_4_LINE_53: SumLine(
            RC381_PART_4_LINE_53,
            ((RC381_PART_4_LINE_47, D("0")), (RC381_PART_4_LINE_52, D("0"))),
            D("0"),
        ),
        RC381_PART_4_LINE_56: SumLine(
            RC381_PART_4_LINE_56,
            ((RC381_PART_4_LINE_53, D("0")), (RC381_PART_4_LINE_55, D("0"))),
            D("0"),
        ),
        # Form RC381 Part 4 line 4 "Add lines 1 to 3." (the pensionable net self-employment
        # earnings, the CPT20 earnings not on a T4 slip and the CPT20 earnings on a T4 slip),
        # line 12 "Line 8 plus line 11 (if negative, show in brackets)" and line 26 "Add lines 24
        # to 25A." (line 25 being the amount from line 13): Return A has no self-employment earnings
        # (lines 4 and 26 are 0) and lines 8 and 11 are 0.00, its T4 box 16 total of 4034.10 being
        # the required 3356.10 and 678.00 of lines 22 and 23 of Part 3.
        RC381_PART_4_LINE_4: SumLine(
            RC381_PART_4_LINE_4,
            (
                (PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS, D("0")),
                (CPT20_EARNINGS, D("0")),
                (CPT20_T4_EARNINGS, D("0")),
            ),
            D("0"),
        ),
        RC381_PART_4_LINE_12: SumLine(
            RC381_PART_4_LINE_12,
            ((RC381_PART_4_LINE_8, D("0.00")), (RC381_PART_4_LINE_11, D("0.00"))),
            D("0.00"),
        ),
        RC381_PART_4_LINE_26: SumLine(
            RC381_PART_4_LINE_26,
            (
                (RC381_PART_4_LINE_24, D("0")),
                (RC381_PART_4_LINE_13, D("4034.10")),
                (RC381_PART_4_LINE_25A, D("0")),
            ),
            D("4034.10"),
        ),
        # Form RC381 Part 3 lines 44, 49, 52, 56, 59, 61, 64, 67 and 69, each "Line N plus line M"
        # (or "Total ...: line N plus line M"): Return A enters a T4 box 16 total of 4034.10
        # (3356.10 base, 678.00 first additional) and no pensionable earnings, so the actual
        # figures are those and the required, QPP and second additional parts are 0.
        RC381_PART_3_LINE_44: SumLine(
            RC381_PART_3_LINE_44,
            ((RC381_PART_3_LINE_42, D("0.00")), (RC381_PART_3_LINE_43, D("0.00"))),
            D("0.00"),
        ),
        RC381_PART_3_LINE_49: SumLine(
            RC381_PART_3_LINE_49,
            ((RC381_PART_3_LINE_20, D("3356.10")), (RC381_PART_3_LINE_40, D("0.00"))),
            D("3356.10"),
        ),
        RC381_PART_3_LINE_52: SumLine(
            RC381_PART_3_LINE_52,
            ((RC381_PART_3_LINE_22, D("3356.10")), (RC381_PART_3_LINE_42, D("0.00"))),
            D("3356.10"),
        ),
        RC381_PART_3_LINE_56: SumLine(
            RC381_PART_3_LINE_56,
            ((RC381_PART_3_LINE_21, D("678.00")), (RC381_PART_3_LINE_41, D("0.00"))),
            D("678.00"),
        ),
        RC381_PART_3_LINE_59: SumLine(
            RC381_PART_3_LINE_59,
            ((RC381_PART_3_LINE_23, D("678.00")), (RC381_PART_3_LINE_43, D("0.00"))),
            D("678.00"),
        ),
        RC381_PART_3_LINE_61: SumLine(
            RC381_PART_3_LINE_61,
            ((RC381_PART_3_LINE_53, D("0.00")), (RC381_PART_3_LINE_60, D("0.00"))),
            D("0.00"),
        ),
        RC381_PART_3_LINE_64: SumLine(
            RC381_PART_3_LINE_64,
            (
                (T4_CPP_SECOND_ADDITIONAL_BOX_16A, D("0")),
                (T4_QPP_SECOND_ADDITIONAL_BOX_17A, D("0")),
            ),
            D("0"),
        ),
        RC381_PART_3_LINE_67: SumLine(
            RC381_PART_3_LINE_67,
            ((RC381_PART_3_LINE_26, D("396.00")), (RC381_PART_3_LINE_46, D("0.00"))),
            D("396.00"),
        ),
        RC381_PART_3_LINE_69: SumLine(
            RC381_PART_3_LINE_69,
            ((RC381_PART_3_LINE_61, D("0.00")), (RC381_PART_3_LINE_68, D("-396.00"))),
            D("-396.00"),
        ),
        # Form RC381 Part 3a line 73 "Line 71 plus line 72" (lines 59 and 67), and Part 3b lines
        # 79 "Line 75 plus line 77", 81 "Line 79 plus line 80", 86 "Line 82 plus line 84", 88
        # "Line 86 plus line 87", 92 "Line 89 plus line 91" and 93 "Line 88 plus line 92": Return
        # A's line 73 is its 678.00 and 396.00 of lines 59 and 67; in Part 3b lines 79 and 81 carry
        # its 3356.10 and lines 86, 88 and 93 its 678.00, and line 92 is 0.
        RC381_PART_3_LINE_73: SumLine(
            RC381_PART_3_LINE_73,
            ((RC381_PART_3_LINE_59, D("678.00")), (RC381_PART_3_LINE_67, D("396.00"))),
            D("1074.00"),
        ),
        RC381_PART_3_LINE_79: SumLine(
            RC381_PART_3_LINE_79,
            ((RC381_PART_3_LINE_75, D("3356.10")), (RC381_PART_3_LINE_77, D("0"))),
            D("3356.10"),
        ),
        RC381_PART_3_LINE_81: SumLine(
            RC381_PART_3_LINE_81,
            ((RC381_PART_3_LINE_79, D("3356.10")), (RC381_PART_3_LINE_80, D("0"))),
            D("3356.10"),
        ),
        RC381_PART_3_LINE_86: SumLine(
            RC381_PART_3_LINE_86,
            ((RC381_PART_3_LINE_82, D("678.00")), (RC381_PART_3_LINE_84, D("0"))),
            D("678.00"),
        ),
        RC381_PART_3_LINE_88: SumLine(
            RC381_PART_3_LINE_88,
            ((RC381_PART_3_LINE_86, D("678.00")), (RC381_PART_3_LINE_87, D("0"))),
            D("678.00"),
        ),
        RC381_PART_3_LINE_92: SumLine(
            RC381_PART_3_LINE_92,
            ((RC381_PART_3_LINE_89, D("0")), (RC381_PART_3_LINE_91, D("0"))),
            D("0"),
        ),
        RC381_PART_3_LINE_93: SumLine(
            RC381_PART_3_LINE_93,
            ((RC381_PART_3_LINE_88, D("678.00")), (RC381_PART_3_LINE_92, D("0"))),
            D("678.00"),
        ),
        # Form RC381 Part 3 line 3 "Line 1 plus line 2 Total pensionable earnings": Return A's T4
        # pensionable earnings are 110000 on line 1 and none on line 2.
        RC381_PART_3_LINE_3: SumLine(
            RC381_PART_3_LINE_3,
            (
                (T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC, D("110000")),
                (T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC, D("0")),
            ),
            D("110000"),
        ),
        # Form RC381 Part 3 line 24 "Line 22 plus line 23": both are 0.
        RC381_PART_3_LINE_24: SumLine(
            RC381_PART_3_LINE_24,
            ((RC381_PART_3_LINE_22, D("3356.10")), (RC381_PART_3_LINE_23, D("678.00"))),
            D("4034.10"),
        ),
    }
