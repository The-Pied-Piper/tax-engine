"""The federal catalog: Form RC381 Part 2, Part 3 lines 1 to 93 and Part 4 lines 1 to 129.

Form RC381 (2025), "Inter-Provincial Calculation for CPP and QPP Contributions and Overpayments":
Part 2 (the months and the monthly proration table, lines G to J being the QPP side) and the CPP
side of Part 3 on employment income (lines 1 to 26), then its QPP side and the totals (lines 27
to 69), then Part 3a and Part 3b (lines 70 to 93) with their three results, then Part 4 (for
residents of a province or territory other than Quebec) through line 129: the CPP side (lines 1 to
27), the QPP side with the second additional contributions and the totals (lines 28 to 56), the
earnings subject to contributions, the self-employed contributions and the overpayment (lines 57
to 91), the base and enhanced contributions through employment income (lines 92 to 110), and the
base and enhanced contributions through self-employment income and other earnings (lines 111 to
129), with the results for the return after Part 3 and Part 4: lines 30800, 22215, 44800, 42100,
31000 and 22200.
Lines C to F of Part 2 are Schedule 8 Part 2's lines B to E, the existing artifacts read with the
same months.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

QPP_MONTHS = CATALOG.declare("qpp_months", int, non_negative=True)
"""Months that QPP applied, Form RC381 Part 2 line B "Enter the number of months that QPP applied
in 2025.": a count the filer enters, as the months of line A are. "The number you enter on line A
cannot be more than the number you enter on line B.", which `RC381_PART_2_LINE_B` checks."""

RC381_PART_2_LINE_B = CATALOG.declare("rc381_part_2_line_b", int, non_negative=True)
"""QPP months, Form RC381 Part 2 line B "Enter the number of months that QPP applied in 2025.",
after the check that "The number you enter on line A cannot be more than the number you enter on
line B.": the key of the monthly proration table for lines G to J."""

T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC = CATALOG.declare(
    "t4_cpp_pensionable_earnings_outside_quebec", Decimal, non_negative=True
)
"""CPP pensionable earnings outside Quebec, Schedule 8 Part 3 line 1 and Form RC381 Part 3 line 1,
both line 50339 "Total CPP pensionable earnings from box 26 of all of your T4 slips where the
province of employment is not Quebec": the amount the filer enters, a starting amount, and the one
figure both forms take (Schedule 8 and Form RC381 are an exclusive group, so one input serves
both). The form's "(if box 26 is blank, enter the amount from box 14)" and "(maximum $81,200 per
slip)" are the filer's to apply to each slip: a slip whose box 26 is blank is entered here as its
box 14, since the check of the box 26 total (`ca/t4_cpp_pensionable_earnings_slip_checked`)
reads this amount."""

T4_CPP_SLIP_COUNT = CATALOG.declare("t4_cpp_slip_count", int, non_negative=True)
"""Number of T4 slips with CPP pensionable earnings, Schedule 8 Part 3 line 1 and Form RC381 Part 3
line 1 "(maximum $81,200 per slip)": a count the filer enters, whole and 0 or more. The forms take
one total over all the slips but print the box 26 maximum for one slip, so the count validates it
(Umar, 2026-10-26, Q6): box 26 is refused above the count times the printed maximum, and with a
count of 0 any box 26 above 0 is refused. A slip is CPP or QPP by its province of employment, so
it is counted in only one of this count and `ca/t4_qpp_slip_count`."""

T4_QPP_SLIP_COUNT = CATALOG.declare("t4_qpp_slip_count", int, non_negative=True)
"""Number of T4 slips with QPP pensionable earnings, Form RC381 Part 3 line 2 "(maximum $81,200 per
slip)": a count the filer enters, whole and 0 or more, that validates the box 26 total as
`ca/t4_cpp_slip_count` does the CPP side. A slip is counted in this count when its province of
employment is Quebec."""

T4_QPP_PENSIONABLE_EARNINGS_IN_QUEBEC = CATALOG.declare(
    "t4_qpp_pensionable_earnings_in_quebec", Decimal, non_negative=True
)
"""QPP pensionable earnings in Quebec, Form RC381 Part 3 line 2 and line 50329 "Total QPP
pensionable earnings from box 26 of all of your T4 slips where the province of employment is
Quebec": the amount the filer enters, a starting amount. The form's "(if box 26 is blank, enter the
amount from box 14)" and "(maximum $81,200 per slip)" are the filer's to apply to each slip: a slip
whose box 26 is blank is entered here as its box 14, since the check of the box 26 total
(`ca/t4_qpp_pensionable_earnings_slip_checked`) reads this amount."""

T4_CPP_SECOND_ADDITIONAL_BOX_16A = CATALOG.declare(
    "t4_cpp_second_additional_box_16a", Decimal, non_negative=True
)
"""CPP second additional contributions on T4 slips, Form RC381 Part 3 line 25 and line 50341 "Total
actual second additional contributions on CPP pensionable earnings from box 16A of all of your T4
slips": the total the filer enters, a starting amount."""

T4_QPP_CONTRIBUTIONS_BOX_17 = CATALOG.declare(
    "t4_qpp_contributions_box_17", Decimal, non_negative=True
)
"""QPP contributions on T4 slips, Form RC381 Part 3 line 39 and line 50330 "Total actual base and
first additional contributions on QPP pensionable earnings from box 17 of all of your T4 slips":
the total the filer enters, a starting amount."""

T4_QPP_SECOND_ADDITIONAL_BOX_17A = CATALOG.declare(
    "t4_qpp_second_additional_box_17a", Decimal, non_negative=True
)
"""QPP second additional contributions on T4 slips, Form RC381 Part 3 line 45 and line 50331 "Total
actual second additional contributions on QPP pensionable earnings from box 17A of all of your T4
slips": the total the filer enters, a starting amount."""

RC381_PART_2_LINE_G = CATALOG.declare("rc381_part_2_line_g", Decimal, non_negative=True)
"""QPP maximum pensionable earnings, Form RC381 Part 2 line G "Your maximum pensionable earnings
for 2025 (maximum $71,300)": the "Maximum pensionable earnings" column of the monthly proration
table, in the row for line B's months."""

RC381_PART_2_LINE_H = CATALOG.declare("rc381_part_2_line_h", Decimal, non_negative=True)
"""QPP maximum amount subject to second additional contributions, Form RC381 Part 2 line H "Your
maximum amount subject to second additional contributions for 2025 (maximum $9,900)": that column
of the monthly proration table, in the row for line B's months."""

RC381_PART_2_LINE_I = CATALOG.declare("rc381_part_2_line_i", Decimal, non_negative=True)
"""QPP additional maximum pensionable earnings, Form RC381 Part 2 line I "Your additional maximum
pensionable earnings for 2025 (maximum $81,200)": that column of the monthly proration table, in
the row for line B's months."""

RC381_PART_2_LINE_J = CATALOG.declare("rc381_part_2_line_j", Decimal, non_negative=True)
"""QPP maximum basic exemption, Form RC381 Part 2 line J "Your maximum basic exemption for 2025
(maximum $3,500)": that column of the monthly proration table, in the row for line B's months."""

RC381_PART_3_LINE_3 = CATALOG.declare("rc381_part_3_line_3", Decimal, non_negative=True)
"""Total pensionable earnings, Form RC381 Part 3 line 3 "Line 1 plus line 2"."""

RC381_PART_3_LINE_6 = CATALOG.declare("rc381_part_3_line_6", Rate)
"""Share of pensionable earnings outside Quebec, Form RC381 Part 3 line 6 "Line 4 divided by line 5
(calculated to the fifth decimal place without rounding)": a rate (0 to 1), not money, truncated
to five decimal places."""

RC381_PART_3_LINE_7 = CATALOG.declare("rc381_part_3_line_7", Decimal, non_negative=True)
"""CPP additional maximum pensionable earnings share, Form RC381 Part 3 line 7 "Amount from line E
of Part 2 multiplied by the rate at line 6"."""

RC381_PART_3_LINE_8 = CATALOG.declare("rc381_part_3_line_8", Decimal, non_negative=True)
"""CPP maximum pensionable earnings share, Form RC381 Part 3 line 8 "Amount from line C of Part 2
multiplied by the rate at line 6"."""

RC381_PART_3_LINE_9 = CATALOG.declare("rc381_part_3_line_9", Decimal, non_negative=True)
"""CPP basic exemption share, Form RC381 Part 3 line 9 "Amount from line F of Part 2 multiplied by
the rate at line 6"."""

RC381_PART_3_LINE_10 = CATALOG.declare("rc381_part_3_line_10", Decimal, non_negative=True)
"""CPP second additional maximum share, Form RC381 Part 3 line 10 "Amount from line D of Part 2
multiplied by the rate at line 6"."""

RC381_PART_3_LINE_11 = CATALOG.declare("rc381_part_3_line_11", Decimal, non_negative=True)
"""Earnings subject to CPP contributions, Form RC381 Part 3 line 11 "Enter whichever is less:
amount from line 1 or line 7."."""

RC381_PART_3_LINE_14 = CATALOG.declare("rc381_part_3_line_14", Decimal, non_negative=True)
"""Form RC381 Part 3 line 14 "Line 12 minus line 13 (if negative, enter "0")", line 12 being the
amount from line 11 and line 13 the amount from line 8."""

RC381_PART_3_LINE_15_LESSER = CATALOG.declare(
    "rc381_part_3_line_15_lesser", Decimal, non_negative=True
)
"""Form RC381 Part 3 line 15 "Enter whichever is less: amount from line 10 or line 14.", before the
gate "If the amount from line 3 is more than the amount from line C of Part 2, complete lines 12 to
15." decides whether line 15 takes it."""

RC381_PART_3_LINE_15 = CATALOG.declare("rc381_part_3_line_15", Decimal, non_negative=True)
"""Earnings subject to second additional CPP contributions, Form RC381 Part 3 line 15 "Enter
whichever is less: amount from line 10 or line 14.", when the amount from line 3 is more than the
amount from line C of Part 2, else 0."""

RC381_PART_3_LINE_16 = CATALOG.declare("rc381_part_3_line_16", Decimal, non_negative=True)
"""Form RC381 Part 3 line 16 "Line 11 minus line 15"."""

RC381_PART_3_LINE_18 = CATALOG.declare("rc381_part_3_line_18", Decimal, non_negative=True)
"""Earnings subject to base and first additional CPP contributions, Form RC381 Part 3 line 18
"Line 16 minus line 17 (if negative, enter "0")", line 17 being the amount from line 9."""

RC381_PART_3_LINE_20 = CATALOG.declare("rc381_part_3_line_20", Decimal, non_negative=True)
"""Actual base contributions on CPP pensionable earnings, Form RC381 Part 3 line 20 "amount from
line 19 x 83.1933%"."""

RC381_PART_3_LINE_21 = CATALOG.declare("rc381_part_3_line_21", Decimal, non_negative=True)
"""Actual first additional contributions on CPP pensionable earnings, Form RC381 Part 3 line 21
"Line 19 minus line 20"."""

RC381_PART_3_LINE_22 = CATALOG.declare("rc381_part_3_line_22", Decimal, non_negative=True)
"""Required base contributions on CPP pensionable earnings, Form RC381 Part 3 line 22 "amount from
line 18 x 4.95% = (maximum $3,356.10)"."""

RC381_PART_3_LINE_23 = CATALOG.declare("rc381_part_3_line_23", Decimal, non_negative=True)
"""Required first additional contributions on CPP pensionable earnings, Form RC381 Part 3 line 23
"amount from line 18 x 1% = (maximum $678.00)"."""

RC381_PART_3_LINE_24 = CATALOG.declare("rc381_part_3_line_24", Decimal, non_negative=True)
"""Required base and first additional contributions on CPP pensionable earnings, Form RC381 Part 3
line 24 "Line 22 plus line 23"."""

RC381_PART_3_LINE_26 = CATALOG.declare("rc381_part_3_line_26", Decimal, non_negative=True)
"""Required second additional contributions on CPP pensionable earnings, Form RC381 Part 3 line 26
"amount from line 15 x 4% = (maximum $396.00)"."""

RC381_PART_3_LINE_27 = CATALOG.declare("rc381_part_3_line_27", Decimal, non_negative=True)
"""QPP additional maximum pensionable earnings left, Form RC381 Part 3 line 27 "Amount from line I
of Part 2 minus the amount from line 7"."""

RC381_PART_3_LINE_28 = CATALOG.declare("rc381_part_3_line_28", Decimal, non_negative=True)
"""QPP maximum pensionable earnings left, Form RC381 Part 3 line 28 "Amount from line G of Part 2
minus the amount from line 8"."""

RC381_PART_3_LINE_29 = CATALOG.declare("rc381_part_3_line_29", Decimal, non_negative=True)
"""QPP basic exemption left, Form RC381 Part 3 line 29 "Amount from line J of Part 2 minus the
amount from line 9"."""

RC381_PART_3_LINE_30 = CATALOG.declare("rc381_part_3_line_30", Decimal, non_negative=True)
"""QPP second additional maximum left, Form RC381 Part 3 line 30 "Amount from line H of Part 2
minus the amount from line 10"."""

RC381_PART_3_LINE_31 = CATALOG.declare("rc381_part_3_line_31", Decimal, non_negative=True)
"""Earnings subject to QPP contributions, Form RC381 Part 3 line 31 "Enter whichever is less:
amount from line 2 or line 27."."""

RC381_PART_3_LINE_34 = CATALOG.declare("rc381_part_3_line_34", Decimal, non_negative=True)
"""Form RC381 Part 3 line 34 "Line 32 minus line 33 (if negative, enter "0")", line 32 being the
amount from line 31 and line 33 the amount from line 28."""

RC381_PART_3_LINE_35_LESSER = CATALOG.declare(
    "rc381_part_3_line_35_lesser", Decimal, non_negative=True
)
"""Form RC381 Part 3 line 35 "Enter whichever is less: amount from line 30 or line 34.", before the
gate "If the amount from line 3 is more than the amount from line G of Part 2, complete lines 32 to
35." decides whether line 35 takes it."""

RC381_PART_3_LINE_35 = CATALOG.declare("rc381_part_3_line_35", Decimal, non_negative=True)
"""Earnings subject to second additional QPP contributions, Form RC381 Part 3 line 35 "Enter
whichever is less: amount from line 30 or line 34.", when the amount from line 3 is more than the
amount from line G of Part 2, else 0."""

RC381_PART_3_LINE_36 = CATALOG.declare("rc381_part_3_line_36", Decimal, non_negative=True)
"""Form RC381 Part 3 line 36 "Line 31 minus line 35"."""

RC381_PART_3_LINE_38 = CATALOG.declare("rc381_part_3_line_38", Decimal, non_negative=True)
"""Earnings subject to base and first additional QPP contributions, Form RC381 Part 3 line 38
"Line 36 minus line 37 (if negative, enter "0")", line 37 being the amount from line 29."""

RC381_PART_3_LINE_40 = CATALOG.declare("rc381_part_3_line_40", Decimal, non_negative=True)
"""Actual base contributions on QPP pensionable earnings, Form RC381 Part 3 line 40 "amount from
line 39 x 84.375%"."""

RC381_PART_3_LINE_41 = CATALOG.declare("rc381_part_3_line_41", Decimal, non_negative=True)
"""Actual first additional contributions on QPP pensionable earnings, Form RC381 Part 3 line 41
"Line 39 minus line 40"."""

RC381_PART_3_LINE_42 = CATALOG.declare("rc381_part_3_line_42", Decimal, non_negative=True)
"""Required base contributions on QPP pensionable earnings, Form RC381 Part 3 line 42 "amount from
line 38 x 5.4% = (maximum $3,661.20)"."""

RC381_PART_3_LINE_43 = CATALOG.declare("rc381_part_3_line_43", Decimal, non_negative=True)
"""Required first additional contributions on QPP pensionable earnings, Form RC381 Part 3 line 43
"amount from line 38 x 1% = (maximum $678.00)"."""

RC381_PART_3_LINE_44 = CATALOG.declare("rc381_part_3_line_44", Decimal, non_negative=True)
"""Required base and first additional contributions on QPP pensionable earnings, Form RC381 Part 3
line 44 "Line 42 plus line 43"."""

RC381_PART_3_LINE_46 = CATALOG.declare("rc381_part_3_line_46", Decimal, non_negative=True)
"""Required second additional contributions on QPP pensionable earnings, Form RC381 Part 3 line 46
"amount from line 35 x 4% = (maximum $396.00)"."""

RC381_PART_3_LINE_49 = CATALOG.declare("rc381_part_3_line_49", Decimal, non_negative=True)
"""Total actual base contributions, Form RC381 Part 3 line 49 "Total actual base contributions: line
47 plus line 48", line 47 being the amount from line 20 and line 48 the amount from line 40."""

RC381_PART_3_LINE_52 = CATALOG.declare("rc381_part_3_line_52", Decimal, non_negative=True)
"""Total required base contributions, Form RC381 Part 3 line 52 "Total required base contributions:
line 50 plus line 51", line 50 being the amount from line 22 and line 51 the amount from line 42."""

RC381_PART_3_LINE_53 = CATALOG.declare("rc381_part_3_line_53", Decimal)
"""Form RC381 Part 3 line 53 "Line 49 minus line 52 (if negative, show in brackets)": signed, the
actual base contributions can be less than the required ones."""

RC381_PART_3_LINE_56 = CATALOG.declare("rc381_part_3_line_56", Decimal, non_negative=True)
"""Total actual first additional contributions, Form RC381 Part 3 line 56 "Line 54 plus line 55",
line 54 being the amount from line 21 and line 55 the amount from line 41."""

RC381_PART_3_LINE_59 = CATALOG.declare("rc381_part_3_line_59", Decimal, non_negative=True)
"""Total required first additional contributions, Form RC381 Part 3 line 59 "Line 57 plus line 58",
line 57 being the amount from line 23 and line 58 the amount from line 43."""

RC381_PART_3_LINE_60 = CATALOG.declare("rc381_part_3_line_60", Decimal)
"""Form RC381 Part 3 line 60 "Line 56 minus line 59 (if negative, show in brackets)": signed, the
actual first additional contributions can be less than the required ones."""

RC381_PART_3_LINE_61 = CATALOG.declare("rc381_part_3_line_61", Decimal)
"""Form RC381 Part 3 line 61 "Line 53 plus line 60 (if negative, show in brackets)": signed."""

RC381_PART_3_LINE_64 = CATALOG.declare("rc381_part_3_line_64", Decimal, non_negative=True)
"""Total actual second additional contributions, Form RC381 Part 3 line 64 "Line 62 plus line 63",
line 62 being the amount from line 25 and line 63 the amount from line 45."""

RC381_PART_3_LINE_67 = CATALOG.declare("rc381_part_3_line_67", Decimal, non_negative=True)
"""Total required second additional contributions, Form RC381 Part 3 line 67 "Line 65 plus line
66", line 65 being the amount from line 26 and line 66 the amount from line 46."""

RC381_PART_3_LINE_68 = CATALOG.declare("rc381_part_3_line_68", Decimal)
"""Form RC381 Part 3 line 68 "Line 64 minus line 67 (if negative, show in brackets)": signed, the
actual second additional contributions can be less than the required ones."""

RC381_PART_3_LINE_69 = CATALOG.declare("rc381_part_3_line_69", Decimal)
"""Form RC381 Part 3 line 69 "Line 61 plus line 68 (if negative, show in brackets)": signed, the
total of the contributions over or under the required ones."""

RC381_PART_3_LINE_73 = CATALOG.declare("rc381_part_3_line_73", Decimal, non_negative=True)
"""Deduction for enhanced contributions on employment income, Form RC381 Part 3a line 73 "Line 71
plus line 72", line 71 being the amount from line 59 and line 72 the amount from line 67 (if
any)."""

RC381_PART_3_LINE_75 = CATALOG.declare("rc381_part_3_line_75", Decimal, non_negative=True)
"""Form RC381 Part 3b line 75 "If line 53 is positive or "0", enter the amount from line 52 at line
75 and line 81, and continue at line 82. If not, enter the amount from line 49 and continue at line
76." A non-negative amount."""

RC381_PART_3_LINE_76 = CATALOG.declare("rc381_part_3_line_76", Decimal, non_negative=True)
"""Form RC381 Part 3b line 76 "Enter the amount from line 53 as a positive amount.", when line 53 is
negative."""

RC381_PART_3_LINE_77 = CATALOG.declare("rc381_part_3_line_77", Decimal, non_negative=True)
"""Form RC381 Part 3b line 77 "If line 53 is negative and line 60 is positive, enter whichever is
less: amount from line 60 or line 76. If not, enter "0"." A non-negative amount."""

RC381_PART_3_LINE_78 = CATALOG.declare("rc381_part_3_line_78", Decimal, non_negative=True)
"""Form RC381 Part 3b line 78 "Line 76 minus line 77"."""

RC381_PART_3_LINE_79 = CATALOG.declare("rc381_part_3_line_79", Decimal, non_negative=True)
"""Form RC381 Part 3b line 79 "Line 75 plus line 77"."""

RC381_PART_3_LINE_80 = CATALOG.declare("rc381_part_3_line_80", Decimal, non_negative=True)
"""Form RC381 Part 3b line 80 "If line 68 and line 78 are both positive, enter whichever is less. If
not, enter "0""."""

RC381_PART_3_LINE_81 = CATALOG.declare("rc381_part_3_line_81", Decimal, non_negative=True)
"""Base contributions through employment income, Form RC381 Part 3b line 81 "Line 79 plus line
80"."""

RC381_PART_3_LINE_82 = CATALOG.declare("rc381_part_3_line_82", Decimal, non_negative=True)
"""Form RC381 Part 3b line 82 "If line 60 is positive or "0", enter the amount from line 59 at line
82 and line 88, and continue at line 89. If not, enter the amount from line 56 and continue at line
83." A non-negative amount."""

RC381_PART_3_LINE_83 = CATALOG.declare("rc381_part_3_line_83", Decimal, non_negative=True)
"""Form RC381 Part 3b line 83 "Enter the amount from line 60 as a positive amount.", when line 60 is
negative."""

RC381_PART_3_LINE_84 = CATALOG.declare("rc381_part_3_line_84", Decimal, non_negative=True)
"""Form RC381 Part 3b line 84 "If line 53 is positive, enter whichever is less: amount from line 53
or line 83. If not, enter "0"." A non-negative amount."""

RC381_PART_3_LINE_85 = CATALOG.declare("rc381_part_3_line_85", Decimal, non_negative=True)
"""Form RC381 Part 3b line 85 "Line 83 minus line 84"."""

RC381_PART_3_LINE_86 = CATALOG.declare("rc381_part_3_line_86", Decimal, non_negative=True)
"""Form RC381 Part 3b line 86 "Line 82 plus line 84"."""

RC381_PART_3_LINE_87_DIFFERENCE = CATALOG.declare("rc381_part_3_line_87_difference", Decimal)
"""Form RC381 Part 3b line 87, the printed "the result of line 68 minus line 80": signed, line 68
may be negative while line 80 is "0"."""

RC381_PART_3_LINE_87 = CATALOG.declare("rc381_part_3_line_87", Decimal, non_negative=True)
"""Form RC381 Part 3b line 87 "If line 68 and line 85 are both positive, enter whichever is less:
amount from line 85 or the result of line 68 minus line 80. If not, enter "0"." A non-negative
amount."""

RC381_PART_3_LINE_88 = CATALOG.declare("rc381_part_3_line_88", Decimal, non_negative=True)
"""Form RC381 Part 3b line 88 "Line 86 plus line 87"."""

RC381_PART_3_LINE_89 = CATALOG.declare("rc381_part_3_line_89", Decimal, non_negative=True)
"""Form RC381 Part 3b line 89 "If line 68 is positive or "0", enter the amount from line 67 at line
89 and line 92, and continue at line 93. If not, enter the amount from line 64 and continue at line
90." A non-negative amount."""

RC381_PART_3_LINE_90 = CATALOG.declare("rc381_part_3_line_90", Decimal, non_negative=True)
"""Form RC381 Part 3b line 90 "Enter the amount from line 68 as a positive amount.", when line 68 is
negative."""

RC381_PART_3_LINE_91 = CATALOG.declare("rc381_part_3_line_91", Decimal, non_negative=True)
"""Form RC381 Part 3b line 91 "If line 61 is positive, enter whichever is less: amount from line 61
or line 90. If not, enter "0"." A non-negative amount."""

RC381_PART_3_LINE_92 = CATALOG.declare("rc381_part_3_line_92", Decimal, non_negative=True)
"""Form RC381 Part 3b line 92 "Line 89 plus line 91"."""

RC381_PART_3_LINE_93 = CATALOG.declare("rc381_part_3_line_93", Decimal, non_negative=True)
"""Deduction for enhanced contributions on employment income, Form RC381 Part 3b line 93 "Line 88
plus line 92"."""

RC381_EMPLOYMENT_CPP_BASE_CONTRIBUTIONS = CATALOG.declare(
    "rc381_employment_cpp_base_contributions", Decimal, non_negative=True
)
"""Base contributions through employment income, Form RC381 Part 3a line 70 (when line 69 is
positive, the amount from line 52) and Part 3b line 81 "Line 79 plus line 80" (when line 69 is "0"
or negative): "Enter this amount (in dollars and cents) on line 30800 of your return.", the same
result by either part."""

RC381_EMPLOYMENT_CPP_ENHANCED_CONTRIBUTIONS = CATALOG.declare(
    "rc381_employment_cpp_enhanced_contributions", Decimal, non_negative=True
)
"""Deduction for enhanced contributions on employment income, Form RC381 Part 3a line 73 (when line
69 is positive, "Line 71 plus line 72") and Part 3b line 93 "Line 88 plus line 92" (when line 69
is "0" or negative): "Enter this amount (in dollars and cents) on line 22215 of your return.",
the same result by either part."""

RC381_CPP_OVERPAYMENT = CATALOG.declare("rc381_cpp_overpayment", Decimal, non_negative=True)
"""Overpayment, Form RC381 Part 3a line 74 "Enter the amount from line 69.": "Enter this amount (in
dollars and cents) on line 44800 of your return." Part 3b has no such line, so it is 0 when line 69
is "0" or negative."""

RC381_PART_4_LINE_4 = CATALOG.declare("rc381_part_4_line_4", Decimal)
"""Form RC381 Part 4 line 4 "Add lines 1 to 3"."""

RC381_PART_4_LINE_8 = CATALOG.declare("rc381_part_4_line_8", Decimal)
"""Form RC381 Part 4 line 8 "Line 6 minus line 7 (if negative, show in brackets)"."""

RC381_PART_4_LINE_11 = CATALOG.declare("rc381_part_4_line_11", Decimal)
"""Form RC381 Part 4 line 11 "Line 9 minus line 10 (if negative, show in brackets)"."""

RC381_PART_4_LINE_12 = CATALOG.declare("rc381_part_4_line_12", Decimal)
"""Form RC381 Part 4 line 12 "Line 8 plus line 11 (if negative, show in brackets)"."""

RC381_PART_4_LINE_13_DIFFERENCE = CATALOG.declare(
    "rc381_part_4_line_13_difference", Decimal, non_negative=True
)
"""Form RC381 Part 4 line 13 "Line 5 minus line 12", when line 61 of Part 3 is positive. A
non-negative amount."""

RC381_PART_4_LINE_13 = CATALOG.declare("rc381_part_4_line_13", Decimal, non_negative=True)
"""Form RC381 Part 4 line 13 "Line 5 minus line 12" when line 61 of Part 3 is positive, or "enter
the amount from line 5 on line 13" when it is negative; when it is "0" the amount from line 5 too,
so that line 26 is line 5 ("Enter the amount from line 5 on line 26"). A non-negative amount."""

RC381_PART_4_LINE_14 = CATALOG.declare("rc381_part_4_line_14", Decimal, non_negative=True)
"""Form RC381 Part 4 line 14 "Enter the amount from line 61 of Part 3 as a positive amount." A
non-negative amount."""

RC381_PART_4_LINE_17 = CATALOG.declare("rc381_part_4_line_17", Decimal)
"""Form RC381 Part 4 line 17 "Line 15 minus line 16 (if negative, show in brackets)"."""

RC381_PART_4_LINE_17A = CATALOG.declare("rc381_part_4_line_17a", Decimal, non_negative=True)
"""Form RC381 Part 4 line 17A "If line 17 is negative, enter it as a positive amount. If not,
enter "0"." A non-negative amount."""

RC381_PART_4_LINE_20 = CATALOG.declare("rc381_part_4_line_20", Decimal)
"""Form RC381 Part 4 line 20 "Line 18 minus line 19 (if negative, show in brackets)"."""

RC381_PART_4_LINE_21_FROM_LINE_17 = CATALOG.declare("rc381_part_4_line_21_from_line_17", Decimal)
"""Form RC381 Part 4 line 21 "If line 17 is positive, enter the amount from line 17 (show in
brackets)"."""

RC381_PART_4_LINE_21_LESSER = CATALOG.declare(
    "rc381_part_4_line_21_lesser", Decimal, non_negative=True
)
"""Form RC381 Part 4 line 21 "If line 20 is positive, enter whichever is less: amount from line
20 or line 17A." A non-negative amount."""

RC381_PART_4_LINE_21 = CATALOG.declare("rc381_part_4_line_21", Decimal)
"""Form RC381 Part 4 line 21 "If line 17 and line 20 are both negative or either amount is "0",
enter "0". If line 17 is positive, enter the amount from line 17 (show in brackets). If line 20
is positive, enter whichever is less: amount from line 20 or line 17A". When both are positive the
form gives both rules; this takes the second, which is "0" there because line 17A is "0"."""

RC381_PART_4_LINE_22 = CATALOG.declare("rc381_part_4_line_22", Rate)
"""Form RC381 Part 4 line 22 "If line 17A is more than line 14, enter "1". If not, enter the
result of line 17A divided by line 14 (calculated to the fifth decimal place without rounding)"."""

RC381_PART_4_LINE_23_LESSER = CATALOG.declare("rc381_part_4_line_23_lesser", Decimal)
"""Form RC381 Part 4 line 23 "If line 69 of Part 3 is positive or "0", enter whichever is less:
amount from line 68 of Part 3 or line 17A"."""

RC381_PART_4_LINE_23_MULTIPLIED = CATALOG.declare("rc381_part_4_line_23_multiplied", Decimal)
"""Form RC381 Part 4 line 23 "If not, enter the result of line 68 of Part 3 multiplied by the
rate at line 22"."""

RC381_PART_4_LINE_23 = CATALOG.declare("rc381_part_4_line_23", Decimal)
"""Form RC381 Part 4 line 23 "If line 69 of Part 3 is positive or "0", enter whichever is less:
amount from line 68 of Part 3 or line 17A. If not, enter the result of line 68 of Part 3
multiplied by the rate at line 22"."""

RC381_PART_4_LINE_24_LESSER = CATALOG.declare("rc381_part_4_line_24_lesser", Decimal)
"""Form RC381 Part 4 line 24 "Enter whichever is less: amount from line 17A or line 23.", when
line 61 of Part 3 is negative."""

RC381_PART_4_LINE_24 = CATALOG.declare("rc381_part_4_line_24", Decimal)
"""Form RC381 Part 4 line 24 "Enter whichever is less: amount from line 17A or line 23.", which
the form completes only when line 61 of Part 3 is negative; otherwise it is "0"."""

RC381_PART_4_LINE_25A = CATALOG.declare("rc381_part_4_line_25a", Decimal)
"""Form RC381 Part 4 line 25A "Amount from line 21", which the form completes only when line 61
of Part 3 is negative; otherwise it is "0"."""

RC381_PART_4_LINE_26 = CATALOG.declare("rc381_part_4_line_26", Decimal)
"""Form RC381 Part 4 line 26 "Add lines 24 to 25A." (line 25 being the amount from line 13)."""

RC381_PART_4_LINE_27 = CATALOG.declare("rc381_part_4_line_27", Decimal)
"""Form RC381 Part 4 line 27 "Amount from line 26 × 16.80672 ="."""

RC381_PART_4_LINE_31_DIFFERENCE = CATALOG.declare("rc381_part_4_line_31_difference", Decimal)
"""Form RC381 Part 4 line 31 "Line 29 minus line 30 (if negative, show in brackets)", line 29 being
the amount from line 61 of Part 3 and line 30 the amount from line 12, entered when line 61 of
Part 3 is positive."""

RC381_PART_4_LINE_31 = CATALOG.declare("rc381_part_4_line_31", Decimal)
"""Form RC381 Part 4 line 31: "Line 29 minus line 30" when line 61 of Part 3 is positive, and
"enter "0" at line 31" when it is negative; with line 61 "0" lines 29 to 39 are not completed,
so it is "0" too. Signed, as line 12 may be more than line 61."""

RC381_PART_4_LINE_32 = CATALOG.declare("rc381_part_4_line_32", Decimal)
"""Form RC381 Part 4 line 32 "Line 28 minus line 31", line 28 being the total actual base and first
additional QPP contributions from line 39 of Part 3. The form prints no floor."""

RC381_PART_4_LINE_33 = CATALOG.declare("rc381_part_4_line_33", Decimal, non_negative=True)
"""Form RC381 Part 4 line 33 "Enter the amount from line 61 of Part 3 as a positive amount." (above
zero only when line 61 is negative). A non-negative amount."""

RC381_PART_4_LINE_34 = CATALOG.declare("rc381_part_4_line_34", Decimal, non_negative=True)
"""Form RC381 Part 4 line 34 "If line 17A is positive, enter whichever is less: amount from line
17A or line 33. If not, enter "0"." A non-negative amount."""

RC381_PART_4_LINE_35 = CATALOG.declare("rc381_part_4_line_35", Decimal, non_negative=True)
"""Form RC381 Part 4 line 35 "Line 33 minus line 34". A non-negative amount, as line 34 is never
more than line 33."""

RC381_PART_4_LINE_35AA_FROM_LINE_17 = CATALOG.declare(
    "rc381_part_4_line_35aa_from_line_17", Decimal, non_negative=True
)
"""Form RC381 Part 4 line 35A "If line 35 and line 17 are both positive, enter the amount from line
17.", before line 35 decides whether line 35A takes it: the amount from line 17 when it is above
zero, else "0". A non-negative amount."""

RC381_PART_4_LINE_35AA = CATALOG.declare("rc381_part_4_line_35aa", Decimal, non_negative=True)
"""Form RC381 Part 4 line 35A "If line 35 and line 17 are both positive, enter the amount from line
17.": the amount from line 17 when line 35 and line 17 are both above zero, else "0". A
non-negative amount."""

RC381_PART_4_LINE_35AB_FROM_LINE_20 = CATALOG.declare(
    "rc381_part_4_line_35ab_from_line_20", Decimal
)
"""Form RC381 Part 4 line 35A "If line 35 is "0" and line 20 is positive, enter the amount from
line 20 (show in brackets).", before line 35 decides whether line 35A takes it: the negative of
line 20 when it is above zero, else "0"."""

RC381_PART_4_LINE_35AB_WHEN_LINE_35_ZERO = CATALOG.declare(
    "rc381_part_4_line_35ab_when_line_35_zero", Decimal
)
"""Form RC381 Part 4 line 35A "If line 35 is "0" and line 20 is positive, enter the amount from
line 20 (show in brackets).": that amount when line 35 is "0", before the block "If line 61 of
Part 3 is ... negative" decides whether line 35A takes it."""

RC381_PART_4_LINE_35AB = CATALOG.declare("rc381_part_4_line_35ab", Decimal)
"""Form RC381 Part 4 line 35A "If line 35 is "0" and line 20 is positive, enter the amount from
line 20 (show in brackets).", which the form completes only when line 61 of Part 3 is negative
(lines 33 to 39 are completed then); otherwise it is "0"."""

RC381_PART_4_LINE_35A = CATALOG.declare("rc381_part_4_line_35a", Decimal)
"""Form RC381 Part 4 line 35A, the two sentences printed on it added: line 17 when lines 35 and 17
are both positive, or line 20 in brackets when line 35 is "0" and line 20 is positive, else "0".
Signed."""

RC381_PART_4_LINE_36 = CATALOG.declare("rc381_part_4_line_36", Decimal, non_negative=True)
"""Form RC381 Part 4 line 36 "Enter the amount from line 68 of Part 3 if positive. If not, enter
"0"." A non-negative amount."""

RC381_PART_4_LINE_38 = CATALOG.declare("rc381_part_4_line_38", Decimal)
"""Form RC381 Part 4 line 38 "Line 36 minus line 37", line 37 being the amount from line 24. The
form prints no floor."""

RC381_PART_4_LINE_39 = CATALOG.declare("rc381_part_4_line_39", Decimal)
"""Form RC381 Part 4 line 39 "Enter whichever is less: amount from line 35 or line 38." The form
prints no floor."""

RC381_PART_4_LINE_40 = CATALOG.declare("rc381_part_4_line_40", Decimal)
"""Form RC381 Part 4 line 40 "Add lines 32, 35A, and 39." (with line 61 of Part 3 at "0", line 28
entered on line 40)."""

RC381_PART_4_LINE_41 = CATALOG.declare("rc381_part_4_line_41", Decimal)
"""Form RC381 Part 4 line 41 "Amount from line 40 × 15.625 ="."""

RC381_PART_4_LINE_42 = CATALOG.declare("rc381_part_4_line_42", Decimal)
"""Form RC381 Part 4 line 42 "Line 27 plus line 41"."""

RC381_PART_4_LINE_46_DIFFERENCE = CATALOG.declare("rc381_part_4_line_46_difference", Decimal)
"""Form RC381 Part 4 line 46 "Line 44 minus line 45 (if negative, show in brackets)", line 44 being
the amount from line 62 of Part 3 and line 45 the amount from line 65 of Part 3, before the gate
"If line 68 of Part 3 is positive, complete lines 44 to 46" decides whether line 46 takes it."""

RC381_PART_4_LINE_46 = CATALOG.declare("rc381_part_4_line_46", Decimal)
"""Form RC381 Part 4 line 46 "Line 44 minus line 45 (if negative, show in brackets)" when line 68
of Part 3 is positive, else "enter "0" on line 46"."""

RC381_PART_4_LINE_47 = CATALOG.declare("rc381_part_4_line_47", Decimal)
"""Form RC381 Part 4 line 47 "Line 43 minus line 46 (if negative, show in brackets)", line 43 being
the total actual second additional CPP contributions from line 25 of Part 3."""

RC381_PART_4_LINE_51_DIFFERENCE = CATALOG.declare("rc381_part_4_line_51_difference", Decimal)
"""Form RC381 Part 4 line 51 "Line 49 minus line 50 (if negative, show in brackets)", line 49 being
the amount from line 68 of Part 3 and line 50 the amount from line 46, before the gate "If line
68 of Part 3 is positive, complete lines 49 to 51" decides whether line 51 takes it."""

RC381_PART_4_LINE_51 = CATALOG.declare("rc381_part_4_line_51", Decimal)
"""Form RC381 Part 4 line 51 "Line 49 minus line 50 (if negative, show in brackets)" when line 68
of Part 3 is positive, else "enter "0" on line 51"."""

RC381_PART_4_LINE_52 = CATALOG.declare("rc381_part_4_line_52", Decimal)
"""Form RC381 Part 4 line 52 "Line 48 minus line 51", line 48 being the total actual second
additional QPP contributions from line 45 of Part 3. The form prints no floor."""

RC381_PART_4_LINE_53 = CATALOG.declare("rc381_part_4_line_53", Decimal)
"""Form RC381 Part 4 line 53 "Line 47 plus line 52"."""

RC381_PART_4_LINE_54 = CATALOG.declare("rc381_part_4_line_54", Decimal, non_negative=True)
"""Form RC381 Part 4 line 54 "Enter the amount from line 68 of Part 3 as a positive amount." (above
zero only when line 68 is negative). A non-negative amount."""

RC381_PART_4_LINE_55 = CATALOG.declare("rc381_part_4_line_55", Decimal, non_negative=True)
"""Form RC381 Part 4 line 55 "If line 61 of Part 3 is positive, enter whichever is less: amount
from line 61 of Part 3 or line 54.", when line 61 is positive and line 68 is negative, else "0".
A non-negative amount."""

RC381_PART_4_LINE_56 = CATALOG.declare("rc381_part_4_line_56", Decimal)
"""Form RC381 Part 4 line 56 "Line 53 plus line 55"."""

RC381_PART_4_LINE_59 = CATALOG.declare("rc381_part_4_line_59", Decimal, non_negative=True)
"""Form RC381 Part 4 line 59 "Line 57 minus line 58 (if negative, enter "0") (maximum $67,800)",
line 57 being the amount from line C of Part 2 and line 58 the amount from line F. A non-
negative amount."""

RC381_PART_4_LINE_61 = CATALOG.declare("rc381_part_4_line_61", Decimal, non_negative=True)
"""Form RC381 Part 4 line 61 "Line 59 minus line 60 (if negative, enter "0")", line 60 being the
amount from line 42. A non-negative amount."""

RC381_PART_4_LINE_62 = CATALOG.declare("rc381_part_4_line_62", Decimal)
"""Form RC381 Part 4 line 62 "Enter whichever is less: amount from line 4 or line 61." Signed, as
line 4 is not floored."""

RC381_PART_4_LINE_65 = CATALOG.declare("rc381_part_4_line_65", Decimal, non_negative=True)
"""Form RC381 Part 4 line 65 "Line 63 minus line 64 (if negative, enter "0" on lines 65 and 69, and
continue at line 70)", line 63 being the amount from line 58 and line 64 the amount from line 3
of Part 3. It is "0" when line 3 of Part 3 is not less than line 58, where the form does not
complete lines 63 to 69. A non-negative amount."""

RC381_PART_4_LINE_68 = CATALOG.declare("rc381_part_4_line_68", Decimal, non_negative=True)
"""Form RC381 Part 4 line 68 "Line 66 minus line 67 (if negative, enter "0")", line 66 being the
amount from line 4 and line 67 the amount from line 59. A non-negative amount."""

RC381_PART_4_LINE_69 = CATALOG.declare("rc381_part_4_line_69", Decimal, non_negative=True)
"""Form RC381 Part 4 line 69 "Line 65 minus line 68 (if negative, enter "0")". It is "0" when line
3 of Part 3 is not less than line 58 ("If not, enter "0" on line 69"), as line 65 is "0" then. A
non-negative amount."""

RC381_PART_4_LINE_70 = CATALOG.declare("rc381_part_4_line_70", Decimal)
"""Self-employment income and other earnings subject to base and first additional contributions,
Form RC381 Part 4 line 70 "Line 62 minus line 69". The form prints no floor, so it is signed."""

RC381_PART_4_LINE_74 = CATALOG.declare("rc381_part_4_line_74", Decimal)
"""Form RC381 Part 4 line 74 "Add lines 71 to 73.", line 71 being the amount from line 4, line 72
the amount from line 11 of Part 3 and line 73 the amount from line 31 of Part 3."""

RC381_PART_4_LINE_76 = CATALOG.declare("rc381_part_4_line_76", Decimal)
"""Form RC381 Part 4 line 76 "Amount from line 56 ÷ 4% ="."""

RC381_PART_4_LINE_77 = CATALOG.declare("rc381_part_4_line_77", Decimal, non_negative=True)
"""Form RC381 Part 4 line 77 "Line 75 minus line 76 (if negative, enter "0")", line 75 being the
amount from line D of Part 2. A non-negative amount."""

RC381_PART_4_LINE_80 = CATALOG.declare("rc381_part_4_line_80", Decimal)
"""Form RC381 Part 4 line 80 "Line 78 minus line 79", line 78 being the amount from line 4 and line
79 the amount from line 65 (if any)."""

RC381_PART_4_LINE_82 = CATALOG.declare("rc381_part_4_line_82", Decimal)
"""Form RC381 Part 4 line 82 "Line 80 minus line 81", line 81 being the amount from line 70. The
form prints no floor."""

RC381_PART_4_LINE_83_LESSER = CATALOG.declare("rc381_part_4_line_83_lesser", Decimal)
"""Form RC381 Part 4 line 83 "Enter whichever is less: amount from line 77 or line 82.", before the
instruction "If line 74 is more than line 57, complete lines 75 to 83. If not, enter "0" on line
83" decides whether line 83 takes it."""

RC381_PART_4_LINE_83 = CATALOG.declare("rc381_part_4_line_83", Decimal)
"""Self-employment income and other earnings subject to second additional contributions, Form RC381
Part 4 line 83 "Enter whichever is less: amount from line 77 or line 82.", which the form
completes only when line 74 is more than line 57 (the amount from line C of Part 2); otherwise
"0"."""

RC381_PART_4_LINE_84 = CATALOG.declare("rc381_part_4_line_84", Decimal, non_negative=True)
"""Required base contributions on CPP pensionable earnings, Form RC381 Part 4 line 84 "amount from
line 70 × 9.9% = (maximum $6,712.20)". A non-negative amount."""

RC381_PART_4_LINE_85 = CATALOG.declare("rc381_part_4_line_85", Decimal, non_negative=True)
"""Required first additional contributions on CPP pensionable earnings, Form RC381 Part 4 line 85
"amount from line 70 × 2% = (maximum $1,356.00)". A non-negative amount."""

RC381_PART_4_LINE_86 = CATALOG.declare("rc381_part_4_line_86", Decimal, non_negative=True)
"""Required second additional contributions on CPP pensionable earnings, Form RC381 Part 4 line 86
"amount from line 83 × 8% = (maximum $792.00)". A non-negative amount."""

RC381_PART_4_LINE_87 = CATALOG.declare("rc381_part_4_line_87", Decimal, non_negative=True)
"""Form RC381 Part 4 line 87 "Line 85 plus line 86". A non-negative amount."""

RC381_PART_4_LINE_88 = CATALOG.declare("rc381_part_4_line_88", Decimal, non_negative=True)
"""Form RC381 Part 4 line 88 "Line 84 plus line 87". A non-negative amount."""

RC381_PART_4_LINE_89_FROM_LINE_69 = CATALOG.declare(
    "rc381_part_4_line_89_from_line_69", Decimal, non_negative=True
)
"""Form RC381 Part 4 line 89 "Amount from line 69 of Part 3 (if positive)", before it is multiplied
by 2: line 69 of Part 3 when it is above zero, else "0". A non-negative amount."""

RC381_PART_4_LINE_89 = CATALOG.declare("rc381_part_4_line_89", Decimal, non_negative=True)
"""Form RC381 Part 4 line 89 "Amount from line 69 of Part 3 (if positive) × 2 =". A non-negative
amount."""

RC381_PART_4_LINE_90 = CATALOG.declare("rc381_part_4_line_90", Decimal)
"""CPP contributions payable on self-employment income and other earnings, Form RC381 Part 4 line
90 "Line 88 minus 89. If positive, enter the amount (in dollars and cents) on line 42100 of your
return and continue at line 92. If negative, show in brackets and continue at line 91." Signed."""

RC381_SELF_EMPLOYMENT_CPP_CONTRIBUTIONS = CATALOG.declare(
    "rc381_self_employment_cpp_contributions", Decimal, non_negative=True
)
"""CPP contributions payable on self-employment income and other earnings, Form RC381 Part 4 line 90
"Line 88 minus 89. If positive, enter the amount (in dollars and cents) on line 42100 of your return
and continue at line 92.": line 90 when it is positive, else "0" (line 91 is completed when it is
negative). A non-negative amount."""

RC381_PART_4_LINE_91_FROM_LINE_90 = CATALOG.declare(
    "rc381_part_4_line_91_from_line_90", Decimal, non_negative=True
)
"""Form RC381 Part 4 line 91 "amount from line 90 entered as a positive amount", before it is
multiplied by 50%: above zero only when line 90 is negative. A non-negative amount."""

RC381_PART_4_LINE_91 = CATALOG.declare("rc381_part_4_line_91", Decimal, non_negative=True)
"""CPP overpayment, Form RC381 Part 4 line 91 "Enter the result of the following calculation (in
dollars and cents) on line 44800 of your return: amount from line 90 entered as a positive amount ×
50% =". A non-negative amount."""

RC381_PART_4_LINE_92 = CATALOG.declare("rc381_part_4_line_92", Decimal, non_negative=True)
"""Form RC381 Part 4 line 92 "If line 53 of Part 3 is positive or "0", enter the amount from line
52 of Part 3 at line 92 and line 98, and continue at line 99. If not, enter the amount from line
49 of Part 3 and continue at line 93." A non-negative amount."""

RC381_PART_4_LINE_93 = CATALOG.declare("rc381_part_4_line_93", Decimal, non_negative=True)
"""Form RC381 Part 4 line 93 "Enter the amount from line 53 of Part 3 as a positive amount." (above
zero only when line 53 is negative). A non-negative amount."""

RC381_PART_4_LINE_94 = CATALOG.declare("rc381_part_4_line_94", Decimal, non_negative=True)
"""Form RC381 Part 4 line 94 "If line 53 of Part 3 is negative and line 60 of Part 3 is positive,
enter whichever is less: amount from line 60 of Part 3 or line 93. If not, enter "0"." A non-
negative amount."""

RC381_PART_4_LINE_95 = CATALOG.declare("rc381_part_4_line_95", Decimal, non_negative=True)
"""Form RC381 Part 4 line 95 "Line 93 minus line 94". A non-negative amount."""

RC381_PART_4_LINE_96 = CATALOG.declare("rc381_part_4_line_96", Decimal, non_negative=True)
"""Form RC381 Part 4 line 96 "Line 92 plus line 94". A non-negative amount."""

RC381_PART_4_LINE_97 = CATALOG.declare("rc381_part_4_line_97", Decimal, non_negative=True)
"""Form RC381 Part 4 line 97 "If line 68 of Part 3 and line 95 are both positive, enter whichever
is less. If not, enter "0"." A non-negative amount."""

RC381_PART_4_LINE_98 = CATALOG.declare("rc381_part_4_line_98", Decimal, non_negative=True)
"""Base CPP contributions through employment income, Form RC381 Part 4 line 98 "Line 96 plus line
97 Enter this amount (in dollars and cents) on line 30800 of your return." A non-negative
amount."""

RC381_PART_4_LINE_99 = CATALOG.declare("rc381_part_4_line_99", Decimal, non_negative=True)
"""Form RC381 Part 4 line 99 "If line 60 of Part 3 is positive or "0", enter the amount from line
59 of Part 3 at line 99 and line 105, and continue at line 106. If not, enter the amount from
line 56 of Part 3 and continue at line 100." A non-negative amount."""

RC381_PART_4_LINE_100 = CATALOG.declare("rc381_part_4_line_100", Decimal, non_negative=True)
"""Form RC381 Part 4 line 100 "Enter the amount from line 60 of Part 3 as a positive amount."
(above zero only when line 60 is negative). A non-negative amount."""

RC381_PART_4_LINE_101 = CATALOG.declare("rc381_part_4_line_101", Decimal, non_negative=True)
"""Form RC381 Part 4 line 101 "If line 53 of Part 3 is positive, enter whichever is less: amount
from line 53 of Part 3 or line 100. If not, enter "0"." A non-negative amount."""

RC381_PART_4_LINE_102 = CATALOG.declare("rc381_part_4_line_102", Decimal, non_negative=True)
"""Form RC381 Part 4 line 102 "Line 100 minus line 101". A non-negative amount."""

RC381_PART_4_LINE_103 = CATALOG.declare("rc381_part_4_line_103", Decimal, non_negative=True)
"""Form RC381 Part 4 line 103 "Line 99 plus line 101". A non-negative amount."""

RC381_PART_4_LINE_104_DIFFERENCE = CATALOG.declare("rc381_part_4_line_104_difference", Decimal)
"""Form RC381 Part 4 line 104, "the result of line 68 of Part 3 minus line 97": above zero only
when line 68 is more than line 97. Signed, as line 68 may be negative."""

RC381_PART_4_LINE_104 = CATALOG.declare("rc381_part_4_line_104", Decimal, non_negative=True)
"""Form RC381 Part 4 line 104 "If line 68 of Part 3 and line 102 are both positive, enter whichever
is less: amount from line 102 or the result of line 68 of Part 3 minus line 97. If not, enter
"0"." A non-negative amount."""

RC381_PART_4_LINE_105 = CATALOG.declare("rc381_part_4_line_105", Decimal, non_negative=True)
"""Form RC381 Part 4 line 105 "Line 103 plus line 104". A non-negative amount."""

RC381_PART_4_LINE_106 = CATALOG.declare("rc381_part_4_line_106", Decimal, non_negative=True)
"""Form RC381 Part 4 line 106 "If line 68 of Part 3 is positive or "0", enter the amount from line
67 of Part 3 at line 106 and line 109, and continue at line 110. If not, enter the amount from
line 64 of Part 3 and continue at line 107." A non-negative amount."""

RC381_PART_4_LINE_107 = CATALOG.declare("rc381_part_4_line_107", Decimal, non_negative=True)
"""Form RC381 Part 4 line 107 "Enter the amount from line 68 of Part 3 as a positive amount."
(above zero only when line 68 is negative). A non-negative amount."""

RC381_PART_4_LINE_108 = CATALOG.declare("rc381_part_4_line_108", Decimal, non_negative=True)
"""Form RC381 Part 4 line 108 "If line 61 of Part 3 is positive and line 68 of Part 3 is negative,
enter whichever is less: amount from line 61 of Part 3 or line 107. If not, enter "0"." A non-
negative amount."""

RC381_PART_4_LINE_109 = CATALOG.declare("rc381_part_4_line_109", Decimal, non_negative=True)
"""Form RC381 Part 4 line 109 "Line 106 plus line 108". A non-negative amount."""

RC381_PART_4_LINE_110 = CATALOG.declare("rc381_part_4_line_110", Decimal, non_negative=True)
"""Deduction for CPP enhanced contributions on employment income, Form RC381 Part 4 line 110 "Line
105 plus line 109 Enter this amount (in dollars and cents) on line 22215 of your return." A non-
negative amount."""

RC381_PART_4_LINE_111 = CATALOG.declare("rc381_part_4_line_111", Decimal, non_negative=True)
"""Base CPP contributions through self-employment income and other earnings, Form RC381 Part 4 line
111 "Enter the result of the following calculation (in dollars and cents) on line 31000 of your
return: amount from line 84 × 50% =". A non-negative amount."""

RC381_PART_4_LINE_112 = CATALOG.declare("rc381_part_4_line_112", Decimal, non_negative=True)
"""Form RC381 Part 4 line 112 "Amount from line 85 × 50% =". A non-negative amount."""

RC381_PART_4_LINE_113 = CATALOG.declare("rc381_part_4_line_113", Decimal, non_negative=True)
"""Form RC381 Part 4 line 113 "Line 111 plus line 112". A non-negative amount."""

RC381_PART_4_LINE_114 = CATALOG.declare("rc381_part_4_line_114", Decimal, non_negative=True)
"""Form RC381 Part 4 line 114 "Enter the amount from line 69 of Part 3 if positive. If not, enter
"0"." A non-negative amount."""

RC381_PART_4_LINE_115 = CATALOG.declare("rc381_part_4_line_115", Decimal)
"""Form RC381 Part 4 line 115 "Line 113 minus line 114 (if negative, show in brackets)". Signed."""

RC381_PART_4_LINE_116_LESSER = CATALOG.declare(
    "rc381_part_4_line_116_lesser", Decimal, non_negative=True
)
"""Form RC381 Part 4 line 116, the amount lettered A: "Enter whichever is less: amount from line
113 or line 114.", the amount that line 116 multiplies by 83.1933% and that line 118 takes line
117 from. A non-negative amount."""

RC381_PART_4_LINE_116 = CATALOG.declare("rc381_part_4_line_116", Decimal, non_negative=True)
"""Form RC381 Part 4 line 116 "A × 83.1933% =". A non-negative amount."""

RC381_PART_4_LINE_118 = CATALOG.declare("rc381_part_4_line_118", Decimal, non_negative=True)
"""Form RC381 Part 4 line 118 "Amount A minus line 117", line 117 being the amount from line 116. A
non-negative amount."""

RC381_PART_4_LINE_121 = CATALOG.declare("rc381_part_4_line_121", Decimal)
"""Form RC381 Part 4 line 121 "Line 119 minus line 120", line 119 being the amount from line 111
and line 120 the amount from line 116. The form prints no floor, so it is signed."""

RC381_PART_4_LINE_124 = CATALOG.declare("rc381_part_4_line_124", Decimal)
"""Form RC381 Part 4 line 124 "Line 122 minus line 123", line 122 being the amount from line 112
and line 123 the amount from line 118. The form prints no floor, so it is signed."""

RC381_PART_4_LINE_125 = CATALOG.declare("rc381_part_4_line_125", Decimal, non_negative=True)
"""Form RC381 Part 4 line 125 "Amount from line 86 × 50% =". A non-negative amount."""

RC381_PART_4_LINE_127 = CATALOG.declare("rc381_part_4_line_127", Decimal, non_negative=True)
"""Form RC381 Part 4 line 127 "If line 115 is negative, enter it as a positive amount." (above zero
only when line 115 is negative). A non-negative amount."""

RC381_PART_4_LINE_128 = CATALOG.declare("rc381_part_4_line_128", Decimal, non_negative=True)
"""Form RC381 Part 4 line 128 "Line 126 minus line 127 (if negative, enter "0")", line 126 being
the amount from line 125. A non-negative amount."""

RC381_PART_4_LINE_129 = CATALOG.declare("rc381_part_4_line_129", Decimal, non_negative=True)
"""Deduction for CPP enhanced contributions on self-employment income and other earnings, Form
RC381 Part 4 line 129 "Add lines 121, 122, 124, 125, and 128. Enter this amount (in dollar and
cents) on line 22200 of your return.", line 122 being the amount from line 112. A non-negative
amount."""

RC381_PART_4_EARNINGS_SUBJECT_TO_CONTRIBUTIONS = CATALOG.declare(
    "rc381_part_4_earnings_subject_to_contributions", Decimal
)
"""Self-employment income and other earnings subject to contributions, Form RC381 Part 3 "If you
are completing Part 4 or Part 5 and calculate that your self-employment income and other
earnings subject to contributions (lines 70 and 83 of Part 4 or lines 68 and 81 of Part 5) are
"0," follow the instructions below.": lines 70 and 83 of Part 4 added. Line 70 prints no floor,
so it is signed; it is above zero exactly when Part 4 has earnings to contribute on."""

RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN = CATALOG.declare(
    "rc381_cpp_base_contributions_on_return", Decimal, non_negative=True
)
"""Base CPP contributions through employment income for line 30800 of the return when Form RC381 is
used: Part 4 line 98 when Part 4 has earnings subject to contributions, else (lines 70 and 83 of
Part 4 "0") Part 3a line 70 or Part 3b line 81 "Enter this amount (in dollars and cents) on line
30800 of your return." A non-negative amount."""

RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN = CATALOG.declare(
    "rc381_cpp_enhanced_contributions_on_return", Decimal, non_negative=True
)
"""Deduction for CPP enhanced contributions on employment income for line 22215 of the return when
Form RC381 is used: Part 4 line 110 when Part 4 has earnings subject to contributions, else Part
3a line 73 or Part 3b line 93 "Enter this amount (in dollars and cents) on line 22215 of your
return." A non-negative amount."""

RC381_CPP_OVERPAYMENT_ON_RETURN = CATALOG.declare(
    "rc381_cpp_overpayment_on_return", Decimal, non_negative=True
)
"""CPP overpayment for line 44800 of the return when Form RC381 is used: Part 4 line 91 when Part 4
has earnings subject to contributions, else Part 3a line 74 "Enter this amount (in dollars and
cents) on line 44800 of your return." (0 for Part 3b). A non-negative amount."""

RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT = CATALOG.declare(
    "rc381_cpp_payable_on_self_employment", Decimal, non_negative=True
)
"""CPP contributions payable on self-employment income and other earnings for line 42100 of the
return when Form RC381 is used: Part 4 line 90 "If positive, enter the amount (in dollars and
cents) on line 42100 of your return" when Part 4 has earnings subject to contributions, else "0"
(Part 4 is not completed). A non-negative amount."""

RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS = CATALOG.declare(
    "rc381_cpp_base_contributions_on_self_employment_and_other_earnings", Decimal, non_negative=True
)
"""Base CPP contributions through self-employment income and other earnings for line 31000 of the
return when Form RC381 is used: Part 4 line 111 "Enter the result of the following calculation
(in dollars and cents) on line 31000 of your return" when Part 4 has earnings subject to
contributions, else "0" (Part 4 is not completed). A non-negative amount."""

RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS = CATALOG.declare(
    "rc381_cpp_deduction_on_self_employment_and_other_earnings", Decimal, non_negative=True
)
"""Deduction for CPP enhanced contributions on self-employment income and other earnings for line
22200 of the return when Form RC381 is used: Part 4 line 129 "Enter this amount (in dollar and
cents) on line 22200 of your return." when Part 4 has earnings subject to contributions, else
"0" (Part 4 is not completed). A non-negative amount."""
