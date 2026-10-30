"""The federal catalog: the Canada workers benefit.

The Canada workers benefit lines.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.jurisdictions.ca.catalog.base import CATALOG

CWB_ELIGIBLE_DEPENDANTS = CATALOG.declare("cwb_eligible_dependants", int, non_negative=True)
"""Number of eligible dependants for the Canada workers benefit, Schedule 6 Step 1 "Line 38100: Do
you have an eligible dependant? 1 Yes or 2 No": a starting count, 0 or 1, the count of 0 answering
no and of 1 yes.

Schedule 6 defines the eligible dependant by its own conditions: "They were your or your spouse's or
common-law partner's child"; "They were under 19 years of age and lived with you on December 31,
2025 ..."; "They were not eligible for the CWB for 2025". They differ from the eligible dependant
claimed for on T1 line 30400, so a dependant can be one and not the other. A count above 1 is
refused by `ca/cwb_eligible_dependants_checked` (`ca/yes_or_no_count`), so the conditions are the
return's to check against its facts; the dependant's own conditions are not computed here.
"""

CWB_ELIGIBLE_DEPENDANTS_CHECKED = CATALOG.declare(
    "cwb_eligible_dependants_checked", int, non_negative=True
)
"""Schedule 6 Step 1 "Line 38100: Do you have an eligible dependant? 1 Yes or 2 No": the answer of
`ca/cwb_eligible_dependants` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1
or 0. A count of 2 or more is refused, not capped."""

CWB_ELIGIBLE_SPOUSES = CATALOG.declare("cwb_eligible_spouses", int, non_negative=True)
"""Number of eligible spouses for the Canada workers benefit, Schedule 6 Step 1 "Line 38101: Do you
have an eligible spouse? 1 Yes or 2 No": a starting count, 0 or 1, the count of 0 answering no and
of 1 yes.

Schedule 6 defines the eligible spouse by its own conditions: "They were your cohabiting spouse or
common-law partner on December 31, 2025"; "They were a resident of Canada throughout 2025"; "They
were not enrolled as a full-time student at a designated educational institution for a total of
more than 13 weeks in the year unless they had an eligible dependant at the end of the year"; "They
were not confined to a prison or similar institution for a period of at least 90 days during the
year"; "They were not exempt from income tax in Canada for a period in the year when they were an
officer or a servant of another country (such as a diplomat) residing in Canada or they were a
family member who resided with such a person or an employee of such a person, at any time in the
year". They are the filer's judgement, as for the eligible dependant. A count above 1 is refused by
`ca/cwb_eligible_spouses_checked`, and a 1 needs a spouse on December 31
(`ca/cwb_spouse_for_eligible_spouse_checked`)."""

CWB_ELIGIBLE_SPOUSES_CHECKED = CATALOG.declare(
    "cwb_eligible_spouses_checked", int, non_negative=True
)
"""Schedule 6 Step 1 "Line 38101: Do you have an eligible spouse? 1 Yes or 2 No": the answer of
`ca/cwb_eligible_spouses` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or
0. A count of 2 or more is refused, not capped."""

CWB_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED = CATALOG.declare(
    "cwb_spouse_for_eligible_spouse_checked", int, non_negative=True
)
"""The eligible spouse answer with a spouse on December 31, 2025, Schedule 6 Step 1 line 38101: the
checked answer `ca/cwb_eligible_spouses_checked` is at least the spouse or common-law partner count
on December 31, 2025 (`ca/spouse_or_common_law_partner_on_december_31_total`), `ca/count_at_least`.
An eligible spouse is a cohabiting spouse or common-law partner on December 31, 2025, so a 1 with no
spouse is an input error. Not a line of the form."""

CWB_SPOUSE_EMPLOYMENT_INCOME = CATALOG.declare(
    "cwb_spouse_employment_income", Decimal, non_negative=True
)
"""Your eligible spouse's employment income, Schedule 6 Part A line 1 "Employment income and other
employment income from line 10100 and line 10400 of the return", column 2 "Your eligible spouse":
the amount as entered for the spouse, not computed here."""

CWB_SPOUSE_TAXABLE_SCHOLARSHIPS = CATALOG.declare(
    "cwb_spouse_taxable_scholarships", Decimal, non_negative=True
)
"""Your eligible spouse's taxable scholarships, Schedule 6 Part A line 2 "Taxable scholarships,
fellowships, bursaries, and artists' project grants from line 13010 of the return", column 2 "Your
eligible spouse" (38106): the amount as entered for the spouse."""

CWB_SPOUSE_SELF_EMPLOYMENT_INCOME = CATALOG.declare(
    "cwb_spouse_self_employment_income", Decimal, non_negative=True
)
"""Your eligible spouse's self-employment income, Schedule 6 Part A line 3 "Total self-employment
income from lines 13500, 13700, 13900, 14100, and 14300 of the return (excluding losses) (Note 2)",
column 2 "Your eligible spouse": the profit only, as Note 2 says, entered for the spouse."""

CWB_EMPLOYMENT_INCOME = CATALOG.declare("cwb_employment_income", Decimal, non_negative=True)
"""Employment income for the Canada workers benefit, Schedule 6 line 1 "Employment income and other
employment income from line 10100 and line 10400 of the return": the employment income and the
other employment income added, as line 1 of the medical supplement's worksheet adds them. The
quote is from Schedule 6 (5000-S6)."""

WORKING_INCOME = CATALOG.declare("working_income", Decimal, non_negative=True)
"""Working income, Schedule 6 line 5 "Add lines 1 to 4. Enter the result, even if it is "0".
Working income": line 1 "Employment income and other employment income from line 10100 and line
10400 of the return" (the employment income and the other employment income, see
CWB_EMPLOYMENT_INCOME), line 2 "Taxable scholarships, fellowships, bursaries, and artists' project
grants from line 13010 of the return", and line 3 "Total self-employment income from lines 13500,
13700, 13900, 14100, and 14300 of the return (excluding losses) (Note 2)". Line 4 "Tax-exempt
working income earned on a reserve" is `ca/cwb_tax_exempt_working_income`, zero unless the election
of line 38105 is yes, and is added here as a line of column 1.

This is column 1 ("You") only; line 6 "Add the amounts from line 5 in columns 1 and 2. Enter this
amount on line 16. Family working income" adds column 2 (`ca/cwb_spouse_working_income`), see
`ca/cwb_family_working_income`."""

CWB_FAMILY_NET_INCOME_LINE_10 = CATALOG.declare("cwb_family_net_income_line_10", Decimal)
"""Your column, Schedule 6 Part B line 10 "Add lines 7 to 9.": line 7 "Net income from line 23600 of
the return (or the amount you would have entered if the instructions on line 23600 said "if
negative, show in brackets")" (the TOSI-adjusted net income of Form T1206 Part 1 line 6, signed) and
line 9 "Total of universal child care benefit (UCCB) repayment (line 21300 of the return) and
registered disability savings plan (RDSP) income repayment (included on line 23200 of the return)"
(the UCCB and RDSP income repayments of the other payments worksheet); line 8 "Total of net exempt
income earned on a reserve" (`ca/cwb_tax_exempt_net_income`, zero unless the election is yes),
signed. The form prints no "(if negative, enter "0")" on line 10, so the kind is signed."""

CWB_FAMILY_NET_INCOME_LINE_12 = CATALOG.declare(
    "cwb_family_net_income_line_12", Decimal, non_negative=True
)
"""Your column, Schedule 6 Part B line 12 "Line 10 minus line 11 (if negative, enter "0")": line 11
is "Total of UCCB (line 11700 of the return) and RDSP income (line 12500 of the return)" (the UCCB
and RDSP income of the other payments worksheet)."""

CWB_INCLUDE_TAX_EXEMPT_INCOME = CATALOG.declare(
    "cwb_include_tax_exempt_income", int, non_negative=True
)
"""Schedule 6 line 38105 "Are you choosing to include tax-exempt income to calculate the CWB? (Note
1) 1 Yes or 2 No": a starting answer, 1 for yes and 0 for no, the election that includes the
tax-exempt income of line 4 and line 8 in both columns. A count above 1 is refused by
`ca/cwb_include_tax_exempt_income_checked` (`ca/yes_or_no_count`)."""

CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED = CATALOG.declare(
    "cwb_include_tax_exempt_income_checked", int, non_negative=True
)
"""Schedule 6 line 38105 "Are you choosing to include tax-exempt income to calculate the CWB? (Note
1) 1 Yes or 2 No": the answer of `ca/cwb_include_tax_exempt_income` after the check that it is 0 or
1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME = CATALOG.declare(
    "cwb_spouse_tax_exempt_working_income", Decimal, non_negative=True
)
"""Your eligible spouse's tax-exempt working income, Schedule 6 Part A column 2 line 4 "Tax-exempt
working income earned on a reserve (from line 10000 of Form T90, Income Exempt from Tax under the
Indian Act) (Note 1) and the tax-exempt portion of any allowance received as an emergency volunteer
(from line 10105 of the return)" 38107, as entered for the spouse: a starting amount, counted only
when the election is yes (`ca/cwb_spouse_tax_exempt_working_income_elected`)."""

CWB_SPOUSE_NET_EXEMPT_INCOME = CATALOG.declare("cwb_spouse_net_exempt_income", Decimal)
"""Your eligible spouse's net exempt income, Schedule 6 Part B column 2 line 8 "Total of net exempt
income earned on a reserve (line 10026 of Form T90) and the tax-exempt portion of any allowance
received as an emergency volunteer (line 10105 of the return)" 38109, as entered for the spouse: a
starting amount, signed as the net exempt income can be in brackets, counted only when the election
is yes (`ca/cwb_spouse_tax_exempt_net_income_elected`)."""

CWB_T90_EXEMPT_WORKING_INCOME_TOTAL = CATALOG.declare(
    "cwb_t90_exempt_working_income_total", Decimal, non_negative=True
)
"""Tax-exempt working income earned on a reserve, Schedule 6 line 4 "(from line 10000 of Form T90,
Income Exempt from Tax under the Indian Act) (Note 1)": the total exempt working income of the T90
form (`ca/t90_exempt_working_income`, T90 line 4 "Total exempt working income 10000"), read as the
one record of the form's export."""

CWB_T90_NET_EXEMPT_INCOME_TOTAL = CATALOG.declare("cwb_t90_net_exempt_income_total", Decimal)
"""Net exempt income earned on a reserve, Schedule 6 line 8 "(line 10026 of Form T90)": the net
exempt income of the T90 form (`ca/t90_net_exempt_income`, T90 line 20 "Net exempt income 10026"),
signed, read as the one record of the form's export."""

CWB_TAX_EXEMPT_WORKING_INCOME_BEFORE_ELECTION = CATALOG.declare(
    "cwb_tax_exempt_working_income_before_election", Decimal, non_negative=True
)
"""Tax-exempt working income before the election, Schedule 6 line 4 "Tax-exempt working income
earned on a reserve" and "the tax-exempt portion of any allowance received as an emergency
volunteer": the T90 total exempt working income (`ca/cwb_t90_exempt_working_income_total`) plus the
tax-exempt portion of the emergency volunteer allowance
(`ca/emergency_services_volunteer_exempt_income`, line 10105 of the return)."""

CWB_TAX_EXEMPT_WORKING_INCOME = CATALOG.declare(
    "cwb_tax_exempt_working_income", Decimal, non_negative=True
)
"""Tax-exempt working income, Schedule 6 Part A column 1 line 4 "Tax-exempt working income earned on
a reserve": the amount before the election, counted only when the election of line 38105 is yes
(`ca/cwb_include_tax_exempt_income_checked`), else 0. Line 5 adds it."""

CWB_TAX_EXEMPT_NET_INCOME_BEFORE_ELECTION = CATALOG.declare(
    "cwb_tax_exempt_net_income_before_election", Decimal
)
"""Tax-exempt net income before the election, Schedule 6 line 8 "Total of net exempt income earned
on a reserve" and "the tax-exempt portion of any allowance received as an emergency volunteer": the
T90 net exempt income (`ca/cwb_t90_net_exempt_income_total`, signed) plus the emergency volunteer
allowance (`ca/emergency_services_volunteer_exempt_income`, line 10105 of the return)."""

CWB_TAX_EXEMPT_NET_INCOME = CATALOG.declare("cwb_tax_exempt_net_income", Decimal)
"""Tax-exempt net income, Schedule 6 Part B column 1 line 8 "Total of net exempt income earned on a
reserve (line 10026 of Form T90) and the tax-exempt portion of any allowance received as an
emergency volunteer (line 10105 of the return)": the amount before the election, counted only when
the election of line 38105 is yes (`ca/cwb_include_tax_exempt_income_checked`), else 0. Signed, as
line 10 adds it."""

CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME_ELECTED = CATALOG.declare(
    "cwb_spouse_tax_exempt_working_income_elected", Decimal, non_negative=True
)
"""Your eligible spouse's tax-exempt working income, Schedule 6 Part A column 2 line 4 "Tax-exempt
working income earned on a reserve" 38107: the spouse's amount as entered
(`ca/cwb_spouse_tax_exempt_working_income`), counted only when the election of line 38105 is yes
(`ca/cwb_include_tax_exempt_income_checked`), else 0."""

CWB_SPOUSE_TAX_EXEMPT_NET_INCOME_ELECTED = CATALOG.declare(
    "cwb_spouse_tax_exempt_net_income_elected", Decimal
)
"""Your eligible spouse's tax-exempt net income, Schedule 6 Part B column 2 line 8 "Total of net
exempt income earned on a reserve" 38109: the spouse's amount as entered
(`ca/cwb_spouse_net_exempt_income`, signed), counted only when the election of line 38105 is yes,
else 0."""

CWB_SPOUSE_WORKING_INCOME_BEFORE_ELIGIBILITY = CATALOG.declare(
    "cwb_spouse_working_income_before_eligibility", Decimal, non_negative=True
)
"""Your eligible spouse's working income before the eligible spouse answer, Schedule 6 Part A line 5
"Add lines 1 to 4. Enter the result, even if it is "0". Working income", column 2 "Your eligible
spouse" 38108: the spouse's lines 1, 2 and 3 added, and line 4
(`ca/cwb_spouse_tax_exempt_working_income_elected`, zero unless the election is yes)."""

CWB_SPOUSE_WORKING_INCOME = CATALOG.declare("cwb_spouse_working_income", Decimal, non_negative=True)
"""Your eligible spouse's working income, Schedule 6 Part A line 5 "Working income", column 2 "Your
eligible spouse" 38108 "=": the amount above, counted only with an eligible spouse
(`ca/cwb_eligible_spouses_checked`), else 0."""

CWB_FAMILY_WORKING_INCOME = CATALOG.declare("cwb_family_working_income", Decimal, non_negative=True)
"""Family working income, Schedule 6 Part A line 6 "Add the amounts from line 5 in columns 1 and 2.
Enter this amount on line 16. Family working income": line 5 of column 1 (`ca/working_income`) and
of column 2 (`ca/cwb_spouse_working_income`), which is 0 with no eligible spouse."""

CWB_SPOUSE_FAMILY_NET_INCOME_LINE_10 = CATALOG.declare(
    "cwb_spouse_family_net_income_line_10", Decimal
)
"""Your eligible spouse's column, Schedule 6 Part B line 10 "Add lines 7 to 9.": line 7 "Net income
from line 23600 of the return" of the spouse (`ca/spouse_net_income_before_adjustments`, signed) and
line 9, the spouse's UCCB repayment and RDSP income repayment, and line 8
(`ca/cwb_spouse_tax_exempt_net_income_elected`, zero unless the election is yes). Signed, as the
form prints no "(if negative, enter "0")" on line 10."""

CWB_SPOUSE_UCCB_AND_RDSP_INCOME = CATALOG.declare(
    "cwb_spouse_uccb_and_rdsp_income", Decimal, non_negative=True
)
"""Your eligible spouse's column, Schedule 6 Part B line 11 "Total of UCCB (line 11700 of the
return) and RDSP income (line 12500 of the return)": the spouse's UCCB and RDSP income as
entered."""

CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12_BEFORE_ELIGIBILITY = CATALOG.declare(
    "cwb_spouse_family_net_income_line_12_before_eligibility", Decimal, non_negative=True
)
"""Your eligible spouse's column, Schedule 6 Part B line 12 "Line 10 minus line 11 (if negative,
enter "0")", before the eligible spouse answer: line 10 less line 11, not below zero."""

CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12 = CATALOG.declare(
    "cwb_spouse_family_net_income_line_12", Decimal, non_negative=True
)
"""Your eligible spouse's column, Schedule 6 Part B line 12 "Line 10 minus line 11 (if negative,
enter "0")", column 2 "Your eligible spouse" 38110: the line above, counted only with an eligible
spouse (`ca/cwb_eligible_spouses_checked`), else 0."""

CWB_FAMILY_NET_INCOME_LINE_13 = CATALOG.declare(
    "cwb_family_net_income_line_13", Decimal, non_negative=True
)
"""Schedule 6 Part B line 13 "Add the amounts from line 12 in columns 1 and 2. If you had an
eligible spouse, continue at line 14; if not, continue at line 15.": the line 12 of column 1
(`ca/cwb_family_net_income_line_12`) and of column 2 (`ca/cwb_spouse_family_net_income_line_12`)
added, the column 2 amount being 0 with no eligible spouse."""

CWB_WORKING_INCOME_LESS_SPOUSE = CATALOG.declare("cwb_working_income_less_spouse", Decimal)
"""Schedule 6 line 14 "If your working income (line 5) is less than your eligible spouse's working
income": the working income of column 1 (`ca/working_income`) less that of column 2
(`ca/cwb_spouse_working_income`). Signed: a negative difference is the "less than" case of the
form, which takes column 1; zero or positive takes column 2 (see `ca/choose_by_sign`)."""

CWB_SECONDARY_EARNER_YOURS = CATALOG.declare(
    "cwb_secondary_earner_yours", Decimal, non_negative=True
)
"""Schedule 6 line 14, the "less than" case: "enter whichever is less from column 1: amount from
line 5 or line 12", the less of the working income of column 1 (`ca/working_income`) and its line
12 (`ca/cwb_family_net_income_line_12`)."""

CWB_SECONDARY_EARNER_SPOUSES = CATALOG.declare(
    "cwb_secondary_earner_spouses", Decimal, non_negative=True
)
"""Schedule 6 line 14, the "equal to or more than" case: "enter whichever is less from column 2:
amount from line 5 or line 12", the less of the working income of column 2
(`ca/cwb_spouse_working_income`) and its line 12 (`ca/cwb_spouse_family_net_income_line_12`)."""

CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM = CATALOG.declare(
    "cwb_secondary_earner_exemption_before_maximum", Decimal, non_negative=True
)
"""Schedule 6 line 14 "Secondary earner exemption", before its maximum: column 1's amount when the
working income is less than the spouse's, else column 2's (`ca/choose_by_sign`)."""

CWB_SECONDARY_EARNER_EXEMPTION = CATALOG.declare(
    "cwb_secondary_earner_exemption", Decimal, non_negative=True
)
"""Schedule 6 line 14 "Secondary earner exemption (maximum $16,386)": the amount before its
maximum, capped at `ca/cwb_secondary_earner_exemption_maximum` (`core/capped_amount`). With no
eligible spouse both spouse figures are 0, so the line is 0."""

ADJUSTED_FAMILY_NET_INCOME = CATALOG.declare("adjusted_family_net_income", Decimal)
"""Adjusted family net income, Schedule 6 line 15 "Line 13 minus line 14 Enter this amount on line
23 and line 35. Adjusted family net income": line 13 (`ca/cwb_family_net_income_line_13`) less line
14 (`ca/cwb_secondary_earner_exemption`, 0 with no eligible spouse). Signed: the form prints no "if
negative, enter 0" on this line."""

CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT = CATALOG.declare(
    "cwb_before_reduction_without_dependant", Decimal, non_negative=True
)
"""Canada workers benefit before its reduction with no eligible spouse and no eligible dependant,
Schedule 6 line 22 "Enter whichever is less: amount from line 20 or line 21.": line 20 "Line 18
multiplied by the percentage from line 19", line 19 "Rate 27%", on line 18 "Line 16 minus line 17
(if negative, enter "0")", the family working income (line 16) over line 17 "Base amount
3,000.00"; line 21 "If you had an eligible spouse or an eligible dependant, enter $2,813. If not,
enter $1,633.", here $1,633.

Schedule 6 states its conditions: "Complete this schedule if you met all of the following
conditions in 2025: You were a resident of Canada throughout the year; You earned working income
(see Part A); You were, at the end of the year, 19 years of age or older, or you resided with your
spouse or common-law partner or your child"; "You cannot claim the CWB for 2025 if any of the
following conditions apply to you: You were enrolled as a full-time student at a designated
educational institution for a total of more than 13 weeks in the year, unless you had an eligible
dependant at the end of the year; You were confined to a prison or similar institution for a period
of at least 90 days during the year; You were exempt from income tax in Canada for a period in the
year when you were an officer or a servant of another country (such as a diplomat) residing in
Canada or you were a family member who resided with such a person or an employee of such a person,
at any time in the year"; and, under line 6, "You can claim the basic CWB in Step 2 if the family
working income on line 6 is more than $3,000." Eligibility is the return's to state, not computed
here. The basic amount only: the disability supplement is Step 3 (`ca/cwb_disability_supplement`)
and the advance payments are Step 4."""

CWB_REDUCTION_WITHOUT_DEPENDANT = CATALOG.declare(
    "cwb_reduction_without_dependant", Decimal, non_negative=True
)
"""Canada workers benefit reduction with no eligible spouse and no eligible dependant, Schedule 6
line 27 "Line 25 multiplied by the percentage from line 26": line 26 "Rate 15%" on line 25 "Line
23 minus line 24 (if negative, enter "0")", line 23 "Adjusted family net income from line 15" over
line 24 "If you had an eligible spouse or an eligible dependant, enter $30,639. If not, enter
$26,855.", here $26,855.

The chart's "Basic CWB: $37,742" limit is not wired: it follows from the arithmetic, as 1,633 less
15% of (37,742 - 26,855) is below zero."""

CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT = CATALOG.declare(
    "canada_workers_benefit_without_dependant", Decimal, non_negative=True
)
"""Canada workers benefit with no eligible spouse and no eligible dependant, Schedule 6 line 28
"Line 22 minus line 27 (if negative, enter "0")": line 22 with $1,633 on line 21, less line 27
with $26,855 on line 24.

Step 3 (the disability supplement) is separate (`ca/cwb_disability_supplement`)."""

CWB_BEFORE_REDUCTION_WITH_DEPENDANT = CATALOG.declare(
    "cwb_before_reduction_with_dependant", Decimal, non_negative=True
)
"""Canada workers benefit before its reduction with an eligible dependant, Schedule 6 line 22
"Enter whichever is less: amount from line 20 or line 21.": line 20 "Line 18 multiplied by the
percentage from line 19", line 19 "Rate 27%", on line 18 "Line 16 minus line 17 (if negative,
enter "0")", the family working income (line 16) over line 17 "Base amount 3,000.00"; line 21 "If
you had an eligible spouse or an eligible dependant, enter $2,813. If not, enter $1,633.", here
$2,813.

Line 21 is the same for an eligible spouse and for an eligible dependant, so this amount holds for
either status; the status is chosen at line 28 (`ca/canada_workers_benefit_line_28`)."""

CWB_REDUCTION_WITH_DEPENDANT = CATALOG.declare(
    "cwb_reduction_with_dependant", Decimal, non_negative=True
)
"""Canada workers benefit reduction with an eligible dependant, Schedule 6 line 27 "Line 25
multiplied by the percentage from line 26": line 26 "Rate 15%" on line 25 "Line 23 minus line 24
(if negative, enter "0")", line 23 "Adjusted family net income from line 15" over line 24 "If you
had an eligible spouse or an eligible dependant, enter $30,639. If not, enter $26,855.", here
$30,639.

The chart's "You had an eligible spouse or an eligible dependant Basic CWB: $49,393" limit is not
wired: it follows from the arithmetic, as 2,813 less 15% of (49,393 - 30,639) is below zero."""

CANADA_WORKERS_BENEFIT_WITH_DEPENDANT = CATALOG.declare(
    "canada_workers_benefit_with_dependant", Decimal, non_negative=True
)
"""Canada workers benefit with an eligible dependant, Schedule 6 line 28 "Line 22 minus line 27
(if negative, enter "0")": line 22 with $2,813 on line 21, less line 27 with $30,639 on line 24.

Step 3 (the disability supplement) is separate (`ca/cwb_disability_supplement`)."""

CANADA_WORKERS_BENEFIT_LINE_28 = CATALOG.declare(
    "canada_workers_benefit_line_28", Decimal, non_negative=True
)
"""Canada workers benefit before the eligibility conditions, Schedule 6 line 28 "Line 22 minus line
27 (if negative, enter "0") If you are not completing Step 3, enter this amount on line 45300 of
your return.": line 28 for the filer's family status, which lines 21 and 24 read ("If you had an
eligible spouse or an eligible dependant ... If not ..."), chosen by the number of Schedule 6
eligible dependants (line 38100): with none, the line 28 by spouse (`ca/cwb_line_28_by_spouse`),
else the benefit with an eligible dependant. The eligible dependants claimed for on T1 line 30400 do
not choose it, as Schedule 6 defines its eligible dependant by its own conditions."""

CWB_LINE_28_BY_SPOUSE = CATALOG.declare("cwb_line_28_by_spouse", Decimal, non_negative=True)
"""Canada workers benefit before the eligibility conditions for the filer's spouse status alone,
Schedule 6 line 28 "Line 22 minus line 27 (if negative, enter "0")" with the line 21 and line 24
amounts "If you had an eligible spouse or an eligible dependant ... If not ...": with no eligible
spouse (`ca/cwb_eligible_spouses_checked` 0) the benefit with no eligible spouse and no eligible
dependant, else the benefit with an eligible spouse or dependant. The first of two choices, the
eligible dependant choice (`ca/canada_workers_benefit_line_28`) nests over it."""

CANADA_WORKERS_BENEFIT = CATALOG.declare("canada_workers_benefit", Decimal, non_negative=True)
"""Canada workers benefit, T1 line 155 (45300) "Canada workers benefit (CWB) (complete Schedule
6)": line 28 (`ca/canada_workers_benefit_line_28`) when the filer meets Schedule 6's conditions
(`ca/cwb_eligible` is 1), else 0, the benefit that a filer who cannot claim it does not get, as
Schedule 6 says "You cannot claim the CWB for 2025 if any of the following conditions apply to
you"."""

AGED_19_OR_OLDER_AT_END_OF_2025 = CATALOG.declare(
    "aged_19_or_older_at_end_of_2025", int, non_negative=True
)
"""19 years of age or older at the end of 2025, Schedule 6 "Complete this schedule if you met all of
the following conditions in 2025 ... You were, at the end of the year, 19 years of age or older, or
you resided with your spouse or common-law partner or your child": the caller's count, 1 when it
applies and 0 when it does not."""

AGED_19_OR_OLDER_AT_END_OF_2025_CHECKED = CATALOG.declare(
    "aged_19_or_older_at_end_of_2025_checked", int, non_negative=True
)
"""19 years of age or older at the end of 2025, Schedule 6: the answer of
`ca/aged_19_or_older_at_end_of_2025` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025 = CATALOG.declare(
    "resided_with_spouse_or_child_at_end_of_2025", int, non_negative=True
)
"""Resided with a spouse or common-law partner or a child at the end of 2025, Schedule 6 "You were,
at the end of the year, 19 years of age or older, or you resided with your spouse or common-law
partner or your child": the caller's count, 1 when it applies and 0 when it does not. It only
matters to a filer under 19, and an eligible dependant (line 38100) already counts as a child the
filer resided with."""

RESIDED_WITH_SPOUSE_OR_CHILD_AT_END_OF_2025_CHECKED = CATALOG.declare(
    "resided_with_spouse_or_child_at_end_of_2025_checked", int, non_negative=True
)
"""Resided with a spouse or common-law partner or a child at the end of 2025, Schedule 6: the answer
of `ca/resided_with_spouse_or_child_at_end_of_2025` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS = CATALOG.declare(
    "full_time_student_for_more_than_13_weeks", int, non_negative=True
)
"""Enrolled as a full-time student at a designated educational institution for a total of more than
13 weeks in 2025, Schedule 6 "You cannot claim the CWB for 2025 if any of the following conditions
apply to you: You were enrolled as a full-time student at a designated educational institution for
a total of more than 13 weeks in the year, unless you had an eligible dependant at the end of the
year": the caller's count, 1 when it applies and 0 when it does not. The months of full-time
attendance on the tuition worksheets are not this answer: they count the months of a qualifying
institution for the tuition credit, not the weeks of the form's own test."""

FULL_TIME_STUDENT_FOR_MORE_THAN_13_WEEKS_CHECKED = CATALOG.declare(
    "full_time_student_for_more_than_13_weeks_checked", int, non_negative=True
)
"""Enrolled as a full-time student for more than 13 weeks in 2025, Schedule 6: the answer of
`ca/full_time_student_for_more_than_13_weeks` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

CONFINED_TO_PRISON_FOR_90_DAYS = CATALOG.declare(
    "confined_to_prison_for_90_days", int, non_negative=True
)
"""Confined to a prison or similar institution for a period of at least 90 days during 2025,
Schedule 6 "You cannot claim the CWB for 2025 if any of the following conditions apply to you: You
were confined to a prison or similar institution for a period of at least 90 days during the year":
the caller's count, 1 when it applies and 0 when it does not."""

CONFINED_TO_PRISON_FOR_90_DAYS_CHECKED = CATALOG.declare(
    "confined_to_prison_for_90_days_checked", int, non_negative=True
)
"""Confined to a prison for at least 90 days in 2025, Schedule 6: the answer of
`ca/confined_to_prison_for_90_days` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY = CATALOG.declare(
    "exempt_as_foreign_officer_or_family", int, non_negative=True
)
"""Exempt from income tax in Canada as an officer or a servant of another country (such as a
diplomat), a family member who resided with one or an employee of one, at any time in 2025, Schedule
6 "You cannot claim the CWB for 2025 if any of the following conditions apply to you": the caller's
count, 1 when it applies and 0 when it does not."""

EXEMPT_AS_FOREIGN_OFFICER_OR_FAMILY_CHECKED = CATALOG.declare(
    "exempt_as_foreign_officer_or_family_checked", int, non_negative=True
)
"""Exempt from income tax in Canada as an officer or a servant of another country, Schedule 6: the
answer of `ca/exempt_as_foreign_officer_or_family` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

CWB_ELIGIBLE = CATALOG.declare("cwb_eligible", int, non_negative=True)
"""Whether the filer meets Schedule 6's conditions, 1 when they do and 0 when any fails: not a
resident of Canada throughout the year; under 19 at the end of the year without a spouse, common-law
partner or child they resided with; enrolled as a full-time student for more than 13 weeks without
an eligible dependant (line 38100); confined to a prison for at least 90 days; exempt from tax as an
officer or a servant of another country. A filer who does not meet them cannot claim the CWB, so
line 45300 is 0, not an input error."""

ACWB_PAID_TO_YOU = CATALOG.declare("acwb_paid_to_you", Decimal, non_negative=True)
"""Schedule 6 line 44 and line 38120 "Total basic ACWB paid to you (box 10 of your RC210 slip)": the
caller's amount, as entered."""

ACWB_PAID_TO_SPOUSE = CATALOG.declare("acwb_paid_to_spouse", Decimal, non_negative=True)
"""Schedule 6 line 45 and line 38121 "Total basic ACWB paid to your spouse or common-law partner
(box 10 of their RC210 slip)": the caller's amount, as entered; the form has the claimant of the
basic CWB report both slips."""

ACWB_DISABILITY_SUPPLEMENT_PAID = CATALOG.declare(
    "acwb_disability_supplement_paid", Decimal, non_negative=True
)
"""Schedule 6 line 47 and line 38122 "Total ACWB disability supplement paid to you (box 11 of your
RC210 slip)": the caller's amount, as entered."""

CWB_SPOUSE_CLAIMING_BASIC = CATALOG.declare("cwb_spouse_claiming_basic", int, non_negative=True)
"""Schedule 6 Step 4 "If you have an eligible spouse who is claiming the basic CWB for you, but you
are claiming your CWB disability supplement, enter "0" on line 46 and continue on line 47.": the
filer's answer, a starting count, 0 or 1, 1 when the eligible spouse is claiming the basic CWB for
the filer. The form prints no line for it, and an answer of no to line 38102 does not say whether
the spouse claims it or neither of them does."""

CWB_SPOUSE_CLAIMING_BASIC_CHECKED = CATALOG.declare(
    "cwb_spouse_claiming_basic_checked", int, non_negative=True
)
"""Schedule 6 Step 4 "an eligible spouse who is claiming the basic CWB for you": the answer of
`ca/cwb_spouse_claiming_basic` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of
1 or 0. A count of 2 or more is refused, not capped."""

CWB_SPOUSE_CLAIMING_BASIC_WITH_SPOUSE_CHECKED = CATALOG.declare(
    "cwb_spouse_claiming_basic_with_spouse_checked", int, non_negative=True
)
"""The spouse-claiming answer with an eligible spouse, Schedule 6 Step 4: the checked answer
`ca/cwb_spouse_claiming_basic_checked` is at most the checked line 38101 answer
(`ca/cwb_eligible_spouses_checked`), as the rule is about "an eligible spouse who is claiming the
basic CWB for you": a 1 with no eligible spouse is an input error. The answer is read only with
line 38102 answered no and the filer claiming the disability supplement; in other cases line 46 is
line 44 plus line 45."""

ACWB_LINES_44_AND_45 = CATALOG.declare("acwb_lines_44_and_45", Decimal, non_negative=True)
"""Schedule 6 line 44 plus line 45: the basic ACWB paid to the filer and to their spouse or
common-law partner, before the rule of line 46 for an eligible spouse claiming the basic CWB."""

ACWB_LINE_46_APPLIES = CATALOG.declare("acwb_line_46_applies", int, non_negative=True)
"""Schedule 6 line 46: 0 when "If you have an eligible spouse who is claiming the basic CWB for you,
but you are claiming your CWB disability supplement, enter "0" on line 46" applies, else 1
(`ca/acwb_line_46_spouse_rule`)."""

ACWB_BASIC_PAID = CATALOG.declare("acwb_basic_paid", Decimal, non_negative=True)
"""Schedule 6 line 46 "Line 44 plus line 45": the basic ACWB paid to the filer and to their spouse
or common-law partner (`ca/acwb_lines_44_and_45`), or 0 when the filer's eligible spouse is claiming
the basic CWB for them and they are claiming their CWB disability supplement."""

ACWB_PAID = CATALOG.declare("acwb_paid", Decimal, non_negative=True)
"""Schedule 6 line 48 "Line 46 plus line 47": the basic ACWB and the ACWB disability supplement
paid."""

CWB_CLAIMED = CATALOG.declare("cwb_claimed", Decimal, non_negative=True)
"""Schedule 6 line 43 "Enter whichever is more: amount from line 28 or line 42. If you are not
claiming the basic CWB or the CWB disability supplement, enter "0".": the Canada workers benefit of
the return (`ca/canada_workers_benefit`: line 42 when the filer is eligible for the disability tax
credit, else line 28, and line 42 is line 40 plus line 41, the line 28 of Step 2, so it is never
below line 28), when the filer meets Schedule 6's conditions, else 0."""

CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC = CATALOG.declare(
    "cwb_eligible_spouse_eligible_for_dtc", int, non_negative=True
)
"""Schedule 6 Step 1 "Line 38104: Is your eligible spouse eligible for the DTC for themselves? If
yes, your eligible spouse must complete Steps 1 and 3 on a separate Schedule 6. 1 Yes or 2 No": a
starting count, 0 or 1, the count of 0 answering no and of 1 yes. Line 38 reads it ("If you had an
eligible spouse who is also eligible for the DTC, enter 7.5%. If not, enter 15%.")."""

CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC_CHECKED = CATALOG.declare(
    "cwb_eligible_spouse_eligible_for_dtc_checked", int, non_negative=True
)
"""Schedule 6 Step 1 "Line 38104: Is your eligible spouse eligible for the DTC for themselves?": the
answer of `ca/cwb_eligible_spouse_eligible_for_dtc` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

CWB_DTC_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED = CATALOG.declare(
    "cwb_dtc_spouse_for_eligible_spouse_checked", int, non_negative=True
)
"""The line 38104 answer with an eligible spouse, Schedule 6 Step 1: the checked answer
`ca/cwb_eligible_spouse_eligible_for_dtc_checked` is at most the checked line 38101 answer
(`ca/cwb_eligible_spouses_checked`), as line 38104 asks about "your eligible spouse": a 1 with no
eligible spouse is an input error."""

CWB_DISABILITY_SUPPLEMENT_BEFORE_REDUCTION = CATALOG.declare(
    "cwb_disability_supplement_before_reduction", Decimal, non_negative=True
)
"""Canada workers benefit disability supplement before its reduction, Schedule 6 Step 3 line 34
"Enter whichever is less: amount from line 33 or $843.": line 33 "Line 31 multiplied by the
percentage from line 32", line 32 "Rate 27%", on line 31 "Line 29 minus line 30 (if negative, enter
"0")", line 29 "Amount from line 5 in column 1" (`ca/working_income`) over line 30 "Base amount
1,150.00". A working income of $1,150 or less gives 0, as the form requires working income "more
than $1,150"."""

CWB_DISABILITY_REDUCTION_WITHOUT_DEPENDANT = CATALOG.declare(
    "cwb_disability_reduction_without_dependant", Decimal, non_negative=True
)
"""Canada workers benefit disability supplement reduction with no eligible spouse and no eligible
dependant, Schedule 6 Step 3 line 39 "Line 37 multiplied by the percentage from line 38": line 38
"Rate: ... If not, enter 15%.", on line 37 "Line 35 minus line 36 (if negative, enter "0")", line 35
"Adjusted family net income from line 15" over line 36 "If you had an eligible spouse or an eligible
dependant, enter $49,389. If not, enter $37,740.", here $37,740."""

CWB_DISABILITY_REDUCTION_WITH_DEPENDANT = CATALOG.declare(
    "cwb_disability_reduction_with_dependant", Decimal, non_negative=True
)
"""Canada workers benefit disability supplement reduction with an eligible spouse or an eligible
dependant, Schedule 6 Step 3 line 39 "Line 37 multiplied by the percentage from line 38" at 15%
("If not, enter 15%."), line 36 being $49,389 for "an eligible spouse or an eligible dependant".

Line 36 is the same for an eligible spouse and for an eligible dependant, so this amount holds for
either status; the status is chosen at line 39 (`ca/cwb_disability_reduction`)."""

CWB_DISABILITY_REDUCTION_WITH_DTC_SPOUSE = CATALOG.declare(
    "cwb_disability_reduction_with_dtc_spouse", Decimal, non_negative=True
)
"""Canada workers benefit disability supplement reduction with an eligible spouse who is also
eligible for the DTC, Schedule 6 Step 3 line 39 "Line 37 multiplied by the percentage from line
38", line 38 "If you had an eligible spouse who is also eligible for the DTC, enter 7.5%.", line 36
being $49,389 for an eligible spouse."""

CWB_DISABILITY_REDUCTION_BY_SPOUSE = CATALOG.declare(
    "cwb_disability_reduction_by_spouse", Decimal, non_negative=True
)
"""Line 39 for the filer's spouse status alone, Schedule 6 Step 3 line 36 "If you had an eligible
spouse or an eligible dependant ... If not ...": with no eligible spouse
(`ca/cwb_eligible_spouses_checked` 0) the reduction with no eligible spouse and no eligible
dependant, else the reduction with an eligible spouse or dependant."""

CWB_DISABILITY_REDUCTION_BY_STATUS = CATALOG.declare(
    "cwb_disability_reduction_by_status", Decimal, non_negative=True
)
"""Line 39 for the filer's family status at 15%, Schedule 6 Step 3 line 36: the reduction by spouse
when there is no eligible dependant (line 38100), else the reduction with an eligible dependant."""

CWB_DISABILITY_REDUCTION = CATALOG.declare("cwb_disability_reduction", Decimal, non_negative=True)
"""Canada workers benefit disability supplement reduction, Schedule 6 Step 3 line 39 "Line 37
multiplied by the percentage from line 38": the reduction of the filer's family status at 15%
(`ca/cwb_disability_reduction_by_status`), or, when line 38104 says the eligible spouse is also
eligible for the DTC, the reduction at 7.5% (`ca/cwb_disability_reduction_with_dtc_spouse`)."""

CWB_DISABILITY_SUPPLEMENT = CATALOG.declare("cwb_disability_supplement", Decimal, non_negative=True)
"""Canada workers benefit disability supplement, Schedule 6 Step 3 line 40 "Line 34 minus line 39
(if negative, enter "0")"."""

CWB_CLAIMING_BASIC = CATALOG.declare("cwb_claiming_basic", int, non_negative=True)
"""Schedule 6 Step 1 "Line 38102: Are you claiming the basic CWB? If yes, complete parts A and B,
then, if applicable, complete Step 2. 1 Yes or 2 No": a starting count, 0 or 1, the count of 0
answering no and of 1 yes. Step 2 says "If you had an eligible spouse, only one of you can claim the
basic CWB" and the same for an eligible dependant, so the filer who does not claim it answers no.
Line 41 reads it ("If you completed Step 2, enter the amount from line 28. If not, enter "0".")."""

CWB_CLAIMING_BASIC_CHECKED = CATALOG.declare("cwb_claiming_basic_checked", int, non_negative=True)
"""Schedule 6 Step 1 "Line 38102: Are you claiming the basic CWB?": the answer of
`ca/cwb_claiming_basic` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or
0. A count of 2 or more is refused, not capped."""

CANADA_WORKERS_BENEFIT_LINE_41 = CATALOG.declare(
    "canada_workers_benefit_line_41", Decimal, non_negative=True
)
"""Schedule 6 Step 3 line 41 "If you completed Step 2, enter the amount from line 28. If not, enter
"0".": line 28 (`ca/canada_workers_benefit_line_28`) when the filer is claiming the basic CWB (line
38102, `ca/cwb_claiming_basic_checked`), else 0."""

CANADA_WORKERS_BENEFIT_LINE_42 = CATALOG.declare(
    "canada_workers_benefit_line_42", Decimal, non_negative=True
)
"""Canada workers benefit with the disability supplement, Schedule 6 Step 3 line 42 "Line 40 plus
line 41 Enter this amount on line 45300 of your return.": line 40 (`ca/cwb_disability_supplement`)
plus line 41 `ca/canada_workers_benefit_line_41`."""

CANADA_WORKERS_BENEFIT_BEFORE_CONDITIONS = CATALOG.declare(
    "canada_workers_benefit_before_conditions", Decimal, non_negative=True
)
"""Canada workers benefit before the eligibility conditions, the amount for T1 line 45300 (155):
line 42 when Schedule 6 line 38103 "Are you eligible for the disability tax credit (DTC)?" is yes
(`ca/eligible_for_disability_amount_checked`, the CRA's approval of Form T2201, the same fact as
the disability amount of line 31600), else line 28 when Step 2 is completed ("If you are not
completing Step 3, enter this amount on line 45300 of your return."), which is line 41 and is 0 when
line 38102 says the basic CWB is not claimed."""
