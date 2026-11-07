"""The federal catalog: deductions from total income.

The split pension, union dues, child care, capital gains deduction, business investment loss,
support, carrying charges, CPP and other deduction lines, down to net income and the repayment lines
that follow it, and the lines of Form T2222 (northern residents deductions) with Chart A and Chart B
of its Step 3, which are record lists, and the moving expenses of Form T1-M (line 21900), a record
list of the moves with the lines of each move.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind, CountKind, RecordListKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

ELECTED_SPLIT_PENSION_DEDUCTION = AmountKind.declare(
    CATALOG, "elected_split_pension_deduction", non_negative=True
)
"""Deduction for elected split-pension amount, T1 line 38 and line 21000 "Deduction for elected
split-pension amount (complete Form T1032)": Form T1032 line 22 when
`ca/t1032_filer_is_transferring_spouse` is 1 (this return is the transferring spouse's), otherwise
0; worked out, never entered."""

UNION_DUES = AmountKind.declare(CATALOG, "union_dues", non_negative=True)
"""Union dues, T1 line 21200 "Annual union, professional, or like dues (receipts and box 44 of all
T4 slips)": the amount claimed, a starting amount."""

CPP_MONTHS = CountKind.declare(CATALOG, "cpp_months", non_negative=True)
"""Months that CPP applied, Schedule 8 Part 2 "Box A: Enter the number of months that CPP applied
in 2025.": the key of the "Monthly proration for 2025" table, a count the filer enters ("Enter "12"
on line A below unless any of the following conditions apply", conditions a) to h)).

A starting count, not computed: the conditions are the filer's to apply. The table has a row for 1
to 12 months only, so "0" (conditions b, d and g) and any other number is refused, not guessed.
Part 1's election months (lines 50372 and 50374) only inform this count and feed no calculation
line, so they are not inputs.
"""

CPT20_T4_EARNINGS = AmountKind.declare(CATALOG, "cpt20_t4_earnings", non_negative=True)
"""Employment earnings shown on a T4 slip that you are electing to pay additional CPP contributions
on, Schedule 8 Part 5 line 3 and line 50399 "Employment earnings shown on a T4 slip that you are
electing to pay additional CPP contributions on (complete Form CPT20)": a starting amount, added
to lines 1 and 2 on Part 5 line 4."""

CPT20_EARNINGS = AmountKind.declare(CATALOG, "cpt20_earnings", non_negative=True)
"""CPT20 earnings, Schedule 8 Part 4 line 2, Form RC381 Part 4 line 2 and line 50373
"Employment earnings not shown on a T4 slip that you are electing to pay additional CPP
contributions on (complete Form CPT20)": a starting amount."""

CPP_PART_4_COMPLETED_YES_OR_NO_CHECKED = CountKind.declare(
    CATALOG, "cpp_part_4_completed_yes_or_no_checked", non_negative=True
)
"""Schedule 8 Part 4 completed, checked, "Part 4 - Complete this part if you are reporting only
self-employment income or other earnings you are electing to pay CPP contributions on. If not,
leave this part blank.": the answer of `ca/cpp_part_4_completed` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped. It is read
by the Form RC381 guard (`ca/count_without_records`).
"""

CPP_PART_5_COMPLETED_YES_OR_NO_CHECKED = CountKind.declare(
    CATALOG, "cpp_part_5_completed_yes_or_no_checked", non_negative=True
)
"""Schedule 8 Part 5 completed, checked, "Part 5 - Complete this part if you are reporting both:
employment income (complete Part 3 first) / self-employment income or other earnings that you are
electing to pay CPP contributions on. If not, leave this part blank.": the answer of
`ca/cpp_part_5_completed` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1
or 0. A count of 2 or more is refused, not capped. It is read by the Form RC381 guard
(`ca/count_without_records`).
"""

CPP_PART_4_COMPLETED_CHECKED = CountKind.declare(
    CATALOG, "cpp_part_4_completed_checked", non_negative=True
)
"""Schedule 8 Part 4 completed, checked, "Part 4 - Complete this part if you are reporting only
self-employment income or other earnings you are electing to pay CPP contributions on. If not,
leave this part blank.": the answer of `ca/cpp_part_4_completed_yes_or_no_checked` after
`ca/count_without_records` checks it against the copies of Form RC381 (`ca/rc381_instances`), a
count of 1 or 0. The check refuses a count above 0 on a return that carries Form RC381, an input
error: the return carries Schedule 8 or Form RC381, never both, and the form's own total already
holds lines 42100, 31000 and 22200.
"""

CPP_PART_5_COMPLETED_CHECKED = CountKind.declare(
    CATALOG, "cpp_part_5_completed_checked", non_negative=True
)
"""Schedule 8 Part 5 completed, checked, "Part 5 - Complete this part if you are reporting both:
employment income (complete Part 3 first) / self-employment income or other earnings that you are
electing to pay CPP contributions on. If not, leave this part blank.": the answer of
`ca/cpp_part_5_completed_yes_or_no_checked` after `ca/count_without_records` checks it against the
copies of Form RC381 (`ca/rc381_instances`), a count of 1 or 0. The check refuses a count above 0 on
a return that carries Form RC381, an input error: the return carries Schedule 8 or Form RC381, never
both, and the form's own total already holds lines 42100, 31000 and 22200.
"""

CPP_PART_4_AND_PART_5_BOTH = CountKind.declare(
    CATALOG, "cpp_part_4_and_part_5_both", non_negative=True
)
"""Schedule 8 Part 4 and Part 5 completed together, "Part 4 - Complete this part if you are
reporting only self-employment income or other earnings you are electing to pay CPP contributions
on. If not, leave this part blank." and "Part 5 - Complete this part if you are reporting both:
employment income (complete Part 3 first) / self-employment income or other earnings that you are
electing to pay CPP contributions on. If not, leave this part blank.": 1 when
`ca/cpp_part_4_completed_checked` and `ca/cpp_part_5_completed_checked` are each more than 0, else
0, a starting count. The two parts are alternatives on the form, so this count of 1 is refused
(see `ca/cpp_part_4_and_part_5_both_checked`), not added: Part 4 for self-employment income only,
Part 5 for employment income as well."""

CPP_PART_4_AND_PART_5_BOTH_CHECKED = CountKind.declare(
    CATALOG, "cpp_part_4_and_part_5_both_checked", non_negative=True
)
"""Schedule 8 Part 4 and Part 5 completed together, checked: the count of
`ca/cpp_part_4_and_part_5_both` when it is 0, the only value produced. A count of 1 is an input
error, not capped, so the self-employed contributions are never counted twice."""

CPP_PART_4_WITH_EMPLOYMENT_EARNINGS = CountKind.declare(
    CATALOG, "cpp_part_4_with_employment_earnings", non_negative=True
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

CPP_PART_4_WITH_EMPLOYMENT_EARNINGS_CHECKED = CountKind.declare(
    CATALOG, "cpp_part_4_with_employment_earnings_checked", non_negative=True
)
"""Schedule 8 Part 4 completed with employment earnings, checked: the count of
`ca/cpp_part_4_with_employment_earnings` when it is 0, the only value produced. A count of 1 is an
input error naming Part 4 and the Part 5 route, not capped, so the employment income is never
treated as self-employment contributions."""

EI_CONTROLLED_CORPORATION_EARNINGS = AmountKind.declare(
    CATALOG, "ei_controlled_corporation_earnings", non_negative=True
)
"""Earnings from a controlled corporation, Schedule 13 line 2 and line 54493 "If you are not
eligible to participate in the EI program as an employee of a corporation because you control more
than 40% of the voting shares of that corporation, enter the amount from box 14 of all your T4
slips from that corporation.": a starting amount."""

EI_EXEMPT_SELF_EMPLOYMENT_INCOME = AmountKind.declare(
    CATALOG, "ei_exempt_self_employment_income", non_negative=True
)
"""Tax-exempt self-employment income, Schedule 13 line 3 and line 54494 "If you are registered or
entitled to be registered under the Indian Act and you earned tax-exempt self-employment income on
a reserve in Canada, enter your total tax-exempt self-employment income.": a starting amount."""

EI_INSURABLE_EARNINGS = AmountKind.declare(CATALOG, "ei_insurable_earnings", non_negative=True)
"""Total EI insurable earnings, Schedule 13 line 6 and line 54780 "Total EI insurable earnings
(amount from box 24 of all your T4 slips; if box 24 is blank, enter the amount from box 14 unless
box 28 shows that the T4 earnings are EI-exempt)": a starting amount, including the employment
income that has no T4 slip (Note 3)."""

EI_SPECIAL_BENEFITS_AGREEMENT = CountKind.declare(
    CATALOG, "ei_special_benefits_agreement", non_negative=True
)
"""Agreement with the Canada Employment Insurance Commission, Schedule 13 "Complete this schedule
to calculate the amount of your employment insurance (EI) premiums on self-employment and other
eligible earnings only if you have entered into an agreement with the Canada Employment Insurance
Commission, through Service Canada, to participate in the EI program for access to EI special
benefits.": 1 when the filer has the agreement, 0 when not, a count the filer states.

It is the number of times Schedule 13's line 9 is entered on the return (lines 31217 and 42120).
"""

EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED = CountKind.declare(
    CATALOG, "ei_special_benefits_agreement_checked", non_negative=True
)
"""Agreement with the Canada Employment Insurance Commission, Schedule 13: the answer of
`ca/ei_special_benefits_agreement` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count
of 1 or 0. A count of 2 or more is refused, not capped."""

CHILD_CARE_EXPENSES_PAID = AmountKind.declare(
    CATALOG, "child_care_expenses_paid", non_negative=True
)
"""Child care expenses paid, Form T778 Part A line 67950 "Total (add all entries for Child care
expenses paid)": a starting amount, also Part B line 5 "Enter the amount from line 67950."."""

CHILDREN_UNDER_SEVEN = CountKind.declare(CATALOG, "children_under_seven", non_negative=True)
"""Number of eligible children born in 2019 or later, Form T778 Part B line 1 "Number of eligible
children born in 2019 or later whom the disability amount cannot be claimed for": a starting
count."""

CHILDREN_WITH_DISABILITY = CountKind.declare(CATALOG, "children_with_disability", non_negative=True)
"""Number of eligible children with the disability amount, Form T778 Part B line 2 (line 67960)
"Number of eligible children born in 2025 or earlier whom the disability amount can be claimed
for": a starting count."""

CHILDREN_SEVEN_TO_SIXTEEN = CountKind.declare(
    CATALOG, "children_seven_to_sixteen", non_negative=True
)
"""Number of eligible children born in 2009 to 2018, Form T778 Part B line 3 "Number of eligible
children born in 2009 to 2018 (and born in 2008 or earlier with a mental or physical infirmity
whom the disability amount cannot be claimed for)": a starting count."""

CHILD_CARE_LIMIT_FOR_CHILDREN_UNDER_SEVEN = AmountKind.declare(
    CATALOG, "child_care_limit_for_children_under_seven", non_negative=True
)
"""Child care limit for the children born in 2019 or later, Form T778 Part B line 1 "multiplied by
$8,000": the line 1 count times $8,000, a part of line 4."""

CHILD_CARE_LIMIT_FOR_CHILDREN_WITH_DISABILITY = AmountKind.declare(
    CATALOG, "child_care_limit_for_children_with_disability", non_negative=True
)
"""Child care limit for the children with the disability amount, Form T778 Part B line 2 (line
67960) "multiplied by $11,000": the line 2 count times $11,000, a part of line 4."""

CHILD_CARE_LIMIT_FOR_CHILDREN_SEVEN_TO_SIXTEEN = AmountKind.declare(
    CATALOG, "child_care_limit_for_children_seven_to_sixteen", non_negative=True
)
"""Child care limit for the children born in 2009 to 2018, Form T778 Part B line 3 "multiplied by
$5,000": the line 3 count times $5,000, a part of line 4."""

CHILD_CARE_BASIC_LIMIT = AmountKind.declare(CATALOG, "child_care_basic_limit", non_negative=True)
"""Child care basic limit, Form T778 Part B line 4 "Add lines 1 to 3.": the limits for each group
of eligible children, in line order."""

CHILD_CARE_EARNED_INCOME = AmountKind.declare(
    CATALOG, "child_care_earned_income", non_negative=True
)
"""Earned income for child care, Form T778 Part B line 6 "Enter your earned income.": "Your earned
income of line 6 is the total of the following: employment income (including tips and gratuities,
and the non-taxable part of an allowance received as an emergency volunteer) ...", here employment
income alone.

The other parts of earned income the form's "Earned income" definition lists are not triggered by
the returns modelled.
"""

CHILD_CARE_EARNED_INCOME_LIMIT = AmountKind.declare(
    CATALOG, "child_care_earned_income_limit", non_negative=True
)
"""Earned income limit for child care, Form T778 Part B line 6 "multiplied by two-thirds": the
earned income times two-thirds, rounded half-up to the cent, once, as line 6 is a dollars-and-cents
box."""

CHILD_CARE_EXPENSES = AmountKind.declare(CATALOG, "child_care_expenses", non_negative=True)
"""Child care expenses deduction, T1 line 41 (line 21400) "Child care expenses (complete Form
T778)": Form T778 Part B line 7 "Enter whichever amount is the least: line 4, line 5 or line 6.",
carried by line 9 "Line 7 minus line 8. ... enter this amount on line 21400 of your return.
Allowable deduction", a deduction from total income.

Line 8 (the other person with the higher net income) is not triggered, so line 9 is line 7; nor
are Parts C and D (the higher-income claimant, school attendance). Eligibility is the return's to
state, not computed here.
"""

CAPITAL_GAINS_DEDUCTIONS_1985_TO_1987 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_1985_to_1987", non_negative=True
)
"""Capital gains deductions claimed for 1985 to 1987, Form T1436 (Capital Gains Worksheet) line
1 "Total amounts from line 254 of your income tax and benefit returns for these years", before
its multiplier "x 2": a starting amount, a figure from the returns of 1985 to 2024."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_OTHER_THAN_ELIGIBLE_CAPITAL_PROPERTY = AmountKind.declare(
    CATALOG,
    "capital_gains_deductions_1988_and_1989_other_than_eligible_capital_property",
    non_negative=True,
)
"""Capital gains deductions claimed for 1988 and 1989 other than for eligible capital property,
Form T1436 (Capital Gains Worksheet) line 2 "Total amounts from line 254 of your returns", before
the amounts reported on lines 543 and 544 of Schedule 3 are taken off and before its multiplier
"x 1.5": a starting amount, a figure from the returns of 1985 to 2024. The filer enters the same
total on line 2 and on line 3; line 2 takes off the Schedule 3 sum, and line 3 is capped by it."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_ELIGIBLE_CAPITAL_PROPERTY = AmountKind.declare(
    CATALOG, "capital_gains_deductions_1988_and_1989_eligible_capital_property", non_negative=True
)
"""Capital gains deductions claimed for 1988 and 1989 for eligible capital property, Form T1436
(Capital Gains Worksheet) line 3 "Total amounts from line 254 of your returns", before amount (a)
is taken off and before its multiplier "x 1.3333": a starting amount, a figure from the returns
of 1985 to 2024. The filer enters the same total on line 2 and on line 3."""

CAPITAL_GAINS_DEDUCTIONS_1990_TO_1999 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_1990_to_1999", non_negative=True
)
"""Capital gains deductions claimed for 1990 to 1999, Form T1436 (Capital Gains Worksheet) line
4 "Total amounts from line 254 of your returns for these years", before its multiplier "x
1.3333": a starting amount, a figure from the returns of 1985 to 2024."""

CAPITAL_GAINS_DEDUCTIONS_2000 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_2000", non_negative=True
)
"""Capital gains deductions claimed for 2000, Form T1436 (Capital Gains Worksheet) line 5 "Amount
from line 254 of your return", before its multiplier "x 1/IR": a starting amount, a figure from
the returns of 1985 to 2024."""

CAPITAL_GAINS_DEDUCTIONS_2001_TO_2024 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_2001_to_2024", non_negative=True
)
"""Capital gains deductions claimed for 2001 to 2024, Form T1436 (Capital Gains Worksheet) line
6 "Total amounts from line 254 of your returns for 2001 to 2018, line 25400 of your returns for
2019 to 2024, and line 25395 of your return for 2024", before its multiplier "x 2": a starting
amount, a figure from the returns of 1985 to 2024."""

SCHEDULE_3_LINE_543 = AmountKind.declare(CATALOG, "schedule_3_line_543", non_negative=True)
"""Schedule 3 line 543, Form T1436 (Capital Gains Worksheet) lines 2 and 3 "amounts reported on
lines 543 and 544 of Schedule 3": the amount the filer enters, a starting amount."""

SCHEDULE_3_LINE_544 = AmountKind.declare(CATALOG, "schedule_3_line_544", non_negative=True)
"""Schedule 3 line 544, Form T1436 (Capital Gains Worksheet) lines 2 and 3 "amounts reported on
lines 543 and 544 of Schedule 3": the amount the filer enters, a starting amount."""

SCHEDULE_3_LINES_543_AND_544_TOTAL = AmountKind.declare(
    CATALOG, "schedule_3_lines_543_and_544_total", non_negative=True
)
"""Schedule 3 lines 543 and 544 added, Form T1436 (Capital Gains Worksheet) lines 2 and 3 "minus
any amounts reported on lines 543 and 544 of Schedule 3" and "cannot be more than the amounts from
lines 543 and 544 of Schedule 3": line 543 plus line 544."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_AMOUNT_A = AmountKind.declare(
    CATALOG, "capital_gains_deductions_1988_and_1989_amount_a", non_negative=True
)
"""Amount (a), Form T1436 (Capital Gains Worksheet) line 2 "minus any amounts reported on lines 543
and 544 of Schedule 3 (if negative, enter "0") (a)": the line 2 total less the Schedule 3 sum, not
below 0; line 2 multiplies it by the printed 1.5."""

CAPITAL_GAINS_DEDUCTIONS_LINE_1 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_line_1", non_negative=True
)
"""Line 1 after its multiplier, Form T1436 (Capital Gains Worksheet) line 1 "For 1985 to 1987:
... x 2 = 1": the amount entered for 1985 to 1987 times the printed 2."""

CAPITAL_GAINS_DEDUCTIONS_LINE_2 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_line_2", non_negative=True
)
"""Line 2 after its multiplier, Form T1436 (Capital Gains Worksheet) line 2 "... (a) x 1.5 = 2":
amount (a) times the printed 1.5."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_AFTER_AMOUNT_A = AmountKind.declare(
    CATALOG, "capital_gains_deductions_1988_and_1989_after_amount_a"
)
"""Line 3 less amount (a), Form T1436 (Capital Gains Worksheet) line 3 "Total amounts from line
254 of your returns minus amount (a) above": the line 3 total less amount (a). The form prints no
floor on it, so it may be negative."""

CAPITAL_GAINS_DEDUCTIONS_1988_AND_1989_LIMITED = AmountKind.declare(
    CATALOG, "capital_gains_deductions_1988_and_1989_limited"
)
"""Line 3 limited, Form T1436 (Capital Gains Worksheet) line 3 "(cannot be more than the amounts
from lines 543 and 544 of Schedule 3)": the lesser of line 3 less amount (a) and the Schedule 3
sum. Signed, as the form prints no floor on the difference."""

CAPITAL_GAINS_DEDUCTIONS_LINE_3 = AmountKind.declare(CATALOG, "capital_gains_deductions_line_3")
"""Line 3 after its multiplier, Form T1436 (Capital Gains Worksheet) line 3 "... x 1.3333 = 3":
the limited amount times the printed 1.3333. Signed, as the form prints no floor on line 3."""

CAPITAL_GAINS_DEDUCTIONS_LINE_4 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_line_4", non_negative=True
)
"""Line 4 after its multiplier, Form T1436 (Capital Gains Worksheet) line 4 "For 1990 to 1999: ...
x 1.3333 = 4": the amount entered for 1990 to 1999 times the printed 1.3333."""

CAPITAL_GAINS_DEDUCTIONS_LINE_5 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_line_5", non_negative=True
)
"""Line 5 after its multiplier, Form T1436 (Capital Gains Worksheet) line 5 "For 2000: ... x 1/IR
(1) = 5": the amount entered for 2000 divided by the 2000 inclusion rate, rounded half-up to the
cent once; 0 when the inclusion rate is 0, as the pre-1986 "1/(IR x 2)" row is."""

CAPITAL_GAINS_DEDUCTIONS_LINE_6 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_line_6", non_negative=True
)
"""Line 6 after its multiplier, Form T1436 (Capital Gains Worksheet) line 6 "For 2001 to 2024:
... x 2 = 6": the amount entered for 2001 to 2024 times the printed 2."""

CAPITAL_GAINS_DEDUCTIONS_CLAIMED_1985_TO_2024 = AmountKind.declare(
    CATALOG, "capital_gains_deductions_claimed_1985_to_2024", non_negative=True
)
"""Total capital gains deductions claimed from 1985 to 2024, Form T1436 (Capital Gains Worksheet)
line 7 "Add lines 1 to 6.": the sum of lines 1 to 6 after their multipliers."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1986_TO_1994 = AmountKind.declare(
    CATALOG, "other_business_investment_loss_reductions_1986_to_1994", non_negative=True
)
"""Other business investment loss reductions for 1986 to 1994, Form T1436 (Capital Gains
Worksheet) line 8: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1994_TO_1996 = AmountKind.declare(
    CATALOG, "other_business_investment_loss_reductions_1994_to_1996", non_negative=True
)
"""Other business investment loss reductions for 1994 to 1996, Form T1436 (Capital Gains
Worksheet) line 9: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1997_TO_1999 = AmountKind.declare(
    CATALOG, "other_business_investment_loss_reductions_1997_to_1999", non_negative=True
)
"""Other business investment loss reductions for 1997 to 1999, Form T1436 (Capital Gains
Worksheet) line 10: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_2000 = AmountKind.declare(
    CATALOG, "other_business_investment_loss_reductions_2000", non_negative=True
)
"""Other business investment loss reductions for 2000, Form T1436 (Capital Gains Worksheet) line
11: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_2001_TO_2023 = AmountKind.declare(
    CATALOG, "other_business_investment_loss_reductions_2001_to_2023", non_negative=True
)
"""Other business investment loss reductions for 2001 to 2023, Form T1436 (Capital Gains
Worksheet) line 12: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_2024 = AmountKind.declare(
    CATALOG, "other_business_investment_loss_reductions_2024", non_negative=True
)
"""Other business investment loss reductions for 2024, Form T1436 (Capital Gains Worksheet) line
13: a starting amount, a figure from the returns of 1986 to 2024."""

OTHER_BUSINESS_INVESTMENT_LOSS_REDUCTIONS_1986_TO_2024 = AmountKind.declare(
    CATALOG, "other_business_investment_loss_reductions_1986_to_2024", non_negative=True
)
"""Total other business investment loss reductions for 1986 to 2024, Form T1436 (Capital Gains
Worksheet) line 14 "Add lines 8 to 13.": the sum of the six reductions of earlier years."""

BUSINESS_INVESTMENT_LOSS_REDUCTION_AVAILABLE = AmountKind.declare(
    CATALOG, "business_investment_loss_reduction_available"
)
"""Business investment loss reduction available, Form T1436 (Capital Gains Worksheet) line 15 "Line
7 minus line 14": the capital gains deductions claimed less the other reductions. The line prints no
"(if negative, enter "0")", so the kind is signed."""

BUSINESS_INVESTMENT_LOSS = AmountKind.declare(
    CATALOG, "business_investment_loss", non_negative=True
)
"""Business investment loss in 2025, Form T1436 line 16 and T1 line 43 gross, line 21699 "Enter
this amount on line 21699 of your return.": a starting amount."""

BUSINESS_INVESTMENT_LOSS_REDUCTION = AmountKind.declare(
    CATALOG, "business_investment_loss_reduction"
)
"""Business investment loss reduction, Form T1436 (Capital Gains Worksheet) line 17 "Enter whichever
is less: amount from line 15 or line 16. Enter this amount on line 17800 of Schedule 3.": the lesser
of the reduction available and the loss. The line prints no floor, so the kind is signed (negative
with line 15)."""

BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION = AmountKind.declare(
    CATALOG, "business_investment_loss_after_reduction", non_negative=True
)
"""Business investment loss after the reduction, Form T1436 (Capital Gains Worksheet) line 18 "Line
16 minus line 17 Business investment loss reduction": never negative, as line 17 is at most line
16."""

ALLOWABLE_BUSINESS_INVESTMENT_LOSS = AmountKind.declare(
    CATALOG, "allowable_business_investment_loss", non_negative=True
)
"""Allowable business investment loss, T1 line 43 and line 21700, Form T1436 line 20 "Line 18
multiplied by the percentage on line 19 Enter this amount on line 21700 of your return.": half
the loss after the reduction, a deduction from total income."""

SUPPORT_PAYMENTS_MADE_TOTAL = AmountKind.declare(
    CATALOG, "support_payments_made_total", non_negative=True
)
"""Support payments made, total, T1 line 21999 "Line 21999: Total" under "Line 45: Support payments
made (go to canada.ca/taxes-support-payments)", Guide 5000-G "Enter on line 21999 of your return the
total amount of support payments that you paid under a court order or written agreement": the bound
that the line 22000 check is made against (`core/at_most`), a caller's amount carried as entered."""

SUPPORT_PAYMENTS_DEDUCTION = AmountKind.declare(
    CATALOG, "support_payments_deduction", non_negative=True
)
"""Support payments deduction, T1 line 22000 "Line 22000: Allowable deduction" and "Enter on line
22000 of your return the deductible part of the support payments that you made.": the deductible
part, a caller's amount checked against `ca/support_payments_made_total` (line 21999) before the
sum reads it."""

SUPPORT_PAYMENTS_DEDUCTION_CHECKED = AmountKind.declare(
    CATALOG, "support_payments_deduction_checked", non_negative=True
)
"""Support payments deduction after the check, T1 line 22000 "Enter on line 22000 of your return the
deductible part of the support payments that you made.": the deductible part is a part of the
total support paid on line 21999, so a line 22000 amount above line 21999 is refused (`core/at_most`
against `ca/support_payments_made_total`), not capped. The sum reads this amount."""

TOTAL_CARRYING_CHARGES = AmountKind.declare(CATALOG, "total_carrying_charges", non_negative=True)
"""Total carrying charges, Federal Worksheet "Line 22100 - Carrying charges, interest expenses,
and other expenses" line 1: a starting amount."""

TOTAL_INTEREST_EXPENSES = AmountKind.declare(CATALOG, "total_interest_expenses", non_negative=True)
"""Total interest expenses, Federal Worksheet "Line 22100 - Carrying charges, interest expenses,
and other expenses" line 2: a starting amount."""

TOTAL_OTHER_EXPENSES = AmountKind.declare(CATALOG, "total_other_expenses", non_negative=True)
"""Total other expenses, Federal Worksheet "Line 22100 - Carrying charges, interest expenses,
and other expenses" line 3: a starting amount."""

CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES = AmountKind.declare(
    CATALOG, "carrying_charges_interest_expenses_and_other_expenses", non_negative=True
)
"""Carrying charges, interest expenses, and other expenses, T1 line 46 and line 22100: Federal
Worksheet "Line 22100 - Carrying charges, interest expenses, and other expenses" line 4 "Add
lines 1 to 3. Enter this amount on line 22100 of your return.", a deduction from total income."""

CPP_FIRST_ADDITIONAL_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "cpp_first_additional_contributions", non_negative=True
)
"""First additional CPP contributions, Schedule 8 Part 3 line 12 "amount from line 7 multiplied
by 1% (maximum $678.00)": the required contributions on the employment income between the basic
exemption and the maximum pensionable earnings. Line 18 is "Amount from line 12"; Part 3b line 37
"If line 19 is positive or "0", enter the amount from line 18 at line 37 and line 43, and continue
at line 44." carries it into line 48 (Part 3a line 26 into line 28 when line 24 is positive).

Line 7 is "Line 5 minus line 6 (if negative, enter "0") (maximum $67,800)", the same earnings
as the base contributions'.
"""

CPP_SECOND_ADDITIONAL_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "cpp_second_additional_contributions", non_negative=True
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

CPP_ENHANCED_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "cpp_enhanced_contributions", non_negative=True
)
"""Enhanced CPP contributions, Schedule 8 Part 3a line 28 "Line 26 plus line 27 Enter this amount
(in dollars and cents) on line 22215 of your return.": the first and second additional
contributions together (lines 12 and 22).

It is the figure Part 3a carries to T1 line 22215 when line 24 is positive. The deduction from
total income is `schedule_8_cpp_enhanced_contributions_on_return`, which is this sum when line 24
is positive and Part 3b line 48 otherwise.
"""

EXPLORATION_AND_DEVELOPMENT_EXPENSES = AmountKind.declare(
    CATALOG, "exploration_and_development_expenses", non_negative=True
)
"""Exploration and development expenses, T1 line 49 and line 22400 "Exploration and development
expenses (complete Form T1229)": a starting amount until CRA publishes a 2025 edition of Form
T1229 (the latest is 2023)."""

CLERGY_EMPLOYER_RESIDENCE_BENEFIT = AmountKind.declare(
    CATALOG, "clergy_employer_residence_benefit", non_negative=True
)
"""Clergy employer residence benefit, Form T1223 Part C (A) "the value of this benefit (including
any allowance for eligible utilities) is shown as a taxable benefit in box 30 of your T4 slip": the
amount for a residence the employer provided, a starting amount taken from box 30. Line (C) adds
its checked amount, `ca/clergy_employer_residence_benefit_checked`, to the (B) amount."""

CLERGY_EMPLOYER_RESIDENCE_BENEFIT_CHECKED = AmountKind.declare(
    CATALOG, "clergy_employer_residence_benefit_checked", non_negative=True
)
"""Clergy employer residence benefit after the check, Form T1223 Part C (A) "the value of this
benefit (including any allowance for eligible utilities) is shown as a taxable benefit in box 30 of
your T4 slip": `ca/clergy_employer_residence_benefit` when it is not more than
`ca/other_employment_income` (`core/at_most`), the amount on line 10400. Guide 5000-G "Member of
the clergy": "Report the amount from box 30 of your T4 slips on line 10400 of your return." Line (C)
adds this amount."""

CLERGY_QUALIFYING_EMPLOYMENT_INCOME = AmountKind.declare(
    CATALOG, "clergy_qualifying_employment_income", non_negative=True
)
"""Income from qualifying employment, Form T1223 Part C line 1 "Income from qualifying employment
from all eligible employers (see note 1)": a starting amount, the income of all eligible employers
combined. Line 2 is one third of it and line 10 is not more than it."""

CLERGY_MONTHS_IN_QUALIFYING_EMPLOYMENT = CountKind.declare(
    CATALOG, "clergy_months_in_qualifying_employment", non_negative=True
)
"""Number of months in qualifying employment, Form T1223 Part C line 3 "Number of months in
qualifying employment": a count, the months the filer gives. Line 4 multiplies it by $1,000."""

CLERGY_ACCOMMODATION_COST = AmountKind.declare(
    CATALOG, "clergy_accommodation_cost", non_negative=True
)
"""Actual rent and eligible utilities, Form T1223 Part C line 6 "Actual rent and eligible utilities
paid or, if residence is owned, fair rental value including eligible utilities for the total period
in the year that the residence was owned or rented and you were in qualifying employment (see note 2
and note 3)": a starting amount, taken as the form takes it."""

CLERGY_OTHER_ACCOMMODATION_CLAIMS = AmountKind.declare(
    CATALOG, "clergy_other_accommodation_claims", non_negative=True
)
"""All amounts claimed for the accommodation, Form T1223 Part C line 7 "All amounts claimed by you,
or any person, for the accommodation (see note 4)": a starting amount, including a spouse's or
common-law partner's claim. Line 8 subtracts its checked amount,
`ca/clergy_other_accommodation_claims_checked`, from line 6."""

CLERGY_OTHER_ACCOMMODATION_CLAIMS_CHECKED = AmountKind.declare(
    CATALOG, "clergy_other_accommodation_claims_checked", non_negative=True
)
"""All amounts claimed for the accommodation after the check, Form T1223 Part C line 7 "All amounts
claimed by you, or any person, for the accommodation (see note 4)":
`ca/clergy_other_accommodation_claims` when it is not more than `ca/clergy_accommodation_cost`
(`core/at_most`), the amount on line 6.
Line 8 "Line 6 minus line 7 =" subtracts this amount. An amount above line 6 is an input error, not
capped: line 8 is not computed from it."""

CLERGY_RESIDENCE_PART_B_COMPLETED = CountKind.declare(
    CATALOG, "clergy_residence_part_b_completed", non_negative=True
)
"""Form T1223 Part C (B) "If you owned or rented the residence that you occupied, complete the
following:": a derived count, 1 when line 3 "Number of months in qualifying employment", line 6
"Actual rent and eligible utilities paid ..." or line 7 "All amounts claimed by you, or any person,
for the accommodation" is more than 0, else 0 (only the (A) employer-provided residence is claimed).
Non-negative, as a count is never below zero."""

CLERGY_RESIDENCE_LINE_2 = AmountKind.declare(CATALOG, "clergy_residence_line_2", non_negative=True)
"""Form T1223 Part C line 2 "Amount from line 1 multiplied by 1/3": one third of the income from
qualifying employment, rounded half-up to the cent."""

CLERGY_RESIDENCE_MONTHS_AMOUNT = AmountKind.declare(
    CATALOG, "clergy_residence_months_amount", non_negative=True
)
"""Form T1223 Part C line 4 "Line 3 multiplied by $1,000 (maximum $10,000)", before the maximum: the
months in qualifying employment times $1,000."""

CLERGY_RESIDENCE_LINE_4 = AmountKind.declare(CATALOG, "clergy_residence_line_4", non_negative=True)
"""Form T1223 Part C line 4 "Line 3 multiplied by $1,000 (maximum $10,000)": the months amount, not
more than the maximum of $10,000."""

CLERGY_RESIDENCE_LINE_5 = AmountKind.declare(CATALOG, "clergy_residence_line_5", non_negative=True)
"""Form T1223 Part C line 5 "Enter whichever is more: line 2 or line 4.": the greater of lines 2
and 4."""

CLERGY_RESIDENCE_LINE_8 = AmountKind.declare(CATALOG, "clergy_residence_line_8")
"""Form T1223 Part C line 8 "Line 6 minus line 7 =": the accommodation cost less the other claims.
The form prints no floor, so a negative line 8 passes through to line 9."""

CLERGY_RESIDENCE_LINE_9 = AmountKind.declare(CATALOG, "clergy_residence_line_9")
"""Form T1223 Part C line 9 "Enter whichever is less: Line 5 or line 8.": the lesser of lines 5 and
8, signed as the form prints it."""

CLERGY_RESIDENCE_LINE_10 = AmountKind.declare(CATALOG, "clergy_residence_line_10")
"""Form T1223 Part C line 10 "Enter whichever is less: Line 1 or line 9.": the (B) amount, the
lesser of the income from qualifying employment and line 9."""

CLERGY_RESIDENCE_TOTAL = AmountKind.declare(CATALOG, "clergy_residence_total")
"""Form T1223 Part C (C) "add amounts (A) and (B)": the employer residence benefit (A) plus the (B)
amount on line 10, not floored."""

CLERGY_RESIDENCE_TOTAL_LIMITED = AmountKind.declare(CATALOG, "clergy_residence_total_limited")
"""Form T1223 Part C (C) "The amount claimed for the clergy residence deduction cannot be more than
the income from qualifying employment on line 1.": the total, not more than line 1."""

CLERGY_RESIDENCE_DEDUCTION = AmountKind.declare(
    CATALOG, "clergy_residence_deduction", non_negative=True
)
"""Clergy residence deduction, T1 line 51 and line 23100 "Clergy residence deduction (complete Form
T1223)", Form T1223 Part C "Enter this amount on line 23100 of your return.": the total of (A) and
(B), limited to line 1 when Part C (B) is completed. The Federal Worksheet "Line 45200 - Refundable
medical expense supplement" takes it off the employment income, as line 23100, and the alternative
minimum tax reads it as line 23100."""

OTHER_DEDUCTIONS = AmountKind.declare(CATALOG, "other_deductions", non_negative=True)
"""Other deductions, T1 line 52 and line 23200 "Other deductions": a starting amount, which
includes the RDSP income repayment (a starting amount of its own, Federal Worksheet for line
25000 line 7).

It excludes the split income, which Form T1206 Part 1 line 4 (`total_split_income`) adds to line
23200 as a part of its own.
"""

SPLIT_INCOME_DIVIDENDS = AmountKind.declare(CATALOG, "split_income_dividends", non_negative=True)
"""Split income dividends, Form T1206 Part 1 line 1 (68330) "Part of the taxable amount of
dividends (eligible and other than eligible) described in the information section received from
taxable Canadian corporations": a starting amount, the filer's classification under the form's
pages 1 to 4. Line 1 reads the checked kind, `ca/split_income_dividends_checked`, not this
amount."""

SPLIT_INCOME_DIVIDENDS_TOTAL = AmountKind.declare(
    CATALOG, "split_income_dividends_total", non_negative=True
)
"""Split income dividends with the T1206 page 6 amount, Form T1206 Part 1 line 1 (68330): the
filer's `ca/split_income_dividends` plus Form T1206 page 6 "In addition, enter this amount on
lines 1 and 2 as indicated in Part 1 on page 7", the amount deemed to be a dividend of a filer
under 18 (`ca/t1206_under_18_dividend_amount`, 0 for 18 or older). The check reads this amount."""

SPLIT_INCOME_DIVIDENDS_CHECKED = AmountKind.declare(
    CATALOG, "split_income_dividends_checked", non_negative=True
)
"""Split income dividends after the check, Form T1206 Part 1 line 1 (68330) "Part of the taxable
amount of dividends (eligible and other than eligible) described in the information section
received from taxable Canadian corporations": `ca/split_income_dividends_total` when it is not
more than `ca/taxable_dividends` (`core/at_most`), the taxable amount of dividends on line 12000 of
the return. An amount above it is refused, not capped. Line 4 and the credit on lines 1 and 2 read
this amount."""

SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE = AmountKind.declare(
    CATALOG, "split_income_dividends_other_than_eligible", non_negative=True
)
"""Split income dividends other than eligible, Form T1206 Part 1 line 2 (68340) "Part of the
taxable amount of dividends other than eligible dividends, included on line 1, from taxable
Canadian corporations": a starting amount. Line 2 reads the checked kind,
`ca/split_income_dividends_other_than_eligible_checked`, not this amount."""

SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_TOTAL = AmountKind.declare(
    CATALOG, "split_income_dividends_other_than_eligible_total", non_negative=True
)
"""Split income dividends other than eligible with the T1206 page 6 amount, Form T1206 Part 1 line
2 (68340): the filer's `ca/split_income_dividends_other_than_eligible` plus the amount deemed to
be a dividend (other than eligible dividend) of a filer under 18
(`ca/t1206_under_18_dividend_amount`, 0 for 18 or older). The check reads this amount."""

SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_PART_OF_LINE_1 = AmountKind.declare(
    CATALOG, "split_income_dividends_other_than_eligible_part_of_line_1", non_negative=True
)
"""Split income dividends other than eligible, part of line 1, Form T1206 Part 1 line 2 (68340)
"Part of the taxable amount of dividends other than eligible dividends, included on line 1, from
taxable Canadian corporations": `ca/split_income_dividends_other_than_eligible_total` when it is
not more than `ca/split_income_dividends_checked` (`core/at_most`), line 1 as checked. An amount
above it is refused, not capped."""

SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED = AmountKind.declare(
    CATALOG, "split_income_dividends_other_than_eligible_checked", non_negative=True
)
"""Split income dividends other than eligible after the check, Form T1206 Part 1 line 2 (68340)
"Part of the taxable amount of dividends other than eligible dividends, included on line 1, from
taxable Canadian corporations": `ca/split_income_dividends_other_than_eligible_part_of_line_1` when
it is not more than `ca/taxable_dividends_other_than_eligible` (`core/at_most`), the amount on line
12010 of the return. An amount above it is refused, not capped. The federal and Ontario
credits on split income read this amount."""

OTHER_SPLIT_INCOME = AmountKind.declare(CATALOG, "other_split_income", non_negative=True)
"""Other split income, Form T1206 Part 1 line 3 "All other split income (see "Split income" on page
1)": a starting amount. Line 3 is checked as `ca/other_split_income_checked`, which line 4 reads;
the bound of `ca/split_income_from_foreign_sources_part_of_line_3` is `ca/other_split_income_total`,
which holds it as entered."""

OTHER_SPLIT_INCOME_TOTAL = AmountKind.declare(
    CATALOG, "other_split_income_total", non_negative=True
)
"""Other split income with the T1206 page 6 amount, Form T1206 Part 1 line 3 "All other split
income (see "Split income" on page 1)": the filer's `ca/other_split_income` plus Form T1206 page 6
"multiply the capital gain for each disposition reported on lines A, B, C and F by 50% and enter
the total on line 3 in Part 1 on page 7" (`ca/t1206_part_1_line_3_amount`, 0 under 18). The
checks of line 3 and of Part 2 line 68370 read this amount."""

OTHER_SPLIT_INCOME_OWN_CHECKED = AmountKind.declare(
    CATALOG, "other_split_income_own_checked", non_negative=True
)
"""The filer's own other split income after the check, Form T1206 Part 1 line 3 "All other split
income (see "Split income" on page 1)": `ca/other_split_income` when it is not more than
`ca/income_before_losses` (`core/at_most`), the income before losses, the T1 income lines of Step 2
with each loss counted as 0, which the whole split income is part of. An amount above it is an
input error, not capped. Form T1206 and Guide 5000-G (line 23200, page 24) were read and print no
limit on line 3, so the bound is the part-over-whole one."""

OTHER_SPLIT_INCOME_CHECKED = AmountKind.declare(
    CATALOG, "other_split_income_checked", non_negative=True
)
"""Other split income, Form T1206 Part 1 line 3 "All other split income (see "Split income" on page
1)": the checked own figure (`ca/other_split_income_own_checked`) plus the Part 1 line 3 amount of
page 6 (`ca/t1206_part_1_line_3_amount`, 50% of line G, computed by the T1206 itself and not bounded
by the income before losses, so a filer whose share losses offset line G is not refused). Line 4
reads this amount."""

SPLIT_INCOME_FROM_FOREIGN_SOURCES = AmountKind.declare(
    CATALOG, "split_income_from_foreign_sources", non_negative=True
)
"""Split income from foreign sources, Form T1206 Part 2 line 68370 "Part of the amount on line 3
that is from foreign sources": a starting amount. Line 23 reads the checked kind,
`ca/split_income_from_foreign_sources_checked`, not this amount."""

SPLIT_INCOME_FROM_FOREIGN_SOURCES_PART_OF_LINE_3 = AmountKind.declare(
    CATALOG, "split_income_from_foreign_sources_part_of_line_3", non_negative=True
)
"""Split income from foreign sources, part of line 3, Form T1206 Part 2 line 68370 "Part of the
amount on line 3 that is from foreign sources": `ca/split_income_from_foreign_sources` when it is
not more than `ca/other_split_income_total` (`core/at_most`), line 3 as the bound. An amount above
it is refused, not capped."""

SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED = AmountKind.declare(
    CATALOG, "split_income_from_foreign_sources_checked", non_negative=True
)
"""Split income from foreign sources after the check, Form T1206 Part 2 line 68370 "Part of the
amount on line 3 that is from foreign sources" over "Total income from foreign sources" 68380:
`ca/split_income_from_foreign_sources_part_of_line_3` when it is not more than
`ca/total_income_from_foreign_sources` (`core/at_most`). The reading is the form's own structure:
the numerator of a share against its denominator. An amount above it is refused, not capped. Line
23 reads this amount as the numerator."""

TOTAL_INCOME_FROM_FOREIGN_SOURCES = AmountKind.declare(
    CATALOG, "total_income_from_foreign_sources", non_negative=True
)
"""Total income from foreign sources, Form T1206 Part 2 line 68380 "Total income from foreign
sources": a starting amount. It is the bound of the checked 68370 and of the checked non-business
total, and line 23 reads it as the denominator as it is, not a checked kind."""

SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES = AmountKind.declare(
    CATALOG, "split_income_non_business_from_foreign_sources", non_negative=True
)
"""Non-business part of the split income from foreign sources, Form T1206 Part 3 line 49 "Part of
the amount from line 68370 on page 8 that is non-business income": a starting amount. Line 49
reads the checked kind, `ca/split_income_non_business_from_foreign_sources_checked`, not this
amount."""

SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_PART_OF_68370 = AmountKind.declare(
    CATALOG, "split_income_non_business_from_foreign_sources_part_of_68370", non_negative=True
)
"""Non-business part of the split income from foreign sources, part of line 68370, Form T1206 Part
3 line 49 "Part of the amount from line 68370 on page 8 that is non-business income":
`ca/split_income_non_business_from_foreign_sources` when it is not more than
`ca/split_income_from_foreign_sources_checked` (`core/at_most`), 68370 as checked. The reading is
the form's own structure: the part of 68370 is the numerator of a share against 68370. An amount
above it is refused, not capped."""

TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES = AmountKind.declare(
    CATALOG, "total_non_business_income_from_foreign_sources", non_negative=True
)
"""Non-business part of the total income from foreign sources, Form T1206 Part 3 line 49 "Part of
the amount from line 68380 on page 8 that is non-business income": a starting amount. Line 49
reads the checked kind, `ca/total_non_business_income_from_foreign_sources_checked`, not this
amount."""

TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED = AmountKind.declare(
    CATALOG, "total_non_business_income_from_foreign_sources_checked", non_negative=True
)
"""Non-business part of the total income from foreign sources after the check, Form T1206 Part 3
line 49 "Part of the amount from line 68380 on page 8 that is non-business income":
`ca/total_non_business_income_from_foreign_sources` when it is not more than
`ca/total_income_from_foreign_sources` (`core/at_most`), 68380 as the bound. An amount above it is
refused, not capped. Line 49 reads this amount as the denominator."""

SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED = AmountKind.declare(
    CATALOG, "split_income_non_business_from_foreign_sources_checked", non_negative=True
)
"""Non-business part of the split income from foreign sources after the check, Form T1206 Part 3
line 49 "Part of the amount from line 68370 on page 8 that is non-business income" over "Part of
the amount from line 68380 on page 8 that is non-business income":
`ca/split_income_non_business_from_foreign_sources_part_of_68370` when it is not more than
`ca/total_non_business_income_from_foreign_sources_checked` (`core/at_most`). The reading is the
form's own structure: the numerator of a share against its denominator. An amount above it is
refused, not capped. Line 49 reads this amount as the numerator."""

CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "cpp_t4_base_and_first_additional_contributions", non_negative=True
)
"""Total actual base and first additional contributions, Schedule 8 Part 3 line 8 and Form RC381
Part 3 line 19, line 50340 "Total actual base and first additional contributions on CPP pensionable
earnings from box 16 of all of your T4 slips": the amount the filer enters from the T4 slips, a
starting amount."""

CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "cpp_t4_second_additional_contributions", non_negative=True
)
"""Total actual second additional contributions, Schedule 8 Part 3 line 21 and line 50341 "Total
actual second additional contributions on CPP pensionable earnings from box 16A of all of your T4
slips": the amount the filer enters from the T4 slips, a starting amount.
"""

T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT = AmountKind.declare(
    CATALOG, "t4_cpp_pensionable_earnings_slip_limit", non_negative=True
)
"""CPP pensionable earnings the T4 slips can show, not a form line: the count of slips with CPP
pensionable earnings (`ca/t4_cpp_slip_count`) times the "(maximum $81,200 per slip)" printed on
Schedule 8 Part 3 line 1 and Form RC381 Part 3 line 1, line 50339. The bound of
`ca/t4_cpp_pensionable_earnings_outside_quebec`; the form prints no total bound."""

T4_CPP_PENSIONABLE_EARNINGS_SLIP_CHECKED = AmountKind.declare(
    CATALOG, "t4_cpp_pensionable_earnings_slip_checked", non_negative=True
)
"""Total CPP pensionable earnings from box 26 of all of your T4 slips where the province of
employment is not Quebec, Schedule 8 Part 3 line 1 and Form RC381 Part 3 line 1, line 50339,
checked: the amount of `ca/t4_cpp_pensionable_earnings_outside_quebec` when it is not more than
`ca/t4_cpp_pensionable_earnings_slip_limit` (`core/at_most`). An amount above the limit is an input
error, not capped. Nothing on the return reads this amount."""

T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT = AmountKind.declare(
    CATALOG, "t4_qpp_pensionable_earnings_slip_limit", non_negative=True
)
"""QPP pensionable earnings the T4 slips can show, not a form line: the count of slips with QPP
pensionable earnings (`ca/t4_qpp_slip_count`) times the "(maximum $81,200 per slip)" printed on Form
RC381 Part 3 line 2, line 50329. The bound of `ca/t4_qpp_pensionable_earnings_in_quebec`; the form
prints no total bound."""

T4_QPP_PENSIONABLE_EARNINGS_SLIP_CHECKED = AmountKind.declare(
    CATALOG, "t4_qpp_pensionable_earnings_slip_checked", non_negative=True
)
"""Total QPP pensionable earnings from box 26 of all of your T4 slips where the province of
employment is Quebec, Form RC381 Part 3 line 2 and line 50329, checked: the amount of
`ca/t4_qpp_pensionable_earnings_in_quebec` when it is not more than
`ca/t4_qpp_pensionable_earnings_slip_limit` (`core/at_most`). An amount above the limit is an input
error, not capped. Nothing on the return reads this amount."""

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


CPP_ACTUAL_BASE_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "cpp_actual_base_contributions", non_negative=True
)
"""Actual base contributions on CPP pensionable earnings, Schedule 8 Part 3 line 9 "amount from
line 8 multiplied by 83.1933% =": the share of the T4 base and first additional contributions that
is the base contributions, to the cent. Line 14 is "Amount from line 9"."""

CPP_ACTUAL_FIRST_ADDITIONAL_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "cpp_actual_first_additional_contributions", non_negative=True
)
"""Actual first additional contributions on CPP pensionable earnings, Schedule 8 Part 3 line 10
"Line 8 minus line 9 =": the rest of the T4 base and first additional contributions. Line 17 is
"Amount from line 10"."""

CPP_REQUIRED_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "cpp_required_base_and_first_additional_contributions", non_negative=True
)
"""Required base and first additional contributions on pensionable earnings, Schedule 8 Part 3
line 13 "Line 11 plus line 12 =": the required base and first additional contributions on the
employment income, the sum of the two required tiers."""

CPP_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE = AmountKind.declare(
    CATALOG, "cpp_first_additional_contributions_difference"
)
"""First additional contributions difference, Schedule 8 Part 3 line 19 "Line 17 minus line 18 (if
negative, show in brackets) =": the actual first additional contributions (line 17, "Amount from
line 10") less the required first additional contributions (line 18, "Amount from line 12")."""

CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE = AmountKind.declare(
    CATALOG, "cpp_base_and_first_additional_contributions_difference"
)
"""Base and first additional contributions difference, Schedule 8 Part 3 line 20 "Line 16 plus
line 19 (if negative, show in brackets) =": the line 16 and line 19 differences together."""

CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE = AmountKind.declare(
    CATALOG, "cpp_second_additional_contributions_difference"
)
"""Second additional contributions difference, Schedule 8 Part 3 line 23 "Line 21 minus line 22
(if negative, show in brackets) =": the actual second additional contributions (line 21, the T4
box 16A total) less the required second additional contributions (line 22)."""

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

PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS = AmountKind.declare(
    CATALOG, "pensionable_net_self_employment_earnings"
)
"""Pensionable net self-employment earnings, Schedule 8 Part 4 line 1 "amount from line 12200 of
your return plus line 27 of your return": the net partnership income plus the net self-employment
income. Negative when line 27 is a loss, as line 1 prints no floor; line 3 is.

Note 1 ("self-employment earnings should be prorated according to the number of months ... that the
conditions a) to g) applied") gives no formula and is not modelled.
"""

CPP_PENSIONABLE_EARNINGS = AmountKind.declare(
    CATALOG, "cpp_pensionable_earnings", non_negative=True
)
"""CPP pensionable earnings, Schedule 8 Part 4 line 3 "Line 1 plus line 2 (if negative, enter "0")":
the pensionable net self-employment earnings plus the CPT20 earnings (line 2), not below zero."""

CPP_PENSIONABLE_EARNINGS_UP_TO_ADDITIONAL_MAXIMUM = AmountKind.declare(
    CATALOG, "cpp_pensionable_earnings_up_to_additional_maximum", non_negative=True
)
"""Pensionable earnings up to the additional maximum, Schedule 8 Part 4 line 4 "Enter whichever is
less: amount from line D of Part 2 or line 3.": the lesser of the additional maximum pensionable
earnings and the pensionable earnings."""

CPP_EARNINGS_SUBJECT_TO_SECOND_ADDITIONAL = AmountKind.declare(
    CATALOG, "cpp_earnings_subject_to_second_additional", non_negative=True
)
"""Earnings subject to second additional contributions, Schedule 8 Part 4 line 6 "Line 4 minus line
5 (if negative, enter "0")": line 4 less the maximum pensionable earnings (line 5, "Amount from
line B of Part 2"), not below zero."""

CPP_EARNINGS_UP_TO_MAXIMUM = AmountKind.declare(
    CATALOG, "cpp_earnings_up_to_maximum", non_negative=True
)
"""Earnings up to the maximum pensionable earnings, Schedule 8 Part 4 line 7 "Line 4 minus line 6
(if negative, enter "0")": line 4 less the earnings subject to second additional contributions,
not below zero."""

CPP_EARNINGS_SUBJECT_TO_BASE_AND_FIRST_ADDITIONAL = AmountKind.declare(
    CATALOG, "cpp_earnings_subject_to_base_and_first_additional", non_negative=True
)
"""Earnings subject to base and first additional contributions, Schedule 8 Part 4 line 9 "Line 7
minus line 8 (if negative, enter "0") (maximum $67,800)": line 7 less the basic exemption (line 8,
"Amount from line E of Part 2"), not below zero."""

SELF_EMPLOYED_CPP_BASE_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "self_employed_cpp_base_contributions", non_negative=True
)
"""Required base contributions on CPP pensionable earnings, Schedule 8 Part 4 line 10 "amount from
line 9 multiplied by 9.9% (maximum $6,712.20)": a self-employed person pays both halves, so twice
the employee's 4.95%."""

SELF_EMPLOYED_CPP_FIRST_ADDITIONAL_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "self_employed_cpp_first_additional_contributions", non_negative=True
)
"""Required first additional contributions on CPP pensionable earnings, Schedule 8 Part 4 line 11
"amount from line 9 multiplied by 2% (maximum $1,356.00)": twice the employee's 1%."""

SELF_EMPLOYED_CPP_SECOND_ADDITIONAL_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "self_employed_cpp_second_additional_contributions", non_negative=True
)
"""Required second additional contributions on CPP pensionable earnings, Schedule 8 Part 4 line 12
"amount from line 6 multiplied by 8% (maximum $792.00)": twice the employee's 4%, on the earnings
of line 6, which Part 2 line C ($9,900 for 12 months) bounds."""

SELF_EMPLOYED_CPP_ENHANCED_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "self_employed_cpp_enhanced_contributions", non_negative=True
)
"""Enhanced contributions on self-employment income, Schedule 8 Part 4 line 13 "Line 11 plus line
12": the first and second additional contributions together; line 16 is "Amount from line 13"."""

SELF_EMPLOYED_CPP_CONTRIBUTIONS_PAYABLE = AmountKind.declare(
    CATALOG, "self_employed_cpp_contributions_payable", non_negative=True
)
"""CPP contributions payable on self-employment income and other earnings, Schedule 8 Part 4 line
14 "Line 10 plus line 13 Enter this amount (in dollars and cents) on line 42100 of your return.":
the base and enhanced contributions together."""

SELF_EMPLOYED_CPP_BASE_CREDIT = AmountKind.declare(
    CATALOG, "self_employed_cpp_base_credit", non_negative=True
)
"""Base CPP contributions on self-employment income and other earnings, Schedule 8 Part 4 line 15
"amount from line 10 multiplied by 50%" ("Enter the result of the following calculation (in dollars
and cents) on line 31000 of your return"): the employee's half of the base contributions, which is
the credit."""

SELF_EMPLOYED_CPP_DEDUCTION = AmountKind.declare(
    CATALOG, "self_employed_cpp_deduction", non_negative=True
)
"""Deduction for CPP contributions on self-employment income and other earnings, Schedule 8 Part 4
line 17 "Line 15 plus line 16 Enter this amount (in dollars and cents) on line 22200 of your
return.": the employer's half of the base contributions (line 15) plus the enhanced contributions
(line 16, "Amount from line 13")."""

CPP_DEDUCTION_ON_SELF_EMPLOYMENT = AmountKind.declare(
    CATALOG, "cpp_deduction_on_self_employment", non_negative=True
)
"""Deduction for CPP contributions on self-employment income and other earnings, T1 line 47 and
line 22200 "Deduction for CPP or QPP contributions on self-employment income and other earnings
(complete Schedule 8 or Form RC381, whichever applies)": Schedule 8 Part 4 line 17, entered once
for each Part 4 completed (1 or 0), a deduction from total income."""

EI_EXCLUDED_SLIP_NET_INCOME = AmountKind.declare(CATALOG, "ei_excluded_slip_net_income")
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

EI_EXCLUDED_SLIPS_NET_INCOME = AmountKind.declare(CATALOG, "ei_excluded_slips_net_income")
"""Net income of the T4 slips with EI premiums in box 18, Schedule 13 line 1 "do not include any net
income (or net loss) reported on lines 13500, 13700, 13900, 14100, and 14300 of your return for that
slip (Note 1)": the net income (or net loss) of every such slip, added. It may be a loss, so the
kind is signed."""

EI_SELF_EMPLOYMENT_BEFORE_SLIPS = AmountKind.declare(CATALOG, "ei_self_employment_before_slips")
"""Schedule 13 line 1 before the slips "Enter the total amount from line 1 1 plus line 27 of your
return": the net partnership income (T1 line 11, line 12200) plus the net self-employment income.
The form text reads "line 1 1", taken as line 11; to be confirmed. It stands before the exclusion of
the slips and the "(if negative, enter "0")" floor of the finished line 1, so the kind is signed."""

EI_SELF_EMPLOYMENT_EARNINGS = AmountKind.declare(
    CATALOG, "ei_self_employment_earnings", non_negative=True
)
"""Self-employment earnings for EI, Schedule 13 line 1 "Enter the total amount from line 1 1 plus
line 27 of your return. If you received a T4 slip for self-employment income with EI premiums in box
18, do not include any net income (or net loss) reported on lines 13500, 13700, 13900, 14100, and
14300 of your return for that slip (Note 1) (if negative, enter "0")": the net partnership income
plus the net self-employment income, less the net income of those slips, not below zero."""

EI_NET_SELF_EMPLOYMENT_INCOME = AmountKind.declare(
    CATALOG, "ei_net_self_employment_income", non_negative=True
)
"""Net self-employment income for EI, Schedule 13 line 4 "Add lines 1 to 3. Net self-employment
income": line 1, the earnings from a controlled corporation (line 2) and the tax-exempt
self-employment income (line 3)."""

EI_MAXIMUM_INSURABLE_EARNINGS = AmountKind.declare(
    CATALOG, "ei_maximum_insurable_earnings", non_negative=True
)
"""Maximum insurable earnings, Schedule 13 line 5 "Maximum insurable earnings 65,700.00": the
printed figure, as an artifact of the same name."""

EI_INSURABLE_EARNINGS_REMAINING = AmountKind.declare(
    CATALOG, "ei_insurable_earnings_remaining", non_negative=True
)
"""Insurable earnings remaining, Schedule 13 line 7 "Line 5 minus line 6 (if negative, enter "0")":
the maximum insurable earnings less the EI insurable earnings already on T4 slips, not below
zero."""

EI_EARNINGS_SUBJECT_TO_PREMIUM = AmountKind.declare(
    CATALOG, "ei_earnings_subject_to_premium", non_negative=True
)
"""Earnings subject to EI premiums, Schedule 13 line 8 "Enter whichever is less: amount from line 4
or line 7.": the lesser of the net self-employment income and the insurable earnings remaining."""

SELF_EMPLOYED_EI_PREMIUMS = AmountKind.declare(
    CATALOG, "self_employed_ei_premiums", non_negative=True
)
"""EI premiums payable on self-employment and other eligible earnings, Schedule 13 line 9
"Residents of a province or territory other than Quebec: Line 9: Amount from line 8 multiplied by
1.64% (maximum $1,077.48)". Line 10, for Quebec residents, is not triggered."""

T929_NET_BUSINESS_INCOME = AmountKind.declare(
    CATALOG, "t929_net_business_income", non_negative=True
)
"""Net self-employment income from business statements, Form T929 Step 2 line 4 "Enter your earned
income" and its definition "net self-employment income, either alone or as an active partner (not
including losses)": the positive net income of each Form T2125 statement, added, so a loss counts
0."""

T929_NET_FARMING_INCOME = AmountKind.declare(CATALOG, "t929_net_farming_income", non_negative=True)
"""Net self-employment income from farming statements, Form T929 Step 2 line 4 and its definition
"net self-employment income, either alone or as an active partner (not including losses)": the
positive net income of each Form T2042 statement, added, so a loss counts 0."""

T929_NET_FISHING_INCOME = AmountKind.declare(CATALOG, "t929_net_fishing_income", non_negative=True)
"""Net self-employment income from fishing statements, Form T929 Step 2 line 4 and its definition
"net self-employment income, either alone or as an active partner (not including losses)": the
positive net income of each Form T2121 statement, added, so a loss counts 0."""

T929_NET_PROFESSIONAL_INCOME = AmountKind.declare(
    CATALOG, "t929_net_professional_income", non_negative=True
)
"""Net self-employment income from professional income, Form T929 Step 2 line 4 and its definition
"net self-employment income, either alone or as an active partner (not including losses)": the
professional income of T1 line 13700, not below zero, so a loss counts 0."""

T929_NET_COMMISSION_INCOME = AmountKind.declare(
    CATALOG, "t929_net_commission_income", non_negative=True
)
"""Net self-employment income from commission income, Form T929 Step 2 line 4 and its definition
"net self-employment income, either alone or as an active partner (not including losses)": the
commission income of T1 line 13900, not below zero, so a loss counts 0."""

T929_LINE_3 = AmountKind.declare(CATALOG, "t929_line_3")
"""Net disability supports expenses, Form T929 Step 1 line 3 "Subtract line 2 from line 1. This
amount is your net disability supports expenses": line 1 less line 2, the amounts paid less the
amounts reimbursed. The form does not floor it, so the kind is signed."""

T929_LINE_4 = AmountKind.declare(CATALOG, "t929_line_4", non_negative=True)
"""Earned income, Form T929 Step 2 line 4 "Enter your earned income": the total of the items of the
definition of earned income, employment income (T1 lines 10100 and 10400), the taxable part of
scholarships (T1 line 13010), the net self-employment income of the four kinds above, and the
other items of the definition the filer enters."""

T929_LINE_7 = AmountKind.declare(CATALOG, "t929_line_7", non_negative=True)
"""Net income above earned income, Form T929 Step 2 line 7 "Line 5 minus line 6 (if negative, enter
"0")": the net income with no claim (line 5) less the earned income of line 4 (line 6), not below
zero."""

T929_LINE_9 = AmountKind.declare(CATALOG, "t929_line_9", non_negative=True)
"""Weeks at the weekly amount, Form T929 Step 2 line 9 "Line 8 multiplied by $375": the weeks
attended (line 8) times $375, rounded half-up to the cent."""

T929_LINE_10 = AmountKind.declare(CATALOG, "t929_line_10", non_negative=True)
"""Amount for attending an educational institution, Form T929 Step 2 line 10 "Enter the amount from
line 7 or line 9, whichever is less. (maximum $15,000)": the lesser of line 7 and line 9, not more
than the $15,000 maximum."""

T929_LINE_11 = AmountKind.declare(CATALOG, "t929_line_11", non_negative=True)
"""Earned income and attendance amount, Form T929 Step 2 line 11 "Add lines 4 and 10": line 4 plus
line 10."""

DISABILITY_SUPPORTS_DEDUCTION = AmountKind.declare(
    CATALOG, "disability_supports_deduction", non_negative=True
)
"""Disability supports deduction, T1 line 21500 "Disability supports deduction (complete Form
T929)": Form T929 line 12 "Enter the amount from line 3 or line 11, whichever is less", which the
form says to enter "on line 21500 of your tax return". The Federal Worksheet "Line 45200 -
Refundable medical expense supplement" line 9 "Amount from line 21500 of your return" reads it, and
so does Part 1 of the alternative minimum tax. The return totals the form's line 12 and adds it to
line 23300."""

DEDUCTIONS_FROM_TOTAL_INCOME = AmountKind.declare(
    CATALOG, "deductions_from_total_income", non_negative=True
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

NET_INCOME_BEFORE_ADJUSTMENTS = AmountKind.declare(CATALOG, "net_income_before_adjustments")
"""Net income before adjustments, T1 line 54 and line 23400 "Line 34 minus line 53 (if negative,
show in brackets)": total income less total deductions, not floored, so the kind is signed."""

NET_INCOME = AmountKind.declare(CATALOG, "net_income", non_negative=True)
"""Net income, T1 line 56 and line 23600 "Line 54 minus line 55 (if negative, enter "0") If
negative, you may have a non-capital loss (see Form T1A) and the negative amount is to be used for
certain calculations (go to canada.ca/line-23600) Net income": the net income before adjustments
(line 23400) less the social benefits repayment (line 23500), not below zero. The amount before
that floor is `NET_INCOME_SIGNED`.
"""

NET_INCOME_SIGNED = AmountKind.declare(CATALOG, "net_income_signed")
"""Net income before its floor, T1 line 56 and line 23600 "Line 54 minus line 55 (if negative,
enter "0")" as Form T1206 Part 1 line 5 "Net income from line 23600 of your tax return (or the
amount you would have entered if the instructions on line 23600 read "if negative, show in
brackets")" reads it, and so does the TOSI-adjusted net income, which Schedule ON479-A column 1
line 1 reads: the net income before adjustments (line 23400) less the social benefits repayment
(line 23500), signed."""

OAS_OVERPAYMENT_RECOVERED = AmountKind.declare(
    CATALOG, "oas_overpayment_recovered", non_negative=True
)
"""Overpayment of OAS benefits recovered, Federal Worksheet "Line 23500 - Social benefits
repayment" line 4 "Overpayment of OAS benefits recovered (box 20 of your T4A(OAS) slip)": a
starting amount from the slip."""

EI_BENEFITS_REPAYMENT = AmountKind.declare(CATALOG, "ei_benefits_repayment", non_negative=True)
"""EI benefits repayment, Federal Worksheet "Line 23500 - Social benefits repayment" line 7 "EI
benefits repayment from line 4 of the repayment chart on your T4E slip, if any": a starting amount
from the slip."""

EI_BENEFITS_REPAYMENT_CHECKED = AmountKind.declare(
    CATALOG, "ei_benefits_repayment_checked", non_negative=True
)
"""EI benefits repayment after the check, Federal Worksheet "Line 23500 - Social benefits
repayment" line 7 "EI benefits repayment from line 4 of the repayment chart on your T4E slip, if
any": the amount of `ca/ei_benefits_repayment` after the check that it is not more than
`ca/ei_and_other_benefits` (`core/at_most`), the EI and other benefits of line 11900 (Guide 5000-G
line 23500 "You have to repay part of the EI benefits (line 11900) that you received in 2025", so
the repayment is part of the benefits). Looked in Federal Worksheet 5000-D1 and Guide 5000-G for
another printed limit and found none (the T4E repayment chart is not in the repo). Lines 10 and 21
read this amount."""

NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO = AmountKind.declare(
    CATALOG, "net_income_before_adjustments_not_below_zero", non_negative=True
)
"""Net income before adjustments, not below zero, Federal Worksheet "Line 25000 - Other payments
deduction" line 1 "Amount from line 23400 of your return (if negative, enter "0")": line 23400
with a negative result replaced by zero. It is not the net income of line 23600, which line 23500
reduces."""

SOCIAL_BENEFITS_REPAYMENT_APPLIES = CountKind.declare(
    CATALOG, "social_benefits_repayment_applies", non_negative=True
)
"""Social benefits repayment chart applies, Federal Worksheet "Line 23500 - Social benefits
repayment" "Complete the chart below if one or both of the following applies:" "You entered an
amount on line 11900 of your return and the amount on line 23400 is more than $82,125" and "You
entered an amount on line 11300 or line 14600 of your return and the amount on line 23400 is more
than $93,454": a count, 1 when either holds and 0 otherwise (T1 line 55 and line 23500 "If not,
enter "0" on line 23500.")."""

OAS_AND_FEDERAL_SUPPLEMENTS = AmountKind.declare(
    CATALOG, "oas_and_federal_supplements", non_negative=True
)
"""OAS and federal supplements, Federal Worksheet "Line 23500 - Social benefits repayment" line 3
"Line 1 plus line 2 =": line 1 "Old age security (OAS) pension from line 11300 of your return" plus
line 2 "Net federal supplements paid from line 14600 of your return"."""

SOCIAL_BENEFITS_LINE_5 = AmountKind.declare(CATALOG, "social_benefits_line_5", non_negative=True)
"""Social benefits chart line 5, Federal Worksheet "Line 23500 - Social benefits repayment" line 5
"Line 3 minus line 4 (if negative, enter "0") =": line 3 less line 4 "Overpayment of OAS benefits
recovered (box 20 of your T4A(OAS) slip)", not below zero."""

SOCIAL_BENEFITS_LINE_6 = AmountKind.declare(CATALOG, "social_benefits_line_6")
"""Social benefits chart line 6, Federal Worksheet "Line 23500 - Social benefits repayment" line 6
"Net income before adjustments from line 23400 of your return", plus, as Form T1206 Part 1 says,
"add the amount from line 4 of this form to line 6 of your Federal Worksheet in the calculation of
the social benefits repayment for the calculation of lines 23500 and 42200 of your tax return, if
applicable": the total split income. The form prints no "(if negative, enter "0")", so the kind is
signed."""

SOCIAL_BENEFITS_LINE_10 = AmountKind.declare(CATALOG, "social_benefits_line_10", non_negative=True)
"""Social benefits chart line 10, Federal Worksheet "Line 23500 - Social benefits repayment" line
10 "Add lines 7 to 9. =": line 7 (the EI benefits repayment), line 8 "Universal child care benefit
(UCCB) from line 11700 of your return" and line 9 "Registered disability savings plan (RDSP)
income from line 12500 of your return"."""

SOCIAL_BENEFITS_LINE_11 = AmountKind.declare(CATALOG, "social_benefits_line_11")
"""Social benefits chart line 11, Federal Worksheet "Line 23500 - Social benefits repayment" line
11 "Line 6 minus line 10 =": line 6 less line 10. The form prints no "(if negative, enter "0")", so
the kind is signed."""

SOCIAL_BENEFITS_LINE_14 = AmountKind.declare(CATALOG, "social_benefits_line_14", non_negative=True)
"""Social benefits chart line 14, Federal Worksheet "Line 23500 - Social benefits repayment" line
14 "Line 12 plus line 13 =": line 12 "UCCB repayment from line 21300 of your return" plus line 13
"RDSP income repayment (included in the amount on line 23200 of your return)"."""

SOCIAL_BENEFITS_LINE_15 = AmountKind.declare(CATALOG, "social_benefits_line_15")
"""Social benefits chart line 15, Federal Worksheet "Line 23500 - Social benefits repayment" line
15 "Line 11 plus line 14 Adjusted net income =": the adjusted net income. The form prints no "(if
negative, enter "0")", so the kind is signed."""

OAS_BENEFITS_BASE_AMOUNT = AmountKind.declare(
    CATALOG, "oas_benefits_base_amount", non_negative=True
)
"""OAS benefits base amount, Federal Worksheet "Line 23500 - Social benefits repayment" line 16
"OAS benefits base amount 93,343.00": a fixed amount, claimed whole."""

SOCIAL_BENEFITS_LINE_17 = AmountKind.declare(CATALOG, "social_benefits_line_17", non_negative=True)
"""Social benefits chart line 17, Federal Worksheet "Line 23500 - Social benefits repayment" line
17 "Line 15 minus line 16 (if negative, enter "0") =": the adjusted net income over the OAS benefits
base amount, not below zero."""

SOCIAL_BENEFITS_LINE_18 = AmountKind.declare(CATALOG, "social_benefits_line_18", non_negative=True)
"""Social benefits chart line 18, Federal Worksheet "Line 23500 - Social benefits repayment" line
18 "Amount from line 17 multiplied by 15% =": the OAS recovery tax before its limit."""

SOCIAL_BENEFITS_LINE_19 = AmountKind.declare(CATALOG, "social_benefits_line_19", non_negative=True)
"""Social benefits chart line 19, Federal Worksheet "Line 23500 - Social benefits repayment" line
19 "Enter whichever is less: amount from line 5 or line 18."."""

SOCIAL_BENEFITS_LINE_21 = AmountKind.declare(CATALOG, "social_benefits_line_21", non_negative=True)
"""Social benefits chart line 21, Federal Worksheet "Line 23500 - Social benefits repayment" line
21 "Line 19 plus line 20. Enter this amount on line 23500 and line 42200 of your return. =": line
19 plus line 20 "Amount from line 7, if any". It is the result of the chart whether or not the
chart applies; line 23500 counts it once only when it does."""

SOCIAL_BENEFITS_REPAYMENT = AmountKind.declare(
    CATALOG, "social_benefits_repayment", non_negative=True
)
"""Social benefits repayment, T1 line 55 and line 23500 "Line 55 and line 23500: If not, enter "0"
on line 23500.": the result of the Federal Worksheet chart (line 21) when the chart applies, else
0. Line 42200 carries it."""

TOTAL_SPLIT_INCOME = AmountKind.declare(CATALOG, "total_split_income", non_negative=True)
"""Total split income, Form T1206 Part 1 line 4 (68360) "Total split income: line 1 plus line 3
Enter this amount on line 23200 of your return.": the dividends of line 1 plus the other split
income of line 3, a part of the T1 line 23300 deductions and the tax base of line 8 (line 7)."""

TOSI_ADJUSTED_NET_INCOME = AmountKind.declare(CATALOG, "tosi_adjusted_net_income")
"""TOSI-adjusted net income, Form T1206 Part 1 line 6 "TOSI-adjusted net income: line 4 plus line 5
If negative, enter the result in brackets": the total split income plus the net income
before its floor (line 5 "or the amount you would have entered if the instructions on
line 23600 read "if negative, show in brackets""), which is line 23400 less line 23500, signed.

The form prints no "(if negative, enter "0")", so the kind is signed; it stands where the form's
note says "use the negative value when it is part of an adjusted net income calculation".
"""

TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO = AmountKind.declare(
    CATALOG, "tosi_adjusted_net_income_not_below_zero", non_negative=True
)
"""TOSI-adjusted net income, not below zero, Form T1206 Part 1 line 6 "(If the TOSI-adjusted net
income at line 6 is negative, use the negative value when it is part of an adjusted net income
calculation, otherwise use zero.)": line 6 with a negative result replaced by zero, for the amounts
that read it otherwise, the basic personal amount, the age amount and Schedule 6 line 7.
"""

CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION = AmountKind.declare(
    CATALOG, "canadian_armed_forces_and_police_deduction", non_negative=True
)
"""Canadian Armed Forces personnel and police deduction, T1 line 58 and line 24400 "Canadian Armed
Forces personnel and police deduction (box 43 of all T4 slips)": a starting amount."""

T4_SECURITY_OPTIONS_BOXES_39_AND_91 = AmountKind.declare(
    CATALOG, "t4_security_options_boxes_39_and_91", non_negative=True
)
"""T4 slips' boxes 39 and 91, Form T691 Part 1 line 28 "Total of all amounts in boxes 39 and 91 of
your T4 slips", the security options deduction under paragraph 110(1)(d) "included on line 24900 of
your return": the caller's amounts, entered once in the form `ca/security_options_boxes_39_and_91`
and read by the return through its total, `ca/t4_security_options_boxes_39_and_91_total`."""

T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL = AmountKind.declare(
    CATALOG, "t4_security_options_boxes_39_and_91_total", non_negative=True
)
"""Total of the T4 slips' boxes 39 and 91, Form T691 Part 1 line 28 "Total of all amounts in boxes
39 and 91 of your T4 slips": the total of the one record of the form
`ca/security_options_boxes_39_and_91` (`core/record_total`), read by line 30 "Line 28 plus line 29"
and by the line 24900 sum."""

T4_SECURITY_OPTIONS_BOXES_41_AND_92 = AmountKind.declare(
    CATALOG, "t4_security_options_boxes_41_and_92", non_negative=True
)
"""T4 slips' boxes 41 and 92, Form T691 Part 1 line 35 "total of all amounts in boxes 41 and 92 of
your T4 slips", the security options deduction under paragraph 110(1)(d.1) "included on line 24900
of your return": the caller's amounts, entered once in the form
`ca/security_options_boxes_41_and_92` and read by the return through its total,
`ca/t4_security_options_boxes_41_and_92_total`."""

T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL = AmountKind.declare(
    CATALOG, "t4_security_options_boxes_41_and_92_total", non_negative=True
)
"""Total of the T4 slips' boxes 41 and 92, Form T691 Part 1 line 35 "total of all amounts in boxes
41 and 92 of your T4 slips": the total of the one record of the form
`ca/security_options_boxes_41_and_92` (`core/record_total`), read by line 38 "Add lines 35 to 37."
and by the line 24900 sum."""

SECURITY_OPTIONS_DEDUCTIONS = AmountKind.declare(
    CATALOG, "security_options_deductions", non_negative=True
)
"""Security options deductions, T1 line 59 and line 24900 "Security options deductions (boxes 39,
41, 91 and 92 of all T4 slips or see Form T1212)", computed, not entered: the sum, in Form T691
Part 1 line order, of line 28 (`ca/t4_security_options_boxes_39_and_91_total`), line 29 (line 2 of
Form T1212), line 31 (the gifts of publicly listed securities "included on line 24900 of your
return"), line 35 (`ca/t4_security_options_boxes_41_and_92_total`), line 36 (the prospector or
grubstaker deduction) and line 37 (the deferred profit-sharing plan deduction), each "included on
line 24900 of your return". Guide 5000-G line 24900 "Claim on line 24900 of your return the total of
the amounts shown in boxes 39, 41, 91, and 92 of your T4 slips" is the same claim."""

UCCB_REPAYMENT = AmountKind.declare(CATALOG, "uccb_repayment", non_negative=True)
"""UCCB repayment, T1 line 40 and line 21300 "Universal child care benefit (UCCB) repayment (box 12
of all RC62 slips)", also Federal Worksheet "Line 25000 - Other payments deduction" line 6 "Amount
from line 21300 of your return": a starting amount, a deduction from total income."""

RDSP_INCOME_REPAYMENT = AmountKind.declare(CATALOG, "rdsp_income_repayment", non_negative=True)
"""RDSP income repayment, Federal Worksheet "Line 25000 - Other payments deduction" line 7 "RDSP
income repayment (included in the amount on line 23200 of your return)": a starting amount."""

RDSP_INCOME_REPAYMENT_CHECKED = AmountKind.declare(
    CATALOG, "rdsp_income_repayment_checked", non_negative=True
)
"""RDSP income repayment after the check, Federal Worksheet "Line 23500 - Social benefits
repayment" line 13 "RDSP income repayment (included in the amount on line 23200 of your return)":
the amount of `ca/rdsp_income_repayment` after the check that it is not more than
`ca/other_deductions` (`core/at_most`), the caller's line 23200 amount. The readers of the
repayment use this amount."""

UCCB_AND_RDSP_INCOME = AmountKind.declare(CATALOG, "uccb_and_rdsp_income", non_negative=True)
"""UCCB and RDSP income, Federal Worksheet "Line 25000 - Other payments deduction" line 4 "Line 2
plus line 3 =": the amount from line 11700 of the return (line 2) and the amount from line 12500
(line 3)."""

NET_INCOME_LESS_UCCB_AND_RDSP_INCOME = AmountKind.declare(
    CATALOG, "net_income_less_uccb_and_rdsp_income"
)
"""Net income less the UCCB and RDSP income, Federal Worksheet "Line 25000 - Other payments
deduction" line 5 "Line 1 minus line 4 =": the net income (line 1, "Amount from line 23400 of your
return (if negative, enter "0")") less line 4.

The form prints no "(if negative, enter "0")" on line 5, so the kind is signed.
"""

UCCB_AND_RDSP_INCOME_REPAYMENTS = AmountKind.declare(
    CATALOG, "uccb_and_rdsp_income_repayments", non_negative=True
)
"""UCCB and RDSP income repayments, Federal Worksheet "Line 25000 - Other payments deduction" line
8 "Line 6 plus line 7 =": the UCCB repayment (line 6) and the RDSP income repayment (line 7)."""

OTHER_PAYMENTS_LIMIT_INCOME = AmountKind.declare(CATALOG, "other_payments_limit_income")
"""Income for the limit, Federal Worksheet "Line 25000 - Other payments deduction" line 9 "Line 5
plus line 8 =": the amount the worksheet compares with $93,454 ("If the amount on line 9 is more
than $93,454, go to canada.ca/line-25000 to find out how much you can deduct.").

The form prints no "(if negative, enter "0")" on line 9, so the kind is signed. The count of line 9
over $93,454 is derived from this line, and the manifest also returns it.
"""

OTHER_PAYMENTS_WORKSHEET_LINE_9_OVER_LIMIT = CountKind.declare(
    CATALOG, "other_payments_worksheet_line_9_over_limit", non_negative=True
)
"""Line 9 over the limit, Federal Worksheet "Line 25000 - Other payments deduction" "If the amount
on line 9 is more than $93,454, go to canada.ca/line-25000 to find out how much you can deduct.":
a derived count, 1 when line 9 (`ca/other_payments_limit_income`) is more than $93,454 and 0
otherwise (`ca/count_by_conditions`)."""

OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT = AmountKind.declare(
    CATALOG, "other_payments_deduction_above_limit", non_negative=True
)
"""Other payments deduction above the limit, Federal Worksheet "Line 25000 - Other payments
deduction" "go to canada.ca/line-25000 to find out how much you can deduct": the amount that
chart gives when line 9 is more than $93,454, a starting amount."""

OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED = AmountKind.declare(
    CATALOG, "other_payments_deduction_above_limit_checked", non_negative=True
)
"""Other payments deduction above the limit after the check, Federal Worksheet "Line 25000 - Other
payments deduction" and Guide 5000-G line 25000 "you may not be entitled to claim the full amount
from line 14700 of your return": the amount of `ca/other_payments_deduction_above_limit` after the
check that it is not more than `ca/income_support_benefits` (`core/at_most`). Line 9 chooses this
amount over line 14700."""

OTHER_PAYMENTS_DEDUCTION_AFTER_LIMIT = AmountKind.declare(
    CATALOG, "other_payments_deduction_after_limit", non_negative=True
)
"""Other payments deduction after the limit, Federal Worksheet "Line 25000 - Other payments
deduction" "Otherwise, enter the amount from line 14700 of your return on line 25000 of your
return.": line 14700 when line 9 is not more than $93,454, else the amount the canada.ca/line-25000
chart gives."""

OTHER_PAYMENTS_WORKSHEET_REQUIRED = CountKind.declare(
    CATALOG, "other_payments_worksheet_required", non_negative=True
)
"""Worksheet required, T1 line 60 and line 25000 "Other payments deduction (enter the amount from
line 14700 if you did not enter an amount on line 14600; otherwise, use Federal Worksheet)": a
derived count, 1 when an amount was entered on line 14600 (`ca/net_federal_supplements`) and 0
otherwise (`ca/count_by_conditions`)."""

OTHER_PAYMENTS_DEDUCTION = AmountKind.declare(
    CATALOG, "other_payments_deduction", non_negative=True
)
"""Other payments deduction, T1 line 60 and line 25000 "Other payments deduction (enter the amount
from line 14700 if you did not enter an amount on line 14600; otherwise, use Federal Worksheet)":
line 14700 when no amount was entered on line 14600, else the Federal Worksheet's result."""

ZONE_A_DAYS_LIVED = CountKind.declare(CATALOG, "zone_a_days_lived", non_negative=True)
"""Zone A days lived, Form T2222 Step 2 line 1 "Enter the number of days you lived in a prescribed
northern zone in 2025.": a starting count of days, as typed
(the form prints no maximum)."""

ZONE_A_ADDITIONAL_RESIDENCY_DAYS = CountKind.declare(
    CATALOG, "zone_a_additional_residency_days", non_negative=True
)
"""Zone A days for the additional residency amount, Form T2222 Step 2 line 2 "Enter the number of
days you qualify for the additional residency amount in 2025.": a starting count of days."""

ZONE_A_ADDITIONAL_RESIDENCY_DAYS_CHECKED = CountKind.declare(
    CATALOG, "zone_a_additional_residency_days_checked", non_negative=True
)
"""Zone A days for the additional residency amount, checked, Form T2222 Step 2 line 2: the days of
line 2 when they are at most the Zone A days of line 1, the days "you used to calculate your basic
residency amount"; more is an input error."""

ZONE_A_BASIC_RESIDENCY_AMOUNT = AmountKind.declare(
    CATALOG, "zone_a_basic_residency_amount", non_negative=True
)
"""Zone A basic residency amount, Form T2222 Step 2 line 1 "Enter the number of days you lived in
a prescribed northern zone in 2025. multiplied by $11.00 =": the days of line 1 times $11.00."""

ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT = AmountKind.declare(
    CATALOG, "zone_a_additional_residency_amount", non_negative=True
)
"""Zone A additional residency amount, Form T2222 Step 2 line 2 "Enter the number of days you
qualify for the additional residency amount in 2025. multiplied by $11.00 =": the days of line 2
times $11.00."""

ZONE_A_RESIDENCY_AMOUNT = AmountKind.declare(CATALOG, "zone_a_residency_amount", non_negative=True)
"""Zone A residency amount, Form T2222 Step 2 line 3 and line 67490 "Line 1 plus line 2 =": the
basic and the additional residency amounts of Zone A."""

ZONE_A_SPECIAL_WORK_SITE_BENEFITS = AmountKind.declare(
    CATALOG, "zone_a_special_work_site_benefits", non_negative=True
)
"""Zone A special work site benefits, Form T2222 Step 2 line 4 and line 67507 "If you worked at a
special work site, enter the amount from box 31 of your T4 slip or box 124 of your T4A slip that
represents the non-taxable benefits for board and lodging at the special work site.": a starting
amount. The site's location within 30 kilometres of a population centre is the filer's to apply."""

ZONE_A_RESIDENCY_AFTER_WORK_SITE = AmountKind.declare(
    CATALOG, "zone_a_residency_after_work_site", non_negative=True
)
"""Zone A residency amount after the work site benefits, Form T2222 Step 2 line 5 "Line 3 minus
line 4 (if negative, enter "0") =": line 3 less line 4, not below zero."""

ZONE_B_DAYS_LIVED = CountKind.declare(CATALOG, "zone_b_days_lived", non_negative=True)
"""Zone B days lived, Form T2222 Step 2 line 6 "Enter the number of days you lived in an
intermediate zone in 2025.": a starting count of days, as typed
(the form prints no maximum)."""

ZONE_B_ADDITIONAL_RESIDENCY_DAYS = CountKind.declare(
    CATALOG, "zone_b_additional_residency_days", non_negative=True
)
"""Zone B days for the additional residency amount, Form T2222 Step 2 line 7 "Enter the number of
days you qualify for the additional residency amount in 2025.": a starting count of days."""

ZONE_B_ADDITIONAL_RESIDENCY_DAYS_CHECKED = CountKind.declare(
    CATALOG, "zone_b_additional_residency_days_checked", non_negative=True
)
"""Zone B days for the additional residency amount, checked, Form T2222 Step 2 line 7: the days of
line 7 when they are at most the Zone B days of line 6, the days "you used to calculate your basic
residency amount"; more is an input error."""

ZONE_B_BASIC_RESIDENCY_AMOUNT = AmountKind.declare(
    CATALOG, "zone_b_basic_residency_amount", non_negative=True
)
"""Zone B basic residency amount, Form T2222 Step 2 line 6 "Enter the number of days you lived in
an intermediate zone in 2025. multiplied by $5.50 =": the days of line 6 times $5.50."""

ZONE_B_ADDITIONAL_RESIDENCY_AMOUNT = AmountKind.declare(
    CATALOG, "zone_b_additional_residency_amount", non_negative=True
)
"""Zone B additional residency amount, Form T2222 Step 2 line 7 "Enter the number of days you
qualify for the additional residency amount in 2025. multiplied by $5.50 =": the days of line 7
times $5.50."""

ZONE_B_RESIDENCY_AMOUNT = AmountKind.declare(CATALOG, "zone_b_residency_amount", non_negative=True)
"""Zone B residency amount, Form T2222 Step 2 line 8 and line 67520 "Line 6 plus line 7 =": the
basic and the additional residency amounts of Zone B."""

ZONE_B_SPECIAL_WORK_SITE_BENEFITS = AmountKind.declare(
    CATALOG, "zone_b_special_work_site_benefits", non_negative=True
)
"""Zone B special work site benefits, Form T2222 Step 2 line 9 and line 67529 "If you worked at a
special work site, enter the amount from box 31 of your T4 slip or box 124 of your T4A slip that
represents the non-taxable benefits for board and lodging at the special work site.": a starting
amount. The site's location within 30 kilometres of a population centre is the filer's to apply."""

ZONE_B_RESIDENCY_AFTER_WORK_SITE = AmountKind.declare(
    CATALOG, "zone_b_residency_after_work_site", non_negative=True
)
"""Zone B residency amount after the work site benefits, Form T2222 Step 2 line 10 "Line 8 minus
line 9 (if negative, enter "0") =": line 8 less line 9, not below zero."""

RESIDENCY_AMOUNT = AmountKind.declare(CATALOG, "residency_amount", non_negative=True)
"""Residency amount, Form T2222 Step 2 line 11 "Line 5 plus line 10 =": the Zone A and Zone B
amounts after the work site benefits."""

RESIDENCY_NET_INCOME_LIMIT = AmountKind.declare(
    CATALOG, "residency_net_income_limit", non_negative=True
)
"""Residency limit on net income, Form T2222 Step 2 line 12 "Enter your net income from line 23600
of your return. multiplied by 20%  =": the net income times 20%."""

RESIDENCY_DEDUCTION = AmountKind.declare(CATALOG, "residency_deduction", non_negative=True)
"""Residency deduction, Form T2222 Step 2 line 13 "Enter whichever is less: amount from line 11 or
line 12. Residency deduction": the lesser of lines 11 and 12; line 17 of Step 4 is this amount."""

TRAVEL_INDIVIDUAL = CountKind.declare(CATALOG, "travel_individual", non_negative=True)
"""Individual, Form T2222 Step 3 Chart A "Row A: Enter the name of each individual, including
yourself, whose travel you are claiming." and Chart B "Column 1: Enter the name of the person who
took the trip.": a count, the number the filer gives each individual, which only names the
individual and which no capability reads."""

TRIP_ZONE = CountKind.declare(CATALOG, "trip_zone", non_negative=True)
"""Zone of a trip, Form T2222 Step 3 Chart B "Enter the lowest amount from column 3, 4, or 5 in the
column for the prescribed zone(s) you resided in at the time of the trip.": a count, 1 for Zone A
(column 6) and 2 for Zone B (column 7)."""

TRIP_BENEFIT_OR_STANDARD_AMOUNT = AmountKind.declare(
    CATALOG, "trip_benefit_or_standard_amount", non_negative=True
)
"""Benefit or standard amount of a trip, Form T2222 Step 3 Chart B "Column 3: Enter either the
taxable travel benefit or the portion of the individual's $1,200 standard amount for the trip.":
an input for each trip."""

TRIP_TRAVEL_EXPENSES = AmountKind.declare(CATALOG, "trip_travel_expenses", non_negative=True)
"""Travel expenses of a trip, Form T2222 Step 3 Chart B "Column 4: Enter the amount of travel
expenses for each trip taken.": an input for each trip."""

TRIP_LOWEST_RETURN_AIRFARE = AmountKind.declare(
    CATALOG, "trip_lowest_return_airfare", non_negative=True
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

STANDARD_AMOUNT_ALLOCATED_1 = AmountKind.declare(
    CATALOG, "standard_amount_allocated_1", non_negative=True
)
"""First allocation of the standard amount, Form T2222 Step 3 Chart A "Row B: Enter the name of
everyone (including yourself) who is claiming a deduction for trips taken by the individual in row
A and the total portion of the $1,200 standard amount allocated by each claimant for all trips
taken by that individual.": the first claimant's portion, an input."""

STANDARD_AMOUNT_ALLOCATED_2 = AmountKind.declare(
    CATALOG, "standard_amount_allocated_2", non_negative=True
)
"""Second allocation of the standard amount, Form T2222 Step 3 Chart A row B: the second
claimant's portion, an input."""

STANDARD_AMOUNT_ALLOCATED_3 = AmountKind.declare(
    CATALOG, "standard_amount_allocated_3", non_negative=True
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

STANDARD_AMOUNT_ALLOCATED = AmountKind.declare(
    CATALOG, "standard_amount_allocated", non_negative=True
)
"""Standard amount allocated, Form T2222 Step 3 Chart A "Row C: Enter the total of all amounts in
row B. This total cannot be more than $1,200.": row C added over the individuals. No line of the
form reads it, so the manifest returns it."""

TRAVEL_TOTAL_ZONE_A = AmountKind.declare(CATALOG, "travel_total_zone_a", non_negative=True)
"""Zone A total of the trips, Form T2222 Step 3 Chart B "(A) Total (add all the amounts under
Column 6) =", line 14 and line 67540 "Amount A of Chart B"."""

TRAVEL_TOTAL_ZONE_B = AmountKind.declare(CATALOG, "travel_total_zone_b", non_negative=True)
"""Zone B total of the trips, Form T2222 Step 3 Chart B "(B) Total (add all the amounts under
Column 7) =", read by line 15 "Enter the total from box B. Line 67560"."""

TRAVEL_ZONE_B_DEDUCTION = AmountKind.declare(CATALOG, "travel_zone_b_deduction", non_negative=True)
"""Zone B travel amount, Form T2222 Step 3 line 15 "Enter the total from box B. Line 67560
multiplied by 50% =": the Zone B total times 50%."""

TRAVEL_DEDUCTION = AmountKind.declare(CATALOG, "travel_deduction", non_negative=True)
"""Travel deduction, Form T2222 Step 3 line 16 "Line 14 plus line 15 Travel deduction =": the Zone
A total (line 14) and line 15; line 18 of Step 4 is this amount."""

NORTHERN_RESIDENTS_DEDUCTIONS = AmountKind.declare(
    CATALOG, "northern_residents_deductions", non_negative=True
)
"""Northern residents deductions, Form T2222 Step 4 line 19 "Line 17 plus line 18 Enter this amount
on line 25500 of your return. Northern residents deductions =" and T1 line 66 and line 25500
"Northern residents deductions (complete Form T2222)": the residency deduction (line 17) and the
travel deduction (line 18)."""

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

CPP_PART_5_DEDUCTION_ON_SELF_EMPLOYMENT = AmountKind.declare(
    CATALOG, "cpp_part_5_deduction_on_self_employment", non_negative=True
)
"""Part 5 line 88 on T1 line 22200, once for each Part 5 completed (1 or 0). Summed with the Part 4
deduction into cpp_deduction_on_self_employment_and_other_earnings."""

CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS = AmountKind.declare(
    CATALOG, "cpp_deduction_on_self_employment_and_other_earnings", non_negative=True
)
"""T1 line 22200: the Part 4 deduction (cpp_deduction_on_self_employment) plus the Part 5 deduction
(cpp_part_5_deduction_on_self_employment), read by 05_deductions and 20_alternative_minimum_tax."""

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

CPP_BASE_CONTRIBUTIONS_ON_RETURN = AmountKind.declare(
    CATALOG, "cpp_base_contributions_on_return", non_negative=True
)
"""Base CPP contributions on the return, T1 line 30800 and ON428 line 58240: the total of
Schedule 8 (schedule_8_cpp_base_contributions_on_return) plus the total of Form RC381
(rc381_cpp_base_contributions_on_return, Part 4 line 98 or Part 3a line 70 or Part 3b line 81).
The return carries one of the two forms, so one of the two totals is 0."""

CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN = AmountKind.declare(
    CATALOG, "cpp_enhanced_contributions_on_return", non_negative=True
)
"""Enhanced CPP contributions on the return, T1 line 22215: the total of Schedule 8
(schedule_8_cpp_enhanced_contributions_on_return) plus the total of Form RC381
(rc381_cpp_enhanced_contributions_on_return, Part 4 line 110 or Part 3a line 73 or Part 3b line
93). A deduction from total income, not a credit. The return carries one of the two forms, so one
of the two totals is 0."""


# Form T1-M, Moving Expenses Deduction, one copy for each move (T1 line 21900). The caller's inputs
# of one move are the fields of the record list `ca/t1_m_moves`, in the form's line order; the
# computed lines are the form's own lines, and the form exports line 29 and line 30.

MOVING_OLD_HOME_DISTANCE = AmountKind.declare(
    CATALOG, "moving_old_home_distance", non_negative=True
)
"""Distance from the old home, Form T1-M Part 2 line 1 "Distance in kilometres between your old home
and your new work location or educational institution": a starting amount in kilometres."""

MOVING_NEW_HOME_DISTANCE = AmountKind.declare(
    CATALOG, "moving_new_home_distance", non_negative=True
)
"""Distance from the new home, Form T1-M Part 2 line 2 "Distance in kilometres between your new home
and your new work location or educational institution": a starting amount in kilometres."""

MOVING_TRANSPORTATION_AND_STORAGE = AmountKind.declare(
    CATALOG, "moving_transportation_and_storage", non_negative=True
)
"""Transportation and storage costs, Form T1-M Part 4 line 4 "Transportation and storage costs for
household items": a starting amount."""

MOVING_TRAVEL_EXPENSES = AmountKind.declare(CATALOG, "moving_travel_expenses", non_negative=True)
"""Travel expenses from the old home to the new home, Form T1-M Part 4 line 5 "Travel expenses":
a starting amount, as the filer works it out by either method."""

MOVING_ACCOMMODATION_EXPENSES = AmountKind.declare(
    CATALOG, "moving_accommodation_expenses", non_negative=True
)
"""Accommodation expenses of the move, Form T1-M Part 4 line 6 "Accommodation expenses": a starting
amount."""

MOVING_MEAL_EXPENSES = AmountKind.declare(CATALOG, "moving_meal_expenses", non_negative=True)
"""Meal expenses of the move, Form T1-M Part 4 line 7 "Meal expenses": a starting amount, as the
filer works it out by either method."""

MOVING_TEMPORARY_LODGING = AmountKind.declare(
    CATALOG, "moving_temporary_lodging", non_negative=True
)
"""Temporary accommodation expenses near the new or old home, Form T1-M Part 4 line 9 "Temporary
living expenses near new or old home (maximum 15 days)" "Accommodation expenses": a starting
amount."""

MOVING_TEMPORARY_MEALS = AmountKind.declare(CATALOG, "moving_temporary_meals", non_negative=True)
"""Temporary meal expenses near the new or old home, Form T1-M Part 4 line 10 "Temporary living
expenses near new or old home (maximum 15 days)" "Meal expenses": a starting amount."""

MOVING_LEASE_CANCELLATION = AmountKind.declare(
    CATALOG, "moving_lease_cancellation", non_negative=True
)
"""Cost of cancelling the lease for the old home, Form T1-M Part 4 line 12 "Cost of cancelling the
lease for your old home": a starting amount."""

MOVING_INCIDENTAL_COSTS = AmountKind.declare(CATALOG, "moving_incidental_costs", non_negative=True)
"""Incidental costs related to the move, Form T1-M Part 4 line 13 "Incidental costs related to the
move (specify):": a starting amount."""

MOVING_OLD_HOME_MAINTENANCE = AmountKind.declare(
    CATALOG, "moving_old_home_maintenance", non_negative=True
)
"""Costs to maintain the old home when vacant, Form T1-M Part 4 line 14 "Costs to maintain your old
home when vacant (maximum $5,000)": the costs the caller paid, before the maximum of line 14 (the
`ca/moving_old_home_maintenance_cap` dataset) is checked."""

MOVING_SELLING_COMMISSION = AmountKind.declare(
    CATALOG, "moving_selling_commission", non_negative=True
)
"""Real estate commission on the sale of the old home, Form T1-M Part 4 line 16 "Real estate
commission": a starting amount."""

MOVING_SELLING_LEGAL_FEES = AmountKind.declare(
    CATALOG, "moving_selling_legal_fees", non_negative=True
)
"""Legal or notarial fees on the sale of the old home, Form T1-M Part 4 line 17 "Legal or notarial
fees": a starting amount."""

MOVING_SELLING_ADVERTISING = AmountKind.declare(
    CATALOG, "moving_selling_advertising", non_negative=True
)
"""Advertising on the sale of the old home, Form T1-M Part 4 line 18 "Advertising": a starting
amount."""

MOVING_SELLING_OTHER_COSTS = AmountKind.declare(
    CATALOG, "moving_selling_other_costs", non_negative=True
)
"""Other selling costs of the old home, Form T1-M Part 4 line 19 "Other selling costs (specify):": a
starting amount."""

MOVING_BUYING_LEGAL_FEES = AmountKind.declare(
    CATALOG, "moving_buying_legal_fees", non_negative=True
)
"""Legal or notarial fees on the purchase of the new home, Form T1-M Part 4 line 21 "Legal or
notarial fees": a starting amount, claimable only when the old home was sold because of the move."""

MOVING_BUYING_TAXES = AmountKind.declare(CATALOG, "moving_buying_taxes", non_negative=True)
"""Taxes paid for the registration or transfer of title to the new home, Form T1-M Part 4 line 22
"Taxes paid for the registration or transfer of title (do not include GST/HST)": a starting
amount."""

MOVING_REIMBURSEMENT = AmountKind.declare(CATALOG, "moving_reimbursement", non_negative=True)
"""Reimbursement or allowance for the moving expenses, Form T1-M Part 4 line 25 "Enter any
reimbursement or allowance that is not included in your income and that you received for
moving expenses included in the amount on line 24.": a starting amount."""

MOVING_NET_ELIGIBLE_INCOME = AmountKind.declare(
    CATALOG, "moving_net_eligible_income", non_negative=True
)
"""Net eligible income at the new work location, Form T1-M Part 4 line 28 "Net eligible income": the
employment or self-employment income, or the student's taxable awards, the caller enters as the
form takes them; a starting amount."""

MOVING_BUSINESS_INCOME = AmountKind.declare(CATALOG, "moving_business_income", non_negative=True)
"""Business income at the new work location, Form T1-M Part 4 line 28 "Net eligible income": "the
net amounts earned at the new work location that are included on lines 13500, 13700, 13900, 14100,
and 14300 of your return", the positive net of the Form T2125 statements on business line 1
(`core/record_positive_total`). A loss counts 0, so it is the part of line 13500 that line 28 is
taken from."""

MOVING_PROFESSIONAL_INCOME = AmountKind.declare(
    CATALOG, "moving_professional_income", non_negative=True
)
"""Professional income at the new work location, Form T1-M Part 4 line 28 "Net eligible income"
("the net amounts earned at the new work location that are included on lines 13500, 13700, 13900,
14100, and 14300 of your return"), the positive net of the Form T2125 statements on professional
line 2 (`core/record_positive_total`). A loss counts 0, so it is the part of line 13700 that line 28
is taken from."""

MOVING_COMMISSION_INCOME = AmountKind.declare(
    CATALOG, "moving_commission_income", non_negative=True
)
"""Commission income at the new work location, Form T1-M Part 4 line 28 "Net eligible income"
("the net amounts earned at the new work location that are included on lines 13500, 13700, 13900,
14100, and 14300 of your return"), the positive net of the Form T2125 statements on commission line
3 (`core/record_positive_total`). A loss counts 0, so it is the part of line 13900 that line 28 is
taken from."""

MOVING_FARMING_INCOME = AmountKind.declare(CATALOG, "moving_farming_income", non_negative=True)
"""Farming income at the new work location, Form T1-M Part 4 line 28 "Net eligible income" ("the
net amounts earned at the new work location that are included on lines 13500, 13700, 13900, 14100,
and 14300 of your return"), the positive net of the Form T2042 statements
(`core/record_positive_total`). A loss counts 0, so it is the part of line 14100 that line 28 is
taken from."""

MOVING_FISHING_INCOME = AmountKind.declare(CATALOG, "moving_fishing_income", non_negative=True)
"""Fishing income at the new work location, Form T1-M Part 4 line 28 "Net eligible income" ("the
net amounts earned at the new work location that are included on lines 13500, 13700, 13900, 14100,
and 14300 of your return"), the positive net of the Form T2121 statements
(`core/record_positive_total`). A loss counts 0, so it is the part of line 14300 that line 28 is
taken from."""

MOVING_ELIGIBLE_INCOME_LINES = AmountKind.declare(
    CATALOG, "moving_eligible_income_lines", non_negative=True
)
"""Income lines that Form T1-M line 28 is taken from, Form T1-M Part 4 line 28 "Net eligible
income": the employment income (line 10100), the other employment income (line 10400), the taxable
scholarships of a student and the five self-employment amounts above, added (`core/sum`). Line 28
is at most this sum, a loss counting 0. The sum is not a form line."""

MOVING_NET_ELIGIBLE_INCOME_CHECKED = AmountKind.declare(
    CATALOG, "moving_net_eligible_income_checked", non_negative=True
)
"""Net eligible income at the new work location after the check, Form T1-M Part 4 line 28 "Net
eligible income": the amount of `ca/moving_net_eligible_income` after the check that it is not more
than `ca/moving_eligible_income_lines` (`core/at_most`). Line 28 is taken from the amounts on lines
10100 and 10400, 13500, 13700, 13900, 14100 and 14300 and the taxable scholarships of a student, so
it is at most their sum (a loss counts 0). The printed text gives no other limit (looked in
t1-m-25e.pdf and 5000-g-25e.txt, found nothing), and the bound is looser than the printed net of
lines 20700, 21200, 22215, 22900, 23100 and 23200. An amount above is an input error, not capped.
Lines 29 and 30 read this amount."""

MOVING_DISTANCE_DIFFERENCE = AmountKind.declare(CATALOG, "moving_distance_difference")
"""Distance difference, Form T1-M Part 2 line 3 "Line 1 minus line 2": the old home distance less
the new one. The form prints no floor, so it may be negative; the 40 kilometre test reads it."""

MOVING_TRAVEL_EXPENSES_SUBTOTAL = AmountKind.declare(
    CATALOG, "moving_travel_expenses_subtotal", non_negative=True
)
"""Travel expenses subtotal, Form T1-M Part 4 line 8 "Add lines 5 to 7.": lines 5, 6 and 7."""

MOVING_TEMPORARY_LIVING_SUBTOTAL = AmountKind.declare(
    CATALOG, "moving_temporary_living_subtotal", non_negative=True
)
"""Temporary living subtotal, Form T1-M Part 4 line 11 "Line 9 plus line 10": lines 9 and 10."""

MOVING_OLD_HOME_MAINTENANCE_CAP = AmountKind.declare(
    CATALOG, "moving_old_home_maintenance_cap", non_negative=True
)
"""Maximum costs to maintain the old home when vacant, Form T1-M Part 4 line 14 "Costs to maintain
your old home when vacant (maximum $5,000)": the $5,000, the most the line can be."""

MOVING_OLD_HOME_MAINTENANCE_CHECKED = AmountKind.declare(
    CATALOG, "moving_old_home_maintenance_checked", non_negative=True
)
"""Costs to maintain the old home when vacant, not above the maximum, Form T1-M Part 4 line 14
"Costs to maintain your old home when vacant (maximum $5,000)": the caller's costs, refused above
the `ca/moving_old_home_maintenance_cap` dataset's amount."""

MOVING_LEASE_AND_INCIDENTAL_SUBTOTAL = AmountKind.declare(
    CATALOG, "moving_lease_and_incidental_subtotal", non_negative=True
)
"""Lease, incidental and old home costs subtotal, Form T1-M Part 4 line 15 "Add lines 12 to 14.":
lines 12, 13 and 14 (the capped line 14)."""

MOVING_SELLING_SUBTOTAL = AmountKind.declare(CATALOG, "moving_selling_subtotal", non_negative=True)
"""Cost of selling the old home subtotal, Form T1-M Part 4 line 20 "Add lines 16 to 19.": lines 16,
17, 18 and 19."""

MOVING_BUYING_SUBTOTAL = AmountKind.declare(CATALOG, "moving_buying_subtotal", non_negative=True)
"""Cost of buying the new home subtotal, Form T1-M Part 4 line 23 "Line 21 plus line 22": lines 21
and 22."""

MOVING_TOTAL_EXPENSES = AmountKind.declare(CATALOG, "moving_total_expenses", non_negative=True)
"""Total moving expenses, Form T1-M Part 4 line 24 "Total moving expenses" "Add lines 4, 8, 11, 15,
20 and 23.": the transportation and storage, travel, temporary living, lease and incidental, selling
and buying subtotals."""

MOVING_NET_EXPENSES = AmountKind.declare(CATALOG, "moving_net_expenses", non_negative=True)
"""Net moving expenses, Form T1-M Part 4 line 26 "Net moving expenses" "Line 24 minus line 25 (if
negative, enter "0")": the total less the reimbursement, not below 0."""

MOVING_NET_EXPENSES_CARRIED = AmountKind.declare(
    CATALOG, "moving_net_expenses_carried", non_negative=True
)
"""Amount from line 26 of the previous page, Form T1-M Part 4 line 27: the net moving expenses of
line 26, carried to the second page."""

MOVING_LESSER_OF_EXPENSES_AND_INCOME = AmountKind.declare(
    CATALOG, "moving_lesser_of_expenses_and_income", non_negative=True
)
"""Lesser of the net moving expenses and the net eligible income, Form T1-M Part 4 "Enter whichever
is less: amount from line 27 or line 28." (before line 29): the lesser of lines 27 and 28."""

MOVING_EXPENSES_CLAIM = AmountKind.declare(CATALOG, "moving_expenses_claim", non_negative=True)
"""Allowable moving expenses of one move, Form T1-M Part 4 line 29 "Allowable moving expenses"
"Enter this amount on line 21900 of your return.": the lesser amount of the move, 0 when the
distance difference of line 3 is under the 40 kilometres of the `ca/moving_distance_threshold`
dataset (Part 2 "If the amount on line 3 is less than 40 kilometres, you cannot deduct your
moving expenses.")."""

MOVING_UNUSED_EXPENSES_BEFORE_TEST = AmountKind.declare(
    CATALOG, "moving_unused_expenses_before_test", non_negative=True
)
"""Line 27 less line 28 of Form T1-M Part 4 line 30 "Line 27 minus line 28 (if negative, enter
"0")", before the 40 kilometre test of Part 2: the net moving expenses of line 27 less line 28, not
below 0."""

MOVING_UNUSED_EXPENSES = AmountKind.declare(CATALOG, "moving_unused_expenses", non_negative=True)
"""Unused moving expenses available to carry forward, Form T1-M Part 4 line 30 "Your unused moving
expenses available to carry forward to a future year": line 27 less line 28, not below 0, and 0
when the distance difference of line 3 is under the 40 kilometres of the
`ca/moving_distance_threshold` dataset (Part 2 "If the amount on line 3 is less than 40
kilometres, you cannot deduct your moving expenses. If this is the case, do not complete the rest
of this form."). Nothing on the return reads it."""

MOVING_EXPENSES_DEDUCTION = AmountKind.declare(
    CATALOG, "moving_expenses_deduction", non_negative=True
)
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
