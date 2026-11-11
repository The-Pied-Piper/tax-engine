"""The federal catalog: deductions from total income.

From the split pension down to net income and the repayment lines after it, plus the lines of Form
T2222 (with Charts A and B as record lists) and the moves of Form T1-M line 21900 as a record list.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

CPP_MONTHS = CountKind.declare(CATALOG, "cpp_months", non_negative=True)
"""Months that CPP applied, Schedule 8 Part 2 "Box A: Enter the number of months that CPP applied
in 2025.": the key of the "Monthly proration for 2025" table, a count the filer enters ("Enter "12"
on line A below unless any of the following conditions apply", conditions a) to h)).

A starting count, not computed: the conditions are the filer's to apply. The table has a row for 1
to 12 months only, so "0" (conditions b, d and g) and any other number is refused, not guessed.
Part 1's election months (lines 50372 and 50374) only inform this count and feed no calculation
line, so they are not inputs.
"""


CPP_MAXIMUM_PENSIONABLE_EARNINGS = AmountKind.declare(
    CATALOG, "cpp_maximum_pensionable_earnings", non_negative=True
)
"""Maximum pensionable earnings, Schedule 8 Part 2 line B "Your maximum pensionable earnings for
2025 (maximum $71,300)": the "Maximum pensionable earnings" column of the "Monthly proration for
2025" table, in the row for the months in box A. Part 4 line 5 is "Amount from line B of Part 2"."""

CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM = AmountKind.declare(
    CATALOG, "cpp_second_additional_earnings_maximum", non_negative=True
)
"""Maximum amount subject to second additional contributions, Schedule 8 Part 2 line C "Your
maximum amount subject to second additional contributions for 2025 (maximum $9,900)": the column of
that name in the table, in the row for the months in box A. Nothing on the return reads it: Part 4
line 12 takes its $9,900 limit from the rate dataset, and Part 5 is wired separately."""

CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS = AmountKind.declare(
    CATALOG, "cpp_additional_maximum_pensionable_earnings", non_negative=True
)
"""Additional maximum pensionable earnings, Schedule 8 Part 2 line D "Your additional maximum
pensionable earnings for 2025 (maximum $81,200)": the "Additional maximum pensionable earnings"
column of the table, in the row for the months in box A. Part 4 line 4 is the lesser of it and
line 3."""

CPP_BASIC_EXEMPTION = AmountKind.declare(CATALOG, "cpp_basic_exemption", non_negative=True)
"""Basic exemption, Schedule 8 Part 2 line E "Your maximum basic exemption for 2025 (maximum
$3,500)": the "Maximum basic exemption" column of the table, in the row for the months in box A.
Part 4 line 8 is "Amount from line E of Part 2"."""

EI_MAXIMUM_INSURABLE_EARNINGS = AmountKind.declare(
    CATALOG, "ei_maximum_insurable_earnings", non_negative=True
)
"""Maximum insurable earnings, Schedule 13 line 5 "Maximum insurable earnings 65,700.00": the
printed figure, as an artifact of the same name."""

DEDUCTIONS_FROM_TOTAL_INCOME = AmountKind.declare(
    CATALOG, "deductions_from_total_income", non_negative=True
)
"""Total deductions, T1 line 23300 "Add lines 35 to 52": in the take-home, one core/record_total
over Schedule 8's export `ca/schedule_8.schedule_8_cpp_enhanced_contributions_on_return` (line
22215, the enhanced CPP contributions), the only deduction a salary-only filer has
(`t1_taxable_income_line_23300.yaml`)."""

NET_INCOME_BEFORE_ADJUSTMENTS = AmountKind.declare(CATALOG, "net_income_before_adjustments")
"""Net income before adjustments, T1 line 54 and line 23400 "Line 34 minus line 53 (if negative,
show in brackets)": total income less total deductions, not floored, so the kind is signed."""

NET_INCOME = AmountKind.declare(CATALOG, "net_income", non_negative=True)
"""Net income, T1 line 56 and line 23600 "Line 54 minus line 55 (if negative, enter "0") If
negative, you may have a non-capital loss (see Form T1A) and the negative amount is to be used for
certain calculations (go to canada.ca/line-23600) Net income": the net income before adjustments
(line 23400) less the social benefits repayment (line 23500), not below zero.
"""

NET_INCOME_SIGNED = AmountKind.declare(CATALOG, "net_income_signed")
"""Net income before its floor, T1 line 56 and line 23600 "Line 54 minus line 55 (if negative,
enter "0")" as Form T1206 Part 1 line 5 "Net income from line 23600 of your tax return (or the
amount you would have entered if the instructions on line 23600 read "if negative, show in
brackets")" reads it, and so does the TOSI-adjusted net income, which Schedule ON479-A column 1
line 1 reads: the net income before adjustments (line 23400) less the social benefits repayment
(line 23500), signed. The take-home produces it in `t1_taxable_income_line_23600_signed.yaml`
(one core/subtract, not floored)."""

OAS_BENEFITS_BASE_AMOUNT = AmountKind.declare(
    CATALOG, "oas_benefits_base_amount", non_negative=True
)
"""OAS benefits base amount, Federal Worksheet "Line 23500 - Social benefits repayment" line 16
"OAS benefits base amount 93,343.00": a fixed amount, claimed whole."""

SOCIAL_BENEFITS_REPAYMENT = AmountKind.declare(
    CATALOG, "social_benefits_repayment", non_negative=True
)
"""Social benefits repayment, T1 line 55 and line 23500 "Line 55 and line 23500: If not, enter "0"
on line 23500.": the result of the Federal Worksheet chart (line 21) when the chart applies, else
0. In the take-home it is an optional input (`t1_taxable_income_inputs.yaml`, default "0"): the
chart applies only with amounts on lines 11900, 11300 or 14600, which a salary-only filer has none
of."""

UCCB_AND_RDSP_INCOME = AmountKind.declare(CATALOG, "uccb_and_rdsp_income", non_negative=True)
"""UCCB and RDSP income, Federal Worksheet "Line 25000 - Other payments deduction" line 4 "Line 2
plus line 3 =": the amount from line 11700 of the return (line 2) and the amount from line 12500
(line 3)."""

CPP_PART_3_LINE_2 = AmountKind.declare(CATALOG, "cpp_part_3_line_2", non_negative=True)
"""Part 3 line 2 "Line 2: Enter whichever is less: amount from line D of Part 2 or line 1.": the
lesser of the additional maximum pensionable earnings (Part 2 line D) and the employment income
(line 1), the amount Part 5 line 32 takes as "Amount from line 2 of Part 3"."""

CPP_PART_3_LINE_4 = AmountKind.declare(CATALOG, "cpp_part_3_line_4", non_negative=True)
"""Earnings subject to second additional contributions, Schedule 8 Part 3 line 4 "Line 2 minus
line 3 (if negative, enter "0")": line 2 (`ca/cpp_part_3_line_2`) less line 3, "Amount from line B
of Part 2" (the maximum pensionable earnings), not below zero. Line 5 and line 22 read it."""

CPP_PART_3_LINE_5 = AmountKind.declare(CATALOG, "cpp_part_3_line_5", non_negative=True)
"""Part 3 line 5 "Line 5: Line 2 minus line 4 (if negative, enter "0")": the employment earnings
(line 2) less line 4, not below zero. Line 7 is "Line 5 minus line 6"."""

CPP_PART_3_LINE_7_DIFFERENCE = AmountKind.declare(
    CATALOG, "cpp_part_3_line_7_difference", non_negative=True
)
"""Part 3 line 7 before its maximum, "Line 5 minus line 6 (if negative, enter "0")": line 5 less
line 6 ("Amount from line E of Part 2"), not below zero. Line 7 caps it at its printed maximum."""

CPP_PART_3_LINE_7 = AmountKind.declare(CATALOG, "cpp_part_3_line_7", non_negative=True)
"""Earnings subject to base and first additional contributions, Schedule 8 Part 3 line 7 "Line 5
minus line 6 (if negative, enter "0") (maximum $67,800)": the lesser of the difference and the
maximum. Lines 11 and 12 take their rates of it."""

CPP_PART_3_LINE_11 = AmountKind.declare(CATALOG, "cpp_part_3_line_11", non_negative=True)
"""Part 3 line 11 "amount from line 7 multiplied by 4.95% (maximum $3,356.10)": the required base
contributions. Line 15 copies it, and line 25 (or line 36, by line 30) carries it to the return."""

CPP_PART_3_LINE_22 = AmountKind.declare(CATALOG, "cpp_part_3_line_22", non_negative=True)
"""Required second additional CPP contributions, Schedule 8 Part 3 line 22 "amount from line 4
multiplied by 4% (maximum $396.00)": line 27 is "Amount from line 22 (if any)", and line 28 is
line 26 plus line 27."""


CPP_PART_3_LINE_12 = AmountKind.declare(CATALOG, "cpp_part_3_line_12", non_negative=True)
"""Schedule 8 Part 3 line 12 "amount from line 7 multiplied by 1% (maximum $678.00)": the required
first additional contributions on the earnings of line 7."""

SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN = AmountKind.declare(
    CATALOG, "schedule_8_cpp_base_contributions_on_return", non_negative=True
)
"""Base CPP contributions of Schedule 8, for T1 line 30800 and ON428 line 58240: Part 3a line 25
"Enter the amount from line 15. Enter this amount (in dollars and cents) on line 30800 of your
return and line 58240 of your Form 428." In the take-home build `schedule_8_line_25.yaml`
produces it as a one-part `core/sum` of Part 3 line 11 (`ca/cpp_part_3_line_11`), the required
base contributions. Part 3b line 36 gives the same figure for a salary-only filer and Part 5 is
out of scope, so the short route (Part 3a only) stands. The form's total over its copies, 0 with
none, is added to Form RC381's (rc381_cpp_base_contributions_on_return) in
cpp_base_contributions_on_return."""

SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN = AmountKind.declare(
    CATALOG, "schedule_8_cpp_enhanced_contributions_on_return", non_negative=True
)
"""Enhanced CPP contributions of Schedule 8, for T1 line 22215: Part 3a line 28 "Line 26 plus line
27 Enter this amount (in dollars and cents) on line 22215 of your return." In the take-home build
`schedule_8_line_28.yaml` produces it as `core/sum` of Part 3 line 12 (`ca/cpp_part_3_line_12`,
the form's line 26) and line 22 (`ca/cpp_part_3_line_22`, the form's line 27). Part 3b line 48 gives
the same figure for a salary-only filer and Part 5 is out of scope, so the short route (Part 3a
only) stands. A deduction from total income, not a credit. The form's total over its copies, 0
with none, is added to Form RC381's (rc381_cpp_enhanced_contributions_on_return) in
cpp_enhanced_contributions_on_return."""


# Form T1-M, Moving Expenses Deduction, one copy for each move (T1 line 21900). The caller's inputs
# of one move are the fields of the record list `ca/t1_m_moves`, in the form's line order; the
# computed lines are the form's own lines, and the form exports line 29 and line 30.
