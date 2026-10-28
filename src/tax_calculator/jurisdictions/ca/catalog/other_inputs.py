"""The federal catalog: the remaining T1 inputs.

The labour-sponsored fund amount, political contributions, the figures of Form T929 (disability
supports deduction), employment expense deductions, business income lines, residence and spouse
figures.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

RL_10_LABOUR_SPONSORED_FUND_AMOUNT = CATALOG.declare(
    "rl_10_labour_sponsored_fund_amount", Decimal, non_negative=True
)
"""Tax Credit for a Labour-Sponsored Fund (Revenu Québec), the guide's "Line 41800 - Special taxes":
"Report, on line 41800 of your return, the result of the following calculation using your RL-10
slip: Tax Credit for a Labour-Sponsored Fund (Revenu Québec)", the tax for not purchasing
replacement shares in a Quebec labour-sponsored fund. The caller's result, as entered: the guide's
text ends the list at "75% of box"."""

POLITICAL_CONTRIBUTIONS = CATALOG.declare("political_contributions", Decimal, non_negative=True)
"""Total federal political contributions, T1 line 135 and line 41000 "Total federal political
contributions (attach receipts) Line 40900": a starting amount, taken as the T1 takes it. The
Federal Worksheet "Line 41000 - Federal political contribution tax credit" line 1 of each column
"Total federal political contributions from line 40900 of your return" reads it.

The worksheet's eligibility text ("contributions that you or your spouse or common-law partner made
in the year to a registered federal political party, a registered association, or a candidate in a
federal election", less any advantage received) is the caller's to apply."""

T929_EXPENSES_PAID = CATALOG.declare("t929_expenses_paid", Decimal, non_negative=True)
"""Amounts paid for disability supports, Form T929 Step 1 line 1 "Enter the total of all amounts in
column 2": the total of the column 2 "Amount paid" entries, as entered."""

T929_EXPENSES_REIMBURSED = CATALOG.declare("t929_expenses_reimbursed", Decimal, non_negative=True)
"""Amounts reimbursed or assistance received, Form T929 Step 1 line 2 "Enter the total of all
amounts in column 3": the total of the column 3 "Amount reimbursed or assistance received" entries,
as entered; "Amounts you cannot claim" says to subtract them from the amounts paid."""

T929_WEEKS_ATTENDED = CATALOG.declare("t929_weeks_attended", int, non_negative=True)
"""Weeks attended, Form T929 Step 2 line 8 "Enter the number of weeks in the year that you attended
the institution or secondary school": a count of weeks, 0 for a filer who did not attend."""

T929_NET_RESEARCH_GRANTS = CATALOG.declare("t929_net_research_grants", Decimal, non_negative=True)
"""Net research grants, Form T929 Step 2 line 4 "Enter your earned income" and its definition of
earned income, "net research grants": the amount, as entered."""

T929_EARNINGS_SUPPLEMENTS = CATALOG.declare("t929_earnings_supplements", Decimal, non_negative=True)
"""Earnings supplements, Form T929 Step 2 line 4 "Enter your earned income" and its definition of
earned income, "any earnings supplement received under a project sponsored by a government in
Canada to encourage employment": the amount, as entered."""

T929_EMPLOYMENT_INSURANCE_PART_2_SUPPORT = CATALOG.declare(
    "t929_employment_insurance_part_2_support", Decimal, non_negative=True
)
"""Financial support under Part II of the Employment Insurance Act, Form T929 Step 2 line 4 "Enter
your earned income" and its definition of earned income, "any financial support received under a
program sponsored under Part II of the Employment Insurance Act, or any similar program": the
amount, as entered."""

T929_INCOME_REPLACEMENT_SUPPORT = CATALOG.declare(
    "t929_income_replacement_support", Decimal, non_negative=True
)
"""Income replacement support, Form T929 Step 2 line 4 "Enter your earned income" and its definition
of earned income, "any financial support received under a program that provides income replacement
benefits similar to those provided under the Employment Insurance Act": the amount, as entered."""

T929_WAGE_EARNER_PROTECTION_AMOUNTS = CATALOG.declare(
    "t929_wage_earner_protection_amounts", Decimal, non_negative=True
)
"""Wage Earner Protection Program amounts, Form T929 Step 2 line 4 "Enter your earned income" and
its definition of earned income, "any amounts received under the Wage Earner Protection Program Act
in respect of wages": the amount, as entered."""

T929_COVID_19_PAYMENTS = CATALOG.declare("t929_covid_19_payments", Decimal, non_negative=True)
"""COVID-19 payments, Form T929 Step 2 line 4 "Enter your earned income" and its definition of
earned income, "any federal, provincial or territorial government COVID-19 payments received in the
year for which you have received a T4A or T4E": the amount, as entered."""

OTHER_EMPLOYMENT_EXPENSES = CATALOG.declare("other_employment_expenses", Decimal, non_negative=True)
"""Other employment expenses, T1 line 50 and line 22900 "Other employment expenses (see Guide
T4044)": computed, not entered; the total of Form T777 line 17 "Total expenses"
(`t777_line_17`) and the total of Form RC359 line 7 "Excess EPSP amount" over the copies
(`rc359_excess_epsp_total`). It is deducted in the line 23300 sum and read by the Federal Worksheet
"Line 45200 - Refundable medical expense supplement" ("minus the amounts from lines 20700, 21200,
22900, and 23100 of your return") and by Form T691 Part 1 line 77."""

WAGE_LOSS_REPLACEMENT_PLAN_INCOME = CATALOG.declare(
    "wage_loss_replacement_plan_income", Decimal, non_negative=True
)
"""Wage-loss replacement plan income, Federal Worksheet "Line 45200 - Refundable medical expense
supplement" "your employment income from lines 10100 and 10400 of your return (other than amounts
received from a wage-loss replacement plan)": the amounts received from such a plan that lines 10100
and 10400 include, the caller's, as entered."""

RESIDENT_IN_CANADA_THROUGHOUT_2025 = CATALOG.declare(
    "resident_in_canada_throughout_2025", int, non_negative=True
)
"""Resident in Canada throughout 2025, Federal Worksheet "Line 45200 - Refundable medical expense
supplement" "You were resident in Canada throughout 2025": the caller's count, 1 when it applies and
0 when it does not."""

RESIDENT_IN_CANADA_THROUGHOUT_2025_CHECKED = CATALOG.declare(
    "resident_in_canada_throughout_2025_checked", int, non_negative=True
)
"""Resident in Canada throughout 2025, Federal Worksheet "Line 45200 - Refundable medical expense
supplement": the answer of `ca/resident_in_canada_throughout_2025` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

AGED_18_OR_OLDER_AT_END_OF_2025 = CATALOG.declare(
    "aged_18_or_older_at_end_of_2025", int, non_negative=True
)
"""18 years of age or older at the end of 2025, Federal Worksheet "Line 45200 - Refundable medical
expense supplement" "You were 18 years of age or older at the end of 2025": the caller's count, 1
when it applies and 0 when it does not."""

AGED_18_OR_OLDER_AT_END_OF_2025_CHECKED = CATALOG.declare(
    "aged_18_or_older_at_end_of_2025_checked", int, non_negative=True
)
"""18 years of age or older at the end of 2025, Federal Worksheet "Line 45200 - Refundable medical
expense supplement": the answer of `ca/aged_18_or_older_at_end_of_2025` after the check that it is 0
or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS = CATALOG.declare(
    "spouse_net_income_before_adjustments", Decimal
)
"""Spouse's net income amount, Federal Worksheet "Line 45200 - Refundable medical expense
supplement" line 1, column 2 "Net income amount from line 23600 of the return (or the amount you
would have entered if the instructions on line 23600 said "if negative, show in brackets")": the
caller's amount for the spouse or common-law partner, signed as the worksheet allows brackets. 0
when there is no spouse or common-law partner, and when "you were separated because of a breakdown
in your relationship for a period of 90 days or more that included December 31, 2025" or "your
spouse or common-law partner died on or before December 31, 2025", as the worksheet says "do not
include their income"."""

SPOUSE_UCCB_REPAYMENT = CATALOG.declare("spouse_uccb_repayment", Decimal, non_negative=True)
"""Spouse's UCCB repayment, Federal Worksheet "Line 45200 - Refundable medical expense supplement"
line 2, column 2 "Total of the universal child care benefit (UCCB) repayment (line 21300 of the
return)": the caller's amount for the spouse or common-law partner, 0 where their income is not
included."""

SPOUSE_RDSP_INCOME_REPAYMENT = CATALOG.declare(
    "spouse_rdsp_income_repayment", Decimal, non_negative=True
)
"""Spouse's RDSP income repayment, Federal Worksheet "Line 45200 - Refundable medical expense
supplement" line 2, column 2 "the registered disability savings plan (RDSP) income repayment
(included in the amount on line 23200 of the return)": the caller's amount for the spouse or
common-law partner, 0 where their income is not included."""

SPOUSE_UNIVERSAL_CHILD_CARE_BENEFIT = CATALOG.declare(
    "spouse_universal_child_care_benefit", Decimal, non_negative=True
)
"""Spouse's UCCB income, Federal Worksheet "Line 45200 - Refundable medical expense supplement" line
4, column 2 "Total of the UCCB income (line 11700 of the return)": the caller's amount for the
spouse or common-law partner, 0 where their income is not included."""

SPOUSE_RDSP_INCOME = CATALOG.declare("spouse_rdsp_income", Decimal, non_negative=True)
"""Spouse's RDSP income, Federal Worksheet "Line 45200 - Refundable medical expense supplement" line
4, column 2 "the RDSP income (line 12500 of the return)": the caller's amount for the spouse or
common-law partner, 0 where their income is not included."""

SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31 = CATALOG.declare(
    "spouse_or_common_law_partner_on_december_31", int, non_negative=True
)
"""Spouse or common-law partner on December 31, 2025, T1 "Marital status on December 31, 2025" Box 1
Married, Box 2 Living common-law: the caller's count, 1 for box 1 or box 2 and 0 for any other. It
is also Schedule ON428-A's "spouse or common-law partner at the end of the year" (Part A or Part B),
so it is entered once, in the form `ca/spouse_on_december_31`. A spouse or common-law partner who
died in the year is entered as 0 ("complete Part A as if you were single")."""

SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_CHECKED = CATALOG.declare(
    "spouse_or_common_law_partner_on_december_31_checked", int, non_negative=True
)
"""Spouse or common-law partner on December 31, 2025, T1 "Marital status on December 31, 2025" Box 1
Married, Box 2 Living common-law: the answer of `ca/spouse_or_common_law_partner_on_december_31`
after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more
is refused, not capped. It is the export of the form `ca/spouse_on_december_31` and is read only
there."""

SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL = CATALOG.declare(
    "spouse_or_common_law_partner_on_december_31_total", int, non_negative=True
)
"""Spouse or common-law partner on December 31, 2025, T1 "Marital status on December 31, 2025" Box 1
Married, Box 2 Living common-law: the export of the form `ca/spouse_on_december_31` (its one record
of `ca/spouse_or_common_law_partner_on_december_31_checked`) read as a count, 1 or 0, by
`core/first_record_count`. ON428 (before lines 75 and 76) and Schedule ON428-A (Part A or Part B)
read it."""

SPECIFIED_FOREIGN_PROPERTY_OVER_100K = CATALOG.declare(
    "specified_foreign_property_over_100k", int, non_negative=True
)
"""Specified foreign property over CAN$100,000, T1 line 26600 "Did you own or hold specified foreign
property where the total cost amount of all such property, at any time in 2025, was more than
CAN$100,000? 1 Yes or 2 No": a 0 for No or 1 for Yes count, carried as entered, which no step
reads."""
