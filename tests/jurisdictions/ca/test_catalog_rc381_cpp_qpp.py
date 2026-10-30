"""Registered, money and count kinds of the federal catalog family `rc381_cpp_qpp`.

Form RC381 (2025), "Inter-Provincial Calculation for CPP and QPP Contributions and Overpayments"
(`docs/cra-forms-2025/rc381-25e.pdf`): Part 2 (the months and the monthly proration table) and
Part 3 lines 1 to 3, 6 to 11, 14 to 16, 18 to 24, 26 to 31, 34 to 36, 38, 40 to 44, 46, 49, 52, 53,
56, 59 to 61, 64 and 67 to 69, and the entries on lines 19, 25, 39 and 45, then Part 3a and Part 3b
(lines 73, 75 to 93, the helper under line 87 and the three results for lines 30800, 22215 and
44800), then Part 4 lines 1 to 27 (the CPP side before the QPP gross-up: lines 4, 8, 11 to 14, 17,
17A, 20 to 27, and the helpers printed inside lines 13, 21, 23 and 24), then Part 4 lines 31 to 56
(the QPP side before the gross-up and the totals: lines 31 to 36, 38 to 42, 46, 47, 51 to 56, and
the helpers printed inside lines 31, 35A, 46 and 51), then Part 4 lines 57 to 91 (the earnings
subject to contributions: lines 59, 61, 62, 65, 68, 69, 70, 74, 76, 77, 80, 82 and 83 with the
helper printed inside line 83; the self-employed contributions: lines 84 to 88; the contributions
payable and the overpayment: lines 89 to 91 with the helpers printed inside lines 89 and 91 and the
amount for line 42100), then Part 4 lines 92 to 110 (the base and enhanced contributions through
employment income: lines 92 to 110 with the helper printed inside line 104), then Part 4 lines 111
to 129 (the base and enhanced contributions through self-employment income and other earnings:
lines 111 to 115, the amount lettered A, which is a helper printed inside line 116, and lines 116,
118, 121, 124, 125, 127, 128 and 129), then the final selection (the earnings subject to
contributions, lines 70 and 83 of Part 4 added, and the six results for lines 30800, 22215, 44800,
42100, 31000 and 22200 of the return). The eight kinds a caller enters and the results carry a
docstring that quotes the form's own words. Lines 53,
60, 61, 68 and 69 are signed: "if negative, show in brackets". So is the helper under line 87, "the
result of line 68 minus line 80". In Part 4 lines 8, 11, 12, 17 and 20 are signed for the same
reason, and so are line 4 (line 1 is not floored), lines 21, 23 to 25A and 26 and 27, then lines 31
and 32 (line 12 may be more than line 61), 35A, 38 to 42, 46, 47, 51 to 53 and 56, then lines 62 and
70 to 83 (no floor is printed, and line 4 is not floored: lines 74 and 76, 80 and 82, the lesser of
lines 77 and 82 before the gate) and line 90 "(if negative, show in brackets)", then the helper
printed inside line 104 ("the result of line 68 of Part 3 minus line 97"), then lines 115 ("if
negative, show in brackets"), 121 and 124 (no floor is printed, and a cent of rounding can make
them negative) and the earnings subject to contributions (line 70 has no floor).
"""

from __future__ import annotations

import ast
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

import tax_engine.jurisdictions.ca.catalog
from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.parameters.rate import Rate
from tax_engine.jurisdictions.ca.catalog import (
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
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
    T4_CPP_SECOND_ADDITIONAL_BOX_16A,
    T4_CPP_SLIP_COUNT,
    T4_QPP_CONTRIBUTIONS_BOX_17,
    T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC,
    T4_QPP_SECOND_ADDITIONAL_BOX_17A,
    T4_QPP_SLIP_COUNT,
)

INPUT_AMOUNTS: tuple[ArtifactKind[Decimal], ...] = (
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
    T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC,
    T4_CPP_SECOND_ADDITIONAL_BOX_16A,
    T4_QPP_CONTRIBUTIONS_BOX_17,
    T4_QPP_SECOND_ADDITIONAL_BOX_17A,
)

PART_2_AMOUNTS: tuple[ArtifactKind[Decimal], ...] = (
    RC381_PART_2_LINE_G,
    RC381_PART_2_LINE_H,
    RC381_PART_2_LINE_I,
    RC381_PART_2_LINE_J,
)

PART_3_AMOUNTS: tuple[ArtifactKind[Decimal], ...] = (
    RC381_PART_3_LINE_3,
    RC381_PART_3_LINE_7,
    RC381_PART_3_LINE_8,
    RC381_PART_3_LINE_9,
    RC381_PART_3_LINE_10,
    RC381_PART_3_LINE_11,
    RC381_PART_3_LINE_14,
    RC381_PART_3_LINE_15_LESSER,
    RC381_PART_3_LINE_15,
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
    RC381_PART_3_LINE_49,
    RC381_PART_3_LINE_52,
    RC381_PART_3_LINE_56,
    RC381_PART_3_LINE_59,
    RC381_PART_3_LINE_64,
    RC381_PART_3_LINE_67,
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
    RC381_PART_3_LINE_88,
    RC381_PART_3_LINE_89,
    RC381_PART_3_LINE_90,
    RC381_PART_3_LINE_91,
    RC381_PART_3_LINE_92,
    RC381_PART_3_LINE_93,
)

# Part 4 lines that cannot come out below zero: the lines that print no "if negative, show in
# brackets" and are an amount less an amount that is never more (line 13 is line 5 less line 12,
# which is line 5 less (line 19 less line 24), so line 24 of Part 3 or line 5 itself), a positive
# part (lines 14, 17A, 33, 36 and 54), or the lesser of two lines that are both above zero (lines
# 21's, 34, 35A's amount from line 17 and 55). Line 35 is line 33 less line 34, which is never
# more than line 33; line 35A's first sentence is line 17 or "0". Lines 59, 61, 65, 68, 69 and 77
# print "(if negative, enter "0")", line 89's amount is line 69 "(if positive)" and line 91's is
# line 90 "entered as a positive amount"; lines 84 to 86 are tiers (never below zero, whatever the
# earnings) and lines 87, 88 and 89 add or double non-negative lines. Lines 92, 99 and 106 are a
# non-negative total of Part 3 either way, lines 93, 100 and 107 are positive parts, lines 94, 97,
# 101, 104 and 108 are the lesser of two lines that are both above zero (else "0"), lines 95 and
# 102 are a line less the lesser of it and another (never below zero), and lines 96, 98, 103, 105,
# 109 and 110 add non-negative lines. Lines 111, 112 and 125 are 50% of a tier (never below zero),
# line 113 adds two of them, line 114 is line 69 of Part 3 "if positive", A is the lesser of two
# non-negative lines, line 116 is 83.1933% of it and line 118 the rest (never below zero, as line
# 116 is less than A), line 127 is a positive part, line 128 prints "(if negative, enter "0")" and
# line 129 is lines 121 and 124 (which together are line 113 less A, never below zero) added to
# non-negative lines.
PART_4_AMOUNTS: tuple[ArtifactKind[Decimal], ...] = (
    RC381_PART_4_LINE_13_DIFFERENCE,
    RC381_PART_4_LINE_13,
    RC381_PART_4_LINE_14,
    RC381_PART_4_LINE_17A,
    RC381_PART_4_LINE_21_LESSER,
    RC381_PART_4_LINE_33,
    RC381_PART_4_LINE_34,
    RC381_PART_4_LINE_35,
    RC381_PART_4_LINE_35AA_FROM_LINE_17,
    RC381_PART_4_LINE_35AA,
    RC381_PART_4_LINE_36,
    RC381_PART_4_LINE_54,
    RC381_PART_4_LINE_55,
    RC381_PART_4_LINE_59,
    RC381_PART_4_LINE_61,
    RC381_PART_4_LINE_65,
    RC381_PART_4_LINE_68,
    RC381_PART_4_LINE_69,
    RC381_PART_4_LINE_77,
    RC381_PART_4_LINE_84,
    RC381_PART_4_LINE_85,
    RC381_PART_4_LINE_86,
    RC381_PART_4_LINE_87,
    RC381_PART_4_LINE_88,
    RC381_PART_4_LINE_89_FROM_LINE_69,
    RC381_PART_4_LINE_89,
    RC381_PART_4_LINE_91_FROM_LINE_90,
    RC381_PART_4_LINE_92,
    RC381_PART_4_LINE_93,
    RC381_PART_4_LINE_94,
    RC381_PART_4_LINE_95,
    RC381_PART_4_LINE_96,
    RC381_PART_4_LINE_97,
    RC381_PART_4_LINE_99,
    RC381_PART_4_LINE_100,
    RC381_PART_4_LINE_101,
    RC381_PART_4_LINE_102,
    RC381_PART_4_LINE_103,
    RC381_PART_4_LINE_104,
    RC381_PART_4_LINE_105,
    RC381_PART_4_LINE_106,
    RC381_PART_4_LINE_107,
    RC381_PART_4_LINE_108,
    RC381_PART_4_LINE_109,
    RC381_PART_4_LINE_112,
    RC381_PART_4_LINE_113,
    RC381_PART_4_LINE_114,
    RC381_PART_4_LINE_116_LESSER,
    RC381_PART_4_LINE_116,
    RC381_PART_4_LINE_118,
    RC381_PART_4_LINE_125,
    RC381_PART_4_LINE_127,
    RC381_PART_4_LINE_128,
)

# The three results of Part 3a and Part 3b for "earnings subject to contributions ... from
# employment income only": lines 30800, 22215 and 44800 of the return. Part 4's line 90 when it is
# positive: line 42100, line 91: line 44800, line 98: line 30800, line 110: line 22215, line 111:
# line 31000 and line 129: line 22200. The final selection's six results are the same six lines of
# the return, from Part 4 when the earnings subject to contributions are above zero, else from
# Part 3 ("return to Part 3") or "0".
RESULT_AMOUNTS: tuple[ArtifactKind[Decimal], ...] = (
    RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS,
    RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS,
    RC381_CPP_OVERPAYMENT,
    RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS,
    RC381_PART_4_LINE_91,
    RC381_PART_4_LINE_98,
    RC381_PART_4_LINE_110,
    RC381_PART_4_LINE_111,
    RC381_PART_4_LINE_129,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_OVERPAYMENT_ON_RETURN,
    RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
)

# Lines whose difference or sum can come out below zero: "if negative, show in brackets".
SIGNED_AMOUNTS: tuple[ArtifactKind[Decimal], ...] = (
    RC381_PART_3_LINE_53,
    RC381_PART_3_LINE_60,
    RC381_PART_3_LINE_61,
    RC381_PART_3_LINE_68,
    RC381_PART_3_LINE_69,
    RC381_PART_3_LINE_87_DIFFERENCE,
    RC381_PART_4_LINE_4,
    RC381_PART_4_LINE_8,
    RC381_PART_4_LINE_11,
    RC381_PART_4_LINE_12,
    RC381_PART_4_LINE_17,
    RC381_PART_4_LINE_20,
    RC381_PART_4_LINE_21_FROM_LINE_17,
    RC381_PART_4_LINE_21,
    RC381_PART_4_LINE_23_LESSER,
    RC381_PART_4_LINE_23_MULTIPLIED,
    RC381_PART_4_LINE_23,
    RC381_PART_4_LINE_24_LESSER,
    RC381_PART_4_LINE_24,
    RC381_PART_4_LINE_25A,
    RC381_PART_4_LINE_26,
    RC381_PART_4_LINE_27,
    RC381_PART_4_LINE_31_DIFFERENCE,
    RC381_PART_4_LINE_31,
    RC381_PART_4_LINE_32,
    RC381_PART_4_LINE_35AB_FROM_LINE_20,
    RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO,
    RC381_PART_4_LINE_35AB,
    RC381_PART_4_LINE_35A,
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
    RC381_PART_4_LINE_56,
    RC381_PART_4_LINE_62,
    RC381_PART_4_LINE_70,
    RC381_PART_4_LINE_74,
    RC381_PART_4_LINE_76,
    RC381_PART_4_LINE_80,
    RC381_PART_4_LINE_82,
    RC381_PART_4_LINE_83_LESSER,
    RC381_PART_4_LINE_83,
    RC381_PART_4_LINE_90,
    RC381_PART_4_LINE_104_DIFFERENCE,
    RC381_PART_4_LINE_115,
    RC381_PART_4_LINE_121,
    RC381_PART_4_LINE_124,
    RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS,
)


def test_the_rc381_part_2_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/qpp_months") is QPP_MONTHS
    assert registry.get("ca/rc381_part_2_line_b") is RC381_PART_2_LINE_B
    assert registry.get("ca/rc381_part_2_line_g") is RC381_PART_2_LINE_G
    assert registry.get("ca/rc381_part_2_line_h") is RC381_PART_2_LINE_H
    assert registry.get("ca/rc381_part_2_line_i") is RC381_PART_2_LINE_I
    assert registry.get("ca/rc381_part_2_line_j") is RC381_PART_2_LINE_J


def test_the_rc381_part_3_input_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert (
        registry.get("ca/t4_cpp_pensionable_earnings_outside_quebec")
        is T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC
    )
    assert (
        registry.get("ca/t4_qpp_pensionable_earnings_in_quebec")
        is T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC
    )
    assert registry.get("ca/t4_cpp_second_additional_box_16a") is T4_CPP_SECOND_ADDITIONAL_BOX_16A
    assert registry.get("ca/t4_qpp_contributions_box_17") is T4_QPP_CONTRIBUTIONS_BOX_17
    assert registry.get("ca/t4_qpp_second_additional_box_17a") is T4_QPP_SECOND_ADDITIONAL_BOX_17A


def test_the_rc381_part_3_line_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/rc381_part_3_line_3") is RC381_PART_3_LINE_3
    assert registry.get("ca/rc381_part_3_line_6") is RC381_PART_3_LINE_6
    assert registry.get("ca/rc381_part_3_line_7") is RC381_PART_3_LINE_7
    assert registry.get("ca/rc381_part_3_line_8") is RC381_PART_3_LINE_8
    assert registry.get("ca/rc381_part_3_line_9") is RC381_PART_3_LINE_9
    assert registry.get("ca/rc381_part_3_line_10") is RC381_PART_3_LINE_10
    assert registry.get("ca/rc381_part_3_line_11") is RC381_PART_3_LINE_11
    assert registry.get("ca/rc381_part_3_line_14") is RC381_PART_3_LINE_14
    # Line 15's "Enter whichever is less: amount from line 10 or line 14.", before the gate on
    # line 3 against line C that decides whether line 15 takes it.
    assert registry.get("ca/rc381_part_3_line_15_lesser") is RC381_PART_3_LINE_15_LESSER
    assert registry.get("ca/rc381_part_3_line_15") is RC381_PART_3_LINE_15
    assert registry.get("ca/rc381_part_3_line_16") is RC381_PART_3_LINE_16
    assert registry.get("ca/rc381_part_3_line_18") is RC381_PART_3_LINE_18
    assert registry.get("ca/rc381_part_3_line_20") is RC381_PART_3_LINE_20
    assert registry.get("ca/rc381_part_3_line_21") is RC381_PART_3_LINE_21
    assert registry.get("ca/rc381_part_3_line_22") is RC381_PART_3_LINE_22
    assert registry.get("ca/rc381_part_3_line_23") is RC381_PART_3_LINE_23
    assert registry.get("ca/rc381_part_3_line_24") is RC381_PART_3_LINE_24
    assert registry.get("ca/rc381_part_3_line_26") is RC381_PART_3_LINE_26
    assert registry.get("ca/rc381_part_3_line_27") is RC381_PART_3_LINE_27
    assert registry.get("ca/rc381_part_3_line_28") is RC381_PART_3_LINE_28
    assert registry.get("ca/rc381_part_3_line_29") is RC381_PART_3_LINE_29
    assert registry.get("ca/rc381_part_3_line_30") is RC381_PART_3_LINE_30
    assert registry.get("ca/rc381_part_3_line_31") is RC381_PART_3_LINE_31
    assert registry.get("ca/rc381_part_3_line_34") is RC381_PART_3_LINE_34
    # Line 35 "Enter whichever is less: amount from line 30 or line 34.", before the gate on
    # line 3 against line G that decides whether line 35 takes it.
    assert registry.get("ca/rc381_part_3_line_35_lesser") is RC381_PART_3_LINE_35_LESSER
    assert registry.get("ca/rc381_part_3_line_35") is RC381_PART_3_LINE_35
    assert registry.get("ca/rc381_part_3_line_36") is RC381_PART_3_LINE_36
    assert registry.get("ca/rc381_part_3_line_38") is RC381_PART_3_LINE_38
    assert registry.get("ca/rc381_part_3_line_40") is RC381_PART_3_LINE_40
    assert registry.get("ca/rc381_part_3_line_41") is RC381_PART_3_LINE_41
    assert registry.get("ca/rc381_part_3_line_42") is RC381_PART_3_LINE_42
    assert registry.get("ca/rc381_part_3_line_43") is RC381_PART_3_LINE_43
    assert registry.get("ca/rc381_part_3_line_44") is RC381_PART_3_LINE_44
    assert registry.get("ca/rc381_part_3_line_46") is RC381_PART_3_LINE_46
    assert registry.get("ca/rc381_part_3_line_49") is RC381_PART_3_LINE_49
    assert registry.get("ca/rc381_part_3_line_52") is RC381_PART_3_LINE_52
    assert registry.get("ca/rc381_part_3_line_53") is RC381_PART_3_LINE_53
    assert registry.get("ca/rc381_part_3_line_56") is RC381_PART_3_LINE_56
    assert registry.get("ca/rc381_part_3_line_59") is RC381_PART_3_LINE_59
    assert registry.get("ca/rc381_part_3_line_60") is RC381_PART_3_LINE_60
    assert registry.get("ca/rc381_part_3_line_61") is RC381_PART_3_LINE_61
    assert registry.get("ca/rc381_part_3_line_64") is RC381_PART_3_LINE_64
    assert registry.get("ca/rc381_part_3_line_67") is RC381_PART_3_LINE_67
    assert registry.get("ca/rc381_part_3_line_68") is RC381_PART_3_LINE_68
    assert registry.get("ca/rc381_part_3_line_69") is RC381_PART_3_LINE_69
    assert registry.get("ca/rc381_part_3_line_73") is RC381_PART_3_LINE_73
    assert registry.get("ca/rc381_part_3_line_75") is RC381_PART_3_LINE_75
    assert registry.get("ca/rc381_part_3_line_76") is RC381_PART_3_LINE_76
    assert registry.get("ca/rc381_part_3_line_77") is RC381_PART_3_LINE_77
    assert registry.get("ca/rc381_part_3_line_78") is RC381_PART_3_LINE_78
    assert registry.get("ca/rc381_part_3_line_79") is RC381_PART_3_LINE_79
    assert registry.get("ca/rc381_part_3_line_80") is RC381_PART_3_LINE_80
    assert registry.get("ca/rc381_part_3_line_81") is RC381_PART_3_LINE_81
    assert registry.get("ca/rc381_part_3_line_82") is RC381_PART_3_LINE_82
    assert registry.get("ca/rc381_part_3_line_83") is RC381_PART_3_LINE_83
    assert registry.get("ca/rc381_part_3_line_84") is RC381_PART_3_LINE_84
    assert registry.get("ca/rc381_part_3_line_85") is RC381_PART_3_LINE_85
    assert registry.get("ca/rc381_part_3_line_86") is RC381_PART_3_LINE_86
    assert registry.get("ca/rc381_part_3_line_87") is RC381_PART_3_LINE_87
    # Line 87 "the result of line 68 minus line 80", printed inside the line: a step of its own.
    assert registry.get("ca/rc381_part_3_line_87_difference") is RC381_PART_3_LINE_87_DIFFERENCE
    assert registry.get("ca/rc381_part_3_line_88") is RC381_PART_3_LINE_88
    assert registry.get("ca/rc381_part_3_line_89") is RC381_PART_3_LINE_89
    assert registry.get("ca/rc381_part_3_line_90") is RC381_PART_3_LINE_90
    assert registry.get("ca/rc381_part_3_line_91") is RC381_PART_3_LINE_91
    assert registry.get("ca/rc381_part_3_line_92") is RC381_PART_3_LINE_92
    assert registry.get("ca/rc381_part_3_line_93") is RC381_PART_3_LINE_93
    assert registry.get("ca/rc381_employment_cpp_base_contributions") is (
        RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS
    )
    assert registry.get("ca/rc381_employment_cpp_enhanced_contributions") is (
        RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS
    )
    assert registry.get("ca/rc381_cpp_overpayment") is RC381_CPP_OVERPAYMENT


def test_the_rc381_part_4_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    # Line 3 and box 50399, the one input of Part 4 lines 1 to 27 that Schedule 8 does not have.
    assert registry.get("ca/rc381_part_4_line_4") is RC381_PART_4_LINE_4
    assert registry.get("ca/rc381_part_4_line_8") is RC381_PART_4_LINE_8
    assert registry.get("ca/rc381_part_4_line_11") is RC381_PART_4_LINE_11
    assert registry.get("ca/rc381_part_4_line_12") is RC381_PART_4_LINE_12
    # Line 13 "Line 5 minus line 12", printed inside the line that enters it when line 61 of Part 3
    # is positive: a step of its own.
    assert registry.get("ca/rc381_part_4_line_13_difference") is RC381_PART_4_LINE_13_DIFFERENCE
    assert registry.get("ca/rc381_part_4_line_13") is RC381_PART_4_LINE_13
    assert registry.get("ca/rc381_part_4_line_14") is RC381_PART_4_LINE_14
    assert registry.get("ca/rc381_part_4_line_17") is RC381_PART_4_LINE_17
    assert registry.get("ca/rc381_part_4_line_17a") is RC381_PART_4_LINE_17A
    assert registry.get("ca/rc381_part_4_line_20") is RC381_PART_4_LINE_20
    # Line 21's "enter the amount from line 17 (show in brackets)" and "enter whichever is less:
    # amount from line 20 or line 17A", each printed inside the line: a step of its own.
    assert registry.get("ca/rc381_part_4_line_21_from_line_17") is (
        RC381_PART_4_LINE_21_FROM_LINE_17
    )
    assert registry.get("ca/rc381_part_4_line_21_lesser") is RC381_PART_4_LINE_21_LESSER
    assert registry.get("ca/rc381_part_4_line_21") is RC381_PART_4_LINE_21
    assert registry.get("ca/rc381_part_4_line_22") is RC381_PART_4_LINE_22
    # Line 23's "whichever is less: amount from line 68 of Part 3 or line 17A" and "line 68 of
    # Part 3 multiplied by the rate at line 22", the two ways the line is entered.
    assert registry.get("ca/rc381_part_4_line_23_lesser") is RC381_PART_4_LINE_23_LESSER
    assert registry.get("ca/rc381_part_4_line_23_multiplied") is RC381_PART_4_LINE_23_MULTIPLIED
    assert registry.get("ca/rc381_part_4_line_23") is RC381_PART_4_LINE_23
    # Line 24's "Enter whichever is less: amount from line 17A or line 23.", before the block's
    # "If line 61 of Part 3 is ... negative" decides whether line 24 takes it.
    assert registry.get("ca/rc381_part_4_line_24_lesser") is RC381_PART_4_LINE_24_LESSER
    assert registry.get("ca/rc381_part_4_line_24") is RC381_PART_4_LINE_24
    assert registry.get("ca/rc381_part_4_line_25a") is RC381_PART_4_LINE_25A
    assert registry.get("ca/rc381_part_4_line_26") is RC381_PART_4_LINE_26
    assert registry.get("ca/rc381_part_4_line_27") is RC381_PART_4_LINE_27


def test_the_rc381_part_4_lines_31_to_56_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    # Line 31 "Line 29 minus line 30" printed inside the line (entered when line 61 of Part 3 is
    # positive), then line 31 itself.
    assert registry.get("ca/rc381_part_4_line_31_difference") is RC381_PART_4_LINE_31_DIFFERENCE
    assert registry.get("ca/rc381_part_4_line_31") is RC381_PART_4_LINE_31
    assert registry.get("ca/rc381_part_4_line_32") is RC381_PART_4_LINE_32
    assert registry.get("ca/rc381_part_4_line_33") is RC381_PART_4_LINE_33
    assert registry.get("ca/rc381_part_4_line_34") is RC381_PART_4_LINE_34
    assert registry.get("ca/rc381_part_4_line_35") is RC381_PART_4_LINE_35
    # Line 35A prints two sentences: "If line 35 and line 17 are both positive, enter the amount
    # from line 17." (35aa, with the amount from line 17 as its helper) and "If line 35 is "0" and
    # line 20 is positive, enter the amount from line 20 (show in brackets)." (35ab, with the
    # amount from line 20 in brackets as its helper and the choice for line 35 at "0" before the
    # block's "negative" gate), and the line is their sum.
    assert registry.get("ca/rc381_part_4_line_35aa_from_line_17") is (
        RC381_PART_4_LINE_35AA_FROM_LINE_17
    )
    assert registry.get("ca/rc381_part_4_line_35aa") is RC381_PART_4_LINE_35AA
    assert registry.get("ca/rc381_part_4_line_35ab_from_line_20") is (
        RC381_PART_4_LINE_35AB_FROM_LINE_20
    )
    assert registry.get("ca/rc381_part_4_line_35ab_when_line_35_zero") is (
        RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO
    )
    assert registry.get("ca/rc381_part_4_line_35ab") is RC381_PART_4_LINE_35AB
    assert registry.get("ca/rc381_part_4_line_35a") is RC381_PART_4_LINE_35A
    assert registry.get("ca/rc381_part_4_line_36") is RC381_PART_4_LINE_36
    assert registry.get("ca/rc381_part_4_line_38") is RC381_PART_4_LINE_38
    assert registry.get("ca/rc381_part_4_line_39") is RC381_PART_4_LINE_39
    assert registry.get("ca/rc381_part_4_line_40") is RC381_PART_4_LINE_40
    assert registry.get("ca/rc381_part_4_line_41") is RC381_PART_4_LINE_41
    assert registry.get("ca/rc381_part_4_line_42") is RC381_PART_4_LINE_42
    # Lines 46 and 51 print "Line 44 minus line 45" and "Line 49 minus line 50", completed only
    # when line 68 of Part 3 is positive ("If not, enter "0""): the difference is a helper.
    assert registry.get("ca/rc381_part_4_line_46_difference") is RC381_PART_4_LINE_46_DIFFERENCE
    assert registry.get("ca/rc381_part_4_line_46") is RC381_PART_4_LINE_46
    assert registry.get("ca/rc381_part_4_line_47") is RC381_PART_4_LINE_47
    assert registry.get("ca/rc381_part_4_line_51_difference") is RC381_PART_4_LINE_51_DIFFERENCE
    assert registry.get("ca/rc381_part_4_line_51") is RC381_PART_4_LINE_51
    assert registry.get("ca/rc381_part_4_line_52") is RC381_PART_4_LINE_52
    assert registry.get("ca/rc381_part_4_line_53") is RC381_PART_4_LINE_53
    assert registry.get("ca/rc381_part_4_line_54") is RC381_PART_4_LINE_54
    assert registry.get("ca/rc381_part_4_line_55") is RC381_PART_4_LINE_55
    assert registry.get("ca/rc381_part_4_line_56") is RC381_PART_4_LINE_56


def test_the_rc381_part_4_lines_57_to_91_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    # Lines 59 to 70, the earnings subject to base and first additional contributions.
    assert registry.get("ca/rc381_part_4_line_59") is RC381_PART_4_LINE_59
    assert registry.get("ca/rc381_part_4_line_61") is RC381_PART_4_LINE_61
    assert registry.get("ca/rc381_part_4_line_62") is RC381_PART_4_LINE_62
    assert registry.get("ca/rc381_part_4_line_65") is RC381_PART_4_LINE_65
    assert registry.get("ca/rc381_part_4_line_68") is RC381_PART_4_LINE_68
    assert registry.get("ca/rc381_part_4_line_69") is RC381_PART_4_LINE_69
    assert registry.get("ca/rc381_part_4_line_70") is RC381_PART_4_LINE_70
    # Lines 74 to 83, the earnings subject to second additional contributions (line 83 prints
    # "Enter whichever is less: amount from line 77 or line 82." and the gate "If line 74 is
    # more than line 57", so the lesser is a helper).
    assert registry.get("ca/rc381_part_4_line_74") is RC381_PART_4_LINE_74
    assert registry.get("ca/rc381_part_4_line_76") is RC381_PART_4_LINE_76
    assert registry.get("ca/rc381_part_4_line_77") is RC381_PART_4_LINE_77
    assert registry.get("ca/rc381_part_4_line_80") is RC381_PART_4_LINE_80
    assert registry.get("ca/rc381_part_4_line_82") is RC381_PART_4_LINE_82
    assert registry.get("ca/rc381_part_4_line_83_lesser") is RC381_PART_4_LINE_83_LESSER
    assert registry.get("ca/rc381_part_4_line_83") is RC381_PART_4_LINE_83
    # Lines 84 to 88, the required contributions.
    assert registry.get("ca/rc381_part_4_line_84") is RC381_PART_4_LINE_84
    assert registry.get("ca/rc381_part_4_line_85") is RC381_PART_4_LINE_85
    assert registry.get("ca/rc381_part_4_line_86") is RC381_PART_4_LINE_86
    assert registry.get("ca/rc381_part_4_line_87") is RC381_PART_4_LINE_87
    assert registry.get("ca/rc381_part_4_line_88") is RC381_PART_4_LINE_88
    # Line 89 prints "Amount from line 69 of Part 3 (if positive) × 2": the amount is a helper.
    # Line 90's positive amount goes on line 42100 of the return.
    assert registry.get("ca/rc381_part_4_line_89_from_line_69") is RC381_PART_4_LINE_89_FROM_LINE_69
    assert registry.get("ca/rc381_part_4_line_89") is RC381_PART_4_LINE_89
    assert registry.get("ca/rc381_part_4_line_90") is RC381_PART_4_LINE_90
    assert registry.get("ca/rc381_self_employment_cpp_contributions") is (
        RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS
    )
    # Line 91 prints "amount from line 90 entered as a positive amount × 50%": the amount is a
    # helper.
    assert registry.get("ca/rc381_part_4_line_91_from_line_90") is RC381_PART_4_LINE_91_FROM_LINE_90
    assert registry.get("ca/rc381_part_4_line_91") is RC381_PART_4_LINE_91


def test_the_rc381_part_4_lines_92_to_110_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    # Lines 92 to 98, the base contributions through employment income (the amount for line
    # 30800 of the return is line 98).
    assert registry.get("ca/rc381_part_4_line_92") is RC381_PART_4_LINE_92
    assert registry.get("ca/rc381_part_4_line_93") is RC381_PART_4_LINE_93
    assert registry.get("ca/rc381_part_4_line_94") is RC381_PART_4_LINE_94
    assert registry.get("ca/rc381_part_4_line_95") is RC381_PART_4_LINE_95
    assert registry.get("ca/rc381_part_4_line_96") is RC381_PART_4_LINE_96
    assert registry.get("ca/rc381_part_4_line_97") is RC381_PART_4_LINE_97
    assert registry.get("ca/rc381_part_4_line_98") is RC381_PART_4_LINE_98
    # Lines 99 to 110, the deduction for the enhanced contributions on employment income (the
    # amount for line 22215 of the return is line 110). Line 104 prints "the result of line 68
    # of Part 3 minus line 97": the difference is a helper.
    assert registry.get("ca/rc381_part_4_line_99") is RC381_PART_4_LINE_99
    assert registry.get("ca/rc381_part_4_line_100") is RC381_PART_4_LINE_100
    assert registry.get("ca/rc381_part_4_line_101") is RC381_PART_4_LINE_101
    assert registry.get("ca/rc381_part_4_line_102") is RC381_PART_4_LINE_102
    assert registry.get("ca/rc381_part_4_line_103") is RC381_PART_4_LINE_103
    assert registry.get("ca/rc381_part_4_line_104_difference") is RC381_PART_4_LINE_104_DIFFERENCE
    assert registry.get("ca/rc381_part_4_line_104") is RC381_PART_4_LINE_104
    assert registry.get("ca/rc381_part_4_line_105") is RC381_PART_4_LINE_105
    assert registry.get("ca/rc381_part_4_line_106") is RC381_PART_4_LINE_106
    assert registry.get("ca/rc381_part_4_line_107") is RC381_PART_4_LINE_107
    assert registry.get("ca/rc381_part_4_line_108") is RC381_PART_4_LINE_108
    assert registry.get("ca/rc381_part_4_line_109") is RC381_PART_4_LINE_109
    assert registry.get("ca/rc381_part_4_line_110") is RC381_PART_4_LINE_110


def test_the_rc381_part_4_lines_111_to_129_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    # Lines 111 to 115, the base contributions through self-employment income and other earnings
    # (the amount for line 31000 of the return is line 111).
    assert registry.get("ca/rc381_part_4_line_111") is RC381_PART_4_LINE_111
    assert registry.get("ca/rc381_part_4_line_112") is RC381_PART_4_LINE_112
    assert registry.get("ca/rc381_part_4_line_113") is RC381_PART_4_LINE_113
    assert registry.get("ca/rc381_part_4_line_114") is RC381_PART_4_LINE_114
    assert registry.get("ca/rc381_part_4_line_115") is RC381_PART_4_LINE_115
    # The amount lettered A, "Enter whichever is less: amount from line 113 or line 114.", is
    # printed in line 116's row, so it is a helper of line 116.
    assert registry.get("ca/rc381_part_4_line_116_lesser") is RC381_PART_4_LINE_116_LESSER
    assert registry.get("ca/rc381_part_4_line_116") is RC381_PART_4_LINE_116
    assert registry.get("ca/rc381_part_4_line_118") is RC381_PART_4_LINE_118
    assert registry.get("ca/rc381_part_4_line_121") is RC381_PART_4_LINE_121
    assert registry.get("ca/rc381_part_4_line_124") is RC381_PART_4_LINE_124
    # Lines 125 to 129, the deduction for the enhanced contributions on self-employment income and
    # other earnings (the amount for line 22200 of the return is line 129).
    assert registry.get("ca/rc381_part_4_line_125") is RC381_PART_4_LINE_125
    assert registry.get("ca/rc381_part_4_line_127") is RC381_PART_4_LINE_127
    assert registry.get("ca/rc381_part_4_line_128") is RC381_PART_4_LINE_128
    assert registry.get("ca/rc381_part_4_line_129") is RC381_PART_4_LINE_129


def test_the_rc381_final_selection_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    # "self-employment income and other earnings subject to contributions (lines 70 and 83 of Part
    # 4 ...)" and the six results for lines 30800, 22215, 44800, 42100, 31000 and 22200.
    assert registry.get("ca/rc381_part_4_earnings_subject_to_contributions") is (
        RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS
    )
    assert registry.get("ca/rc381_cpp_base_contributions_on_return") is (
        RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN
    )
    assert registry.get("ca/rc381_cpp_enhanced_contributions_on_return") is (
        RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN
    )
    assert registry.get("ca/rc381_cpp_overpayment_on_return") is RC381_CPP_OVERPAYMENT_ON_RETURN
    assert registry.get("ca/rc381_cpp_payable_on_self_employment") is (
        RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT
    )
    assert registry.get(
        "ca/rc381_cpp_base_contributions_on_self_employment_and_other_earnings"
    ) is (RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS)
    assert registry.get("ca/rc381_cpp_deduction_on_self_employment_and_other_earnings") is (
        RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS
    )


def test_the_rc381_amounts_are_money() -> None:
    for kind in (
        *INPUT_AMOUNTS,
        *PART_2_AMOUNTS,
        *PART_3_AMOUNTS,
        *PART_4_AMOUNTS,
        *RESULT_AMOUNTS,
        *SIGNED_AMOUNTS,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_line_6_is_a_rate_kind() -> None:
    # Line 6 "Line 4 divided by line 5 (calculated to the fifth decimal place without rounding)" is
    # "the rate at line 6" that lines 7 to 10 multiply by: a `Rate` (0 to 1), not money.
    assert RC381_PART_3_LINE_6.value_type is Rate


def test_part_4_line_22_is_a_rate_kind() -> None:
    # Part 4 line 22 "If line 17A is more than line 14, enter "1". If not, enter the result of line
    # 17A divided by line 14 (calculated to the fifth decimal place without rounding)." is "the
    # rate at line 22" that line 23 multiplies line 68 by: a `Rate` (0 to 1), not money.
    assert RC381_PART_4_LINE_22.value_type is Rate


def test_the_rc381_months_are_counts() -> None:
    # Line B is a count of months the filer enters, and the line B the table is read with is the
    # same count after the check that line A "cannot be more than the number you enter on line B".
    assert QPP_MONTHS.value_type is int
    assert RC381_PART_2_LINE_B.value_type is int


def test_every_rc381_kind_is_non_negative() -> None:
    kinds: tuple[ArtifactKind[Any], ...] = (
        QPP_MONTHS,
        RC381_PART_2_LINE_B,
        *INPUT_AMOUNTS,
        *PART_2_AMOUNTS,
        *PART_3_AMOUNTS,
        *PART_4_AMOUNTS,
        *RESULT_AMOUNTS,
    )
    for kind in kinds:
        assert kind.non_negative is True, kind.identifier
    # A rate kind is bounded by `Rate` itself (0 to 1), as the Ontario CARE credit rate is.


def test_the_rc381_lines_that_may_be_negative_are_signed() -> None:
    # Line 53 "Line 49 minus line 52 (if negative, show in brackets)", line 60 "Line 56 minus line
    # 59 (if negative, show in brackets)", line 61 "Line 53 plus line 60 (if negative, show in
    # brackets)", line 68 "Line 64 minus line 67 (if negative, show in brackets)" and line 69
    # "Line 61 plus line 68 (if negative, show in brackets)": the actual contributions can be less
    # than the required ones, so these are not non-negative.
    # Line 87 helper "the result of line 68 minus line 80": line 68 may be negative while line
    # 80 is "0", so the difference can be below zero.
    # Part 4 line 4 "Add lines 1 to 3." (line 1 prints no floor, as Schedule 8 Part 4 line 1 does
    # not), lines 8, 11, 12, 17 and 20 "(if negative, show in brackets)", line 21 "(show in
    # brackets)", lines 23 and 24 (line 68 of Part 3 may be negative, and "whichever is less" has
    # no floor), line 25A (line 21), line 26 "Add lines 24 to 25A." and line 27 (line 26 times
    # 16.80672).
    # Part 4 line 31 (and its helper) "Line 29 minus line 30 (if negative, show in brackets)", line
    # 32 "Line 28 minus line 31" (line 31 may be negative), line 35A's second sentence "(show in
    # brackets)", lines 38 and 39 (no floor is printed; line 38 is not below zero in fact, which
    # the kind does not rely on), line 40 "Add lines 32, 35A, and 39.", line 41 (line 40 times
    # 15.625), line 42, lines 46, 47, 51 and 52 "(if negative, show in brackets)" (and the
    # helpers printed inside lines 46 and 51), line 53 and line 56.
    # Part 4 line 62 (line 4 is not floored), line 70 "Line 62 minus line 69" (no floor is
    # printed), line 74 (line 4), line 76 (line 56 ÷ 4%), lines 80 and 82 ("Line 78 minus line 79"
    # and "Line 80 minus line 81", no floor), line 83 and the lesser printed inside it (lines 77
    # and 82) and line 90 "(if negative, show in brackets)".
    # Part 4 line 104's helper "the result of line 68 of Part 3 minus line 97": line 68 may be
    # negative while line 97 is "0", so the difference can be below zero.
    # Part 4 line 115 "Line 113 minus line 114 (if negative, show in brackets)", lines 121 and 124
    # ("Line 119 minus line 120" and "Line 122 minus line 123", no floor: each can be a cent below
    # zero when line 116 rounds up) and the earnings subject to contributions (line 70 is signed).
    for kind in SIGNED_AMOUNTS:
        assert kind.non_negative is False, kind.identifier


# The words of the form each result's docstring quotes.
RESULT_QUOTES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "rc381_employment_cpp_base_contributions",
        (
            "Enter this amount (in dollars and cents) on line 30800 of your return.",
            "Part 3a",
            "Part 3b",
            "line 69",
        ),
    ),
    (
        "rc381_employment_cpp_enhanced_contributions",
        (
            "Enter this amount (in dollars and cents) on line 22215 of your return.",
            "Part 3a",
            "Part 3b",
            "line 69",
        ),
    ),
    (
        "rc381_cpp_overpayment",
        (
            "Enter this amount (in dollars and cents) on line 44800 of your return.",
            "Part 3a",
            "line 69",
        ),
    ),
    (
        "rc381_self_employment_cpp_contributions",
        (
            "Line 88 minus 89. If positive, enter the amount (in dollars and cents) on line 42100 "
            "of your return",
            "Part 4",
            "line 90",
        ),
    ),
    (
        "rc381_part_4_line_91",
        (
            "Enter the result of the following calculation (in dollars and cents) on line 44800 of "
            "your return: amount from line 90 entered as a positive amount",
            "50%",
            "Part 4",
        ),
    ),
    (
        "rc381_part_4_line_98",
        (
            "Enter this amount (in dollars and cents) on line 30800 of your return.",
            "Line 96 plus line 97",
            "Part 4",
        ),
    ),
    (
        "rc381_part_4_line_110",
        (
            "Enter this amount (in dollars and cents) on line 22215 of your return.",
            "Line 105 plus line 109",
            "Part 4",
        ),
    ),
    (
        "rc381_part_4_line_111",
        (
            "Enter the result of the following calculation (in dollars and cents) on line 31000 of "
            "your return: amount from line 84 × 50% =",
            "Part 4",
        ),
    ),
    (
        "rc381_part_4_line_129",
        (
            "Add lines 121, 122, 124, 125, and 128. Enter this amount (in dollar and cents) on "
            "line 22200 of your return.",
            "Part 4",
        ),
    ),
    (
        "rc381_part_4_earnings_subject_to_contributions",
        (
            "self-employment income and other earnings subject to contributions (lines 70 and 83 "
            "of Part 4 or lines 68 and 81 of Part 5)",
            'are "0," follow the instructions below.',
        ),
    ),
    (
        "rc381_cpp_base_contributions_on_return",
        (
            "Enter this amount (in dollars and cents) on line 30800 of your return.",
            "Part 4 line 98",
            "Part 3a line 70 or Part 3b line 81",
        ),
    ),
    (
        "rc381_cpp_enhanced_contributions_on_return",
        (
            "Enter this amount (in dollars and cents) on line 22215 of your return.",
            "Part 4 line 110",
            "Part 3a line 73 or Part 3b line 93",
        ),
    ),
    (
        "rc381_cpp_overpayment_on_return",
        (
            "Enter this amount (in dollars and cents) on line 44800 of your return.",
            "Part 4 line 91",
            "Part 3a line 74",
        ),
    ),
    (
        "rc381_cpp_payable_on_self_employment",
        (
            "If positive, enter the amount (in dollars and cents) on line 42100 of your return",
            "Part 4 line 90",
        ),
    ),
    (
        "rc381_cpp_base_contributions_on_self_employment_and_other_earnings",
        (
            "Enter the result of the following calculation (in dollars and cents) on line 31000 of "
            "your return",
            "Part 4 line 111",
        ),
    ),
    (
        "rc381_cpp_deduction_on_self_employment_and_other_earnings",
        (
            "Enter this amount (in dollar and cents) on line 22200 of your return.",
            "Part 4 line 129",
        ),
    ),
)

# The words of the form each input's docstring quotes (`docs/cra-forms-2025/rc381-25e.pdf`), and
# the box number of the line, which the form prints beside it.
INPUT_QUOTES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("qpp_months", ("Enter the number of months that QPP applied in 2025.", "Part 2")),
    (
        "t4_cpp_pensionable_earnings_outside_quebec",
        (
            "Total CPP pensionable earnings from box 26 of all of your T4 slips where the "
            "province of employment is not Quebec",
            "50339",
            "Part 3",
        ),
    ),
    (
        "t4_qpp_pensionable_earnings_in_quebec",
        (
            "Total QPP pensionable earnings from box 26 of all of your T4 slips where the "
            "province of employment is Quebec",
            "50329",
            "Part 3",
        ),
    ),
    (
        "t4_cpp_second_additional_box_16a",
        (
            "Total actual second additional contributions on CPP pensionable earnings from box "
            "16A of all of your T4 slips",
            "50341",
            "Part 3",
        ),
    ),
    (
        "t4_qpp_contributions_box_17",
        (
            "Total actual base and first additional contributions on QPP pensionable earnings "
            "from box 17 of all of your T4 slips",
            "50330",
            "Part 3",
        ),
    ),
    (
        "t4_qpp_second_additional_box_17a",
        (
            "Total actual second additional contributions on QPP pensionable earnings from box "
            "17A of all of your T4 slips",
            "50331",
            "Part 3",
        ),
    ),
)


def squashed(text: str) -> str:
    """`text` with every run of white space made one blank."""
    return re.sub(r"\s+", " ", text).strip()


def docstring_of(name: str) -> str:
    """The string right after `NAME = CATALOG.declare("<name>", ...)` in a catalog module."""
    folder = Path(tax_engine.jurisdictions.ca.catalog.__file__).parent
    for path in sorted(folder.glob("*.py")):
        body = ast.parse(path.read_text()).body
        for statement, following in zip(body, body[1:], strict=False):
            if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
                continue
            arguments = statement.value.args
            if not (
                arguments
                and isinstance(arguments[0], ast.Constant)
                and arguments[0].value == name
                and isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
            ):
                continue
            return str(following.value.value)
    raise AssertionError(f"no declaration of {name!r} followed by a docstring")


@pytest.mark.parametrize(("name", "quotes"), INPUT_QUOTES, ids=[n for n, _ in INPUT_QUOTES])
def test_each_rc381_input_docstring_quotes_the_form(name: str, quotes: tuple[str, ...]) -> None:
    docstring = squashed(docstring_of(name))

    assert "RC381" in docstring
    for quote in quotes:
        assert squashed(quote) in docstring, quote


@pytest.mark.parametrize(("name", "quotes"), RESULT_QUOTES, ids=[n for n, _ in RESULT_QUOTES])
def test_each_rc381_result_docstring_quotes_the_form(name: str, quotes: tuple[str, ...]) -> None:
    docstring = squashed(docstring_of(name))

    assert "RC381" in docstring
    for quote in quotes:
        assert squashed(quote) in docstring, quote


def test_the_t4_slip_counts_are_registered_whole_numbers_of_0_or_more(
    registry: ArtifactRegistry,
) -> None:
    # The number of T4 slips with CPP and with QPP pensionable earnings (Umar, 2026-10-26, Q6).
    for identifier, kind in (
        ("ca/t4_cpp_slip_count", T4_CPP_SLIP_COUNT),
        ("ca/t4_qpp_slip_count", T4_QPP_SLIP_COUNT),
    ):
        assert registry.get(identifier) is kind
        assert kind.value_type is int
        assert kind.non_negative is True
