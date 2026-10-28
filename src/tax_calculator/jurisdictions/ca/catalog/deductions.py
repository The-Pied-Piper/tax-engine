"""The federal catalog: deductions from total income.

The split pension, union dues, child care, capital gains deduction, business investment loss,
support, carrying charges, CPP and other deduction lines, down to net income and the repayment lines
that follow it, and the lines of Form T2222 (northern residents deductions) with Chart A and Chart B
of its Step 3, which are record lists, and the moving expenses of Form T1-M (line 21900), a record
list of the moves with the lines of each move.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

ELECTED_SPLIT_PENSION_DEDUCTION = CATALOG.declare(
    "elected_split_pension_deduction", Decimal, non_negative=True
)
"""Deduction for elected split-pension amount, T1 line 38 and line 21000 "Deduction for elected
split-pension amount (complete Form T1032)": Form T1032 line 22 when
`ca/t1032_filer_is_transferring_spouse` is 1 (this return is the transferring spouse's), otherwise
0; worked out, never entered."""

UNION_DUES = CATALOG.declare("union_dues", Decimal, non_negative=True)
"""Union dues, T1 line 21200 "Annual union, professional, or like dues (receipts and box 44 of all
T4 slips)": the amount claimed, a starting amount."""

CPP_MONTHS = CATALOG.declare("cpp_months", int, non_negative=True)
"""Months that CPP applied, Schedule 8 Part 2 "Box A: Enter the number of months that CPP applied
in 2025.": the key of the "Monthly proration for 2025" table, a count the filer enters ("Enter "12"
on line A below unless any of the following conditions apply", conditions a) to h)).

A starting count, not computed: the conditions are the filer's to apply. The table has a row for 1
to 12 months only, so "0" (conditions b, d and g) and any other number is refused, not guessed.
Part 1's election months (lines 50372 and 50374) only inform this count and feed no calculation
line, so they are not inputs.
"""

CPT20_T4_EARNINGS = CATALOG.declare("cpt20_t4_earnings", Decimal, non_negative=True)
"""Employment earnings shown on a T4 slip that you are electing to pay additional CPP contributions
on, Schedule 8 Part 5 line 3 and line 50399 "Employment earnings shown on a T4 slip that you are
electing to pay additional CPP contributions on (complete Form CPT20)": a starting amount, added
to lines 1 and 2 on Part 5 line 4."""

CPT20_EARNINGS = CATALOG.declare("cpt20_earnings", Decimal, non_negative=True)
"""CPT20 earnings, Schedule 8 Part 4 line 2, Form RC381 Part 4 line 2 and line 50373
"Employment earnings not shown on a T4 slip that you are electing to pay additional CPP
contributions on (complete Form CPT20)": a starting amount."""

CPP_PART_5_COMPLETED = CATALOG.declare("cpp_part_5_completed", int, non_negative=True)
"""Schedule 8 Part 5 completed, "Part 5 - Complete this part if you are reporting both: employment
income (complete Part 3 first) / self-employment income or other earnings that you are electing to
pay CPP contributions on. If not, leave this part blank.": 1 when the filer completes Part 5, 0
when not, a count the filer states. Part 3 and Part 5 are the filer's choice on the form, so 1
replaces the Part 3 route on lines 30800, 22215 and 44800. Both counts at 1 are refused (see
`ca/cpp_part_4_and_part_5_both_checked`), Part 4 and Part 5 being alternatives. The count is checked
first by `ca/cpp_part_5_completed_yes_or_no_checked`, a count of 2 or more is refused, not capped.
On a return that carries Form RC381 it is then checked by `ca/cpp_part_5_completed_checked`
against that form: a count above 0 is refused, the form's own total already holding those lines.
The form leaves the choice to the filer on a return with Schedule 8."""

CPP_PART_4_COMPLETED = CATALOG.declare("cpp_part_4_completed", int, non_negative=True)
"""Schedule 8 Part 4 completed, "Part 4 - Complete this part if you are reporting only
self-employment income or other earnings you are electing to pay CPP contributions on. If not,
leave this part blank.": 1 when the filer completes Part 4, 0 when not, a count the filer states.

It is a yes or no answer, a count of 1 or 0: 1 enters Part 4's lines 14, 15 and 17 on the return
(lines 42100, 31000 and 22200). A count of 2 or more is refused by `ca/yes_or_no_count`, not
capped. Part 5, for a filer reporting employment income as well, is counted by
cpp_part_5_completed.
"""

CPP_PART_4_COMPLETED_YES_OR_NO_CHECKED = CATALOG.declare(
    "cpp_part_4_completed_yes_or_no_checked", int, non_negative=True
)
"""Schedule 8 Part 4 completed, checked, "Part 4 - Complete this part if you are reporting only
self-employment income or other earnings you are electing to pay CPP contributions on. If not,
leave this part blank.": the answer of `ca/cpp_part_4_completed` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped. It is read
by the Form RC381 guard (`ca/count_without_records`).
"""

CPP_PART_5_COMPLETED_YES_OR_NO_CHECKED = CATALOG.declare(
    "cpp_part_5_completed_yes_or_no_checked", int, non_negative=True
)
"""Schedule 8 Part 5 completed, checked, "Part 5 - Complete this part if you are reporting both:
employment income (complete Part 3 first) / self-employment income or other earnings that you are
electing to pay CPP contributions on. If not, leave this part blank.": the answer of
`ca/cpp_part_5_completed` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1
or 0. A count of 2 or more is refused, not capped. It is read by the Form RC381 guard
(`ca/count_without_records`).
"""

CPP_PART_4_COMPLETED_CHECKED = CATALOG.declare(
    "cpp_part_4_completed_checked", int, non_negative=True
)
"""Schedule 8 Part 4 completed, checked, "Part 4 - Complete this part if you are reporting only
self-employment income or other earnings you are electing to pay CPP contributions on. If not,
leave this part blank.": the answer of `ca/cpp_part_4_completed_yes_or_no_checked` after
`ca/count_without_records` checks it against the copies of Form RC381 (`ca/rc381_instances`), a
count of 1 or 0. The check refuses a count above 0 on a return that carries Form RC381, an input
error: the return carries Schedule 8 or Form RC381, never both, and the form's own total already
holds lines 42100, 31000 and 22200.
"""

CPP_PART_5_COMPLETED_CHECKED = CATALOG.declare(
    "cpp_part_5_completed_checked", int, non_negative=True
)
"""Schedule 8 Part 5 completed, checked, "Part 5 - Complete this part if you are reporting both:
employment income (complete Part 3 first) / self-employment income or other earnings that you are
electing to pay CPP contributions on. If not, leave this part blank.": the answer of
`ca/cpp_part_5_completed_yes_or_no_checked` after `ca/count_without_records` checks it against the
copies of Form RC381 (`ca/rc381_instances`), a count of 1 or 0. The check refuses a count above 0 on
a return that carries Form RC381, an input error: the return carries Schedule 8 or Form RC381, never
both, and the form's own total already holds lines 42100, 31000 and 22200.
"""

CPP_PART_4_AND_PART_5_BOTH = CATALOG.declare("cpp_part_4_and_part_5_both", int, non_negative=True)
"""Schedule 8 Part 4 and Part 5 completed together, "Part 4 - Complete this part if you are
reporting only self-employment income or other earnings you are electing to pay CPP contributions
on. If not, leave this part blank." and "Part 5 - Complete this part if you are reporting both:
employment income (complete Part 3 first) / self-employment income or other earnings that you are
electing to pay CPP contributions on. If not, leave this part blank.": 1 when
`ca/cpp_part_4_completed_checked` and `ca/cpp_part_5_completed_checked` are each more than 0, else
0, a starting count. The two parts are alternatives on the form, so this count of 1 is refused
(see `ca/cpp_part_4_and_part_5_both_checked`), not added: Part 4 for self-employment income only,
Part 5 for employment income as well."""

CPP_PART_4_AND_PART_5_BOTH_CHECKED = CATALOG.declare(
    "cpp_part_4_and_part_5_both_checked", int, non_negative=True
)
"""Schedule 8 Part 4 and Part 5 completed together, checked: the count of
`ca/cpp_part_4_and_part_5_both` when it is 0, the only value produced. A count of 1 is an input
error, not capped, so the self-employed contributions are never counted twice."""

CPP_PART_4_WITH_EMPLOYMENT_EARNINGS = CATALOG.declare(
    "cpp_part_4_with_employment_earnings", int, non_negative=True
)
"""Schedule 8 Part 4 completed with employment earnings, Part 4 "Contributions on self-employment
income and other earnings only (no employment income)" and "Part 4 - Complete this part if you are
reporting only self-employment income or other earnings you are electing to pay CPP contributions
on. If not, leave this part blank." with Part 3 line 1 and line 50339 "Total CPP pensionable
earnings from box 26 of all of your T4 slips where the province of employment is not Quebec": 1
when `ca/cpp_part_4_completed_checked` is more than 0 and
`ca/t4_cpp_pensionable_earnings_outside_quebec` is more than 0, else 0, a starting count.
"Employment income" in the Part 4 heading is read as
`ca/t4_cpp_pensionable_earnings_outside_quebec`, the input that Part 3 and Part 5 use; Quebec T4
earnings are not read, and employment income that is not carried into that input is not detected.
Part 4 is for a filer with no employment income, so this count of 1 is
refused (see `ca/cpp_part_4_with_employment_earnings_checked`), not added. Part 5 completed with no
such earnings is not refused: its form text says only "(complete Part 3 first)", and a T4 with zero
box 14 is legitimate."""

CPP_PART_4_WITH_EMPLOYMENT_EARNINGS_CHECKED = CATALOG.declare(
    "cpp_part_4_with_employment_earnings_checked", int, non_negative=True
)
"""Schedule 8 Part 4 completed with employment earnings, checked: the count of
`ca/cpp_part_4_with_employment_earnings` when it is 0, the only value produced. A count of 1 is an
input error naming Part 4 and the Part 5 route, not capped, so the employment income is never
treated as self-employment contributions."""

EI_CONTROLLED_CORPORATION_EARNINGS = CATALOG.declare(
    "ei_controlled_corporation_earnings", Decimal, non_negative=True
)
"""Earnings from a controlled corporation, Schedule 13 line 2 and line 54493 "If you are not
eligible to participate in the EI program as an employee of a corporation because you control more
than 40% of the voting shares of that corporation, enter the amount from box 14 of all your T4
slips from that corporation.": a starting amount."""

EI_EXEMPT_SELF_EMPLOYMENT_INCOME = CATALOG.declare(
    "ei_exempt_self_employment_income", Decimal, non_negative=True
)
"""Tax-exempt self-employment income, Schedule 13 line 3 and line 54494 "If you are registered or
entitled to be registered under the Indian Act and you earned tax-exempt self-employment income on
a reserve in Canada, enter your total tax-exempt self-employment income.": a starting amount."""

EI_INSURABLE_EARNINGS = CATALOG.declare("ei_insurable_earnings", Decimal, non_negative=True)
"""Total EI insurable earnings, Schedule 13 line 6 and line 54780 "Total EI insurable earnings
(amount from box 24 of all your T4 slips; if box 24 is blank, enter the amount from box 14 unless
box 28 shows that the T4 earnings are EI-exempt)": a starting amount, including the employment
income that has no T4 slip (Note 3)."""

EI_SPECIAL_BENEFITS_AGREEMENT = CATALOG.declare(
    "ei_special_benefits_agreement", int, non_negative=True
)
"""Agreement with the Canada Employment Insurance Commission, Schedule 13 "Complete this schedule
to calculate the amount of your employment insurance (EI) premiums on self-employment and other
eligible earnings only if you have entered into an agreement with the Canada Employment Insurance
Commission, through Service Canada, to participate in the EI program for access to EI special
benefits.": 1 when the filer has the agreement, 0 when not, a count the filer states.

It is the number of times Schedule 13's line 9 is entered on the return (lines 31217 and 42120).
"""

EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED = CATALOG.declare(
    "ei_special_benefits_agreement_checked", int, non_negative=True
)
"""Agreement with the Canada Employment Insurance Commission, Schedule 13: the answer of
`ca/ei_special_benefits_agreement` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count
of 1 or 0. A count of 2 or more is refused, not capped."""

CHILD_CARE_EXPENSES_PAID = CATALOG.declare("child_care_expenses_paid", Decimal, non_negative=True)
"""Child care expenses paid, Form T778 Part A line 67950 "Total (add all entries for Child care
expenses paid)": a starting amount, also Part B line 5 "Enter the amount from line 67950."."""

CHILDREN_UNDER_SEVEN = CATALOG.declare("children_under_seven", int, non_negative=True)
"""Number of eligible children born in 2019 or later, Form T778 Part B line 1 "Number of eligible
children born in 2019 or later whom the disability amount cannot be claimed for": a starting
count."""

CHILDREN_WITH_DISABILITY = CATALOG.declare("children_with_disability", int, non_negative=True)
"""Number of eligible children with the disability amount, Form T778 Part B line 2 (line 67960)
"Number of eligible children born in 2025 or earlier whom the disability amount can be claimed
for": a starting count."""

CHILDREN_SEVEN_TO_SIXTEEN = CATALOG.declare("children_seven_to_sixteen", int, non_negative=True)
"""Number of eligible children born in 2009 to 2018, Form T778 Part B line 3 "Number of eligible
children born in 2009 to 2018 (and born in 2008 or earlier with a mental or physical infirmity
whom the disability amount cannot be claimed for)": a starting count."""

CHILD_CARE_LIMIT_FOR_CHILDREN_UNDER_SEVEN = CATALOG.declare(
    "child_care_limit_for_children_under_seven", Decimal, non_negative=True
)
"""Child care limit for the children born in 2019 or later, Form T778 Part B line 1 "multiplied by
$8,000": the line 1 count times $8,000, a part of line 4."""

CHILD_CARE_LIMIT_FOR_CHILDREN_WITH_DISABILITY = CATALOG.declare(
    "child_care_limit_for_children_with_disability", Decimal, non_negative=True
)
"""Child care limit for the children with the disability amount, Form T778 Part B line 2 (line
67960) "multiplied by $11,000": the line 2 count times $11,000, a part of line 4."""

CHILD_CARE_LIMIT_FOR_CHILDREN_SEVEN_TO_SIXTEEN = CATALOG.declare(
    "child_care_limit_for_children_seven_to_sixteen", Decimal, non_negative=True
)
"""Child care limit for the children born in 2009 to 2018, Form T778 Part B line 3 "multiplied by
$5,000": the line 3 count times $5,000, a part of line 4."""

CHILD_CARE_BASIC_LIMIT = CATALOG.declare("child_care_basic_limit", Decimal, non_negative=True)
"""Child care basic limit, Form T778 Part B line 4 "Add lines 1 to 3.": the limits for each group
of eligible children, in line order."""

CHILD_CARE_EARNED_INCOME = CATALOG.declare("child_care_earned_income", Decimal, non_negative=True)
"""Earned income for child care, Form T778 Part B line 6 "Enter your earned income.": "Your earned
income of line 6 is the total of the following: employment income (including tips and gratuities,
and the non-taxable part of an allowance received as an emergency volunteer) ...", here employment
income alone.

The other parts of earned income the form's "Earned income" definition lists are not triggered by
the returns modelled.
"""

CHILD_CARE_EARNED_INCOME_LIMIT = CATALOG.declare(
    "child_care_earned_income_limit", Decimal, non_negative=True
)
"""Earned income limit for child care, Form T778 Part B line 6 "multiplied by two-thirds": the
earned income times two-thirds, rounded half-up to the cent, once, as line 6 is a dollars-and-cents
box."""

CHILD_CARE_EXPENSES = CATALOG.declare("child_care_expenses", Decimal, non_negative=True)
"""Child care expenses deduction, T1 line 41 (line 21400) "Child care expenses (complete Form
T778)": Form T778 Part B line 7 "Enter whichever amount is the least: line 4, line 5 or line 6.",
carried by line 9 "Line 7 minus line 8. ... enter this amount on line 21400 of your return.
Allowable deduction", a deduction from total income.

Line 8 (the other person with the higher net income) is not triggered, so line 9 is line 7; nor
are Parts C and D (the higher-income claimant, school attendance). Eligibility is the return's to
state, not computed here.
"""

CAPITAL_GAINS_DEDUCTIONS_1985_TO_1987 = CATALOG.declare(
    "capital_gains_deductions_1985_to_1987", Decimal, non_negative=True
)
"""Capital gains deductions claimed for 1985 to 1987, Form T1436 (Capital Gains Worksheet) line
1 "Total amounts from line 254 of your income tax and benefit returns for these years", before
its multiplier "x 2": a starting amount, a figure from the returns of 1985 to 2024."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_OTHER_THAN_ELIGIBLE_CAPITAL_PROPERTY = CATALOG.declare(
    "capital_gains_deductions_1988_and_1989_other_than_eligible_capital_property",
    Decimal,
    non_negative=True,
)
"""Capital gains deductions claimed for 1988 and 1989 other than for eligible capital property,
Form T1436 (Capital Gains Worksheet) line 2 "Total amounts from line 254 of your returns", before
the amounts reported on lines 543 and 544 of Schedule 3 are taken off and before its multiplier
"x 1.5": a starting amount, a figure from the returns of 1985 to 2024. The filer enters the same
total on line 2 and on line 3; line 2 takes off the Schedule 3 sum, and line 3 is capped by it."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_ELIGIBLE_CAPITAL_PROPERTY = CATALOG.declare(
    "capital_gains_deductions_1988_and_1989_eligible_capital_property", Decimal, non_negative=True
)
"""Capital gains deductions claimed for 1988 and 1989 for eligible capital property, Form T1436
(Capital Gains Worksheet) line 3 "Total amounts from line 254 of your returns", before amount (a)
is taken off and before its multiplier "x 1.3333": a starting amount, a figure from the returns
of 1985 to 2024. The filer enters the same total on line 2 and on line 3."""

CAPITAL_GAINS_DEDUCTIONS_1990_TO_1999 = CATALOG.declare(
    "capital_gains_deductions_1990_to_1999", Decimal, non_negative=True
)
"""Capital gains deductions claimed for 1990 to 1999, Form T1436 (Capital Gains Worksheet) line
4 "Total amounts from line 254 of your returns for these years", before its multiplier "x
1.3333": a starting amount, a figure from the returns of 1985 to 2024."""

CAPITAL_GAINS_DEDUCTIONS_2000 = CATALOG.declare(
    "capital_gains_deductions_2000", Decimal, non_negative=True
)
"""Capital gains deductions claimed for 2000, Form T1436 (Capital Gains Worksheet) line 5 "Amount
from line 254 of your return", before its multiplier "x 1/IR": a starting amount, a figure from
the returns of 1985 to 2024."""

CAPITAL_GAINS_DEDUCTIONS_2001_TO_2024 = CATALOG.declare(
    "capital_gains_deductions_2001_to_2024", Decimal, non_negative=True
)
"""Capital gains deductions claimed for 2001 to 2024, Form T1436 (Capital Gains Worksheet) line
6 "Total amounts from line 254 of your returns for 2001 to 2018, line 25400 of your returns for
2019 to 2024, and line 25395 of your return for 2024", before its multiplier "x 2": a starting
amount, a figure from the returns of 1985 to 2024."""

SCHEDULE_3_LINE_543 = CATALOG.declare("schedule_3_line_543", Decimal, non_negative=True)
"""Schedule 3 line 543, Form T1436 (Capital Gains Worksheet) lines 2 and 3 "amounts reported on
lines 543 and 544 of Schedule 3": the amount the filer enters, a starting amount."""

SCHEDULE_3_LINE_544 = CATALOG.declare("schedule_3_line_544", Decimal, non_negative=True)
"""Schedule 3 line 544, Form T1436 (Capital Gains Worksheet) lines 2 and 3 "amounts reported on
lines 543 and 544 of Schedule 3": the amount the filer enters, a starting amount."""

SCHEDULE_3_LINES_543_AND_544_TOTAL = CATALOG.declare(
    "schedule_3_lines_543_and_544_total", Decimal, non_negative=True
)
"""Schedule 3 lines 543 and 544 added, Form T1436 (Capital Gains Worksheet) lines 2 and 3 "minus
any amounts reported on lines 543 and 544 of Schedule 3" and "cannot be more than the amounts from
lines 543 and 544 of Schedule 3": line 543 plus line 544."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_AMOUNT_A = CATALOG.declare(
    "capital_gains_deductions_1988_and_1989_amount_a", Decimal, non_negative=True
)
"""Amount (a), Form T1436 (Capital Gains Worksheet) line 2 "minus any amounts reported on lines 543
and 544 of Schedule 3 (if negative, enter "0") (a)": the line 2 total less the Schedule 3 sum, not
below 0; line 2 multiplies it by the printed 1.5."""

CAPITAL_GAINS_DEDUCTIONS_LINE_1 = CATALOG.declare(
    "capital_gains_deductions_line_1", Decimal, non_negative=True
)
"""Line 1 after its multiplier, Form T1436 (Capital Gains Worksheet) line 1 "For 1985 to 1987:
... x 2 = 1": the amount entered for 1985 to 1987 times the printed 2."""

CAPITAL_GAINS_DEDUCTIONS_LINE_2 = CATALOG.declare(
    "capital_gains_deductions_line_2", Decimal, non_negative=True
)
"""Line 2 after its multiplier, Form T1436 (Capital Gains Worksheet) line 2 "... (a) x 1.5 = 2":
amount (a) times the printed 1.5."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_AFTER_AMOUNT_A = CATALOG.declare(
    "capital_gains_deductions_1988_and_1989_after_amount_a", Decimal
)
"""Line 3 less amount (a), Form T1436 (Capital Gains Worksheet) line 3 "Total amounts from line
254 of your returns minus amount (a) above": the line 3 total less amount (a). The form prints no
floor on it, so it may be negative."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_LIMITED = CATALOG.declare(
    "capital_gains_deductions_1988_and_1989_limited", Decimal
)
"""Line 3 limited, Form T1436 (Capital Gains Worksheet) line 3 "(cannot be more than the amounts
from lines 543 and 544 of Schedule 3)": the lesser of line 3 less amount (a) and the Schedule 3
sum. Signed, as the form prints no floor on the difference."""

CAPITAL_GAINS_DEDUCTIONS_LINE_3 = CATALOG.declare("capital_gains_deductions_line_3", Decimal)
"""Line 3 after its multiplier, Form T1436 (Capital Gains Worksheet) line 3 "... x 1.3333 = 3":
the limited amount times the printed 1.3333. Signed, as the form prints no floor on line 3."""

CAPITAL_GAINS_DEDUCTIONS_LINE_4 = CATALOG.declare(
    "capital_gains_deductions_line_4", Decimal, non_negative=True
)
"""Line 4 after its multiplier, Form T1436 (Capital Gains Worksheet) line 4 "For 1990 to 1999: ...
x 1.3333 = 4": the amount entered for 1990 to 1999 times the printed 1.3333."""

CAPITAL_GAINS_DEDUCTIONS_LINE_5 = CATALOG.declare(
    "capital_gains_deductions_line_5", Decimal, non_negative=True
)
"""Line 5 after its multiplier, Form T1436 (Capital Gains Worksheet) line 5 "For 2000: ... x 1/IR
(1) = 5": the amount entered for 2000 divided by the 2000 inclusion rate, rounded half-up to the
cent once; 0 when the inclusion rate is 0, as the pre-1986 "1/(IR x 2)" row is."""

CAPITAL_GAINS_DEDUCTIONS_LINE_6 = CATALOG.declare(
    "capital_gains_deductions_line_6", Decimal, non_negative=True
)
"""Line 6 after its multiplier, Form T1436 (Capital Gains Worksheet) line 6 "For 2001 to 2024:
... x 2 = 6": the amount entered for 2001 to 2024 times the printed 2."""

CAPITAL_GAINS_DEDUCTIONS_CLAIMED_1985_TO_2024 = CATALOG.declare(
    "capital_gains_deductions_claimed_1985_to_2024", Decimal, non_negative=True
)
"""Total capital gains deductions claimed from 1985 to 2024, Form T1436 (Capital Gains Worksheet)
line 7 "Add lines 1 to 6.": the sum of lines 1 to 6 after their multipliers."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1986_TO_1994 = CATALOG.declare(
    "other_business_investment_loss_reductions_1986_to_1994", Decimal, non_negative=True
)
"""Other business investment loss reductions for 1986 to 1994, Form T1436 (Capital Gains
Worksheet) line 8: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1994_TO_1996 = CATALOG.declare(
    "other_business_investment_loss_reductions_1994_to_1996", Decimal, non_negative=True
)
"""Other business investment loss reductions for 1994 to 1996, Form T1436 (Capital Gains
Worksheet) line 9: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1997_TO_1999 = CATALOG.declare(
    "other_business_investment_loss_reductions_1997_to_1999", Decimal, non_negative=True
)
"""Other business investment loss reductions for 1997 to 1999, Form T1436 (Capital Gains
Worksheet) line 10: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_2000 = CATALOG.declare(
    "other_business_investment_loss_reductions_2000", Decimal, non_negative=True
)
"""Other business investment loss reductions for 2000, Form T1436 (Capital Gains Worksheet) line
11: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_2001_TO_2023 = CATALOG.declare(
    "other_business_investment_loss_reductions_2001_to_2023", Decimal, non_negative=True
)
"""Other business investment loss reductions for 2001 to 2023, Form T1436 (Capital Gains
Worksheet) line 12: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_2024 = CATALOG.declare(
    "other_business_investment_loss_reductions_2024", Decimal, non_negative=True
)
"""Other business investment loss reductions for 2024, Form T1436 (Capital Gains Worksheet) line
13: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1986_TO_2024 = CATALOG.declare(
    "other_business_investment_loss_reductions_1986_to_2024", Decimal, non_negative=True
)
"""Total other business investment loss reductions for 1986 to 2024, Form T1436 (Capital Gains
Worksheet) line 14 "Add lines 8 to 13.": the sum of the six reductions of earlier years."""

BUSINESS_INVESTMENT_LOSS_REDUCTION_AVAILABLE = CATALOG.declare(
    "business_investment_loss_reduction_available", Decimal
)
"""Business investment loss reduction available, Form T1436 (Capital Gains Worksheet) line 15 "Line
7 minus line 14": the capital gains deductions claimed less the other reductions. The line prints no
"(if negative, enter "0")", so the kind is signed."""

BUSINESS_INVESTMENT_LOSS = CATALOG.declare("business_investment_loss", Decimal, non_negative=True)
"""Business investment loss in 2025, Form T1436 line 16 and T1 line 43 gross, line 21699 "Enter
this amount on line 21699 of your return.": a starting amount."""

BUSINESS_INVESTMENT_LOSS_REDUCTION = CATALOG.declare("business_investment_loss_reduction", Decimal)
"""Business investment loss reduction, Form T1436 (Capital Gains Worksheet) line 17 "Enter whichever
is less: amount from line 15 or line 16. Enter this amount on line 17800 of Schedule 3.": the lesser
of the reduction available and the loss. The line prints no floor, so the kind is signed (negative
with line 15)."""

BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION = CATALOG.declare(
    "business_investment_loss_after_reduction", Decimal, non_negative=True
)
"""Business investment loss after the reduction, Form T1436 (Capital Gains Worksheet) line 18 "Line
16 minus line 17 Business investment loss reduction": never negative, as line 17 is at most line
16."""

ALLOWABLE_BUSINESS_INVESTMENT_LOSS = CATALOG.declare(
    "allowable_business_investment_loss", Decimal, non_negative=True
)
"""Allowable business investment loss, T1 line 43 and line 21700, Form T1436 line 20 "Line 18
multiplied by the percentage on line 19 Enter this amount on line 21700 of your return.": half
the loss after the reduction, a deduction from total income."""

SUPPORT_PAYMENTS_MADE_TOTAL = CATALOG.declare(
    "support_payments_made_total", Decimal, non_negative=True
)
"""Support payments made, total, T1 line 21999 "Line 21999: Total" under "Line 45: Support payments
made (go to canada.ca/taxes-support-payments)", Guide 5000-G "Enter on line 21999 of your return the
total amount of support payments that you paid under a court order or written agreement": the bound
that the line 22000 check is made against (`core/at_most`), a caller's amount carried as entered."""

SUPPORT_PAYMENTS_DEDUCTION = CATALOG.declare(
    "support_payments_deduction", Decimal, non_negative=True
)
"""Support payments deduction, T1 line 22000 "Line 22000: Allowable deduction" and "Enter on line
22000 of your return the deductible part of the support payments that you made.": the deductible
part, a caller's amount checked against `ca/support_payments_made_total` (line 21999) before the
sum reads it."""

SUPPORT_PAYMENTS_DEDUCTION_CHECKED = CATALOG.declare(
    "support_payments_deduction_checked", Decimal, non_negative=True
)
"""Support payments deduction after the check, T1 line 22000 "Enter on line 22000 of your return the
deductible part of the support payments that you made.": the deductible part is a part of the
total support paid on line 21999, so a line 22000 amount above line 21999 is refused (`core/at_most`
against `ca/support_payments_made_total`), not capped. The sum reads this amount."""

TOTAL_CARRYING_CHARGES = CATALOG.declare("total_carrying_charges", Decimal, non_negative=True)
"""Total carrying charges, Federal Worksheet "Line 22100 - Carrying charges, interest expenses,
and other expenses" line 1: a starting amount."""

TOTAL_INTEREST_EXPENSES = CATALOG.declare("total_interest_expenses", Decimal, non_negative=True)
"""Total interest expenses, Federal Worksheet "Line 22100 - Carrying charges, interest expenses,
and other expenses" line 2: a starting amount."""

TOTAL_OTHER_EXPENSES = CATALOG.declare("total_other_expenses", Decimal, non_negative=True)
"""Total other expenses, Federal Worksheet "Line 22100 - Carrying charges, interest expenses,
and other expenses" line 3: a starting amount."""

CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES = CATALOG.declare(
    "carrying_charges_interest_expenses_and_other_expenses", Decimal, non_negative=True
)
"""Carrying charges, interest expenses, and other expenses, T1 line 46 and line 22100: Federal
Worksheet "Line 22100 - Carrying charges, interest expenses, and other expenses" line 4 "Add
lines 1 to 3. Enter this amount on line 22100 of your return.", a deduction from total income."""

CPP_FIRST_ADDITIONAL_CONTRIBUTIONS = CATALOG.declare(
    "cpp_first_additional_contributions", Decimal, non_negative=True
)
"""First additional CPP contributions, Schedule 8 Part 3 line 12 "amount from line 7 multiplied
by 1% (maximum $678.00)": the required contributions on the employment income between the basic
exemption and the maximum pensionable earnings. Line 18 is "Amount from line 12"; Part 3b line 37
"If line 19 is positive or "0", enter the amount from line 18 at line 37 and line 43, and continue
at line 44." carries it into line 48 (Part 3a line 26 into line 28 when line 24 is positive).

Line 7 is "Line 5 minus line 6 (if negative, enter "0") (maximum $67,800)", the same earnings
as the base contributions'.
"""

CPP_SECOND_ADDITIONAL_CONTRIBUTIONS = CATALOG.declare(
    "cpp_second_additional_contributions", Decimal, non_negative=True
)
"""Second additional CPP contributions, Schedule 8 Part 3 line 22 "amount from line 4 multiplied
by 4% (maximum $396.00)": the required contributions on the employment income between the
maximum and the additional maximum pensionable earnings. Part 3b line 44 "If line 23 is positive
or "0", enter the amount from line 22 on line 44 and line 47, and continue at line 48." carries it
into line 48 (Part 3a line 27 "Amount from line 22 (if any)" into line 28 when line 24 is
positive).

Line 4 is "Line 2 minus line 3 (if negative, enter "0")": the earnings, at most the additional
maximum (line 2), less the maximum pensionable earnings (line 3).
"""

CPP_ENHANCED_CONTRIBUTIONS = CATALOG.declare(
    "cpp_enhanced_contributions", Decimal, non_negative=True
)
"""Enhanced CPP contributions, Schedule 8 Part 3a line 28 "Line 26 plus line 27 Enter this amount
(in dollars and cents) on line 22215 of your return.": the first and second additional
contributions together (lines 12 and 22).

It is the figure Part 3a carries to T1 line 22215 when line 24 is positive. The deduction from
total income is `schedule_8_cpp_enhanced_contributions_on_return`, which is this sum when line 24
is positive and Part 3b line 48 otherwise.
"""

EXPLORATION_AND_DEVELOPMENT_EXPENSES = CATALOG.declare(
    "exploration_and_development_expenses", Decimal, non_negative=True
)
"""Exploration and development expenses, T1 line 49 and line 22400 "Exploration and development
expenses (complete Form T1229)": a starting amount until CRA publishes a 2025 edition of Form
T1229 (the latest is 2023)."""

CLERGY_EMPLOYER_RESIDENCE_BENEFIT = CATALOG.declare(
    "clergy_employer_residence_benefit", Decimal, non_negative=True
)
"""Clergy employer residence benefit, Form T1223 Part C (A) "the value of this benefit (including
any allowance for eligible utilities) is shown as a taxable benefit in box 30 of your T4 slip": the
amount for a residence the employer provided, a starting amount taken from box 30. Line (C) adds
its checked amount, `ca/clergy_employer_residence_benefit_checked`, to the (B) amount."""

CLERGY_EMPLOYER_RESIDENCE_BENEFIT_CHECKED = CATALOG.declare(
    "clergy_employer_residence_benefit_checked", Decimal, non_negative=True
)
"""Clergy employer residence benefit after the check, Form T1223 Part C (A) "the value of this
benefit (including any allowance for eligible utilities) is shown as a taxable benefit in box 30 of
your T4 slip": `ca/clergy_employer_residence_benefit` when it is not more than
`ca/other_employment_income` (`core/at_most`), the amount on line 10400. Guide 5000-G "Member of
the clergy": "Report the amount from box 30 of your T4 slips on line 10400 of your return." Line (C)
adds this amount."""

CLERGY_QUALIFYING_EMPLOYMENT_INCOME = CATALOG.declare(
    "clergy_qualifying_employment_income", Decimal, non_negative=True
)
"""Income from qualifying employment, Form T1223 Part C line 1 "Income from qualifying employment
from all eligible employers (see note 1)": a starting amount, the income of all eligible employers
combined. Line 2 is one third of it and line 10 is not more than it."""

CLERGY_MONTHS_IN_QUALIFYING_EMPLOYMENT = CATALOG.declare(
    "clergy_months_in_qualifying_employment", int, non_negative=True
)
"""Number of months in qualifying employment, Form T1223 Part C line 3 "Number of months in
qualifying employment": a count, the months the filer gives. Line 4 multiplies it by $1,000."""

CLERGY_ACCOMMODATION_COST = CATALOG.declare("clergy_accommodation_cost", Decimal, non_negative=True)
"""Actual rent and eligible utilities, Form T1223 Part C line 6 "Actual rent and eligible utilities
paid or, if residence is owned, fair rental value including eligible utilities for the total period
in the year that the residence was owned or rented and you were in qualifying employment (see note 2
and note 3)": a starting amount, taken as the form takes it."""

CLERGY_OTHER_ACCOMMODATION_CLAIMS = CATALOG.declare(
    "clergy_other_accommodation_claims", Decimal, non_negative=True
)
"""All amounts claimed for the accommodation, Form T1223 Part C line 7 "All amounts claimed by you,
or any person, for the accommodation (see note 4)": a starting amount, including a spouse's or
common-law partner's claim. Line 8 subtracts its checked amount,
`ca/clergy_other_accommodation_claims_checked`, from line 6."""

CLERGY_OTHER_ACCOMMODATION_CLAIMS_CHECKED = CATALOG.declare(
    "clergy_other_accommodation_claims_checked", Decimal, non_negative=True
)
"""All amounts claimed for the accommodation after the check, Form T1223 Part C line 7 "All amounts
claimed by you, or any person, for the accommodation (see note 4)":
`ca/clergy_other_accommodation_claims` when it is not more than `ca/clergy_accommodation_cost`
(`core/at_most`), the amount on line 6.
Line 8 "Line 6 minus line 7 =" subtracts this amount. An amount above line 6 is an input error, not
capped: line 8 is not computed from it."""

CLERGY_RESIDENCE_PART_B_COMPLETED = CATALOG.declare(
    "clergy_residence_part_b_completed", int, non_negative=True
)
"""Form T1223 Part C (B) "If you owned or rented the residence that you occupied, complete the
following:": a derived count, 1 when line 3 "Number of months in qualifying employment", line 6
"Actual rent and eligible utilities paid ..." or line 7 "All amounts claimed by you, or any person,
for the accommodation" is more than 0, else 0 (only the (A) employer-provided residence is claimed).
Non-negative, as a count is never below zero."""

CLERGY_RESIDENCE_LINE_2 = CATALOG.declare("clergy_residence_line_2", Decimal, non_negative=True)
"""Form T1223 Part C line 2 "Amount from line 1 multiplied by 1/3": one third of the income from
qualifying employment, rounded half-up to the cent."""

CLERGY_RESIDENCE_MONTHS_AMOUNT = CATALOG.declare(
    "clergy_residence_months_amount", Decimal, non_negative=True
)
"""Form T1223 Part C line 4 "Line 3 multiplied by $1,000 (maximum $10,000)", before the maximum: the
months in qualifying employment times $1,000."""

CLERGY_RESIDENCE_LINE_4 = CATALOG.declare("clergy_residence_line_4", Decimal, non_negative=True)
"""Form T1223 Part C line 4 "Line 3 multiplied by $1,000 (maximum $10,000)": the months amount, not
more than the maximum of $10,000."""

CLERGY_RESIDENCE_LINE_5 = CATALOG.declare("clergy_residence_line_5", Decimal, non_negative=True)
"""Form T1223 Part C line 5 "Enter whichever is more: line 2 or line 4.": the greater of lines 2
and 4."""

CLERGY_RESIDENCE_LINE_8 = CATALOG.declare("clergy_residence_line_8", Decimal)
"""Form T1223 Part C line 8 "Line 6 minus line 7 =": the accommodation cost less the other claims.
The form prints no floor, so a negative line 8 passes through to line 9."""

CLERGY_RESIDENCE_LINE_9 = CATALOG.declare("clergy_residence_line_9", Decimal)
"""Form T1223 Part C line 9 "Enter whichever is less: Line 5 or line 8.": the lesser of lines 5 and
8, signed as the form prints it."""

CLERGY_RESIDENCE_LINE_10 = CATALOG.declare("clergy_residence_line_10", Decimal)
"""Form T1223 Part C line 10 "Enter whichever is less: Line 1 or line 9.": the (B) amount, the
lesser of the income from qualifying employment and line 9."""

CLERGY_RESIDENCE_TOTAL = CATALOG.declare("clergy_residence_total", Decimal)
"""Form T1223 Part C (C) "add amounts (A) and (B)": the employer residence benefit (A) plus the (B)
amount on line 10, not floored."""

CLERGY_RESIDENCE_TOTAL_LIMITED = CATALOG.declare("clergy_residence_total_limited", Decimal)
"""Form T1223 Part C (C) "The amount claimed for the clergy residence deduction cannot be more than
the income from qualifying employment on line 1.": the total, not more than line 1."""

CLERGY_RESIDENCE_DEDUCTION = CATALOG.declare(
    "clergy_residence_deduction", Decimal, non_negative=True
)
"""Clergy residence deduction, T1 line 51 and line 23100 "Clergy residence deduction (complete Form
T1223)", Form T1223 Part C "Enter this amount on line 23100 of your return.": the total of (A) and
(B), limited to line 1 when Part C (B) is completed. The Federal Worksheet "Line 45200 - Refundable
medical expense supplement" takes it off the employment income, as line 23100, and the alternative
minimum tax reads it as line 23100."""

OTHER_DEDUCTIONS = CATALOG.declare("other_deductions", Decimal, non_negative=True)
"""Other deductions, T1 line 52 and line 23200 "Other deductions": a starting amount, which
includes the RDSP income repayment (a starting amount of its own, Federal Worksheet for line
25000 line 7).

It excludes the split income, which Form T1206 Part 1 line 4 (`total_split_income`) adds to line
23200 as a part of its own.
"""

SPLIT_INCOME_DIVIDENDS = CATALOG.declare("split_income_dividends", Decimal, non_negative=True)
"""Split income dividends, Form T1206 Part 1 line 1 (68330) "Part of the taxable amount of
dividends (eligible and other than eligible) described in the information section received from
taxable Canadian corporations": a starting amount, the filer's classification under the form's
pages 1 to 4. Line 1 reads the checked kind, `ca/split_income_dividends_checked`, not this
amount."""

SPLIT_INCOME_DIVIDENDS_TOTAL = CATALOG.declare(
    "split_income_dividends_total", Decimal, non_negative=True
)
"""Split income dividends with the T1206 page 6 amount, Form T1206 Part 1 line 1 (68330): the
filer's `ca/split_income_dividends` plus Form T1206 page 6 "In addition, enter this amount on
lines 1 and 2 as indicated in Part 1 on page 7", the amount deemed to be a dividend of a filer
under 18 (`ca/t1206_under_18_dividend_amount`, 0 for 18 or older). The check reads this amount."""

SPLIT_INCOME_DIVIDENDS_CHECKED = CATALOG.declare(
    "split_income_dividends_checked", Decimal, non_negative=True
)
"""Split income dividends after the check, Form T1206 Part 1 line 1 (68330) "Part of the taxable
amount of dividends (eligible and other than eligible) described in the information section
received from taxable Canadian corporations": `ca/split_income_dividends_total` when it is not
more than `ca/taxable_dividends` (`core/at_most`), the taxable amount of dividends on line 12000 of
the return. An amount above it is refused, not capped. Line 4 and the credit on lines 1 and 2 read
this amount."""

SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE = CATALOG.declare(
    "split_income_dividends_other_than_eligible", Decimal, non_negative=True
)
"""Split income dividends other than eligible, Form T1206 Part 1 line 2 (68340) "Part of the
taxable amount of dividends other than eligible dividends, included on line 1, from taxable
Canadian corporations": a starting amount. Line 2 reads the checked kind,
`ca/split_income_dividends_other_than_eligible_checked`, not this amount."""

SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_TOTAL = CATALOG.declare(
    "split_income_dividends_other_than_eligible_total", Decimal, non_negative=True
)
"""Split income dividends other than eligible with the T1206 page 6 amount, Form T1206 Part 1 line
2 (68340): the filer's `ca/split_income_dividends_other_than_eligible` plus the amount deemed to
be a dividend (other than eligible dividend) of a filer under 18
(`ca/t1206_under_18_dividend_amount`, 0 for 18 or older). The check reads this amount."""

SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_PART_OF_LINE_1 = CATALOG.declare(
    "split_income_dividends_other_than_eligible_part_of_line_1", Decimal, non_negative=True
)
"""Split income dividends other than eligible, part of line 1, Form T1206 Part 1 line 2 (68340)
"Part of the taxable amount of dividends other than eligible dividends, included on line 1, from
taxable Canadian corporations": `ca/split_income_dividends_other_than_eligible_total` when it is
not more than `ca/split_income_dividends_checked` (`core/at_most`), line 1 as checked. An amount
above it is refused, not capped."""

SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED = CATALOG.declare(
    "split_income_dividends_other_than_eligible_checked", Decimal, non_negative=True
)
"""Split income dividends other than eligible after the check, Form T1206 Part 1 line 2 (68340)
"Part of the taxable amount of dividends other than eligible dividends, included on line 1, from
taxable Canadian corporations": `ca/split_income_dividends_other_than_eligible_part_of_line_1` when
it is not more than `ca/taxable_dividends_other_than_eligible` (`core/at_most`), the amount on line
12010 of the return. An amount above it is refused, not capped. The federal and Ontario
credits on split income read this amount."""

OTHER_SPLIT_INCOME = CATALOG.declare("other_split_income", Decimal, non_negative=True)
"""Other split income, Form T1206 Part 1 line 3 "All other split income (see "Split income" on page
1)": a starting amount. Line 3 is checked as `ca/other_split_income_checked`, which line 4 reads;
the bound of `ca/split_income_from_foreign_sources_part_of_line_3` is `ca/other_split_income_total`,
which holds it as entered."""

OTHER_SPLIT_INCOME_TOTAL = CATALOG.declare("other_split_income_total", Decimal, non_negative=True)
"""Other split income with the T1206 page 6 amount, Form T1206 Part 1 line 3 "All other split
income (see "Split income" on page 1)": the filer's `ca/other_split_income` plus Form T1206 page 6
"multiply the capital gain for each disposition reported on lines A, B, C and F by 50% and enter
the total on line 3 in Part 1 on page 7" (`ca/t1206_part_1_line_3_amount`, 0 under 18). The
checks of line 3 and of Part 2 line 68370 read this amount."""

OTHER_SPLIT_INCOME_OWN_CHECKED = CATALOG.declare(
    "other_split_income_own_checked", Decimal, non_negative=True
)
"""The filer's own other split income after the check, Form T1206 Part 1 line 3 "All other split
income (see "Split income" on page 1)": `ca/other_split_income` when it is not more than
`ca/income_before_losses` (`core/at_most`), the income before losses, the T1 income lines of Step 2
with each loss counted as 0, which the whole split income is part of. An amount above it is an
input error, not capped. Form T1206 and Guide 5000-G (line 23200, page 24) were read and print no
limit on line 3, so the bound is the part-over-whole one."""

OTHER_SPLIT_INCOME_CHECKED = CATALOG.declare(
    "other_split_income_checked", Decimal, non_negative=True
)
"""Other split income, Form T1206 Part 1 line 3 "All other split income (see "Split income" on page
1)": the checked own figure (`ca/other_split_income_own_checked`) plus the Part 1 line 3 amount of
page 6 (`ca/t1206_part_1_line_3_amount`, 50% of line G, computed by the T1206 itself and not bounded
by the income before losses, so a filer whose share losses offset line G is not refused). Line 4
reads this amount."""

SPLIT_INCOME_FROM_FOREIGN_SOURCES = CATALOG.declare(
    "split_income_from_foreign_sources", Decimal, non_negative=True
)
"""Split income from foreign sources, Form T1206 Part 2 line 68370 "Part of the amount on line 3
that is from foreign sources": a starting amount. Line 23 reads the checked kind,
`ca/split_income_from_foreign_sources_checked`, not this amount."""

SPLIT_INCOME_FROM_FOREIGN_SOURCES_PART_OF_LINE_3 = CATALOG.declare(
    "split_income_from_foreign_sources_part_of_line_3", Decimal, non_negative=True
)
"""Split income from foreign sources, part of line 3, Form T1206 Part 2 line 68370 "Part of the
amount on line 3 that is from foreign sources": `ca/split_income_from_foreign_sources` when it is
not more than `ca/other_split_income_total` (`core/at_most`), line 3 as the bound. An amount above
it is refused, not capped."""

SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED = CATALOG.declare(
    "split_income_from_foreign_sources_checked", Decimal, non_negative=True
)
"""Split income from foreign sources after the check, Form T1206 Part 2 line 68370 "Part of the
amount on line 3 that is from foreign sources" over "Total income from foreign sources" 68380:
`ca/split_income_from_foreign_sources_part_of_line_3` when it is not more than
`ca/total_income_from_foreign_sources` (`core/at_most`). The reading is the form's own structure:
the numerator of a share against its denominator. An amount above it is refused, not capped. Line
23 reads this amount as the numerator."""

TOTAL_INCOME_FROM_FOREIGN_SOURCES = CATALOG.declare(
    "total_income_from_foreign_sources", Decimal, non_negative=True
)
"""Total income from foreign sources, Form T1206 Part 2 line 68380 "Total income from foreign
sources": a starting amount. It is the bound of the checked 68370 and of the checked non-business
total, and line 23 reads it as the denominator as it is, not a checked kind."""

SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES = CATALOG.declare(
    "split_income_non_business_from_foreign_sources", Decimal, non_negative=True
)
"""Non-business part of the split income from foreign sources, Form T1206 Part 3 line 49 "Part of
the amount from line 68370 on page 8 that is non-business income": a starting amount. Line 49
reads the checked kind, `ca/split_income_non_business_from_foreign_sources_checked`, not this
amount."""

SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_PART_OF_68370 = CATALOG.declare(
    "split_income_non_business_from_foreign_sources_part_of_68370", Decimal, non_negative=True
)
"""Non-business part of the split income from foreign sources, part of line 68370, Form T1206 Part
3 line 49 "Part of the amount from line 68370 on page 8 that is non-business income":
`ca/split_income_non_business_from_foreign_sources` when it is not more than
`ca/split_income_from_foreign_sources_checked` (`core/at_most`), 68370 as checked. The reading is
the form's own structure: the part of 68370 is the numerator of a share against 68370. An amount
above it is refused, not capped."""

TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES = CATALOG.declare(
    "total_non_business_income_from_foreign_sources", Decimal, non_negative=True
)
"""Non-business part of the total income from foreign sources, Form T1206 Part 3 line 49 "Part of
the amount from line 68380 on page 8 that is non-business income": a starting amount. Line 49
reads the checked kind, `ca/total_non_business_income_from_foreign_sources_checked`, not this
amount."""

TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED = CATALOG.declare(
    "total_non_business_income_from_foreign_sources_checked", Decimal, non_negative=True
)
"""Non-business part of the total income from foreign sources after the check, Form T1206 Part 3
line 49 "Part of the amount from line 68380 on page 8 that is non-business income":
`ca/total_non_business_income_from_foreign_sources` when it is not more than
`ca/total_income_from_foreign_sources` (`core/at_most`), 68380 as the bound. An amount above it is
refused, not capped. Line 49 reads this amount as the denominator."""

SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED = CATALOG.declare(
    "split_income_non_business_from_foreign_sources_checked", Decimal, non_negative=True
)
"""Non-business part of the split income from foreign sources after the check, Form T1206 Part 3
line 49 "Part of the amount from line 68370 on page 8 that is non-business income" over "Part of
the amount from line 68380 on page 8 that is non-business income":
`ca/split_income_non_business_from_foreign_sources_part_of_68370` when it is not more than
`ca/total_non_business_income_from_foreign_sources_checked` (`core/at_most`). The reading is the
form's own structure: the numerator of a share against its denominator. An amount above it is
refused, not capped. Line 49 reads this amount as the numerator."""

CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS = CATALOG.declare(
    "cpp_t4_base_and_first_additional_contributions", Decimal, non_negative=True
)
"""Total actual base and first additional contributions, Schedule 8 Part 3 line 8 and Form RC381
Part 3 line 19, line 50340 "Total actual base and first additional contributions on CPP pensionable
earnings from box 16 of all of your T4 slips": the amount the filer enters from the T4 slips, a
starting amount."""

CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS = CATALOG.declare(
    "cpp_t4_second_additional_contributions", Decimal, non_negative=True
)
"""Total actual second additional contributions, Schedule 8 Part 3 line 21 and line 50341 "Total
actual second additional contributions on CPP pensionable earnings from box 16A of all of your T4
slips": the amount the filer enters from the T4 slips, a starting amount.
"""

T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT = CATALOG.declare(
    "t4_cpp_pensionable_earnings_slip_limit", Decimal, non_negative=True
)
"""CPP pensionable earnings the T4 slips can show, not a form line: the count of slips with CPP
pensionable earnings (`ca/t4_cpp_slip_count`) times the "(maximum $81,200 per slip)" printed on
Schedule 8 Part 3 line 1 and Form RC381 Part 3 line 1, line 50339. The bound of
`ca/t4_cpp_pensionable_earnings_outside_quebec`; the form prints no total bound."""

T4_CPP_PENSIONABLE_EARNINGS_SLIP_CHECKED = CATALOG.declare(
    "t4_cpp_pensionable_earnings_slip_checked", Decimal, non_negative=True
)
"""Total CPP pensionable earnings from box 26 of all of your T4 slips where the province of
employment is not Quebec, Schedule 8 Part 3 line 1 and Form RC381 Part 3 line 1, line 50339,
checked: the amount of `ca/t4_cpp_pensionable_earnings_outside_quebec` when it is not more than
`ca/t4_cpp_pensionable_earnings_slip_limit` (`core/at_most`). An amount above the limit is an input
error, not capped. Nothing on the return reads this amount."""

T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT = CATALOG.declare(
    "t4_qpp_pensionable_earnings_slip_limit", Decimal, non_negative=True
)
"""QPP pensionable earnings the T4 slips can show, not a form line: the count of slips with QPP
pensionable earnings (`ca/t4_qpp_slip_count`) times the "(maximum $81,200 per slip)" printed on Form
RC381 Part 3 line 2, line 50329. The bound of `ca/t4_qpp_pensionable_earnings_in_quebec`; the form
prints no total bound."""

T4_QPP_PENSIONABLE_EARNINGS_SLIP_CHECKED = CATALOG.declare(
    "t4_qpp_pensionable_earnings_slip_checked", Decimal, non_negative=True
)
"""Total QPP pensionable earnings from box 26 of all of your T4 slips where the province of
employment is Quebec, Form RC381 Part 3 line 2 and line 50329, checked: the amount of
`ca/t4_qpp_pensionable_earnings_in_quebec` when it is not more than
`ca/t4_qpp_pensionable_earnings_slip_limit` (`core/at_most`). An amount above the limit is an input
error, not capped. Nothing on the return reads this amount."""

SCHEDULE_8_INSTANCES = RecordListKind.declare(CATALOG, "schedule_8_instances", fields=())
"""Copies of Schedule 8, Canada Pension Plan contributions and overpayment, one record for each
copy of the form the return carries (none or one): a record has no fields, because every figure the
form reads is a starting amount of the return. The form `ca/schedule_8` runs once for each record;
the return reads its lines through totals, which are 0 with no record. A field is not an artifact
of the return."""

RC381_INSTANCES = RecordListKind.declare(CATALOG, "rc381_instances", fields=())
"""Copies of Form RC381, Inter-Provincial Calculation for CPP and QPP Contributions and
Overpayments, one record for each copy of the form the return carries (none or one): a record has
no fields, because every figure the form reads is a starting amount of the return. The form
`ca/rc381` runs once for each record; the return reads its results through totals, which are 0
with no record. The return carries Schedule 8 or Form RC381, not both."""

T929_INSTANCES = RecordListKind.declare(CATALOG, "t929_instances", fields=())
"""Copies of Form T929, Disability Supports Deduction, one record for each copy of the form the
return carries (none or one): a record has no fields, because every figure the form takes is a
manifest input. The form `ca/t929` runs once for each record; the return reads its line 12 through
a total, which is 0 with no record. A field is not an artifact of the return."""


CPP_ACTUAL_BASE_CONTRIBUTIONS = CATALOG.declare(
    "cpp_actual_base_contributions", Decimal, non_negative=True
)
"""Actual base contributions on CPP pensionable earnings, Schedule 8 Part 3 line 9 "amount from
line 8 multiplied by 83.1933% =": the share of the T4 base and first additional contributions that
is the base contributions, to the cent. Line 14 is "Amount from line 9"."""

CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS = CATALOG.declare(
    "cpp_actual_first_additional_contributions", Decimal, non_negative=True
)
"""Actual first additional contributions on CPP pensionable earnings, Schedule 8 Part 3 line 10
"Line 8 minus line 9 =": the rest of the T4 base and first additional contributions. Line 17 is
"Amount from line 10"."""

CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS = CATALOG.declare(
    "cpp_required_base_and_first_additional_contributions", Decimal, non_negative=True
)
"""Required base and first additional contributions on pensionable earnings, Schedule 8 Part 3
line 13 "Line 11 plus line 12 =": the required base and first additional contributions on the
employment income, the sum of the two required tiers."""

CPP_BASE_CONTRIBUTIONS_DIFFERENCE = CATALOG.declare("cpp_base_contributions_difference", Decimal)
"""Base contributions difference, Schedule 8 Part 3 line 16 "Line 14 minus line 15 (if negative,
show in brackets) =": the actual base contributions (line 14, "Amount from line 9") less the
required base contributions (line 15, "Amount from line 11"). A negative amount is a shortfall."""

CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE = CATALOG.declare(
    "cpp_first_additional_contributions_difference", Decimal
)
"""First additional contributions difference, Schedule 8 Part 3 line 19 "Line 17 minus line 18 (if
negative, show in brackets) =": the actual first additional contributions (line 17, "Amount from
line 10") less the required first additional contributions (line 18, "Amount from line 12")."""

CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE = CATALOG.declare(
    "cpp_base_and_first_additional_contributions_difference", Decimal
)
"""Base and first additional contributions difference, Schedule 8 Part 3 line 20 "Line 16 plus
line 19 (if negative, show in brackets) =": the line 16 and line 19 differences together."""

CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE = CATALOG.declare(
    "cpp_second_additional_contributions_difference", Decimal
)
"""Second additional contributions difference, Schedule 8 Part 3 line 23 "Line 21 minus line 22
(if negative, show in brackets) =": the actual second additional contributions (line 21, the T4
box 16A total) less the required second additional contributions (line 22)."""

CPP_CONTRIBUTIONS_DIFFERENCE = CATALOG.declare("cpp_contributions_difference", Decimal)
"""Contributions difference, Schedule 8 Part 3 line 24 "Line 20 plus line 23 (if negative, show in
brackets) =": the total of the contributions deducted above (positive) or below (negative) the
required ones. When it is positive, Part 3a line 29 "Enter the amount from line 24." carries it to
line 44800 of the return, the CPP overpayment."""

CPP_MAXIMUM_PENSIONABLE_EARNINGS = CATALOG.declare(
    "cpp_maximum_pensionable_earnings", Decimal, non_negative=True
)
"""Maximum pensionable earnings, Schedule 8 Part 2 line B "Your maximum pensionable earnings for
2025 (maximum $71,300)": the "Maximum pensionable earnings" column of the "Monthly proration for
2025" table, in the row for the months in box A. Part 4 line 5 is "Amount from line B of Part 2"."""

CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM = CATALOG.declare(
    "cpp_second_additional_earnings_maximum", Decimal, non_negative=True
)
"""Maximum amount subject to second additional contributions, Schedule 8 Part 2 line C "Your
maximum amount subject to second additional contributions for 2025 (maximum $9,900)": the column of
that name in the table, in the row for the months in box A. Nothing on the return reads it: Part 4
line 12 takes its $9,900 limit from the rate dataset, and Part 5 is wired separately."""

CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS = CATALOG.declare(
    "cpp_additional_maximum_pensionable_earnings", Decimal, non_negative=True
)
"""Additional maximum pensionable earnings, Schedule 8 Part 2 line D "Your additional maximum
pensionable earnings for 2025 (maximum $81,200)": the "Additional maximum pensionable earnings"
column of the table, in the row for the months in box A. Part 4 line 4 is the lesser of it and
line 3."""

CPP_BASIC_EXEMPTION = CATALOG.declare("cpp_basic_exemption", Decimal, non_negative=True)
"""Basic exemption, Schedule 8 Part 2 line E "Your maximum basic exemption for 2025 (maximum
$3,500)": the "Maximum basic exemption" column of the table, in the row for the months in box A.
Part 4 line 8 is "Amount from line E of Part 2"."""

PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS = CATALOG.declare(
    "pensionable_net_self_employment_earnings", Decimal
)
"""Pensionable net self-employment earnings, Schedule 8 Part 4 line 1 "amount from line 12200 of
your return plus line 27 of your return": the net partnership income plus the net self-employment
income. Negative when line 27 is a loss, as line 1 prints no floor; line 3 is.

Note 1 ("self-employment earnings should be prorated according to the number of months ... that the
conditions a) to g) applied") gives no formula and is not modelled.
"""

CPP_PENSIONABLE_EARNINGS = CATALOG.declare("cpp_pensionable_earnings", Decimal, non_negative=True)
"""CPP pensionable earnings, Schedule 8 Part 4 line 3 "Line 1 plus line 2 (if negative, enter "0")":
the pensionable net self-employment earnings plus the CPT20 earnings (line 2), not below zero."""

CPP_PENSIONABLE_EARNINGS_UP_TO_ADDITIONAL_MAXIMUM = CATALOG.declare(
    "cpp_pensionable_earnings_up_to_additional_maximum", Decimal, non_negative=True
)
"""Pensionable earnings up to the additional maximum, Schedule 8 Part 4 line 4 "Enter whichever is
less: amount from line D of Part 2 or line 3.": the lesser of the additional maximum pensionable
earnings and the pensionable earnings."""

CPP_EARNINGS_SUBJECT_TO_SECOND_ADDITIONAL = CATALOG.declare(
    "cpp_earnings_subject_to_second_additional", Decimal, non_negative=True
)
"""Earnings subject to second additional contributions, Schedule 8 Part 4 line 6 "Line 4 minus line
5 (if negative, enter "0")": line 4 less the maximum pensionable earnings (line 5, "Amount from
line B of Part 2"), not below zero."""

CPP_EARNINGS_UP_TO_MAXIMUM = CATALOG.declare(
    "cpp_earnings_up_to_maximum", Decimal, non_negative=True
)
"""Earnings up to the maximum pensionable earnings, Schedule 8 Part 4 line 7 "Line 4 minus line 6
(if negative, enter "0")": line 4 less the earnings subject to second additional contributions,
not below zero."""

CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL = CATALOG.declare(
    "cpp_earnings_subject_to_base_and_first_additional", Decimal, non_negative=True
)
"""Earnings subject to base and first additional contributions, Schedule 8 Part 4 line 9 "Line 7
minus line 8 (if negative, enter "0") (maximum $67,800)": line 7 less the basic exemption (line 8,
"Amount from line E of Part 2"), not below zero."""

SELF_EMPLOYED_CPP_BASE_CONTRIBUTIONS = CATALOG.declare(
    "self_employed_cpp_base_contributions", Decimal, non_negative=True
)
"""Required base contributions on CPP pensionable earnings, Schedule 8 Part 4 line 10 "amount from
line 9 multiplied by 9.9% (maximum $6,712.20)": a self-employed person pays both halves, so twice
the employee's 4.95%."""

SELF_EMPLOYED_CPP_FIRST_ADDITIONAL_CONTRIBUTIONS = CATALOG.declare(
    "self_employed_cpp_first_additional_contributions", Decimal, non_negative=True
)
"""Required first additional contributions on CPP pensionable earnings, Schedule 8 Part 4 line 11
"amount from line 9 multiplied by 2% (maximum $1,356.00)": twice the employee's 1%."""

SELF_EMPLOYED_CPP_SECOND_ADDITIONAL_CONTRIBUTIONS = CATALOG.declare(
    "self_employed_cpp_second_additional_contributions", Decimal, non_negative=True
)
"""Required second additional contributions on CPP pensionable earnings, Schedule 8 Part 4 line 12
"amount from line 6 multiplied by 8% (maximum $792.00)": twice the employee's 4%, on the earnings
of line 6, which Part 2 line C ($9,900 for 12 months) bounds."""

SELF_EMPLOYED_CPP_ENHANCED_CONTRIBUTIONS = CATALOG.declare(
    "self_employed_cpp_enhanced_contributions", Decimal, non_negative=True
)
"""Enhanced contributions on self-employment income, Schedule 8 Part 4 line 13 "Line 11 plus line
12": the first and second additional contributions together; line 16 is "Amount from line 13"."""

SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE = CATALOG.declare(
    "self_employed_cpp_contributions_payable", Decimal, non_negative=True
)
"""CPP contributions payable on self-employment income and other earnings, Schedule 8 Part 4 line
14 "Line 10 plus line 13 Enter this amount (in dollars and cents) on line 42100 of your return.":
the base and enhanced contributions together."""

SELF_EMPLOYED_CPP_BASE_CREDIT = CATALOG.declare(
    "self_employed_cpp_base_credit", Decimal, non_negative=True
)
"""Base CPP contributions on self-employment income and other earnings, Schedule 8 Part 4 line 15
"amount from line 10 multiplied by 50%" ("Enter the result of the following calculation (in dollars
and cents) on line 31000 of your return"): the employee's half of the base contributions, which is
the credit."""

SELF_EMPLOYED_CPP_DEDUCTION = CATALOG.declare(
    "self_employed_cpp_deduction", Decimal, non_negative=True
)
"""Deduction for CPP contributions on self-employment income and other earnings, Schedule 8 Part 4
line 17 "Line 15 plus line 16 Enter this amount (in dollars and cents) on line 22200 of your
return.": the employer's half of the base contributions (line 15) plus the enhanced contributions
(line 16, "Amount from line 13")."""

CPP_DEDUCTION_ON_SELF_EMPLOYMENT = CATALOG.declare(
    "cpp_deduction_on_self_employment", Decimal, non_negative=True
)
"""Deduction for CPP contributions on self-employment income and other earnings, T1 line 47 and
line 22200 "Deduction for CPP or QPP contributions on self-employment income and other earnings
(complete Schedule 8 or Form RC381, whichever applies)": Schedule 8 Part 4 line 17, entered once
for each Part 4 completed (1 or 0), a deduction from total income."""

EI_EXCLUDED_SLIP_NET_INCOME = CATALOG.declare("ei_excluded_slip_net_income", Decimal)
"""Net income (or net loss) reported for a T4 slip with EI premiums in box 18, Schedule 13 line 1
"If you received a T4 slip for self-employment income with EI premiums in box 18, do not include any
net income (or net loss) reported on lines 13500, 13700, 13900, 14100, and 14300 of your return for
that slip (Note 1)": a field of each record of the slips, taken as the form takes it, on whichever
of those lines the slip was reported. A net loss is negative, so the kind is signed."""

EI_EXCLUDED_SLIPS = RecordListKind.declare(
    CATALOG,
    "ei_excluded_slips",
    fields=(EI_EXCLUDED_SLIP_NET_INCOME,),
)
"""T4 slips with EI premiums in box 18, Schedule 13 line 1 "If you received a T4 slip for
self-employment income with EI premiums in box 18, do not include any net income (or net loss)
reported on lines 13500, 13700, 13900, 14100, and 14300 of your return for that slip (Note 1)": a
starting list with one record for each such slip, holding the net income (or net loss) reported for
it. Possibly empty."""

EI_EXCLUDED_SLIPS_NET_INCOME = CATALOG.declare("ei_excluded_slips_net_income", Decimal)
"""Net income of the T4 slips with EI premiums in box 18, Schedule 13 line 1 "do not include any net
income (or net loss) reported on lines 13500, 13700, 13900, 14100, and 14300 of your return for that
slip (Note 1)": the net income (or net loss) of every such slip, added. It may be a loss, so the
kind is signed."""

EI_SELF_EMPLOYMENT_BEFORE_SLIPS = CATALOG.declare("ei_self_employment_before_slips", Decimal)
"""Schedule 13 line 1 before the slips "Enter the total amount from line 1 1 plus line 27 of your
return": the net partnership income (T1 line 11, line 12200) plus the net self-employment income.
The form text reads "line 1 1", taken as line 11; to be confirmed. It stands before the exclusion of
the slips and the "(if negative, enter "0")" floor of the finished line 1, so the kind is signed."""

EI_SELF_EMPLOYMENT_EARNINGS = CATALOG.declare(
    "ei_self_employment_earnings", Decimal, non_negative=True
)
"""Self-employment earnings for EI, Schedule 13 line 1 "Enter the total amount from line 1 1 plus
line 27 of your return. If you received a T4 slip for self-employment income with EI premiums in box
18, do not include any net income (or net loss) reported on lines 13500, 13700, 13900, 14100, and
14300 of your return for that slip (Note 1) (if negative, enter "0")": the net partnership income
plus the net self-employment income, less the net income of those slips, not below zero."""

EI_NET_SELF_EMPLOYMENT_INCOME = CATALOG.declare(
    "ei_net_self_employment_income", Decimal, non_negative=True
)
"""Net self-employment income for EI, Schedule 13 line 4 "Add lines 1 to 3. Net self-employment
income": line 1, the earnings from a controlled corporation (line 2) and the tax-exempt
self-employment income (line 3)."""

EI_MAXIMUM_INSURABLE_EARNINGS = CATALOG.declare(
    "ei_maximum_insurable_earnings", Decimal, non_negative=True
)
"""Maximum insurable earnings, Schedule 13 line 5 "Maximum insurable earnings 65,700.00": the
printed figure, as an artifact of the same name."""

EI_INSURABLE_EARNINGS_REMAINING = CATALOG.declare(
    "ei_insurable_earnings_remaining", Decimal, non_negative=True
)
"""Insurable earnings remaining, Schedule 13 line 7 "Line 5 minus line 6 (if negative, enter "0")":
the maximum insurable earnings less the EI insurable earnings already on T4 slips, not below
zero."""

EI_EARNINGS_SUBJECT_TO_PREMIUM = CATALOG.declare(
    "ei_earnings_subject_to_premium", Decimal, non_negative=True
)
"""Earnings subject to EI premiums, Schedule 13 line 8 "Enter whichever is less: amount from line 4
or line 7.": the lesser of the net self-employment income and the insurable earnings remaining."""

SELF_EMPLOYED_EI_PREMIUMS = CATALOG.declare("self_employed_ei_premiums", Decimal, non_negative=True)
"""EI premiums payable on self-employment and other eligible earnings, Schedule 13 line 9
"Residents of a province or territory other than Quebec: Line 9: Amount from line 8 multiplied by
1.64% (maximum $1,077.48)". Line 10, for Quebec residents, is not triggered."""

T929_NET_BUSINESS_INCOME = CATALOG.declare("t929_net_business_income", Decimal, non_negative=True)
"""Net self-employment income from business statements, Form T929 Step 2 line 4 "Enter your earned
income" and its definition "net self-employment income, either alone or as an active partner (not
including losses)": the positive net income of each Form T2125 statement, added, so a loss counts
0."""

T929_NET_FARMING_INCOME = CATALOG.declare("t929_net_farming_income", Decimal, non_negative=True)
"""Net self-employment income from farming statements, Form T929 Step 2 line 4 and its definition
"net self-employment income, either alone or as an active partner (not including losses)": the
positive net income of each Form T2042 statement, added, so a loss counts 0."""

T929_NET_FISHING_INCOME = CATALOG.declare("t929_net_fishing_income", Decimal, non_negative=True)
"""Net self-employment income from fishing statements, Form T929 Step 2 line 4 and its definition
"net self-employment income, either alone or as an active partner (not including losses)": the
positive net income of each Form T2121 statement, added, so a loss counts 0."""

T929_NET_PROFESSIONAL_INCOME = CATALOG.declare(
    "t929_net_professional_income", Decimal, non_negative=True
)
"""Net self-employment income from professional income, Form T929 Step 2 line 4 and its definition
"net self-employment income, either alone or as an active partner (not including losses)": the
professional income of T1 line 13700, not below zero, so a loss counts 0."""

T929_NET_COMMISSION_INCOME = CATALOG.declare(
    "t929_net_commission_income", Decimal, non_negative=True
)
"""Net self-employment income from commission income, Form T929 Step 2 line 4 and its definition
"net self-employment income, either alone or as an active partner (not including losses)": the
commission income of T1 line 13900, not below zero, so a loss counts 0."""

T929_LINE_3 = CATALOG.declare("t929_line_3", Decimal)
"""Net disability supports expenses, Form T929 Step 1 line 3 "Subtract line 2 from line 1. This
amount is your net disability supports expenses": line 1 less line 2, the amounts paid less the
amounts reimbursed. The form does not floor it, so the kind is signed."""

T929_LINE_4 = CATALOG.declare("t929_line_4", Decimal, non_negative=True)
"""Earned income, Form T929 Step 2 line 4 "Enter your earned income": the total of the items of the
definition of earned income, employment income (T1 lines 10100 and 10400), the taxable part of
scholarships (T1 line 13010), the net self-employment income of the four kinds above, and the
other items of the definition the filer enters."""

T929_LINE_7 = CATALOG.declare("t929_line_7", Decimal, non_negative=True)
"""Net income above earned income, Form T929 Step 2 line 7 "Line 5 minus line 6 (if negative, enter
"0")": the net income with no claim (line 5) less the earned income of line 4 (line 6), not below
zero."""

T929_LINE_9 = CATALOG.declare("t929_line_9", Decimal, non_negative=True)
"""Weeks at the weekly amount, Form T929 Step 2 line 9 "Line 8 multiplied by $375": the weeks
attended (line 8) times $375, rounded half-up to the cent."""

T929_LINE_10 = CATALOG.declare("t929_line_10", Decimal, non_negative=True)
"""Amount for attending an educational institution, Form T929 Step 2 line 10 "Enter the amount from
line 7 or line 9, whichever is less. (maximum $15,000)": the lesser of line 7 and line 9, not more
than the $15,000 maximum."""

T929_LINE_11 = CATALOG.declare("t929_line_11", Decimal, non_negative=True)
"""Earned income and attendance amount, Form T929 Step 2 line 11 "Add lines 4 and 10": line 4 plus
line 10."""

DISABILITY_SUPPORTS_DEDUCTION = CATALOG.declare(
    "disability_supports_deduction", Decimal, non_negative=True
)
"""Disability supports deduction, T1 line 21500 "Disability supports deduction (complete Form
T929)": Form T929 line 12 "Enter the amount from line 3 or line 11, whichever is less", which the
form says to enter "on line 21500 of your tax return". The Federal Worksheet "Line 45200 -
Refundable medical expense supplement" line 9 "Amount from line 21500 of your return" reads it, and
so does Part 1 of the alternative minimum tax. The return totals the form's line 12 and adds it to
line 23300."""

DEDUCTIONS_FROM_TOTAL_INCOME = CATALOG.declare(
    "deductions_from_total_income", Decimal, non_negative=True
)
"""Total deductions, T1 line 23300 "Add lines 35 to 52": the sum of the deductions from total
income, here, in line order, the RPP deduction (line 20700), the RRSP deduction (line 20800), the
FHSA deduction (line 20805), the elected split-pension deduction (line 21000), union dues (line
21200), the UCCB repayment (line 21300), the child care expenses (line 21400), the disability
supports deduction (line 21500), the allowable business investment loss (line 21700), the moving
expenses of Form T1-M (line 21900), the deductible support payments (line 22000), carrying charges,
interest expenses and other expenses (line 22100), the CPP contributions on self-employment income
(line 22200), the enhanced CPP contributions (line 22215), exploration and development expenses
(line 22400), other employment expenses (line 22900), the clergy residence deduction (line 23100)
and other deductions (line 23200)."""

NET_INCOME_BEFORE_ADJUSTMENTS = CATALOG.declare("net_income_before_adjustments", Decimal)
"""Net income before adjustments, T1 line 54 and line 23400 "Line 34 minus line 53 (if negative,
show in brackets)": total income less total deductions, not floored, so the kind is signed."""

NET_INCOME = CATALOG.declare("net_income", Decimal, non_negative=True)
"""Net income, T1 line 56 and line 23600 "Line 54 minus line 55 (if negative, enter "0") If
negative, you may have a non-capital loss (see Form T1A) and the negative amount is to be used for
certain calculations (go to canada.ca/line-23600) Net income": the net income before adjustments
(line 23400) less the social benefits repayment (line 23500), not below zero. The amount before
that floor is `NET_INCOME_SIGNED`.
"""

NET_INCOME_SIGNED = CATALOG.declare("net_income_signed", Decimal)
"""Net income before its floor, T1 line 56 and line 23600 "Line 54 minus line 55 (if negative,
enter "0")" as Form T1206 Part 1 line 5 "Net income from line 23600 of your tax return (or the
amount you would have entered if the instructions on line 23600 read "if negative, show in
brackets")" reads it, and so does the TOSI-adjusted net income, which Schedule ON479-A column 1
line 1 reads: the net income before adjustments (line 23400) less the social benefits repayment
(line 23500), signed."""

OAS_OVERPAYMENT_RECOVERED = CATALOG.declare("oas_overpayment_recovered", Decimal, non_negative=True)
"""Overpayment of OAS benefits recovered, Federal Worksheet "Line 23500 - Social benefits
repayment" line 4 "Overpayment of OAS benefits recovered (box 20 of your T4A(OAS) slip)": a
starting amount from the slip."""

EI_BENEFITS_REPAYMENT = CATALOG.declare("ei_benefits_repayment", Decimal, non_negative=True)
"""EI benefits repayment, Federal Worksheet "Line 23500 - Social benefits repayment" line 7 "EI
benefits repayment from line 4 of the repayment chart on your T4E slip, if any": a starting amount
from the slip."""

EI_BENEFITS_REPAYMENT_CHECKED = CATALOG.declare(
    "ei_benefits_repayment_checked", Decimal, non_negative=True
)
"""EI benefits repayment after the check, Federal Worksheet "Line 23500 - Social benefits
repayment" line 7 "EI benefits repayment from line 4 of the repayment chart on your T4E slip, if
any": the amount of `ca/ei_benefits_repayment` after the check that it is not more than
`ca/ei_and_other_benefits` (`core/at_most`), the EI and other benefits of line 11900 (Guide 5000-G
line 23500 "You have to repay part of the EI benefits (line 11900) that you received in 2025", so
the repayment is part of the benefits). Looked in Federal Worksheet 5000-D1 and Guide 5000-G for
another printed limit and found none (the T4E repayment chart is not in the repo). Lines 10 and 21
read this amount."""

NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO = CATALOG.declare(
    "net_income_before_adjustments_not_below_zero", Decimal, non_negative=True
)
"""Net income before adjustments, not below zero, Federal Worksheet "Line 25000 - Other payments
deduction" line 1 "Amount from line 23400 of your return (if negative, enter "0")": line 23400
with a negative result replaced by zero. It is not the net income of line 23600, which line 23500
reduces."""

SOCIAL_BENEFITS_REPAYMENT_APPLIES = CATALOG.declare(
    "social_benefits_repayment_applies", int, non_negative=True
)
"""Social benefits repayment chart applies, Federal Worksheet "Line 23500 - Social benefits
repayment" "Complete the chart below if one or both of the following applies:" "You entered an
amount on line 11900 of your return and the amount on line 23400 is more than $82,125" and "You
entered an amount on line 11300 or line 14600 of your return and the amount on line 23400 is more
than $93,454": a count, 1 when either holds and 0 otherwise (T1 line 55 and line 23500 "If not,
enter "0" on line 23500.")."""

OAS_AND_FEDERAL_SUPPLEMENTS = CATALOG.declare(
    "oas_and_federal_supplements", Decimal, non_negative=True
)
"""OAS and federal supplements, Federal Worksheet "Line 23500 - Social benefits repayment" line 3
"Line 1 plus line 2 =": line 1 "Old age security (OAS) pension from line 11300 of your return" plus
line 2 "Net federal supplements paid from line 14600 of your return"."""

SOCIAL_BENEFITS_LINE_5 = CATALOG.declare("social_benefits_line_5", Decimal, non_negative=True)
"""Social benefits chart line 5, Federal Worksheet "Line 23500 - Social benefits repayment" line 5
"Line 3 minus line 4 (if negative, enter "0") =": line 3 less line 4 "Overpayment of OAS benefits
recovered (box 20 of your T4A(OAS) slip)", not below zero."""

SOCIAL_BENEFITS_LINE_6 = CATALOG.declare("social_benefits_line_6", Decimal)
"""Social benefits chart line 6, Federal Worksheet "Line 23500 - Social benefits repayment" line 6
"Net income before adjustments from line 23400 of your return", plus, as Form T1206 Part 1 says,
"add the amount from line 4 of this form to line 6 of your Federal Worksheet in the calculation of
the social benefits repayment for the calculation of lines 23500 and 42200 of your tax return, if
applicable": the total split income. The form prints no "(if negative, enter "0")", so the kind is
signed."""

SOCIAL_BENEFITS_LINE_10 = CATALOG.declare("social_benefits_line_10", Decimal, non_negative=True)
"""Social benefits chart line 10, Federal Worksheet "Line 23500 - Social benefits repayment" line
10 "Add lines 7 to 9. =": line 7 (the EI benefits repayment), line 8 "Universal child care benefit
(UCCB) from line 11700 of your return" and line 9 "Registered disability savings plan (RDSP)
income from line 12500 of your return"."""

SOCIAL_BENEFITS_LINE_11 = CATALOG.declare("social_benefits_line_11", Decimal)
"""Social benefits chart line 11, Federal Worksheet "Line 23500 - Social benefits repayment" line
11 "Line 6 minus line 10 =": line 6 less line 10. The form prints no "(if negative, enter "0")", so
the kind is signed."""

SOCIAL_BENEFITS_LINE_14 = CATALOG.declare("social_benefits_line_14", Decimal, non_negative=True)
"""Social benefits chart line 14, Federal Worksheet "Line 23500 - Social benefits repayment" line
14 "Line 12 plus line 13 =": line 12 "UCCB repayment from line 21300 of your return" plus line 13
"RDSP income repayment (included in the amount on line 23200 of your return)"."""

SOCIAL_BENEFITS_LINE_15 = CATALOG.declare("social_benefits_line_15", Decimal)
"""Social benefits chart line 15, Federal Worksheet "Line 23500 - Social benefits repayment" line
15 "Line 11 plus line 14 Adjusted net income =": the adjusted net income. The form prints no "(if
negative, enter "0")", so the kind is signed."""

OAS_BENEFITS_BASE_AMOUNT = CATALOG.declare("oas_benefits_base_amount", Decimal, non_negative=True)
"""OAS benefits base amount, Federal Worksheet "Line 23500 - Social benefits repayment" line 16
"OAS benefits base amount 93,343.00": a fixed amount, claimed whole."""

SOCIAL_BENEFITS_LINE_17 = CATALOG.declare("social_benefits_line_17", Decimal, non_negative=True)
"""Social benefits chart line 17, Federal Worksheet "Line 23500 - Social benefits repayment" line
17 "Line 15 minus line 16 (if negative, enter "0") =": the adjusted net income over the OAS benefits
base amount, not below zero."""

SOCIAL_BENEFITS_LINE_18 = CATALOG.declare("social_benefits_line_18", Decimal, non_negative=True)
"""Social benefits chart line 18, Federal Worksheet "Line 23500 - Social benefits repayment" line
18 "Amount from line 17 multiplied by 15% =": the OAS recovery tax before its limit."""

SOCIAL_BENEFITS_LINE_19 = CATALOG.declare("social_benefits_line_19", Decimal, non_negative=True)
"""Social benefits chart line 19, Federal Worksheet "Line 23500 - Social benefits repayment" line
19 "Enter whichever is less: amount from line 5 or line 18."."""

SOCIAL_BENEFITS_LINE_21 = CATALOG.declare("social_benefits_line_21", Decimal, non_negative=True)
"""Social benefits chart line 21, Federal Worksheet "Line 23500 - Social benefits repayment" line
21 "Line 19 plus line 20. Enter this amount on line 23500 and line 42200 of your return. =": line
19 plus line 20 "Amount from line 7, if any". It is the result of the chart whether or not the
chart applies; line 23500 counts it once only when it does."""

SOCIAL_BENEFITS_REPAYMENT = CATALOG.declare("social_benefits_repayment", Decimal, non_negative=True)
"""Social benefits repayment, T1 line 55 and line 23500 "Line 55 and line 23500: If not, enter "0"
on line 23500.": the result of the Federal Worksheet chart (line 21) when the chart applies, else
0. Line 42200 carries it."""

TOTAL_SPLIT_INCOME = CATALOG.declare("total_split_income", Decimal, non_negative=True)
"""Total split income, Form T1206 Part 1 line 4 (68360) "Total split income: line 1 plus line 3
Enter this amount on line 23200 of your return.": the dividends of line 1 plus the other split
income of line 3, a part of the T1 line 23300 deductions and the tax base of line 8 (line 7)."""

TOSI_ADJUSTED_NET_INCOME = CATALOG.declare("tosi_adjusted_net_income", Decimal)
"""TOSI-adjusted net income, Form T1206 Part 1 line 6 "TOSI-adjusted net income: line 4 plus line 5
If negative, enter the result in brackets": the total split income plus the net income
before its floor (line 5 "or the amount you would have entered if the instructions on
line 23600 read "if negative, show in brackets""), which is line 23400 less line 23500, signed.

The form prints no "(if negative, enter "0")", so the kind is signed; it stands where the form's
note says "use the negative value when it is part of an adjusted net income calculation".
"""

TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO = CATALOG.declare(
    "tosi_adjusted_net_income_not_below_zero", Decimal, non_negative=True
)
"""TOSI-adjusted net income, not below zero, Form T1206 Part 1 line 6 "(If the TOSI-adjusted net
income at line 6 is negative, use the negative value when it is part of an adjusted net income
calculation, otherwise use zero.)": line 6 with a negative result replaced by zero, for the amounts
that read it otherwise, the basic personal amount, the age amount and Schedule 6 line 7.
"""

CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION = CATALOG.declare(
    "canadian_armed_forces_and_police_deduction", Decimal, non_negative=True
)
"""Canadian Armed Forces personnel and police deduction, T1 line 58 and line 24400 "Canadian Armed
Forces personnel and police deduction (box 43 of all T4 slips)": a starting amount."""

T4_SECURITY_OPTIONS_BOXES_39_AND_91 = CATALOG.declare(
    "t4_security_options_boxes_39_and_91", Decimal, non_negative=True
)
"""T4 slips' boxes 39 and 91, Form T691 Part 1 line 28 "Total of all amounts in boxes 39 and 91 of
your T4 slips", the security options deduction under paragraph 110(1)(d) "included on line 24900 of
your return": the caller's amounts, entered once in the form `ca/security_options_boxes_39_and_91`
and read by the return through its total, `ca/t4_security_options_boxes_39_and_91_total`."""

T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL = CATALOG.declare(
    "t4_security_options_boxes_39_and_91_total", Decimal, non_negative=True
)
"""Total of the T4 slips' boxes 39 and 91, Form T691 Part 1 line 28 "Total of all amounts in boxes
39 and 91 of your T4 slips": the total of the one record of the form
`ca/security_options_boxes_39_and_91` (`core/record_total`), read by line 30 "Line 28 plus line 29"
and by the line 24900 sum."""

T4_SECURITY_OPTIONS_BOXES_41_AND_92 = CATALOG.declare(
    "t4_security_options_boxes_41_and_92", Decimal, non_negative=True
)
"""T4 slips' boxes 41 and 92, Form T691 Part 1 line 35 "total of all amounts in boxes 41 and 92 of
your T4 slips", the security options deduction under paragraph 110(1)(d.1) "included on line 24900
of your return": the caller's amounts, entered once in the form
`ca/security_options_boxes_41_and_92` and read by the return through its total,
`ca/t4_security_options_boxes_41_and_92_total`."""

T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL = CATALOG.declare(
    "t4_security_options_boxes_41_and_92_total", Decimal, non_negative=True
)
"""Total of the T4 slips' boxes 41 and 92, Form T691 Part 1 line 35 "total of all amounts in boxes
41 and 92 of your T4 slips": the total of the one record of the form
`ca/security_options_boxes_41_and_92` (`core/record_total`), read by line 38 "Add lines 35 to 37."
and by the line 24900 sum."""

SECURITY_OPTIONS_DEDUCTIONS = CATALOG.declare(
    "security_options_deductions", Decimal, non_negative=True
)
"""Security options deductions, T1 line 59 and line 24900 "Security options deductions (boxes 39,
41, 91 and 92 of all T4 slips or see Form T1212)", computed, not entered: the sum, in Form T691
Part 1 line order, of line 28 (`ca/t4_security_options_boxes_39_and_91_total`), line 29 (line 2 of
Form T1212), line 31 (the gifts of publicly listed securities "included on line 24900 of your
return"), line 35 (`ca/t4_security_options_boxes_41_and_92_total`), line 36 (the prospector or
grubstaker deduction) and line 37 (the deferred profit-sharing plan deduction), each "included on
line 24900 of your return". Guide 5000-G line 24900 "Claim on line 24900 of your return the total of
the amounts shown in boxes 39, 41, 91, and 92 of your T4 slips" is the same claim."""

UCCB_REPAYMENT = CATALOG.declare("uccb_repayment", Decimal, non_negative=True)
"""UCCB repayment, T1 line 40 and line 21300 "Universal child care benefit (UCCB) repayment (box 12
of all RC62 slips)", also Federal Worksheet "Line 25000 - Other payments deduction" line 6 "Amount
from line 21300 of your return": a starting amount, a deduction from total income."""

RDSP_INCOME_REPAYMENT = CATALOG.declare("rdsp_income_repayment", Decimal, non_negative=True)
"""RDSP income repayment, Federal Worksheet "Line 25000 - Other payments deduction" line 7 "RDSP
income repayment (included in the amount on line 23200 of your return)": a starting amount."""

RDSP_INCOME_REPAYMENT_CHECKED = CATALOG.declare(
    "rdsp_income_repayment_checked", Decimal, non_negative=True
)
"""RDSP income repayment after the check, Federal Worksheet "Line 23500 - Social benefits
repayment" line 13 "RDSP income repayment (included in the amount on line 23200 of your return)":
the amount of `ca/rdsp_income_repayment` after the check that it is not more than
`ca/other_deductions` (`core/at_most`), the caller's line 23200 amount. The readers of the
repayment use this amount."""

UCCB_AND_RDSP_INCOME = CATALOG.declare("uccb_and_rdsp_income", Decimal, non_negative=True)
"""UCCB and RDSP income, Federal Worksheet "Line 25000 - Other payments deduction" line 4 "Line 2
plus line 3 =": the amount from line 11700 of the return (line 2) and the amount from line 12500
(line 3)."""

NET_INCOME_LESS_UCCB_AND_RDSP_INCOME = CATALOG.declare(
    "net_income_less_uccb_and_rdsp_income", Decimal
)
"""Net income less the UCCB and RDSP income, Federal Worksheet "Line 25000 - Other payments
deduction" line 5 "Line 1 minus line 4 =": the net income (line 1, "Amount from line 23400 of your
return (if negative, enter "0")") less line 4.

The form prints no "(if negative, enter "0")" on line 5, so the kind is signed.
"""

UCCB_AND_RDSP_INCOME_REPAYMENTS = CATALOG.declare(
    "uccb_and_rdsp_income_repayments", Decimal, non_negative=True
)
"""UCCB and RDSP income repayments, Federal Worksheet "Line 25000 - Other payments deduction" line
8 "Line 6 plus line 7 =": the UCCB repayment (line 6) and the RDSP income repayment (line 7)."""

OTHER_PAYMENTS_LIMIT_INCOME = CATALOG.declare("other_payments_limit_income", Decimal)
"""Income for the limit, Federal Worksheet "Line 25000 - Other payments deduction" line 9 "Line 5
plus line 8 =": the amount the worksheet compares with $93,454 ("If the amount on line 9 is more
than $93,454, go to canada.ca/line-25000 to find out how much you can deduct.").

The form prints no "(if negative, enter "0")" on line 9, so the kind is signed. The count of line 9
over $93,454 is derived from this line, and the manifest also returns it.
"""

OTHER_PAYMENTS_WORKSHEET_LINE_9_OVER_LIMIT = CATALOG.declare(
    "other_payments_worksheet_line_9_over_limit", int, non_negative=True
)
"""Line 9 over the limit, Federal Worksheet "Line 25000 - Other payments deduction" "If the amount
on line 9 is more than $93,454, go to canada.ca/line-25000 to find out how much you can deduct.":
a derived count, 1 when line 9 (`ca/other_payments_limit_income`) is more than $93,454 and 0
otherwise (`ca/count_by_conditions`)."""

OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT = CATALOG.declare(
    "other_payments_deduction_above_limit", Decimal, non_negative=True
)
"""Other payments deduction above the limit, Federal Worksheet "Line 25000 - Other payments
deduction" "go to canada.ca/line-25000 to find out how much you can deduct": the amount that
chart gives when line 9 is more than $93,454, a starting amount."""

OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED = CATALOG.declare(
    "other_payments_deduction_above_limit_checked", Decimal, non_negative=True
)
"""Other payments deduction above the limit after the check, Federal Worksheet "Line 25000 - Other
payments deduction" and Guide 5000-G line 25000 "you may not be entitled to claim the full amount
from line 14700 of your return": the amount of `ca/other_payments_deduction_above_limit` after the
check that it is not more than `ca/income_support_benefits` (`core/at_most`). Line 9 chooses this
amount over line 14700."""

OTHER_PAYMENTS_DEDUCTION_AFTER_LIMIT = CATALOG.declare(
    "other_payments_deduction_after_limit", Decimal, non_negative=True
)
"""Other payments deduction after the limit, Federal Worksheet "Line 25000 - Other payments
deduction" "Otherwise, enter the amount from line 14700 of your return on line 25000 of your
return.": line 14700 when line 9 is not more than $93,454, else the amount the canada.ca/line-25000
chart gives."""

OTHER_PAYMENTS_WORKSHEET_REQUIRED = CATALOG.declare(
    "other_payments_worksheet_required", int, non_negative=True
)
"""Worksheet required, T1 line 60 and line 25000 "Other payments deduction (enter the amount from
line 14700 if you did not enter an amount on line 14600; otherwise, use Federal Worksheet)": a
derived count, 1 when an amount was entered on line 14600 (`ca/net_federal_supplements`) and 0
otherwise (`ca/count_by_conditions`)."""

OTHER_PAYMENTS_DEDUCTION = CATALOG.declare("other_payments_deduction", Decimal, non_negative=True)
"""Other payments deduction, T1 line 60 and line 25000 "Other payments deduction (enter the amount
from line 14700 if you did not enter an amount on line 14600; otherwise, use Federal Worksheet)":
line 14700 when no amount was entered on line 14600, else the Federal Worksheet's result."""

ZONE_A_DAYS_LIVED = CATALOG.declare("zone_a_days_lived", int, non_negative=True)
"""Zone A days lived, Form T2222 Step 2 line 1 "Enter the number of days you lived in a prescribed
northern zone in 2025.": a starting count of days, as typed
(the form prints no maximum)."""

ZONE_A_ADDITIONAL_RESIDENCY_DAYS = CATALOG.declare(
    "zone_a_additional_residency_days", int, non_negative=True
)
"""Zone A days for the additional residency amount, Form T2222 Step 2 line 2 "Enter the number of
days you qualify for the additional residency amount in 2025.": a starting count of days."""

ZONE_A_ADDITIONAL_RESIDENCY_DAYS_CHECKED = CATALOG.declare(
    "zone_a_additional_residency_days_checked", int, non_negative=True
)
"""Zone A days for the additional residency amount, checked, Form T2222 Step 2 line 2: the days of
line 2 when they are at most the Zone A days of line 1, the days "you used to calculate your basic
residency amount"; more is an input error."""

ZONE_A_BASIC_RESIDENCY_AMOUNT = CATALOG.declare(
    "zone_a_basic_residency_amount", Decimal, non_negative=True
)
"""Zone A basic residency amount, Form T2222 Step 2 line 1 "Enter the number of days you lived in
a prescribed northern zone in 2025. multiplied by $11.00 =": the days of line 1 times $11.00."""

ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT = CATALOG.declare(
    "zone_a_additional_residency_amount", Decimal, non_negative=True
)
"""Zone A additional residency amount, Form T2222 Step 2 line 2 "Enter the number of days you
qualify for the additional residency amount in 2025. multiplied by $11.00 =": the days of line 2
times $11.00."""

ZONE_A_RESIDENCY_AMOUNT = CATALOG.declare("zone_a_residency_amount", Decimal, non_negative=True)
"""Zone A residency amount, Form T2222 Step 2 line 3 and line 67490 "Line 1 plus line 2 =": the
basic and the additional residency amounts of Zone A."""

ZONE_A_SPECIAL_WORK_SITE_BENEFITS = CATALOG.declare(
    "zone_a_special_work_site_benefits", Decimal, non_negative=True
)
"""Zone A special work site benefits, Form T2222 Step 2 line 4 and line 67507 "If you worked at a
special work site, enter the amount from box 31 of your T4 slip or box 124 of your T4A slip that
represents the non-taxable benefits for board and lodging at the special work site.": a starting
amount. The site's location within 30 kilometres of a population centre is the filer's to apply."""

ZONE_A_RESIDENCY_AFTER_WORK_SITE = CATALOG.declare(
    "zone_a_residency_after_work_site", Decimal, non_negative=True
)
"""Zone A residency amount after the work site benefits, Form T2222 Step 2 line 5 "Line 3 minus
line 4 (if negative, enter "0") =": line 3 less line 4, not below zero."""

ZONE_B_DAYS_LIVED = CATALOG.declare("zone_b_days_lived", int, non_negative=True)
"""Zone B days lived, Form T2222 Step 2 line 6 "Enter the number of days you lived in an
intermediate zone in 2025.": a starting count of days, as typed
(the form prints no maximum)."""

ZONE_B_ADDITIONAL_RESIDENCY_DAYS = CATALOG.declare(
    "zone_b_additional_residency_days", int, non_negative=True
)
"""Zone B days for the additional residency amount, Form T2222 Step 2 line 7 "Enter the number of
days you qualify for the additional residency amount in 2025.": a starting count of days."""

ZONE_B_ADDITIONAL_RESIDENCY_DAYS_CHECKED = CATALOG.declare(
    "zone_b_additional_residency_days_checked", int, non_negative=True
)
"""Zone B days for the additional residency amount, checked, Form T2222 Step 2 line 7: the days of
line 7 when they are at most the Zone B days of line 6, the days "you used to calculate your basic
residency amount"; more is an input error."""

ZONE_B_BASIC_RESIDENCY_AMOUNT = CATALOG.declare(
    "zone_b_basic_residency_amount", Decimal, non_negative=True
)
"""Zone B basic residency amount, Form T2222 Step 2 line 6 "Enter the number of days you lived in
an intermediate zone in 2025. multiplied by $5.50 =": the days of line 6 times $5.50."""

ZONE_B_ADDITIONAL_RESIDENCY_AMOUNT = CATALOG.declare(
    "zone_b_additional_residency_amount", Decimal, non_negative=True
)
"""Zone B additional residency amount, Form T2222 Step 2 line 7 "Enter the number of days you
qualify for the additional residency amount in 2025. multiplied by $5.50 =": the days of line 7
times $5.50."""

ZONE_B_RESIDENCY_AMOUNT = CATALOG.declare("zone_b_residency_amount", Decimal, non_negative=True)
"""Zone B residency amount, Form T2222 Step 2 line 8 and line 67520 "Line 6 plus line 7 =": the
basic and the additional residency amounts of Zone B."""

ZONE_B_SPECIAL_WORK_SITE_BENEFITS = CATALOG.declare(
    "zone_b_special_work_site_benefits", Decimal, non_negative=True
)
"""Zone B special work site benefits, Form T2222 Step 2 line 9 and line 67529 "If you worked at a
special work site, enter the amount from box 31 of your T4 slip or box 124 of your T4A slip that
represents the non-taxable benefits for board and lodging at the special work site.": a starting
amount. The site's location within 30 kilometres of a population centre is the filer's to apply."""

ZONE_B_RESIDENCY_AFTER_WORK_SITE = CATALOG.declare(
    "zone_b_residency_after_work_site", Decimal, non_negative=True
)
"""Zone B residency amount after the work site benefits, Form T2222 Step 2 line 10 "Line 8 minus
line 9 (if negative, enter "0") =": line 8 less line 9, not below zero."""

RESIDENCY_AMOUNT = CATALOG.declare("residency_amount", Decimal, non_negative=True)
"""Residency amount, Form T2222 Step 2 line 11 "Line 5 plus line 10 =": the Zone A and Zone B
amounts after the work site benefits."""

RESIDENCY_NET_INCOME_LIMIT = CATALOG.declare(
    "residency_net_income_limit", Decimal, non_negative=True
)
"""Residency limit on net income, Form T2222 Step 2 line 12 "Enter your net income from line 23600
of your return. multiplied by 20%  =": the net income times 20%."""

RESIDENCY_DEDUCTION = CATALOG.declare("residency_deduction", Decimal, non_negative=True)
"""Residency deduction, Form T2222 Step 2 line 13 "Enter whichever is less: amount from line 11 or
line 12. Residency deduction": the lesser of lines 11 and 12; line 17 of Step 4 is this amount."""

TRAVEL_INDIVIDUAL = CATALOG.declare("travel_individual", int, non_negative=True)
"""Individual, Form T2222 Step 3 Chart A "Row A: Enter the name of each individual, including
yourself, whose travel you are claiming." and Chart B "Column 1: Enter the name of the person who
took the trip.": a count, the number the filer gives each individual, which only names the
individual and which no capability reads."""

TRIP_ZONE = CATALOG.declare("trip_zone", int, non_negative=True)
"""Zone of a trip, Form T2222 Step 3 Chart B "Enter the lowest amount from column 3, 4, or 5 in the
column for the prescribed zone(s) you resided in at the time of the trip.": a count, 1 for Zone A
(column 6) and 2 for Zone B (column 7)."""

TRIP_BENEFIT_OR_STANDARD_AMOUNT = CATALOG.declare(
    "trip_benefit_or_standard_amount", Decimal, non_negative=True
)
"""Benefit or standard amount of a trip, Form T2222 Step 3 Chart B "Column 3: Enter either the
taxable travel benefit or the portion of the individual's $1,200 standard amount for the trip.":
an input for each trip."""

TRIP_TRAVEL_EXPENSES = CATALOG.declare("trip_travel_expenses", Decimal, non_negative=True)
"""Travel expenses of a trip, Form T2222 Step 3 Chart B "Column 4: Enter the amount of travel
expenses for each trip taken.": an input for each trip."""

TRIP_LOWEST_RETURN_AIRFARE = CATALOG.declare(
    "trip_lowest_return_airfare", Decimal, non_negative=True
)
"""Lowest return airfare of a trip, Form T2222 Step 3 Chart B "Column 5: Enter the cost of the
lowest return airfare.": an input for each trip."""

TRAVEL_TRIPS = RecordListKind.declare(
    CATALOG,
    "travel_trips",
    fields=(
        TRAVEL_INDIVIDUAL,
        TRIP_ZONE,
        TRIP_BENEFIT_OR_STANDARD_AMOUNT,
        TRIP_TRAVEL_EXPENSES,
        TRIP_LOWEST_RETURN_AIRFARE,
    ),
)
"""Trips, Form T2222 Step 3 Chart B, one record for each trip: the individual who took it ("Column
1"), the zone whose column the amount goes in, and "Column 3", "Column 4" and "Column 5". A starting
list, possibly empty."""

STANDARD_AMOUNT_ALLOCATED_1 = CATALOG.declare(
    "standard_amount_allocated_1", Decimal, non_negative=True
)
"""First allocation of the standard amount, Form T2222 Step 3 Chart A "Row B: Enter the name of
everyone (including yourself) who is claiming a deduction for trips taken by the individual in row
A and the total portion of the $1,200 standard amount allocated by each claimant for all trips
taken by that individual.": the first claimant's portion, an input."""

STANDARD_AMOUNT_ALLOCATED_2 = CATALOG.declare(
    "standard_amount_allocated_2", Decimal, non_negative=True
)
"""Second allocation of the standard amount, Form T2222 Step 3 Chart A row B: the second
claimant's portion, an input."""

STANDARD_AMOUNT_ALLOCATED_3 = CATALOG.declare(
    "standard_amount_allocated_3", Decimal, non_negative=True
)
"""Third allocation of the standard amount, Form T2222 Step 3 Chart A row B: the third claimant's
portion, an input."""

TRAVEL_INDIVIDUALS = RecordListKind.declare(
    CATALOG,
    "travel_individuals",
    fields=(
        TRAVEL_INDIVIDUAL,
        STANDARD_AMOUNT_ALLOCATED_1,
        STANDARD_AMOUNT_ALLOCATED_2,
        STANDARD_AMOUNT_ALLOCATED_3,
    ),
)
"""Individuals, Form T2222 Step 3 Chart A "Row A: Enter the name of each individual, including
yourself, whose travel you are claiming.", one record for each individual with the three amounts of
"Row B". A starting list, possibly empty."""

STANDARD_AMOUNT_ALLOCATED = CATALOG.declare("standard_amount_allocated", Decimal, non_negative=True)
"""Standard amount allocated, Form T2222 Step 3 Chart A "Row C: Enter the total of all amounts in
row B. This total cannot be more than $1,200.": row C added over the individuals. No line of the
form reads it, so the manifest returns it."""

TRAVEL_TOTAL_ZONE_A = CATALOG.declare("travel_total_zone_a", Decimal, non_negative=True)
"""Zone A total of the trips, Form T2222 Step 3 Chart B "(A) Total (add all the amounts under
Column 6) =", line 14 and line 67540 "Amount A of Chart B"."""

TRAVEL_TOTAL_ZONE_B = CATALOG.declare("travel_total_zone_b", Decimal, non_negative=True)
"""Zone B total of the trips, Form T2222 Step 3 Chart B "(B) Total (add all the amounts under
Column 7) =", read by line 15 "Enter the total from box B. Line 67560"."""

TRAVEL_ZONE_B_DEDUCTION = CATALOG.declare("travel_zone_b_deduction", Decimal, non_negative=True)
"""Zone B travel amount, Form T2222 Step 3 line 15 "Enter the total from box B. Line 67560
multiplied by 50% =": the Zone B total times 50%."""

TRAVEL_DEDUCTION = CATALOG.declare("travel_deduction", Decimal, non_negative=True)
"""Travel deduction, Form T2222 Step 3 line 16 "Line 14 plus line 15 Travel deduction =": the Zone
A total (line 14) and line 15; line 18 of Step 4 is this amount."""

NORTHERN_RESIDENTS_DEDUCTIONS = CATALOG.declare(
    "northern_residents_deductions", Decimal, non_negative=True
)
"""Northern residents deductions, Form T2222 Step 4 line 19 "Line 17 plus line 18 Enter this amount
on line 25500 of your return. Northern residents deductions =" and T1 line 66 and line 25500
"Northern residents deductions (complete Form T2222)": the residency deduction (line 17) and the
travel deduction (line 18)."""

CPP_ZERO = CATALOG.declare("cpp_zero", Decimal, non_negative=True)
"""Schedule 8 zero, Part 3b "If not, enter "0"": the amount of the "enter "0"" alternatives of lines
32, 35, 39, 42 and 46, and the base of lines 31, 38 and 45, which are "as a positive amount"."""

CPP_LINE_24_POSITIVE = CATALOG.declare("cpp_line_24_positive", int, non_negative=True)
"""Line 24 is positive, Schedule 8 Part 3 line 24 "Line 20 plus line 23 (if negative, show in
brackets) =": 1 when the line is positive, the Part 3a branch ("positive, complete Part 3a
below"), and 0 when it is "0" or negative, the Part 3b branch."""

CPP_LINE_16_NOT_NEGATIVE = CATALOG.declare("cpp_line_16_not_negative", int, non_negative=True)
"""Line 16 is positive or "0", Schedule 8 Part 3 line 16 "Line 14 minus line 15 (if negative, show
in brackets) =": 1 when the line is not negative, the test of Part 3b line 30 "If line 16 is
positive or "0"", and 0 when it is negative."""

CPP_LINE_19_NOT_NEGATIVE = CATALOG.declare("cpp_line_19_not_negative", int, non_negative=True)
"""Line 19 is positive or "0", Schedule 8 Part 3 line 19 "Line 17 minus line 18 (if negative, show
in brackets) =": 1 when the line is not negative, the test of Part 3b line 37 (printed as line 36)
"If line 19 is positive or "0"", and 0 when it is negative."""

CPP_LINE_23_NOT_NEGATIVE = CATALOG.declare("cpp_line_23_not_negative", int, non_negative=True)
"""Line 23 is positive or "0", Schedule 8 Part 3 line 23 "Line 21 minus line 22 (if negative, show
in brackets) =": 1 when the line is not negative, the test of Part 3b line 44 "If line 23 is
positive or "0"", and 0 when it is negative."""

CPP_LINE_16_NEGATIVE_LINE_19_POSITIVE = CATALOG.declare(
    "cpp_line_16_negative_line_19_positive", int, non_negative=True
)
"""Line 16 is negative and line 19 is positive, Schedule 8 Part 3b line 32 "If line 16 is negative
and line 19 is positive, enter whichever is less": 1 when line 16 is negative (the count of line
16 not negative is 0) and line 19 is positive, and 0 otherwise."""

CPP_LINE_23_AND_LINE_33_POSITIVE = CATALOG.declare(
    "cpp_line_23_and_line_33_positive", int, non_negative=True
)
"""Line 23 and line 33 are both positive, Schedule 8 Part 3b line 35 "If line 23 and line 33 are
both positive, enter whichever is less. If not, enter "0"": 1 when both lines are positive, 0
otherwise."""

CPP_LINE_16_POSITIVE = CATALOG.declare("cpp_line_16_positive", int, non_negative=True)
"""Line 16 is positive, Schedule 8 Part 3b line 39 "If line 16 is positive, enter whichever is
less": 1 when the line is more than 0, 0 otherwise."""

CPP_LINE_23_AND_LINE_40_POSITIVE = CATALOG.declare(
    "cpp_line_23_and_line_40_positive", int, non_negative=True
)
"""Line 23 and line 40 are both positive, Schedule 8 Part 3b line 42 "If line 23 and line 40 are
both positive, enter whichever is less: amount from line 40 or the result of line 23 minus line
35": 1 when both lines are positive, 0 otherwise."""

CPP_LINE_20_POSITIVE = CATALOG.declare("cpp_line_20_positive", int, non_negative=True)
"""Line 20 is positive, Schedule 8 Part 3b line 46 "If line 20 is positive, enter whichever is
less": 1 when the line is more than 0, 0 otherwise."""

CPP_PART_3B_LINE_30 = CATALOG.declare("cpp_part_3b_line_30", Decimal, non_negative=True)
"""Part 3b line 30 "If line 16 is positive or "0", enter the amount from line 15 at line 30 and
line 36, and continue at line 37. If not, enter the amount from line 14 and continue at line 31.":
the required base contributions (line 15) when line 16 is not negative, else the actual base
contributions (line 14, from line 9)."""

CPP_PART_3B_LINE_31 = CATALOG.declare("cpp_part_3b_line_31", Decimal, non_negative=True)
"""Part 3b line 31 "Enter the amount from line 16 as a positive amount.", under "If line 16 is
negative:": line 16 as a positive amount, and 0 when line 16 is positive or "0"."""

CPP_PART_3B_LINE_32_LESSER = CATALOG.declare("cpp_part_3b_line_32_lesser", Decimal)
"""Part 3b line 32 candidate, "If line 16 is negative and line 19 is positive, enter whichever is
less: amount from line 19 or line 31": the lesser of line 19 and line 31, which line 32 takes only
when the count of line 16 negative and line 19 positive applies."""

CPP_PART_3B_LINE_32 = CATALOG.declare("cpp_part_3b_line_32", Decimal, non_negative=True)
"""Part 3b line 32 "amount from line 19 or line 31. If not, enter "0".": the candidate above when
line 16 is negative and line 19 is positive, else "0"."""

CPP_PART_3B_LINE_33 = CATALOG.declare("cpp_part_3b_line_33", Decimal, non_negative=True)
"""Part 3b line 33 "Line 31 minus line 32 =": the part of line 31 that line 32 does not take."""

CPP_PART_3B_LINE_34 = CATALOG.declare("cpp_part_3b_line_34", Decimal, non_negative=True)
"""Part 3b line 34 "Line 30 plus line 32 =": the sum of lines 30 and 32."""

CPP_PART_3B_LINE_35_LESSER = CATALOG.declare("cpp_part_3b_line_35_lesser", Decimal)
"""Part 3b line 35 candidate, "If line 23 and line 33 are both positive, enter whichever is less":
the lesser of line 23 and line 33, which line 35 takes only when both are positive."""

CPP_PART_3B_LINE_35 = CATALOG.declare("cpp_part_3b_line_35", Decimal, non_negative=True)
"""Part 3b line 35 "If line 23 and line 33 are both positive, enter whichever is less. If not,
enter "0".": the candidate above when both are positive, else "0"."""

CPP_PART_3B_LINE_36 = CATALOG.declare("cpp_part_3b_line_36", Decimal, non_negative=True)
"""Part 3b line 36 "Line 34 plus line 35. Enter this amount (in dollars and cents) on line 30800 of
your return and line 58240 of your Form 428.": the base contributions of the Part 3b branch, which
schedule_8_cpp_base_contributions_on_return carries to line 30800 when line 24 is "0" or
negative."""

CPP_PART_3B_LINE_37 = CATALOG.declare("cpp_part_3b_line_37", Decimal, non_negative=True)
"""Part 3b line 37 (printed as "Line 36" on the form's second page), "If line 19 is positive or "0",
enter the amount from line 18 at line 37 and line 43, and continue at line 44. If not, enter the
amount from line 17 and continue at line 38.": the required first additional contributions (line
18) when line 19 is not negative, else the actual first additional contributions (line 17)."""

CPP_PART_3B_LINE_38 = CATALOG.declare("cpp_part_3b_line_38", Decimal, non_negative=True)
"""Part 3b line 38 "If line 19 is negative: Enter the amount from line 19 as a positive amount.":
line 19 as a positive amount, and 0 when line 19 is positive or "0"."""

CPP_PART_3B_LINE_39_LESSER = CATALOG.declare("cpp_part_3b_line_39_lesser", Decimal)
"""Part 3b line 39 candidate, "If line 16 is positive, enter whichever is less: amount from line 16
or line 38": the lesser of line 16 and line 38, which line 39 takes only when line 16 is
positive."""

CPP_PART_3B_LINE_39 = CATALOG.declare("cpp_part_3b_line_39", Decimal, non_negative=True)
"""Part 3b line 39 "amount from line 16 or line 38. If not, enter "0".": the candidate above when
line 16 is positive, else "0"."""

CPP_PART_3B_LINE_40 = CATALOG.declare("cpp_part_3b_line_40", Decimal, non_negative=True)
"""Part 3b line 40 "Line 38 minus line 39 =": the part of line 38 that line 39 does not take."""

CPP_PART_3B_LINE_41 = CATALOG.declare("cpp_part_3b_line_41", Decimal, non_negative=True)
"""Part 3b line 41 "Line 37 plus line 39 =": the sum of lines 37 and 39."""

CPP_PART_3B_LINE_23_LESS_LINE_35 = CATALOG.declare("cpp_part_3b_line_23_less_line_35", Decimal)
"""Part 3b line 42, "the result of line 23 minus line 35": line 23 less line 35, signed, the
comparison amount of the line 42 candidate."""

CPP_PART_3B_LINE_42_LESSER = CATALOG.declare("cpp_part_3b_line_42_lesser", Decimal)
"""Part 3b line 42 candidate, "If line 23 and line 40 are both positive, enter whichever is less:
amount from line 40 or the result of line 23 minus line 35": the lesser of line 40 and line 23
minus line 35, which line 42 takes only when both line 23 and line 40 are positive."""

CPP_PART_3B_LINE_42 = CATALOG.declare("cpp_part_3b_line_42", Decimal, non_negative=True)
"""Part 3b line 42 "... enter whichever is less ... If not, enter "0".": the candidate above when
line 23 and line 40 are both positive, else "0"."""

CPP_PART_3B_LINE_43 = CATALOG.declare("cpp_part_3b_line_43", Decimal, non_negative=True)
"""Part 3b line 43 "Line 41 plus line 42 =": the sum of lines 41 and 42."""

CPP_PART_3B_LINE_44 = CATALOG.declare("cpp_part_3b_line_44", Decimal, non_negative=True)
"""Part 3b line 44 "If line 23 is positive or "0", enter the amount from line 22 on line 44 and
line 47, and continue at line 48. If not, enter the amount from line 21 and continue at line 45.":
the required second additional contributions (line 22) when line 23 is not negative, else the
T4 box 16A total (line 21)."""

CPP_PART_3B_LINE_45 = CATALOG.declare("cpp_part_3b_line_45", Decimal, non_negative=True)
"""Part 3b line 45 "If line 23 is negative: Enter the amount from line 23 as a positive amount.":
line 23 as a positive amount, and 0 when line 23 is positive or "0"."""

CPP_PART_3B_LINE_46_LESSER = CATALOG.declare("cpp_part_3b_line_46_lesser", Decimal)
"""Part 3b line 46 candidate, "If line 20 is positive, enter whichever is less: amount from line 20
or line 45": the lesser of line 20 and line 45, which line 46 takes only when line 20 is
positive."""

CPP_PART_3B_LINE_46 = CATALOG.declare("cpp_part_3b_line_46", Decimal, non_negative=True)
"""Part 3b line 46 "amount from line 20 or line 45. If not, enter "0".": the candidate above when
line 20 is positive, else "0"."""

CPP_PART_3B_LINE_47 = CATALOG.declare("cpp_part_3b_line_47", Decimal, non_negative=True)
"""Part 3b line 47 "Line 44 plus line 46 =": the sum of lines 44 and 46."""

CPP_PART_3B_LINE_48 = CATALOG.declare("cpp_part_3b_line_48", Decimal, non_negative=True)
"""Part 3b line 48 "Line 43 plus line 47 Enter this amount (in dollars and cents) on line 22215 of
your return.": the enhanced contributions of the Part 3b branch, which
schedule_8_cpp_enhanced_contributions_on_return carries to line 22215 when line 24 is "0" or
negative."""

CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN = CATALOG.declare(
    "cpp_part_3_base_contributions_on_return", Decimal, non_negative=True
)
"""Part 3 route of the base CPP contributions, T1 line 30800 and ON428 line 58240: Part 3a line 25
"Enter the amount from line 15. Enter this amount (in dollars and cents) on line 30800 of your
return and line 58240 of your Form 428." when line 24 is positive (the required base contributions,
line 11), else Part 3b line 36 (the same instruction), chosen by the count of line 24 being
positive. schedule_8_cpp_base_contributions_on_return takes it on line 30800 unless Part 5 is
completed."""

CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN = CATALOG.declare(
    "cpp_part_3_enhanced_contributions_on_return", Decimal, non_negative=True
)
"""Part 3 route of the enhanced CPP contributions, T1 line 22215: Part 3a line 28 "Line 26 plus line
27 Enter this amount (in dollars and cents) on line 22215 of your return." when line 24 is positive,
else Part 3b line 48 (the same instruction), chosen by the count of line 24 being positive.
schedule_8_cpp_enhanced_contributions_on_return takes it on line 22215 unless Part 5 is completed.
A deduction from total income, not a credit."""

CPP_PART_3_OVERPAYMENT = CATALOG.declare("cpp_part_3_overpayment", Decimal, non_negative=True)
"""Part 3 route of the CPP overpayment, T1 line 44800: Part 3a line 29 "Enter the amount from line
24. Enter this amount (in dollars and cents) on line 44800 of your return." when line 24 is
positive, else "0". schedule_8_cpp_overpayment takes it on line 44800 unless Part 5 is completed."""

CPP_PART_3_LINE_2 = CATALOG.declare("cpp_part_3_line_2", Decimal, non_negative=True)
"""Part 3 line 2 "Line 2: Enter whichever is less: amount from line D of Part 2 or line 1.": the
lesser of the additional maximum pensionable earnings (Part 2 line D) and the employment income
(line 1), the amount Part 5 line 32 takes as "Amount from line 2 of Part 3"."""

CPP_PART_5_LINE_20_NEGATIVE_LINE_23_POSITIVE = CATALOG.declare(
    "cpp_part_5_line_20_negative_line_23_positive", int, non_negative=True
)
"""Count, Schedule 8 Part 5 "If the amount from line 20 of Part 3 is negative and line 23 of Part 3
is positive, complete lines 8 and 9. If not, enter "0" on line 9": 1 when line 20 of Part 3 is
negative and line 23 is positive, 0 otherwise."""

CPP_PART_5_LINE_20_POSITIVE_LINE_23_NEGATIVE = CATALOG.declare(
    "cpp_part_5_line_20_positive_line_23_negative", int, non_negative=True
)
"""Count, Schedule 8 Part 5 "If the amount from line 20 of Part 3 is positive and line 23 of Part 3
is negative, complete lines 14 and 15. If not, enter "0" on line 15": 1 when line 20 of Part 3
is positive and line 23 is negative, 0 otherwise."""

CPP_PART_5_LINE_33_MORE_THAN_LINE_17 = CATALOG.declare(
    "cpp_part_5_line_33_more_than_line_17", int, non_negative=True
)
"""Line 33 is more than line 17, Schedule 8 Part 5 "If the amount from line 33 is more than line
17, complete lines 34 to 42. If not, enter "0" on line 42 and continue at line 43": 1 when line
33 is more than line 17, 0 otherwise."""

CPP_PART_5_LINE_4 = CATALOG.declare("cpp_part_5_line_4", Decimal)
"""Part 5 line 4 "Line 4: Add lines 1 to 3. =": the pensionable net self-employment earnings (line
1, "amount from line 12200 of your return plus line 27 of your return") plus the CPT20 earnings
not on a T4 slip (line 2) and on a T4 slip (line 3). Signed: the form prints no floor, so a loss
on line 1 stays negative."""

CPP_PART_5_LINE_6 = CATALOG.declare("cpp_part_5_line_6", Decimal, non_negative=True)
"""Part 5 line 6 "Line 6: Enter the amount from line 20 of Part 3 if positive. If not, enter "0".":
line 20 of Part 3 when it is positive, else 0."""

CPP_PART_5_LINE_7 = CATALOG.declare("cpp_part_5_line_7", Decimal)
"""Part 5 line 7 "Line 7: Line 5 minus line 6 =": the total actual base and first additional
contributions from line 8 of Part 3 (line 5) less line 6. Signed."""

CPP_PART_5_LINE_8 = CATALOG.declare("cpp_part_5_line_8", Decimal, non_negative=True)
"""Part 5 line 8 "Line 8: Enter the amount from line 20 of Part 3 as a positive amount.": line 20
of Part 3 as a positive amount, 0 when line 20 is not negative."""

CPP_PART_5_LINE_9_LESSER = CATALOG.declare("cpp_part_5_line_9_lesser", Decimal)
"""Part 5 line 9 candidate, "Line 9: Enter whichever is less: amount from line 23 of Part 3 or line
8.": the lesser of line 23 of Part 3 and line 8, which line 9 takes only when the count of line
20 negative and line 23 positive applies. Signed, as line 23 of Part 3 is."""

CPP_PART_5_LINE_9 = CATALOG.declare("cpp_part_5_line_9", Decimal, non_negative=True)
"""Part 5 line 9 "Line 9: Enter whichever is less: amount from line 23 of Part 3 or line 8." "If
not, enter "0" on line 9": the candidate above when line 20 of Part 3 is negative and line 23 is
positive, else "0"."""

CPP_PART_5_LINE_10 = CATALOG.declare("cpp_part_5_line_10", Decimal)
"""Part 5 line 10 "Line 10: Line 7 plus line 9 =": the sum of lines 7 and 9. Signed."""

CPP_PART_5_LINE_12 = CATALOG.declare("cpp_part_5_line_12", Decimal, non_negative=True)
"""Part 5 line 12 "Line 12: Enter the amount from line 23 of Part 3 if positive. If not, enter
"0".": line 23 of Part 3 when it is positive, else 0."""

CPP_PART_5_LINE_13 = CATALOG.declare("cpp_part_5_line_13", Decimal)
"""Part 5 line 13 "Line 13: Line 11 minus line 12 =": the total actual second additional
contributions from line 21 of Part 3 (line 11) less line 12. Signed."""

CPP_PART_5_LINE_14 = CATALOG.declare("cpp_part_5_line_14", Decimal, non_negative=True)
"""Part 5 line 14 "Line 14: Enter the amount from line 23 of Part 3 as a positive amount.": line 23
of Part 3 as a positive amount, 0 when line 23 is not negative."""

CPP_PART_5_LINE_15_LESSER = CATALOG.declare("cpp_part_5_line_15_lesser", Decimal)
"""Part 5 line 15 candidate, "Line 15: Enter whichever is less: amount from line 20 of Part 3 or
line 14.": the lesser of line 20 of Part 3 and line 14, which line 15 takes only when the count
of line 20 positive and line 23 negative applies. Signed, as line 20 of Part 3 is."""

CPP_PART_5_LINE_15 = CATALOG.declare("cpp_part_5_line_15", Decimal, non_negative=True)
"""Part 5 line 15 "Line 15: Enter whichever is less: amount from line 20 of Part 3 or line 14." "If
not, enter "0" on line 15": the candidate above when line 20 of Part 3 is positive and line 23
is negative, else "0"."""

CPP_PART_5_LINE_16 = CATALOG.declare("cpp_part_5_line_16", Decimal)
"""Part 5 line 16 "Line 16: Line 13 plus line 15 =": the sum of lines 13 and 15. Signed."""

CPP_PART_5_LINE_19 = CATALOG.declare("cpp_part_5_line_19", Decimal, non_negative=True)
"""Part 5 line 19 "Line 19: Line 17 minus line 18 (if negative, enter "0") (maximum $67,800) =":
the amount from line B of Part 2 less the amount from line E of Part 2, not below zero. The
form's $67,800 is the full-year maximum."""

CPP_PART_5_LINE_20 = CATALOG.declare("cpp_part_5_line_20", Decimal)
"""Part 5 line 20 "Line 20: Amount from line 10 multiplied by 16.80672 =": line 10 times 16.80672,
rounded half-up to the cent by the dataset. Signed, as line 10 is: the form prints no floor."""

CPP_PART_5_LINE_21 = CATALOG.declare("cpp_part_5_line_21", Decimal, non_negative=True)
"""Part 5 line 21 "Line 21: Line 19 minus line 20 (if negative, enter "0") =": line 19 less line
20, not below zero."""

CPP_PART_5_LINE_22 = CATALOG.declare("cpp_part_5_line_22", Decimal)
"""Part 5 line 22 "Line 22: Enter whichever is less: amount from line 4 or line 21.": the lesser of
line 4 and line 21. Signed, as line 4 is."""

CPP_PART_5_LINE_25 = CATALOG.declare("cpp_part_5_line_25", Decimal, non_negative=True)
"""Part 5 line 25 "Line 25: Line 23 minus line 24 (if negative, enter "0" on lines 25 and 29, and
continue at line 30) =": the amount from line 18 (the basic exemption) less the employment
income (line 1 of Part 3), not below zero. Line 25 is 0 when the employment income is not less
than line 18, so the form's gate "If the amount from line 1 of Part 3 is less than line 18,
complete lines 23 to 29. If not, enter "0" on line 29" needs no count: line 29 is 0 then too."""

CPP_PART_5_LINE_28 = CATALOG.declare("cpp_part_5_line_28", Decimal, non_negative=True)
"""Part 5 line 28 "Line 28: Line 26 minus line 27 (if negative, enter "0") =": line 4 less line 19,
not below zero."""

CPP_PART_5_LINE_29 = CATALOG.declare("cpp_part_5_line_29", Decimal, non_negative=True)
"""Part 5 line 29 "Line 29: Line 25 minus line 28 (if negative, enter "0") =": line 25 less line
28, not below zero. It is 0 when line 1 of Part 3 is not less than line 18, because line 25 is
then 0."""

CPP_PART_5_LINE_30 = CATALOG.declare("cpp_part_5_line_30", Decimal, non_negative=True)
"""Part 5 line 30 "Line 30: Self-employment income and other earnings subject to base and first
additional contributions: Line 22 minus line 29 (if negative, enter "0") =": line 22 less line
29, not below zero. Read by lines 43 and 44."""

CPP_PART_5_LINE_33 = CATALOG.declare("cpp_part_5_line_33", Decimal)
"""Part 5 line 33 "Line 33: Line 31 plus line 32 =": line 4 (line 31) plus the amount from line 2
of Part 3 (line 32). Signed, as line 4 is."""

CPP_PART_5_LINE_35 = CATALOG.declare("cpp_part_5_line_35", Decimal)
"""Part 5 line 35 "Line 35: Amount from line 16 divided by 4% =": line 16 divided by 0.04, rounded
half-up to the cent by the dataset. Signed, as line 16 is: the form prints no floor."""

CPP_PART_5_LINE_36 = CATALOG.declare("cpp_part_5_line_36", Decimal)
"""Part 5 line 36 "Line 36: Line 34 minus line 35 =": the amount from line C of Part 2 less line
35. Signed: the form prints no floor, and line 42 takes the lesser of this and line 41."""

CPP_PART_5_LINE_39 = CATALOG.declare("cpp_part_5_line_39", Decimal)
"""Part 5 line 39 "Line 39: Line 37 minus line 38 =": line 4 (line 37) less the amount from line 25
(line 38, "if any"). Signed: the form prints no floor."""

CPP_PART_5_LINE_41 = CATALOG.declare("cpp_part_5_line_41", Decimal)
"""Part 5 line 41 "Line 41: Line 39 minus line 40 =": line 39 less the amount from line 30 (line
40). Signed: the form prints no floor."""

CPP_PART_5_LINE_42_LESSER = CATALOG.declare("cpp_part_5_line_42_lesser", Decimal)
"""Part 5 line 42 candidate, "Line 42: Enter whichever is less: amount from line 36 or line 41.":
the lesser of lines 36 and 41, which line 42 takes only when the count of line 33 more than line
17 applies. Signed: the form prints no floor."""

CPP_PART_5_LINE_42 = CATALOG.declare("cpp_part_5_line_42", Decimal)
"""Part 5 line 42 "Line 42: Enter whichever is less: amount from line 36 or line 41." "If not,
enter "0" on line 42": the candidate above when line 33 is more than line 17, else "0". Signed:
the form prints no floor, so a negative lesser stays negative. Read by line 45."""

CPP_PART_5_LINE_43 = CATALOG.declare("cpp_part_5_line_43", Decimal, non_negative=True)
"""Part 5 line 43 "Required base contributions on CPP pensionable earnings: Line 43: amount from
line 30 multiplied by 9.9% (maximum $6,712.20) =": the base contribution tier on line 30, the
same tier Part 4 line 10 takes, capped at the maximum."""

CPP_PART_5_LINE_44 = CATALOG.declare("cpp_part_5_line_44", Decimal, non_negative=True)
"""Part 5 line 44 "Required first additional contributions on CPP pensionable earnings: Line 44:
amount from line 30 multiplied by 2% (maximum $1,356.00) =": the first additional contribution
tier on line 30, capped at the maximum."""

CPP_PART_5_LINE_45 = CATALOG.declare("cpp_part_5_line_45", Decimal, non_negative=True)
"""Part 5 line 45 "Required second additional contributions on CPP pensionable earnings: Line 45:
amount from line 42 multiplied by 8% (maximum $792.00) =": the second additional contribution
tier on line 42. A negative line 42 (a loss with employment income above $71,300) floors the
band at 0, so the line is 0."""

CPP_PART_5_LINE_46 = CATALOG.declare("cpp_part_5_line_46", Decimal, non_negative=True)
"""Part 5 line 46 "Line 44 plus line 45 =": the sum of lines 44 and 45."""

CPP_PART_5_LINE_47 = CATALOG.declare("cpp_part_5_line_47", Decimal, non_negative=True)
"""Part 5 line 47 "Line 47: Line 43 plus line 46 =": the sum of lines 43 and 46."""

CPP_PART_5_LINE_48_LINE_24_IF_POSITIVE = CATALOG.declare(
    "cpp_part_5_line_48_line_24_if_positive", Decimal, non_negative=True
)
"""Part 5 line 48 "Amount from line 24 of Part 3 (if positive)": line 24 of Part 3 as a positive
amount, 0 when line 24 is negative or "0". The base of line 48, before the multiplier."""

CPP_PART_5_LINE_48 = CATALOG.declare("cpp_part_5_line_48", Decimal, non_negative=True)
"""Part 5 line 48 "Amount from line 24 of Part 3 (if positive) multiplied by 2 =": the amount
from line 24 of Part 3 if positive, multiplied by 2, rounded half-up to the cent by the dataset.
The overpayment's offset, subtracted on line 49."""

CPP_PART_5_LINE_49 = CATALOG.declare("cpp_part_5_line_49", Decimal)
"""Part 5 line 49 "CPP contributions payable on self-employment income and other earnings: Line 47
minus line 48. If positive, enter the amount (in dollars and cents) on line 42100 of your return
and continue at line 51. If negative, show in brackets and continue at line 50. =": line 47 less
line 48. Signed: a negative result is shown in brackets and line 50 takes it as a positive
amount."""

CPP_PART_5_LINE_50_LINE_49_POSITIVE = CATALOG.declare(
    "cpp_part_5_line_50_line_49_positive", Decimal, non_negative=True
)
"""Part 5 line 50 "amount from line 49 entered as a positive amount": "0" less line 49, not below
zero, so 0 when line 49 is positive or "0". The base of line 50, before the rate."""

CPP_PART_5_LINE_50 = CATALOG.declare("cpp_part_5_line_50", Decimal, non_negative=True)
"""Part 5 line 50 "CPP overpayment: Enter the result of the following calculation (in dollars and
cents) on line 44800 of your return: amount from line 49 entered as a positive amount multiplied
by 50% =": the overpayment, the amount from line 49 as a positive amount times 50%, rounded
half-up to the cent by the dataset."""

CPP_PART_5_LINE_51 = CATALOG.declare("cpp_part_5_line_51", Decimal, non_negative=True)
"""Part 5 line 51 "If line 16 of Part 3 is positive or "0", enter the amount from line 11 of Part 3
at lines 51 and 57, and continue at line 58. If not, enter the amount from line 9 of Part 3 and
continue at line 52.": the required base contributions (Part 3 line 11) when line 16 is not
negative, else the actual base contributions (Part 3 line 9)."""

CPP_PART_5_LINE_52 = CATALOG.declare("cpp_part_5_line_52", Decimal, non_negative=True)
"""Part 5 line 52 "If line 16 of Part 3 is negative: Line 52: Enter the amount from line 16 of Part
3 as a positive amount.": line 16 of Part 3 as a positive amount, 0 when line 16 is positive or
"0"."""

CPP_PART_5_LINE_53_LESSER = CATALOG.declare("cpp_part_5_line_53_lesser", Decimal)
"""Part 5 line 53 candidate, "Line 53: If line 16 of Part 3 is negative and line 19 of Part 3 is
positive, enter whichever is less: amount from line 19 of Part 3 or line 52.": the lesser of line
19 of Part 3 and line 52, which line 53 takes only when line 16 of Part 3 is negative and line 19
is positive. Signed, as line 19 of Part 3 is."""

CPP_PART_5_LINE_53 = CATALOG.declare("cpp_part_5_line_53", Decimal, non_negative=True)
"""Part 5 line 53 "If line 16 of Part 3 is negative and line 19 of Part 3 is positive, enter
whichever is less: amount from line 19 of Part 3 or line 52. If not, enter "0".": the candidate
above when line 16 of Part 3 is negative and line 19 is positive, else "0"."""

CPP_PART_5_LINE_54 = CATALOG.declare("cpp_part_5_line_54", Decimal, non_negative=True)
"""Part 5 line 54 "Line 52 minus line 53 =": line 52 less line 53. Line 53 is never more than line
52 (it is the lesser of line 19 and line 52, or 0), so the result is not negative."""

CPP_PART_5_LINE_55 = CATALOG.declare("cpp_part_5_line_55", Decimal, non_negative=True)
"""Part 5 line 55 "Line 51 plus line 53 =": the sum of lines 51 and 53."""

CPP_PART_5_LINE_23_AND_LINE_54_POSITIVE = CATALOG.declare(
    "cpp_part_5_line_23_and_line_54_positive", int, non_negative=True
)
"""Count, Schedule 8 Part 5 line 56 "If line 23 of Part 3 and line 54 are both positive, enter
whichever is less. If not, enter "0"": 1 when line 23 of Part 3 and line 54 are both more than 0,
0 otherwise."""

CPP_PART_5_LINE_56_LESSER = CATALOG.declare("cpp_part_5_line_56_lesser", Decimal)
"""Part 5 line 56 candidate, "enter whichever is less": the lesser of line 23 of Part 3 and line
54, which line 56 takes only when both are positive. Signed, as line 23 of Part 3 is."""

CPP_PART_5_LINE_56 = CATALOG.declare("cpp_part_5_line_56", Decimal, non_negative=True)
"""Part 5 line 56 "If line 23 of Part 3 and line 54 are both positive, enter whichever is less. If
not, enter "0".": the candidate above when line 23 of Part 3 and line 54 are both positive, else
"0"."""

CPP_PART_5_LINE_57 = CATALOG.declare("cpp_part_5_line_57", Decimal, non_negative=True)
"""Part 5 line 57 "Base CPP contributions through employment income: Line 55 plus line 56 Enter
this amount (in dollars and cents) on line 30800 of your return.": the sum of lines 55 and 56."""

CPP_PART_5_LINE_58 = CATALOG.declare("cpp_part_5_line_58", Decimal, non_negative=True)
"""Part 5 line 58 "If line 19 of Part 3 is positive or "0", enter the amount from line 12 of Part 3
at line 58 and line 64, and continue at line 65. If not, enter the amount from line 10 of Part 3
and continue at line 59.": the required first additional contributions (Part 3 line 12) when line
19 is not negative, else the actual first additional contributions (Part 3 line 10)."""

CPP_PART_5_LINE_59 = CATALOG.declare("cpp_part_5_line_59", Decimal, non_negative=True)
"""Part 5 line 59 "If line 19 of Part 3 is negative: Line 59: Enter the amount from line 19 of Part
3 as a positive amount.": line 19 of Part 3 as a positive amount, 0 when line 19 is positive or
"0"."""

CPP_PART_5_LINE_60_LESSER = CATALOG.declare("cpp_part_5_line_60_lesser", Decimal)
"""Part 5 line 60 candidate, "If line 16 of Part 3 is positive, enter whichever is less: Line 60:
amount from line 16 of Part 3 or line 59.": the lesser of line 16 of Part 3 and line 59, which
line 60 takes only when line 16 of Part 3 is positive. Signed, as line 16 of Part 3 is."""

CPP_PART_5_LINE_60 = CATALOG.declare("cpp_part_5_line_60", Decimal, non_negative=True)
"""Part 5 line 60 "If not, enter "0".": the candidate above when line 16 of Part 3 is positive,
else "0"."""

CPP_PART_5_LINE_61 = CATALOG.declare("cpp_part_5_line_61", Decimal, non_negative=True)
"""Part 5 line 61 "Line 61: Line 59 minus line 60 =": line 59 less line 60. Line 60 is never more
than line 59 (it is the lesser of line 16 and line 59, or 0), so the result is not negative."""

CPP_PART_5_LINE_62 = CATALOG.declare("cpp_part_5_line_62", Decimal, non_negative=True)
"""Part 5 line 62 "Line 62: Line 58 plus line 60 =": the sum of lines 58 and 60."""

CPP_PART_5_LINE_23_LESS_LINE_56 = CATALOG.declare("cpp_part_5_line_23_less_line_56", Decimal)
"""Part 5 line 63 candidate, "the result of line 23 of Part 3 minus line 56": line 23 of Part 3
less line 56. Signed: the form prints no floor."""

CPP_PART_5_LINE_23_AND_LINE_61_POSITIVE = CATALOG.declare(
    "cpp_part_5_line_23_and_line_61_positive", int, non_negative=True
)
"""Count, Schedule 8 Part 5 line 63 "If line 23 of Part 3 and line 61 are both positive, enter
whichever is less": 1 when line 23 of Part 3 and line 61 are both more than 0, 0 otherwise."""

CPP_PART_5_LINE_63_LESSER = CATALOG.declare("cpp_part_5_line_63_lesser", Decimal)
"""Part 5 line 63 candidate, "Line 63: amount from line 61 or the result of line 23 of Part 3 minus
line 56": the lesser of line 61 and line 23 of Part 3 less line 56, which line 63 takes only when
line 23 of Part 3 and line 61 are both positive. Signed: the form prints no floor."""

CPP_PART_5_LINE_63 = CATALOG.declare("cpp_part_5_line_63", Decimal, non_negative=True)
"""Part 5 line 63 "If line 23 of Part 3 and line 61 are both positive, enter whichever is less:
Line 63: amount from line 61 or the result of line 23 of Part 3 minus line 56. If not, enter
"0".": the candidate above when line 23 of Part 3 and line 61 are both positive, else "0"."""

CPP_PART_5_LINE_64 = CATALOG.declare("cpp_part_5_line_64", Decimal, non_negative=True)
"""Part 5 line 64 "Line 64: Line 62 plus line 63 =": the sum of lines 62 and 63."""

CPP_PART_5_LINE_65 = CATALOG.declare("cpp_part_5_line_65", Decimal, non_negative=True)
"""Part 5 line 65 "If line 23 of Part 3 is positive or "0", enter the amount from line 22 of Part 3
on line 65 and line 68, and continue at line 69. If not, enter the amount from line 21 of Part 3
and continue at line 66.": the required second additional contributions (Part 3 line 22) when
line 23 is not negative, else the T4 box 16A total (Part 3 line 21)."""

CPP_PART_5_LINE_66 = CATALOG.declare("cpp_part_5_line_66", Decimal, non_negative=True)
"""Part 5 line 66 "If line 23 of Part 3 is negative: Line 66: Enter the amount from line 23 of Part
3 as a positive amount.": line 23 of Part 3 as a positive amount, 0 when line 23 is positive or
"0"."""

CPP_PART_5_LINE_67_LESSER = CATALOG.declare("cpp_part_5_line_67_lesser", Decimal)
"""Part 5 line 67 candidate, "If line 20 of Part 3 is positive, enter whichever is less: Line 67:
amount from line 20 of Part 3 or line 66.": the lesser of line 20 of Part 3 and line 66, which
line 67 takes only when line 20 of Part 3 is positive. Signed, as line 20 of Part 3 is."""

CPP_PART_5_LINE_67 = CATALOG.declare("cpp_part_5_line_67", Decimal, non_negative=True)
"""Part 5 line 67 "If not, enter "0".": the candidate above when line 20 of Part 3 is positive,
else "0"."""

CPP_PART_5_LINE_68 = CATALOG.declare("cpp_part_5_line_68", Decimal, non_negative=True)
"""Part 5 line 68 "Line 68: Line 65 plus line 67 =": the sum of lines 65 and 67."""

CPP_PART_5_LINE_69 = CATALOG.declare("cpp_part_5_line_69", Decimal, non_negative=True)
"""Part 5 line 69 "Deduction for CPP enhanced contributions on employment income: Line 69: Line 64
plus line 68 Enter this amount (in dollars and cents) on line 22215 of your return.": the sum of
lines 64 and 68."""

CPP_PART_5_LINE_49_IF_POSITIVE = CATALOG.declare(
    "cpp_part_5_line_49_if_positive", Decimal, non_negative=True
)
"""Part 5 line 49 "If positive, enter the amount (in dollars and cents) on line 42100 of your
return and continue at line 51.": line 49 when it is positive, else "0" (line 49 less "0", not
below zero). 11_net_tax takes it once for each Part 5 completed, for line 42100."""

CPP_PART_5_LINE_70 = CATALOG.declare("cpp_part_5_line_70", Decimal, non_negative=True)
"""Part 5 line 70 "Base CPP contributions through self-employment income and other earnings: Line
70: Enter the result of the following calculation (in dollars and cents) on line 31000 of your
return. amount from line 43 multiplied by 50% =": line 43 times 0.5, rounded half-up to the cent.
08_non_refundable_credits takes it once for each Part 5 completed, for line 31000."""

CPP_PART_5_LINE_71 = CATALOG.declare("cpp_part_5_line_71", Decimal, non_negative=True)
"""Part 5 line 71 "Line 71: Amount from line 44 multiplied by 50% =": line 44 times 0.5, rounded
half-up to the cent. Line 72 adds it to line 70, and line 81 repeats it."""

CPP_PART_5_LINE_72 = CATALOG.declare("cpp_part_5_line_72", Decimal, non_negative=True)
"""Part 5 line 72 "Line 72: Line 70 plus line 71 =": the sum of lines 70 and 71."""

CPP_PART_5_LINE_73 = CATALOG.declare("cpp_part_5_line_73", Decimal, non_negative=True)
"""Part 5 line 73 "Enter the amount from line 24 of Part 3 if positive. If not, enter "0".": line 24
of Part 3 when it is positive, else "0" (line 24 less "0", not below zero). Part 5 line 48 takes the
same amount through its own step."""

CPP_PART_5_LINE_74 = CATALOG.declare("cpp_part_5_line_74", Decimal)
"""Part 5 line 74 "Line 74: Line 72 minus line 73 (if negative, show in brackets) =": line 72 less
line 73, signed. Line 86 takes it as a positive amount when it is negative."""

CPP_PART_5_LINE_75_BASE = CATALOG.declare("cpp_part_5_line_75_base", Decimal, non_negative=True)
"""Part 5 line A, "Enter whichever is less: amount from line 72 or line 73 Line A": the lesser of
lines 72 and 73. Line 75 multiplies it by 83.1933%, and line 77 takes line 76 off it."""

CPP_PART_5_LINE_75 = CATALOG.declare("cpp_part_5_line_75", Decimal, non_negative=True)
"""Part 5 line 75 "Line 75: amount from line 72 or line 73 Line A multiply by 83.1933 =": line A
times 0.831933, rounded half-up to the cent. Line 76 is a copy of it, and line 79 copies it too."""

CPP_PART_5_LINE_77 = CATALOG.declare("cpp_part_5_line_77", Decimal, non_negative=True)
"""Part 5 line 77 "Line 77: Amount A minus line 76 =": line A less line 75 (line 76 is a copy of
line 75). Line 82 takes it."""

CPP_PART_5_LINE_80 = CATALOG.declare("cpp_part_5_line_80", Decimal)
"""Part 5 line 80 "Line 80: Line 78 minus line 79 =": line 70 less line 75 (lines 78 and 79 are
copies of them), signed, since line 75 can be a cent more than line 70 when the amounts are a few
dollars or less."""

CPP_PART_5_LINE_83 = CATALOG.declare("cpp_part_5_line_83", Decimal, non_negative=True)
"""Part 5 line 83 "Line 83: Line 81 minus line 82 =": line 71 less line 77 (lines 81 and 82 are
copies of lines 71 and 77). The form prints no brackets for it."""

CPP_PART_5_LINE_84 = CATALOG.declare("cpp_part_5_line_84", Decimal, non_negative=True)
"""Part 5 line 84 "Line 84: Amount from line 45 multiplied by 50% =": line 45 times 0.5, rounded
half-up to the cent. Line 85 is a copy of it."""

CPP_PART_5_LINE_86 = CATALOG.declare("cpp_part_5_line_86", Decimal, non_negative=True)
"""Part 5 line 86 "If line 74 is negative, enter it as a positive amount. If line 74 is positive or
"0", enter the amount from line 85 on line 87 and continue at line 88.": "0" less line 74, not
below zero, so 0 when line 74 is positive or "0"."""

CPP_PART_5_LINE_87 = CATALOG.declare("cpp_part_5_line_87", Decimal, non_negative=True)
"""Part 5 line 87 "Line 87: Line 85 minus line 86 (if negative, enter "0") =": line 84 less line
86, not below zero (line 85 is a copy of line 84)."""

CPP_PART_5_LINE_88 = CATALOG.declare("cpp_part_5_line_88", Decimal, non_negative=True)
"""Part 5 line 88 "Deduction for CPP enhanced contributions on self-employment income and other
earnings: Add lines 80, 81, 83, 84, and 87. Enter this amount (in dollar and cents) on line 22200
of your return. =": the sum of lines 80, 81, 83, 84 and 87, as printed. When line 74 is not
negative, line 87 equals line 84, so lines 84 and 71 each enter twice."""

CPP_PART_5_DEDUCTION_ON_SELF_EMPLOYMENT = CATALOG.declare(
    "cpp_part_5_deduction_on_self_employment", Decimal, non_negative=True
)
"""Part 5 line 88 on T1 line 22200, once for each Part 5 completed (1 or 0). Summed with the Part 4
deduction into cpp_deduction_on_self_employment_and_other_earnings."""

CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS = CATALOG.declare(
    "cpp_deduction_on_self_employment_and_other_earnings", Decimal, non_negative=True
)
"""T1 line 22200: the Part 4 deduction (cpp_deduction_on_self_employment) plus the Part 5 deduction
(cpp_part_5_deduction_on_self_employment), read by 05_deductions and 20_alternative_minimum_tax."""

SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN = CATALOG.declare(
    "schedule_8_cpp_base_contributions_on_return", Decimal, non_negative=True
)
"""Base CPP contributions of Schedule 8, for T1 line 30800 and ON428 line 58240: Part 5 line 57
"Base CPP contributions through employment income: Line 55 plus line 56 Enter this amount (in
dollars and cents) on line 30800 of your return." when Part 5 is completed, else the Part 3 route,
cpp_part_3_base_contributions_on_return. The choice is by the count of cpp_part_5_completed. The
form's total over its copies, 0 with none, is added to Form RC381's
(rc381_cpp_base_contributions_on_return) in cpp_base_contributions_on_return."""

SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN = CATALOG.declare(
    "schedule_8_cpp_enhanced_contributions_on_return", Decimal, non_negative=True
)
"""Enhanced CPP contributions of Schedule 8, for T1 line 22215: Part 5 line 69 "Deduction for CPP
enhanced contributions on employment income: Line 64 plus line 68 Enter this amount (in dollars and
cents) on line 22215 of your return." when Part 5 is completed, else the Part 3 route,
cpp_part_3_enhanced_contributions_on_return. A deduction from total income, not a credit. The
form's total over its copies, 0 with none, is added to Form RC381's
(rc381_cpp_enhanced_contributions_on_return) in cpp_enhanced_contributions_on_return."""

SCHEDULE_8_CPP_OVERPAYMENT = CATALOG.declare(
    "schedule_8_cpp_overpayment", Decimal, non_negative=True
)
"""CPP overpayment of Schedule 8, for T1 line 44800: Part 5 line 50 "CPP overpayment: Enter the
result of the following calculation (in dollars and cents) on line 44800 of your return: amount
from line 49 entered as a positive amount multiplied by 50% =" when Part 5 is completed, else the
Part 3 route, cpp_part_3_overpayment. The form's total over its copies, 0 with none, is added to
Form RC381's (rc381_cpp_overpayment_on_return) in cpp_overpayment."""

CPP_BASE_CONTRIBUTIONS_ON_RETURN = CATALOG.declare(
    "cpp_base_contributions_on_return", Decimal, non_negative=True
)
"""Base CPP contributions on the return, T1 line 30800 and ON428 line 58240: the total of
Schedule 8 (schedule_8_cpp_base_contributions_on_return) plus the total of Form RC381
(rc381_cpp_base_contributions_on_return, Part 4 line 98 or Part 3a line 70 or Part 3b line 81).
The return carries one of the two forms, so one of the two totals is 0."""

CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN = CATALOG.declare(
    "cpp_enhanced_contributions_on_return", Decimal, non_negative=True
)
"""Enhanced CPP contributions on the return, T1 line 22215: the total of Schedule 8
(schedule_8_cpp_enhanced_contributions_on_return) plus the total of Form RC381
(rc381_cpp_enhanced_contributions_on_return, Part 4 line 110 or Part 3a line 73 or Part 3b line
93). A deduction from total income, not a credit. The return carries one of the two forms, so one
of the two totals is 0."""

CPP_OVERPAYMENT = CATALOG.declare("cpp_overpayment", Decimal, non_negative=True)
"""CPP overpayment, T1 line 44800: the total of Schedule 8 (schedule_8_cpp_overpayment) plus the
total of Form RC381 (rc381_cpp_overpayment_on_return, Part 4 line 91 or Part 3a line 74). The
return carries one of the two forms, so one of the two totals is 0. The return's refund total
reads it at line 152 "CPP or QPP overpayment" (Form 5006-R, line 152 and line 44800)."""


# Form T1-M, Moving Expenses Deduction, one copy for each move (T1 line 21900). The caller's inputs
# of one move are the fields of the record list `ca/t1_m_moves`, in the form's line order; the
# computed lines are the form's own lines, and the form exports line 29 and line 30.

MOVING_OLD_HOME_DISTANCE = CATALOG.declare("moving_old_home_distance", Decimal, non_negative=True)
"""Distance from the old home, Form T1-M Part 2 line 1 "Distance in kilometres between your old home
and your new work location or educational institution": a starting amount in kilometres."""

MOVING_NEW_HOME_DISTANCE = CATALOG.declare("moving_new_home_distance", Decimal, non_negative=True)
"""Distance from the new home, Form T1-M Part 2 line 2 "Distance in kilometres between your new home
and your new work location or educational institution": a starting amount in kilometres."""

MOVING_TRANSPORTATION_AND_STORAGE = CATALOG.declare(
    "moving_transportation_and_storage", Decimal, non_negative=True
)
"""Transportation and storage costs, Form T1-M Part 4 line 4 "Transportation and storage costs for
household items": a starting amount."""

MOVING_TRAVEL_EXPENSES = CATALOG.declare("moving_travel_expenses", Decimal, non_negative=True)
"""Travel expenses from the old home to the new home, Form T1-M Part 4 line 5 "Travel expenses":
a starting amount, as the filer works it out by either method."""

MOVING_ACCOMMODATION_EXPENSES = CATALOG.declare(
    "moving_accommodation_expenses", Decimal, non_negative=True
)
"""Accommodation expenses of the move, Form T1-M Part 4 line 6 "Accommodation expenses": a starting
amount."""

MOVING_MEAL_EXPENSES = CATALOG.declare("moving_meal_expenses", Decimal, non_negative=True)
"""Meal expenses of the move, Form T1-M Part 4 line 7 "Meal expenses": a starting amount, as the
filer works it out by either method."""

MOVING_TEMPORARY_LODGING = CATALOG.declare("moving_temporary_lodging", Decimal, non_negative=True)
"""Temporary accommodation expenses near the new or old home, Form T1-M Part 4 line 9 "Temporary
living expenses near new or old home (maximum 15 days)" "Accommodation expenses": a starting
amount."""

MOVING_TEMPORARY_MEALS = CATALOG.declare("moving_temporary_meals", Decimal, non_negative=True)
"""Temporary meal expenses near the new or old home, Form T1-M Part 4 line 10 "Temporary living
expenses near new or old home (maximum 15 days)" "Meal expenses": a starting amount."""

MOVING_LEASE_CANCELLATION = CATALOG.declare("moving_lease_cancellation", Decimal, non_negative=True)
"""Cost of cancelling the lease for the old home, Form T1-M Part 4 line 12 "Cost of cancelling the
lease for your old home": a starting amount."""

MOVING_INCIDENTAL_COSTS = CATALOG.declare("moving_incidental_costs", Decimal, non_negative=True)
"""Incidental costs related to the move, Form T1-M Part 4 line 13 "Incidental costs related to the
move (specify):": a starting amount."""

MOVING_OLD_HOME_MAINTENANCE = CATALOG.declare(
    "moving_old_home_maintenance", Decimal, non_negative=True
)
"""Costs to maintain the old home when vacant, Form T1-M Part 4 line 14 "Costs to maintain your old
home when vacant (maximum $5,000)": the costs the caller paid, before the maximum of line 14 (the
`ca/moving_old_home_maintenance_cap` dataset) is checked."""

MOVING_SELLING_COMMISSION = CATALOG.declare("moving_selling_commission", Decimal, non_negative=True)
"""Real estate commission on the sale of the old home, Form T1-M Part 4 line 16 "Real estate
commission": a starting amount."""

MOVING_SELLING_LEGAL_FEES = CATALOG.declare("moving_selling_legal_fees", Decimal, non_negative=True)
"""Legal or notarial fees on the sale of the old home, Form T1-M Part 4 line 17 "Legal or notarial
fees": a starting amount."""

MOVING_SELLING_ADVERTISING = CATALOG.declare(
    "moving_selling_advertising", Decimal, non_negative=True
)
"""Advertising on the sale of the old home, Form T1-M Part 4 line 18 "Advertising": a starting
amount."""

MOVING_SELLING_OTHER_COSTS = CATALOG.declare(
    "moving_selling_other_costs", Decimal, non_negative=True
)
"""Other selling costs of the old home, Form T1-M Part 4 line 19 "Other selling costs (specify):": a
starting amount."""

MOVING_BUYING_LEGAL_FEES = CATALOG.declare("moving_buying_legal_fees", Decimal, non_negative=True)
"""Legal or notarial fees on the purchase of the new home, Form T1-M Part 4 line 21 "Legal or
notarial fees": a starting amount, claimable only when the old home was sold because of the move."""

MOVING_BUYING_TAXES = CATALOG.declare("moving_buying_taxes", Decimal, non_negative=True)
"""Taxes paid for the registration or transfer of title to the new home, Form T1-M Part 4 line 22
"Taxes paid for the registration or transfer of title (do not include GST/HST)": a starting
amount."""

MOVING_REIMBURSEMENT = CATALOG.declare("moving_reimbursement", Decimal, non_negative=True)
"""Reimbursement or allowance for the moving expenses, Form T1-M Part 4 line 25 "Enter any
reimbursement or allowance that is not included in your income and that you received for
moving expenses included in the amount on line 24.": a starting amount."""

MOVING_NET_ELIGIBLE_INCOME = CATALOG.declare(
    "moving_net_eligible_income", Decimal, non_negative=True
)
"""Net eligible income at the new work location, Form T1-M Part 4 line 28 "Net eligible income": the
employment or self-employment income, or the student's taxable awards, the caller enters as the
form takes them; a starting amount."""

MOVING_BUSINESS_INCOME = CATALOG.declare("moving_business_income", Decimal, non_negative=True)
"""Business income at the new work location, Form T1-M Part 4 line 28 "Net eligible income": "the
net amounts earned at the new work location that are included on lines 13500, 13700, 13900, 14100,
and 14300 of your return", the positive net of the Form T2125 statements on business line 1
(`core/record_positive_total`). A loss counts 0, so it is the part of line 13500 that line 28 is
taken from."""

MOVING_PROFESSIONAL_INCOME = CATALOG.declare(
    "moving_professional_income", Decimal, non_negative=True
)
"""Professional income at the new work location, Form T1-M Part 4 line 28 "Net eligible income"
("the net amounts earned at the new work location that are included on lines 13500, 13700, 13900,
14100, and 14300 of your return"), the positive net of the Form T2125 statements on professional
line 2 (`core/record_positive_total`). A loss counts 0, so it is the part of line 13700 that line 28
is taken from."""

MOVING_COMMISSION_INCOME = CATALOG.declare("moving_commission_income", Decimal, non_negative=True)
"""Commission income at the new work location, Form T1-M Part 4 line 28 "Net eligible income"
("the net amounts earned at the new work location that are included on lines 13500, 13700, 13900,
14100, and 14300 of your return"), the positive net of the Form T2125 statements on commission line
3 (`core/record_positive_total`). A loss counts 0, so it is the part of line 13900 that line 28 is
taken from."""

MOVING_FARMING_INCOME = CATALOG.declare("moving_farming_income", Decimal, non_negative=True)
"""Farming income at the new work location, Form T1-M Part 4 line 28 "Net eligible income" ("the
net amounts earned at the new work location that are included on lines 13500, 13700, 13900, 14100,
and 14300 of your return"), the positive net of the Form T2042 statements
(`core/record_positive_total`). A loss counts 0, so it is the part of line 14100 that line 28 is
taken from."""

MOVING_FISHING_INCOME = CATALOG.declare("moving_fishing_income", Decimal, non_negative=True)
"""Fishing income at the new work location, Form T1-M Part 4 line 28 "Net eligible income" ("the
net amounts earned at the new work location that are included on lines 13500, 13700, 13900, 14100,
and 14300 of your return"), the positive net of the Form T2121 statements
(`core/record_positive_total`). A loss counts 0, so it is the part of line 14300 that line 28 is
taken from."""

MOVING_ELIGIBLE_INCOME_LINES = CATALOG.declare(
    "moving_eligible_income_lines", Decimal, non_negative=True
)
"""Income lines that Form T1-M line 28 is taken from, Form T1-M Part 4 line 28 "Net eligible
income": the employment income (line 10100), the other employment income (line 10400), the taxable
scholarships of a student and the five self-employment amounts above, added (`core/sum`). Line 28
is at most this sum, a loss counting 0. The sum is not a form line."""

MOVING_NET_ELIGIBLE_INCOME_CHECKED = CATALOG.declare(
    "moving_net_eligible_income_checked", Decimal, non_negative=True
)
"""Net eligible income at the new work location after the check, Form T1-M Part 4 line 28 "Net
eligible income": the amount of `ca/moving_net_eligible_income` after the check that it is not more
than `ca/moving_eligible_income_lines` (`core/at_most`). Line 28 is taken from the amounts on lines
10100 and 10400, 13500, 13700, 13900, 14100 and 14300 and the taxable scholarships of a student, so
it is at most their sum (a loss counts 0). The printed text gives no other limit (looked in
t1-m-25e.pdf and 5000-g-25e.txt, found nothing), and the bound is looser than the printed net of
lines 20700, 21200, 22215, 22900, 23100 and 23200. An amount above is an input error, not capped.
Lines 29 and 30 read this amount."""

MOVING_DISTANCE_DIFFERENCE = CATALOG.declare("moving_distance_difference", Decimal)
"""Distance difference, Form T1-M Part 2 line 3 "Line 1 minus line 2": the old home distance less
the new one. The form prints no floor, so it may be negative; the 40 kilometre test reads it."""

MOVING_TRAVEL_EXPENSES_SUBTOTAL = CATALOG.declare(
    "moving_travel_expenses_subtotal", Decimal, non_negative=True
)
"""Travel expenses subtotal, Form T1-M Part 4 line 8 "Add lines 5 to 7.": lines 5, 6 and 7."""

MOVING_TEMPORARY_LIVING_SUBTOTAL = CATALOG.declare(
    "moving_temporary_living_subtotal", Decimal, non_negative=True
)
"""Temporary living subtotal, Form T1-M Part 4 line 11 "Line 9 plus line 10": lines 9 and 10."""

MOVING_OLD_HOME_MAINTENANCE_CAP = CATALOG.declare(
    "moving_old_home_maintenance_cap", Decimal, non_negative=True
)
"""Maximum costs to maintain the old home when vacant, Form T1-M Part 4 line 14 "Costs to maintain
your old home when vacant (maximum $5,000)": the $5,000, the most the line can be."""

MOVING_OLD_HOME_MAINTENANCE_CHECKED = CATALOG.declare(
    "moving_old_home_maintenance_checked", Decimal, non_negative=True
)
"""Costs to maintain the old home when vacant, not above the maximum, Form T1-M Part 4 line 14
"Costs to maintain your old home when vacant (maximum $5,000)": the caller's costs, refused above
the `ca/moving_old_home_maintenance_cap` dataset's amount."""

MOVING_LEASE_AND_INCIDENTAL_SUBTOTAL = CATALOG.declare(
    "moving_lease_and_incidental_subtotal", Decimal, non_negative=True
)
"""Lease, incidental and old home costs subtotal, Form T1-M Part 4 line 15 "Add lines 12 to 14.":
lines 12, 13 and 14 (the capped line 14)."""

MOVING_SELLING_SUBTOTAL = CATALOG.declare("moving_selling_subtotal", Decimal, non_negative=True)
"""Cost of selling the old home subtotal, Form T1-M Part 4 line 20 "Add lines 16 to 19.": lines 16,
17, 18 and 19."""

MOVING_BUYING_SUBTOTAL = CATALOG.declare("moving_buying_subtotal", Decimal, non_negative=True)
"""Cost of buying the new home subtotal, Form T1-M Part 4 line 23 "Line 21 plus line 22": lines 21
and 22."""

MOVING_TOTAL_EXPENSES = CATALOG.declare("moving_total_expenses", Decimal, non_negative=True)
"""Total moving expenses, Form T1-M Part 4 line 24 "Total moving expenses" "Add lines 4, 8, 11, 15,
20 and 23.": the transportation and storage, travel, temporary living, lease and incidental, selling
and buying subtotals."""

MOVING_NET_EXPENSES = CATALOG.declare("moving_net_expenses", Decimal, non_negative=True)
"""Net moving expenses, Form T1-M Part 4 line 26 "Net moving expenses" "Line 24 minus line 25 (if
negative, enter "0")": the total less the reimbursement, not below 0."""

MOVING_NET_EXPENSES_CARRIED = CATALOG.declare(
    "moving_net_expenses_carried", Decimal, non_negative=True
)
"""Amount from line 26 of the previous page, Form T1-M Part 4 line 27: the net moving expenses of
line 26, carried to the second page."""

MOVING_LESSER_OF_EXPENSES_AND_INCOME = CATALOG.declare(
    "moving_lesser_of_expenses_and_income", Decimal, non_negative=True
)
"""Lesser of the net moving expenses and the net eligible income, Form T1-M Part 4 "Enter whichever
is less: amount from line 27 or line 28." (before line 29): the lesser of lines 27 and 28."""

MOVING_EXPENSES_CLAIM = CATALOG.declare("moving_expenses_claim", Decimal, non_negative=True)
"""Allowable moving expenses of one move, Form T1-M Part 4 line 29 "Allowable moving expenses"
"Enter this amount on line 21900 of your return.": the lesser amount of the move, 0 when the
distance difference of line 3 is under the 40 kilometres of the `ca/moving_distance_threshold`
dataset (Part 2 "If the amount on line 3 is less than 40 kilometres, you cannot deduct your
moving expenses.")."""

MOVING_UNUSED_EXPENSES_BEFORE_TEST = CATALOG.declare(
    "moving_unused_expenses_before_test", Decimal, non_negative=True
)
"""Line 27 less line 28 of Form T1-M Part 4 line 30 "Line 27 minus line 28 (if negative, enter
"0")", before the 40 kilometre test of Part 2: the net moving expenses of line 27 less line 28, not
below 0."""

MOVING_UNUSED_EXPENSES = CATALOG.declare("moving_unused_expenses", Decimal, non_negative=True)
"""Unused moving expenses available to carry forward, Form T1-M Part 4 line 30 "Your unused moving
expenses available to carry forward to a future year": line 27 less line 28, not below 0, and 0
when the distance difference of line 3 is under the 40 kilometres of the
`ca/moving_distance_threshold` dataset (Part 2 "If the amount on line 3 is less than 40
kilometres, you cannot deduct your moving expenses. If this is the case, do not complete the rest
of this form."). Nothing on the return reads it."""

MOVING_EXPENSES_DEDUCTION = CATALOG.declare("moving_expenses_deduction", Decimal, non_negative=True)
"""Moving expenses deduction, T1 line 21900 "Moving expenses (complete Form T1-M)": line 29 of each
move's Form T1-M added over the moves (0 with none). Line 23300 and Form T691 Part 1 line 56 read
it."""

T1_M_MOVES = RecordListKind.declare(
    CATALOG,
    "t1_m_moves",
    fields=(
        MOVING_OLD_HOME_DISTANCE,
        MOVING_NEW_HOME_DISTANCE,
        MOVING_TRANSPORTATION_AND_STORAGE,
        MOVING_TRAVEL_EXPENSES,
        MOVING_ACCOMMODATION_EXPENSES,
        MOVING_MEAL_EXPENSES,
        MOVING_TEMPORARY_LODGING,
        MOVING_TEMPORARY_MEALS,
        MOVING_LEASE_CANCELLATION,
        MOVING_INCIDENTAL_COSTS,
        MOVING_OLD_HOME_MAINTENANCE,
        MOVING_SELLING_COMMISSION,
        MOVING_SELLING_LEGAL_FEES,
        MOVING_SELLING_ADVERTISING,
        MOVING_SELLING_OTHER_COSTS,
        MOVING_BUYING_LEGAL_FEES,
        MOVING_BUYING_TAXES,
        MOVING_REIMBURSEMENT,
        MOVING_NET_ELIGIBLE_INCOME,
    ),
)
"""Form T1-M, one record for each move (any number, none included): the 19 caller inputs of the
move, the lines 1, 2, 4, 5, 6, 7, 9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 22, 25 and 28 of the form,
in the form's line order. Form T1-M: "Complete a separate form for each move"."""
