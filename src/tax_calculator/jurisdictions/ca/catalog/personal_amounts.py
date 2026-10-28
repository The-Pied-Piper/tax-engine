"""The federal catalog: personal amounts.

The basic personal, age, spouse, eligible dependant, caregiver, medical and disability amounts, the
principal residence gain lines, the fields of the capital cost allowance table and the infirm
children amount.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

FEDERAL_BASIC_TAX = CATALOG.declare("federal_basic_tax", Decimal, non_negative=True)
"""Federal tax on taxable income from the bracket schedule, before non-refundable credits.

Its T1 line reference is still to be confirmed: design.md §2 marks federal line semantics
UNVERIFIED.
"""

BASIC_PERSONAL_AMOUNT = CATALOG.declare("basic_personal_amount", Decimal, non_negative=True)
"""Basic personal amount, T1 line 30000 "If the amount on line 23600 is $177,882 or less, enter
$16,129. If the amount on line 23600 is $253,414 or more, enter $14,538. Otherwise, use the
Federal Worksheet to calculate the amount to enter. (maximum $16,129)": the first part of the
total of the credit amounts.

It is computed from net income (line 23600) by the Federal Worksheet (form 5000-D1), line 30000:
line 11 "Line 1 plus line 10 Enter this amount on line 30000 of your return. (maximum $16,129)",
the base amount of line 1 plus the supplement amount of line 2 less its reduction for net income
over the income threshold of line 4 (line 10 "Line 2 minus line 9 (if negative, enter "0")").
"""

BORN_IN_1960_OR_EARLIER = CATALOG.declare("born_in_1960_or_earlier", int, non_negative=True)
"""Born in 1960 or earlier, T1 line 78 (line 30100) "Age amount (if you were born in 1960 or
earlier) (use Federal Worksheet) (maximum $9,028)": a starting count, 0 or 1, from the date of birth
the return asks for.

The age amount is claimed only if the filer was born in 1960 or earlier; a count is only declared
non-negative, so that condition is the return's to keep. It multiplies the age amount, as the form
takes it.
"""

BORN_IN_1960_OR_EARLIER_CHECKED = CATALOG.declare(
    "born_in_1960_or_earlier_checked", int, non_negative=True
)
"""Born in 1960 or earlier, T1 line 78 (line 30100) "Age amount (if you were born in 1960 or
earlier)": the answer of `ca/born_in_1960_or_earlier` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

AGE_MAXIMUM = CATALOG.declare("age_maximum", Decimal, non_negative=True)
"""Maximum age amount, Federal Worksheet (form 5000-D1), "Line 30100 - Age amount", line 1 "Maximum
amount 9,028.00": the dataset as an artifact."""

AGE_INCOME_THRESHOLD = CATALOG.declare("age_income_threshold", Decimal, non_negative=True)
"""Income threshold of the age amount, Federal Worksheet (form 5000-D1), "Line 30100 - Age amount",
line 3 "Income threshold 45,522.00": the dataset as an artifact."""

AGE_INCOME_OVER_THRESHOLD = CATALOG.declare("age_income_over_threshold", Decimal, non_negative=True)
"""Net income over the income threshold, Federal Worksheet (form 5000-D1), "Line 30100 - Age
amount", line 4 "Line 2 minus line 3 (if negative, enter "0")": line 2 "Amount from line 23600 of
your return" less the income threshold of line 3, not below zero."""

AGE_REDUCTION = CATALOG.declare("age_reduction", Decimal, non_negative=True)
"""Reduction of the age amount, Federal Worksheet (form 5000-D1), "Line 30100 - Age amount", line 6
"Line 4 multiplied by the percentage from line 5": line 4 at the applicable rate of line 5 "15%"."""

AGE_AMOUNT_BEFORE_COUNT = CATALOG.declare("age_amount_before_count", Decimal, non_negative=True)
"""Age amount before it is claimed, Federal Worksheet (form 5000-D1), "Line 30100 - Age amount",
line 7 "Line 1 minus line 6 (if negative, enter "0") Enter this amount on line 30100 of your
return.": the maximum amount less the reduction, not below zero."""

AGE_AMOUNT = CATALOG.declare("age_amount", Decimal, non_negative=True)
"""Age amount, T1 line 78 (line 30100) "Age amount (if you were born in 1960 or earlier) (use
Federal Worksheet) (maximum $9,028)": the worksheet's line 7 once if the filer was born in 1960 or
earlier, else 0; a part of the total of the credit amounts."""

SPOUSE_NET_INCOME = CATALOG.declare("spouse_net_income", Decimal, non_negative=True)
"""Spouse's net income, Schedule 5 line 4 "Your spouse's or common-law partner's net income from
line 23600 of their return (Note 1)": a starting amount, also line 2 "Net income for this person
from line 23600 of their return" of the Canada caregiver calculation for line 30425, and ON428
line 12 "Your spouse's or common-law partner's net income from line 23600 of their return".
"""

SPOUSES_CLAIMED = CATALOG.declare("spouses_claimed", int, non_negative=True)
"""Number of spouse or common-law partner amounts claimed, T1 line 79 (line 30300) "Spouse or
common-law partner amount (complete Schedule 5)": a starting count, 0 or 1.

Schedule 5 states "Claim this amount if, at any time in the year, you supported your spouse or
common-law partner" and "Only one spouse or common-law partner can claim the amount on line 30300
for each other for the same year"; a count is only declared non-negative, so that rule is the
return's to keep. The claim is the filer's statement; without it a return with no spouse would claim
the whole basic personal amount.
"""

SPOUSES_CLAIMED_CHECKED = CATALOG.declare("spouses_claimed_checked", int, non_negative=True)
"""Spouse or common-law partner amount claimed, T1 line 79 (line 30300) "Spouse or common-law
partner amount (complete Schedule 5)": the answer of `ca/spouses_claimed` after the check that it is
0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

SPOUSE_CAREGIVER_ELIGIBLE = CATALOG.declare("spouse_caregiver_eligible", int, non_negative=True)
"""Eligible for the Canada caregiver amount for the spouse, Schedule 5 line 2 and line 51090 "If you
are eligible for the Canada caregiver amount for your spouse or common-law partner, enter $2,687
(see line 30425 on page 4)": a starting count, 0 or 1.

Eligibility is the filer's statement, as the schedule takes it, and is not computed here. It adds
the $2,687 at line 2 of line 30300 and triggers line 30425, which the schedule asks for only if
"you entered $2,687 on line 51090 or line 51100".
"""

SPOUSE_CAREGIVER_ELIGIBLE_CHECKED = CATALOG.declare(
    "spouse_caregiver_eligible_checked", int, non_negative=True
)
"""Eligible for the Canada caregiver amount for the spouse, Schedule 5 line 51090: the answer of
`ca/spouse_caregiver_eligible` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of
1 or 0. A count of 2 or more is refused, not capped."""

SPOUSE_INFIRMITY_SUPPLEMENT = CATALOG.declare(
    "spouse_infirmity_supplement", Decimal, non_negative=True
)
"""Supplement for a spouse with an infirmity, Schedule 5, "Line 30300 - Spouse or common-law partner
amount", line 2 and line 51090 "If you are eligible for the Canada caregiver amount for your spouse
or common-law partner, enter $2,687": the dataset once if eligible, else 0."""

SPOUSE_AMOUNT_BASIS = CATALOG.declare("spouse_amount_basis", Decimal, non_negative=True)
"""Basis of the spouse or common-law partner amount, Schedule 5, "Line 30300 - Spouse or common-law
partner amount", line 3 "Line 1 plus line 2": line 1 "Basic personal amount from line 30000 of your
return" plus the supplement of line 2."""

SPOUSE_AMOUNT_BEFORE_COUNT = CATALOG.declare(
    "spouse_amount_before_count", Decimal, non_negative=True
)
"""Spouse or common-law partner amount before it is claimed, Schedule 5, "Line 30300 - Spouse or
common-law partner amount", line 5 "Line 3 minus line 4 (if negative, enter "0") Enter this amount
on line 30300 of your return.": line 3 less line 4, the spouse's net income, not below zero."""

SPOUSE_AMOUNT = CATALOG.declare("spouse_amount", Decimal, non_negative=True)
"""Spouse or common-law partner amount, T1 line 79 (line 30300) "Spouse or common-law partner amount
(complete Schedule 5)": Schedule 5 line 5 once if the filer claims it, else 0; a part of the total
of the credit amounts."""

ELIGIBLE_DEPENDANTS = CATALOG.declare("eligible_dependants", int, non_negative=True)
"""Number of eligible dependants claimed for, T1 line 80 (line 30400) "Amount for an eligible
dependant (complete Schedule 5)": a starting count, 0 or 1.

Schedule 5 states "Each household is allowed only one claim for this amount"; a count above 1 is
refused by `ca/eligible_dependants_checked` (`ca/yes_or_no_count`), not read as a second claim. The
conditions are the return's to keep: "You did not have a spouse or common-law partner or, if you
did, you were not living with them, supporting them, or being supported by them"; "You supported the
dependant in 2025"; "You lived with the dependant (in most cases in Canada) in a home ... you
maintained"; the dependant is "your child, grandchild, brother or sister under 18 years of age" (or
"your parent or grandparent", or "your child, grandchild, brother or sister 18 years of age or older
with a mental or physical infirmity"); and "You had to pay child support in 2025 for the eligible
dependant" bars the claim, with exceptions.
Eligibility is not computed here.
"""

ELIGIBLE_DEPENDANTS_CHECKED = CATALOG.declare("eligible_dependants_checked", int, non_negative=True)
"""Number of eligible dependants claimed for, T1 line 80 (line 30400) "Amount for an eligible
dependant (complete Schedule 5)": the answer of `ca/eligible_dependants` after the check that it is
0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

SPOUSE_AND_DEPENDANT_BOTH = CATALOG.declare("spouse_and_dependant_both", int, non_negative=True)
"""Spouse or common-law partner amount and eligible dependant amount both claimed, Schedule 5 line
30400 "If you did not claim an amount on line 30300 of your return, you may be able to claim the
amount for one eligible dependant": 1 when `ca/spouses_claimed` and `ca/eligible_dependants_checked`
are each more than 0, else 0, a starting count. The schedule allows the dependant amount only when
no amount is claimed on line 30300, so this count of 1 is refused (see
`ca/spouse_and_dependant_both_checked`)."""

SPOUSE_AND_DEPENDANT_BOTH_CHECKED = CATALOG.declare(
    "spouse_and_dependant_both_checked", int, non_negative=True
)
"""Spouse or common-law partner amount and eligible dependant amount both claimed, checked: the
count of `ca/spouse_and_dependant_both` when it is 0, the only value produced. A count of 1 is an
input error, not capped, so the two amounts are never credited together."""

SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT = CATALOG.declare(
    "spouse_caregiver_without_spouse_amount", int, non_negative=True
)
"""Canada caregiver amount for the spouse claimed without the spouse amount, Schedule 5 line 30425
"You may be able to claim this amount if you can claim an amount for your spouse or common-law
partner on line 30300 of your return": 1 when `ca/spouse_caregiver_eligible` is more than 0 and
`ca/spouses_claimed` is 0, else 0, a starting count. The amount is an add-on to line 30300, so this
count of 1 is refused (see `ca/spouse_caregiver_without_spouse_amount_checked`)."""

SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT_CHECKED = CATALOG.declare(
    "spouse_caregiver_without_spouse_amount_checked", int, non_negative=True
)
"""Canada caregiver amount for the spouse claimed without the spouse amount, checked: the count of
`ca/spouse_caregiver_without_spouse_amount` when it is 0, the only value produced. A count of 1 is
an input error, not capped, so the caregiver amount is never claimed without its spouse amount."""

DEPENDANT_NET_INCOME = CATALOG.declare("dependant_net_income", Decimal, non_negative=True)
"""Dependant's net income, Schedule 5 line 4 (line 51106) "Dependant's net income from line 23600
of their return": a starting amount, also ON428 line 15 "Your eligible dependant's net income from
line 23600 of their return"."""

DEPENDANT_CAREGIVER_ELIGIBLE = CATALOG.declare(
    "dependant_caregiver_eligible", int, non_negative=True
)
"""Eligible for the Canada caregiver amount for the eligible dependant, Schedule 5 line 2 and line
51100 "If you are eligible for the Canada caregiver amount for your dependant (other than your
infirm child under 18 years of age), enter $2,687 (Note 2) (see line 30425 below)": a starting
count, 0 or 1.

Eligibility is the filer's statement, as the schedule takes it ("Does this dependant have a mental
or physical infirmity? Yes or No"), and is not computed here. It adds the $2,687 at line 2 of line
30400 and triggers line 30425, which the schedule asks for only for a dependant 18 years of age or
older. The age condition on line 30425 is not this count's: it is the second count,
`dependant_caregiver_aged_18_or_older`, applied after this one.
"""

DEPENDANT_CAREGIVER_ELIGIBLE_CHECKED = CATALOG.declare(
    "dependant_caregiver_eligible_checked", int, non_negative=True
)
"""Eligible for the Canada caregiver amount for the eligible dependant, Schedule 5 line 51100: the
answer of `ca/dependant_caregiver_eligible` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT = CATALOG.declare(
    "dependant_caregiver_without_dependant_amount", int, non_negative=True
)
"""Canada caregiver amount for the eligible dependant claimed without the eligible dependant amount,
Schedule 5 line 30425 "You may be able to claim this amount if you can claim an amount ... for an
eligible dependant 18 years of age or older on line 30400 of your return": 1 when
`ca/dependant_caregiver_eligible` is more than 0 and `ca/eligible_dependants_checked` is 0, else 0,
a starting count. The amount is an add-on to line 30400, so this count of 1 is refused (see
`ca/dependant_caregiver_without_dependant_amount_checked`)."""

DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT_CHECKED = CATALOG.declare(
    "dependant_caregiver_without_dependant_amount_checked", int, non_negative=True
)
"""Canada caregiver amount for the eligible dependant claimed without the eligible dependant amount,
checked: the count of `ca/dependant_caregiver_without_dependant_amount` when it is 0, the only value
produced. A count of 1 is an input error, not capped, so the caregiver amount is never claimed
without its dependant amount."""

DEPENDANT_CAREGIVER_AGED_18_OR_OLDER = CATALOG.declare(
    "dependant_caregiver_aged_18_or_older", int, non_negative=True
)
"""Eligible dependant 18 years of age or older, Schedule 5 "Line 30425 - Canada caregiver amount for
spouse or common-law partner, or eligible dependant age 18 or older": a starting count, 0 or 1.

Line 30425 is asked only for a dependant 18 years of age or older. The age is the filer's statement,
as the schedule takes it, and is not computed here. It is the count on line 30425 alone: the
dependant's amount on line 30400 (line 2 and line 51100) does not depend on it."""

DEPENDANT_CAREGIVER_AGED_18_OR_OLDER_CHECKED = CATALOG.declare(
    "dependant_caregiver_aged_18_or_older_checked", int, non_negative=True
)
"""Eligible dependant 18 years of age or older, Schedule 5 "Line 30425": the answer of
`ca/dependant_caregiver_aged_18_or_older` after the check that it is 0 or 1 (`ca/yes_or_no_count`),
a count of 1 or 0. A count of 2 or more is refused, not capped."""

DEPENDANT_INFIRMITY_SUPPLEMENT = CATALOG.declare(
    "dependant_infirmity_supplement", Decimal, non_negative=True
)
"""Supplement for an eligible dependant with an infirmity, Schedule 5, "Line 30400 - Amount for an
eligible dependant", line 2 and line 51100 "If you are eligible for the Canada caregiver amount for
your dependant (other than your infirm child under 18 years of age), enter $2,687": the dataset
once if eligible, else 0."""

ELIGIBLE_DEPENDANT_AMOUNT_BASIS = CATALOG.declare(
    "eligible_dependant_amount_basis", Decimal, non_negative=True
)
"""Basis of the amount for an eligible dependant, Schedule 5, "Line 30400 - Amount for an eligible
dependant", line 3 "Line 1 plus line 2": line 1 "Basic personal amount from line 30000 of your
return" plus the supplement of line 2."""

ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT = CATALOG.declare(
    "eligible_dependant_amount_before_count", Decimal, non_negative=True
)
"""Amount for an eligible dependant before it is claimed, Schedule 5 line 5 "Line 3 minus line 4
(if negative, enter "0") Enter this amount on line 30400 of your return.": line 3 (the basis, the
basic personal amount plus the infirmity supplement) less the dependant's net income (line 4), not
below zero."""

ELIGIBLE_DEPENDANT_AMOUNT = CATALOG.declare("eligible_dependant_amount", Decimal, non_negative=True)
"""Amount for an eligible dependant, T1 line 80 (line 30400) "Amount for an eligible dependant
(complete Schedule 5)": Schedule 5 line 5 for each eligible dependant claimed for, a part of the
total of the credit amounts."""

SPOUSE_CAREGIVER_BASE = CATALOG.declare("spouse_caregiver_base", Decimal, non_negative=True)
"""Base amount for the Canada caregiver amount for a spouse, Schedule 5, "Line 30425 - Canada
caregiver amount for spouse or common-law partner, or eligible dependant age 18 or older", line 1
"Base amount 28,798.00": the dataset as an artifact."""

SPOUSE_CAREGIVER_BEFORE_MAXIMUM = CATALOG.declare(
    "spouse_caregiver_before_maximum", Decimal, non_negative=True
)
"""Canada caregiver amount for a spouse before its maximum, Schedule 5 (form 5000-S5), "Line 30425",
line 3 "Line 1 minus line 2 (if negative, enter "0") (maximum $8,601)": line 1 "Base amount
28,798.00" less line 2 "Net income for this person from line 23600 of their return", not below
zero, before the "(maximum $8,601)" is applied."""

SPOUSE_CAREGIVER_LIMIT = CATALOG.declare("spouse_caregiver_limit", Decimal, non_negative=True)
"""Canada caregiver amount for a spouse at most its maximum, Schedule 5 (form 5000-S5), "Line
30425", line 3 "Line 1 minus line 2 (if negative, enter "0") (maximum $8,601)": the amount before
its maximum, at most $8,601.

It is not named `..._before_count`, as the eligible dependant's capped amount is, because that name
is the line 5 result's (`spouse_caregiver_amount_before_count`), which line 4 comes off first.
"""

SPOUSE_CAREGIVER_AMOUNT_BEFORE_COUNT = CATALOG.declare(
    "spouse_caregiver_amount_before_count", Decimal, non_negative=True
)
"""Canada caregiver amount for a spouse before it is claimed, Schedule 5, "Line 30425", line 5 "Line
3 minus line 4 (if negative, enter "0") Enter this amount on line 30425 of your return. Allowable
amount for this person": line 3 less line 4 "Amount claimed on line 30300 or line 30400 of your
return, if applicable", here the spouse amount, not below zero.

The condition "a person whose net income is between $8,624 and $28,798" needs no gate: below $8,624
line 4 is already more than $8,601, so line 5 is 0.
"""

SPOUSE_CAREGIVER_AMOUNT = CATALOG.declare("spouse_caregiver_amount", Decimal, non_negative=True)
"""Canada caregiver amount for a spouse, Schedule 5 line 5 "Line 30425" once if the spouse is
eligible for it (line 51090), else 0; a part of T1 line 81 (line 30425) "Canada caregiver amount
for spouse or common-law partner, or eligible dependant age 18 or older (complete Schedule 5)",
with the dependant's amount."""

DEPENDANT_CAREGIVER_BEFORE_MAXIMUM = CATALOG.declare(
    "dependant_caregiver_before_maximum", Decimal, non_negative=True
)
"""Canada caregiver amount for an eligible dependant 18 or older before its maximum, Schedule 5
"Line 30425", line 3 "Line 1 minus line 2 (if negative, enter "0") (maximum $8,601)": line 1 "Base
amount 28,798.00" (the spouse's base) less line 2 "Net income for this person from line 23600 of
their return" (the dependant's net income), not below zero, before the "(maximum $8,601)" is
applied."""

DEPENDANT_CAREGIVER_LIMIT = CATALOG.declare("dependant_caregiver_limit", Decimal, non_negative=True)
"""Canada caregiver amount for an eligible dependant 18 or older at most its maximum, Schedule 5
(form 5000-S5), "Line 30425", line 3 "Line 1 minus line 2 (if negative, enter "0") (maximum
$8,601)": the amount before its maximum, at most $8,601.
"""

DEPENDANT_CAREGIVER_AMOUNT_BEFORE_COUNT = CATALOG.declare(
    "dependant_caregiver_amount_before_count", Decimal, non_negative=True
)
"""Canada caregiver amount for an eligible dependant 18 or older before it is claimed, Schedule 5,
"Line 30425", line 5 "Line 3 minus line 4 (if negative, enter "0") Enter this amount on line 30425
of your return. Allowable amount for this person": line 3 less line 4 "Amount claimed on line 30300
or line 30400 of your return, if applicable", here the amount for this dependant on line 30400, not
below zero."""

DEPENDANT_CAREGIVER_AMOUNT_BEFORE_AGE_COUNT = CATALOG.declare(
    "dependant_caregiver_amount_before_age_count", Decimal, non_negative=True
)
"""Canada caregiver amount for an eligible dependant before the age count, Schedule 5, "Line
30425", line 5 "Line 3 minus line 4 (if negative, enter "0") Enter this amount on line 30425 of your
return. Allowable amount for this person": line 5 of the amount before the count, times the infirm
dependant count `dependant_caregiver_eligible`, so it is the amount once if the dependant is infirm,
else 0.

The age condition is not applied here, so an infirm dependant under 18 who is not the filer's child
keeps the amount on line 30400 and gets 0 on line 30425."""

DEPENDANT_CAREGIVER_AMOUNT = CATALOG.declare(
    "dependant_caregiver_amount", Decimal, non_negative=True
)
"""Canada caregiver amount for an eligible dependant 18 or older, Schedule 5 line 5 "Line 30425"
once if the dependant is infirm (`dependant_caregiver_eligible`, line 2 of line 30400) and the filer
states 18 or older (`dependant_caregiver_aged_18_or_older`), else 0; a part of T1 line 81 (line
30425), with the spouse's amount."""

CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT = CATALOG.declare(
    "caregiver_amount_for_spouse_or_dependant", Decimal, non_negative=True
)
"""Canada caregiver amount for spouse or common-law partner, or eligible dependant age 18 or older,
T1 line 81 (line 30425) "Canada caregiver amount for spouse or common-law partner, or eligible
dependant age 18 or older (complete Schedule 5)": the spouse's Schedule 5 line 5 and the
dependant's, added; a part of the total of the credit amounts. Only one claim can be made for this
amount, which the schedule leaves to the return: the two counts are not checked against each
other."""

INFIRM_DEPENDANTS = RecordListKind.declare(
    CATALOG, "infirm_dependants", fields=(DEPENDANT_NET_INCOME,)
)
"""Infirm dependants, Schedule 5 "Line 30450 - Canada caregiver amount for other infirm dependants
age 18 or older" "Complete the chart below for each dependant who meets the conditions above": a
starting list with one record for each such dependant, holding line 2 "Infirm dependant's net
income from line 23600 of their return". The caller lists only the dependants who meet the
conditions."""

CAREGIVER_AMOUNT = CATALOG.declare("caregiver_amount", Decimal, non_negative=True)
"""Canada caregiver amount for other infirm dependants, T1 line 82 (line 30450) "Canada caregiver
amount for other infirm dependants age 18 or older (complete Schedule 5)": "the total of allowable
amounts claimed for all dependants", each line 3 "Line 1 minus line 2 (if negative, enter "0")
(maximum $8,601)", a part of the total of the credit amounts."""

OTHER_DEPENDANT_MEDICAL_EXPENSES = CATALOG.declare(
    "other_dependant_medical_expenses", Decimal, non_negative=True
)
"""Medical expenses for an other dependant, Federal Worksheet for line 33199, line 1 "Medical
expenses for other dependant": a field of each record of the other dependants, not an artifact of
its own."""

OTHER_DEPENDANTS = RecordListKind.declare(
    CATALOG,
    "other_dependants",
    fields=(OTHER_DEPENDANT_MEDICAL_EXPENSES, DEPENDANT_NET_INCOME),
)
"""Other dependants, Federal Worksheet for line 33199 "Complete one column for each dependant": a
starting list with one record for each dependant whose medical expenses are claimed, holding line 1
"Medical expenses for other dependant" and the dependant's net income from line 23600 of their
return, from which line 2 "amount from line 109 of the dependant's return" is worked out. A list
of its own: the infirm dependants of line 30450 are a different set of people."""

OTHER_DEPENDANTS_MEDICAL = CATALOG.declare("other_dependants_medical", Decimal, non_negative=True)
"""Allowable amount of medical expenses for other dependants, T1 line 111 (line 33199) "Allowable
amount of medical expenses for other dependants (use Federal Worksheet)": line 4 "Add the amounts
from line 3 of columns 1, 2, and 3 (and others, if any)", each line 3 being "Line 1 minus line 2
(if negative, enter "0")"."""

MEDICAL_EXPENSES = CATALOG.declare("medical_expenses", Decimal, non_negative=True)
"""Medical expenses, T1 line 107 and line 33099 "Medical expenses for self, spouse or common-law
partner and your dependent children under 18 years of age": a starting amount."""

MEDICAL_NET_INCOME_SHARE = CATALOG.declare("medical_net_income_share", Decimal, non_negative=True)
"""Share of the net income for medical expenses, T1 line 108 "Amount from line 23600" "multiplied by
3%": 3% of the net income."""

MEDICAL_THRESHOLD = CATALOG.declare("medical_threshold", Decimal, non_negative=True)
"""Threshold for medical expenses, T1 line 109 "Enter whichever is less: $2,834 or the amount from
line 108.": the lesser of the ceiling and the share of the net income."""

MEDICAL_EXPENSES_OVER_THRESHOLD = CATALOG.declare(
    "medical_expenses_over_threshold", Decimal, non_negative=True
)
"""Medical expenses over the threshold, T1 line 110 "Line 107 minus line 109 (if negative, enter
"0")": the filer's own group, not below zero."""

MEDICAL_CLAIM = CATALOG.declare("medical_claim", Decimal, non_negative=True)
"""Allowable medical expenses, T1 line 112 and line 33200 "Line 110 plus line 111": the filer's own
group plus the allowable amount for other dependants, a part of the total of the credit amounts
(line 33500)."""

DEPENDANT_UNDER_18 = CATALOG.declare("dependant_under_18", int, non_negative=True)
"""Dependant under 18, Federal Worksheet "Line 31800 - Disability amount transferred from a
dependant" "If the dependant was under 18 years of age on December 31, 2025, complete lines 2 to
13. If the dependant was 18 years of age or older, complete lines 7 to 13.": 1 if the dependant was
under 18 on December 31, 2025, else 0, taken as a count like the forms' other yes or no questions;
a starting count, a field of each record of the dependants with a disability."""

DEPENDANT_CARE_EXPENSES = CATALOG.declare("dependant_care_expenses", Decimal, non_negative=True)
"""Dependant's care expenses, Federal Worksheet for line 31800, line 3 "Total of child care and
attendant care expenses for your dependant that you or another person claimed": a starting amount,
a field of each record of the dependants with a disability. It matters only for a dependant under
18."""

DEPENDANT_CREDIT_AMOUNTS = CATALOG.declare("dependant_credit_amounts", Decimal, non_negative=True)
"""Dependant's credit amounts, Federal Worksheet for line 31800, line 9 "For provinces and
territories other than Quebec: amount from line 98 of your dependant's return", where 5000-R line
98 is "Add lines 85, 96, and 97.": a starting amount from another person's return, a field of each
record of the dependants with a disability."""

DEPENDANT_TAXABLE_INCOME = CATALOG.declare("dependant_taxable_income", Decimal, non_negative=True)
"""Dependant's taxable income, Federal Worksheet for line 31800, line 11 "Dependant's taxable
income from line 26000 of their return": a starting amount from another person's return, a field
of each record of the dependants with a disability."""

DISABILITY_DEPENDANTS = RecordListKind.declare(
    CATALOG,
    "disability_dependants",
    fields=(
        DEPENDANT_UNDER_18,
        DEPENDANT_CARE_EXPENSES,
        DEPENDANT_CREDIT_AMOUNTS,
        DEPENDANT_TAXABLE_INCOME,
    ),
)
"""Dependants with a disability, Federal Worksheet "Line 31800 - Disability amount transferred from
a dependant" "Complete the following calculation fore ach dependant who is eligible for the
disability tax credit in 2025": a starting list with one record for each such dependant, holding
whether they were under 18 on December 31, 2025, line 3 the child care and attendant care
expenses, line 9 line 98 of their return and line 11 their taxable income. The caller lists only
the dependants who meet the conditions."""

DISABILITY_TRANSFERRED_AMOUNT = CATALOG.declare(
    "disability_transferred_amount", Decimal, non_negative=True
)
"""Disability amount transferred from a dependant, T1 line 100 (line 31800) "Disability amount
transferred from a dependant (use Federal Worksheet)": "the total of allowable amounts claimed for
all dependants who qualify for the disability tax credit", each line 13 "Enter whichever is less:
amount from line 8 or line 12. Allowable amount for this dependant", a part of the total of the
credit amounts."""

ELIGIBLE_FOR_DISABILITY_AMOUNT = CATALOG.declare(
    "eligible_for_disability_amount", int, non_negative=True
)
"""Qualifies for the disability amount, Federal Worksheet (form 5000-D1), "Line 31600 - Disability
amount for self", "If you qualify for the disability amount": a starting count, 0 or 1, the CRA's
approval of the filer on Form T2201; the amount is claimed once if it is 1."""

ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED = CATALOG.declare(
    "eligible_for_disability_amount_checked", int, non_negative=True
)
"""Qualifies for the disability amount, Federal Worksheet (form 5000-D1) "Line 31600 - Disability
amount for self": the answer of `ca/eligible_for_disability_amount` after the check that it is 0 or
1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

UNDER_18_ON_DECEMBER_31 = CATALOG.declare("under_18_on_december_31", int, non_negative=True)
"""Under 18 years of age on December 31, 2025, Federal Worksheet (form 5000-D1), "Line 31600 -
Disability amount for self", "under 18 years of age, complete the calculation below": a starting
count, 0 or 1, from the date of birth the return asks for."""

UNDER_18_ON_DECEMBER_31_CHECKED = CATALOG.declare(
    "under_18_on_december_31_checked", int, non_negative=True
)
"""Under 18 years of age on December 31, 2025, Federal Worksheet (form 5000-D1) "Line 31600 -
Disability amount for self": the answer of `ca/under_18_on_december_31` after the check that it is 0
or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

UNDER_18_AND_BORN_IN_1960_OR_EARLIER = CATALOG.declare(
    "under_18_and_born_in_1960_or_earlier", int, non_negative=True
)
"""Entered as both under 18 and born in 1960 or earlier, Worksheet ON428 line 58440 "if you were
under 18 years of age on December 31, 2025" and Form ON428 line 10 "Age amount (if you were born in
1960 or earlier)": 1 when `ca/under_18_on_december_31` and `ca/born_in_1960_or_earlier` are each
more than 0, else 0, a starting count. Born in 1960 or earlier means 65 or older, so a count of 1 is
refused (see `ca/under_18_and_born_in_1960_or_earlier_checked`)."""

UNDER_18_AND_BORN_IN_1960_OR_EARLIER_CHECKED = CATALOG.declare(
    "under_18_and_born_in_1960_or_earlier_checked", int, non_negative=True
)
"""Entered as both under 18 and born in 1960 or earlier, checked: the count of
`ca/under_18_and_born_in_1960_or_earlier` when it is 0, the only value produced. A count of 1 is an
input error, not capped, so the disability amount for a filer under 18 is never claimed beside the
age amount."""

UNDER_18_AND_AGED_18_OR_OLDER = CATALOG.declare(
    "under_18_and_aged_18_or_older", int, non_negative=True
)
"""Entered as both under 18 and 18 or older, Worksheet ON428 line 58440 "if you were under 18 years
of age on December 31, 2025" and the Federal Worksheet for line 45200 "You were 18 years of age or
older at the end of 2025": 1 when `ca/under_18_on_december_31` and
`ca/aged_18_or_older_at_end_of_2025` are each more than 0, else 0, a starting count. The two exclude
each other, so a count of 1 is refused (see `ca/under_18_and_aged_18_or_older_checked`)."""

UNDER_18_AND_AGED_18_OR_OLDER_CHECKED = CATALOG.declare(
    "under_18_and_aged_18_or_older_checked", int, non_negative=True
)
"""Entered as both under 18 and 18 or older, checked: the count of
`ca/under_18_and_aged_18_or_older` when it is 0, the only value produced. A count of 1 is an input
error, not capped, so the two ages are never accepted together."""

DISABILITY_SELF_CARE_EXPENSES = CATALOG.declare(
    "disability_self_care_expenses", Decimal, non_negative=True
)
"""Child care and attendant care expenses for self, Federal Worksheet (form 5000-D1), "Line 31600 -
Disability amount for self", line 3 "Total of child care and attendant care expenses for you that
you or another person claimed": a starting amount, the caller's figure, the same figure as the
Ontario worksheet's line 3."""

DISABILITY_SELF_BASE_AMOUNT = CATALOG.declare(
    "disability_self_base_amount", Decimal, non_negative=True
)
"""Base amount for self, Federal Worksheet (form 5000-D1), "Line 31600 - Disability amount for
self", line 1 "Base amount 10,138.00": the dataset as an artifact."""

DISABILITY_SELF_SUPPLEMENT_MAXIMUM = CATALOG.declare(
    "disability_self_supplement_maximum", Decimal, non_negative=True
)
"""Maximum supplement for self, Federal Worksheet (form 5000-D1), "Line 31600 - Disability amount
for self", line 2 "Maximum supplement 5,914.00": the dataset as an artifact."""

DISABILITY_SELF_CARE_THRESHOLD = CATALOG.declare(
    "disability_self_care_threshold", Decimal, non_negative=True
)
"""Threshold for child care and attendant care expenses for self, Federal Worksheet (form
5000-D1), "Line 31600 - Disability amount for self", line 4 "Threshold for child care and attendant
care expenses 3,464.00": the dataset as an artifact."""

DISABILITY_SELF_CARE_OVER_THRESHOLD = CATALOG.declare(
    "disability_self_care_over_threshold", Decimal, non_negative=True
)
"""Care expenses over the threshold for self, Federal Worksheet (form 5000-D1), "Line 31600 -
Disability amount for self", line 5 "Line 3 minus line 4 (if negative, enter "0")": line 3 less the
threshold of line 4, not below zero."""

DISABILITY_SELF_SUPPLEMENT = CATALOG.declare(
    "disability_self_supplement", Decimal, non_negative=True
)
"""Supplement for self, Federal Worksheet (form 5000-D1), "Line 31600 - Disability amount for self",
line 6 "Line 2 minus line 5 (if negative, enter "0")": the maximum supplement less the care
expenses over the threshold, not below zero."""

DISABILITY_SELF_WORKSHEET_AMOUNT = CATALOG.declare(
    "disability_self_worksheet_amount", Decimal, non_negative=True
)
"""Disability amount for self under 18, Federal Worksheet (form 5000-D1), "Line 31600 - Disability
amount for self", line 7 "Line 1 plus line 6 Enter this amount on line 31600 of your return.
(maximum $16,052)": the base amount plus the supplement; the printed maximum is met without a cap,
as the supplement is at most the maximum supplement."""

DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE = CATALOG.declare(
    "disability_amount_for_self_if_eligible", Decimal, non_negative=True
)
"""Disability amount for self before the qualification, Federal Worksheet (form 5000-D1), "Line
31600 - Disability amount for self": "18 years of age or older, enter $10,138 on line 31600 of your
return", the base amount of line 1 for a filer 18 or older on December 31, 2025, and the worksheet
amount of line 7 for a filer under 18."""

DISABILITY_AMOUNT_FOR_SELF = CATALOG.declare(
    "disability_amount_for_self", Decimal, non_negative=True
)
"""Disability amount for self, T1 line 99 and line 31600 "Disability amount for self (if you were
under 18 years of age, use Federal Worksheet; if not, claim $10,138)": the amount once if the
filer qualifies, else 0; a part of the total of the credit amounts. Read by Form T1206 Part 2
line 11 "Amount from line 31600 of your return"."""

RESIDENCE_YEARS_DESIGNATED_AFTER_1981 = CATALOG.declare(
    "residence_years_designated_after_1981", int, non_negative=True
)
"""Years designated after 1981, Form T2091(IND) line 1 "Designation" "After 1981": the number of
tax years after 1981 for which the property is designated as the principal residence; a starting
count, a field of each record of the properties sold."""

RESIDENCE_YEARS_DESIGNATED_1972_TO_1981 = CATALOG.declare(
    "residence_years_designated_1972_to_1981", int, non_negative=True
)
"""Years designated from 1972 to 1981, Form T2091(IND) line 2 "Designation" "After 1971 and before
1982": the number of tax years in that period for which the property is designated as the
principal residence; a starting count, a field of each record of the properties sold."""

RESIDENCE_YEARS_OWNED_AFTER_1981 = CATALOG.declare(
    "residence_years_owned_after_1981", int, non_negative=True
)
"""Years owned after 1981, Form T2091(IND) line 5 "Number of tax years ending after the acquisition
date in which you owned the property" "After 1981": a starting count, a field of each record of
the properties sold."""

RESIDENCE_YEARS_OWNED_1972_TO_1981 = CATALOG.declare(
    "residence_years_owned_1972_to_1981", int, non_negative=True
)
"""Years owned from 1972 to 1981, Form T2091(IND) line 6 "Number of tax years ending after the
acquisition date in which you owned the property" "After 1971 and before 1982": a starting count,
a field of each record of the properties sold."""

RESIDENCE_PROCEEDS = CATALOG.declare("residence_proceeds", Decimal, non_negative=True)
"""Proceeds of disposition, Form T2091(IND) line 8 "Proceeds of disposition or deemed disposition"
(carried to line 14): a starting amount, a field of each record of the properties sold."""

RESIDENCE_OUTLAYS = CATALOG.declare("residence_outlays", Decimal, non_negative=True)
"""Outlays and expenses, Form T2091(IND) line 9 "Outlays and expenses made or incurred related to
the disposition" (carried to line 16): a starting amount, a field of each record of the properties
sold."""

RESIDENCE_ADJUSTED_COST_BASE = CATALOG.declare(
    "residence_adjusted_cost_base", Decimal, non_negative=True
)
"""Adjusted cost base, Form T2091(IND) line 10 "Adjusted cost base at the time of disposition"
(carried to line 15): a starting amount, a field of each record of the properties sold."""

RESIDENCE_PLUS_ONE_YEAR = CATALOG.declare("residence_plus_one_year", int, non_negative=True)
"""The "plus one" year, Form T2091(IND) line 20 "Line 4 plus 1 (see note on page 4)" with the note
"One year is granted by law. If you disposed of your principal residence after October 2, 2016,
and were a non-resident throughout the year of acquisition of the property, you are not eligible
to use the "plus one" rule in this calculation.": 1 if the property may use it, else 0, taken as a
count like the forms' other yes or no questions; a starting count, a field of each record of the
properties sold."""

RESIDENCE_PART_2_APPLIES = CATALOG.declare("residence_part_2_applies", int, non_negative=True)
"""Part 2 applies, Form T2091(IND) Part 2 "Complete Part 2 if the property disposed of is one of two
or more properties that qualify as principal residences a family member owned on December 31, 1981,
and continuously thereafter until its disposition.": 1 if the property is one of them, else 0, taken
as a count like the forms' other yes or no questions; a starting count, a field of each record of
the properties sold."""

RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981 = CATALOG.declare(
    "residence_adjusted_cost_base_dec_31_1981", Decimal, non_negative=True
)
"""Adjusted cost base on December 31, 1981, Form T2091(IND) line 11 "Adjusted cost base on December
31, 1981": a starting amount, a field of each record of the properties sold, used by Part 2 only."""

RESIDENCE_FMV_DEC_31_1981 = CATALOG.declare("residence_fmv_dec_31_1981", Decimal, non_negative=True)
"""Fair market value on December 31, 1981, Form T2091(IND) line 12 "Fair market value on December
31, 1981": a starting amount, a field of each record of the properties sold, used by Part 2 only."""

RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981 = CATALOG.declare(
    "residence_cost_base_adjustments_after_1981", Decimal, non_negative=True
)
"""Adjustments to the cost base made after 1981, Form T2091(IND) line 13 "Adjustments to the cost
base made after 1981 (for example, capital expenditures)": a starting amount, a field of each record
of the properties sold, used by Part 2 only."""

RESIDENCE_T664_FILED = CATALOG.declare("residence_t664_filed", int, non_negative=True)
"""Form T664 or T664(Seniors) filed for the property, Form T2091(IND) Part 4 "Complete Part 4 if you
or your spouse or common-law partner filed Form T664 or T664(Seniors) for this property.": 1 if it
was filed, else 0, taken as a count like the forms' other yes or no questions; a starting count, a
field of each record of the properties sold, used by the worksheet and Part 4 only."""

RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981 = CATALOG.declare(
    "residence_ws_years_designated_after_1981", int, non_negative=True
)
"""Years designated after 1981 and before 1995, Form T2091(IND)-WS line 1 "After 1981 and before
1995": a starting count from the 1994 election, a field of each record of the properties sold, used
by the worksheet only."""

RESIDENCE_WS_YEARS_OWNED_AFTER_1981 = CATALOG.declare(
    "residence_ws_years_owned_after_1981", int, non_negative=True
)
"""Years owned after 1981 and before 1995, Form T2091(IND)-WS line 4 "After 1981 and before 1995": a
starting count from the 1994 election, a field of each record of the properties sold, used by the
worksheet only."""

RESIDENCE_WS_DESIGNATED_PROCEEDS = CATALOG.declare(
    "residence_ws_designated_proceeds", Decimal, non_negative=True
)
"""Designated proceeds of disposition, Form T2091(IND)-WS line 7 "Designated proceeds of disposition
(column 2, Chart B of Form T664, or column 2, Step 2 of Form T664(Seniors))": a starting amount from
the 1994 election, a field of each record of the properties sold, used by the worksheet only."""

RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994 = CATALOG.declare(
    "residence_ws_adjusted_cost_base_feb_22_1994", Decimal, non_negative=True
)
"""Adjusted cost base at the end of February 22, 1994, Form T2091(IND)-WS line 8 "Adjusted cost base
at the end of February 22, 1994 (column 1, Chart B of Form T664, or column 1, Step 2 of Form
T664(Seniors))": a starting amount from the 1994 election, a field of each record of the properties
sold, used by the worksheet only."""

RESIDENCE_WS_FMV_FEB_22_1994 = CATALOG.declare(
    "residence_ws_fmv_feb_22_1994", Decimal, non_negative=True
)
"""Fair market value at the end of February 22, 1994, Form T2091(IND)-WS line 10 "Fair market value
at the end of February 22, 1994 (Step 1 of Form T664 or T664(Seniors))": a starting amount from the
1994 election, a field of each record of the properties sold, used by the worksheet only."""

RESIDENCE_WS_ELECTED_CAPITAL_GAIN = CATALOG.declare(
    "residence_ws_elected_capital_gain", Decimal, non_negative=True
)
"""Elected capital gain, Form T2091(IND)-WS line 13 "Elected capital gain (column 5, Chart B of Form
T664, or column 5, Step 2 of Form T664(Seniors))": a starting amount from the 1994 election, a field
of each record of the properties sold, used by the worksheet only."""

RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992 = CATALOG.declare(
    "residence_ws_months_owned_after_feb_1992", int, non_negative=True
)
"""Months owned after February 1992 and before March 1994, Form T2091(IND)-WS line 60 "Number of
months you owned the property after February 1992 and before March 1994 (do not include any months
you or your spouse or common-law partner designated the property as a principal residence)": a
starting count, a field of each record of the properties sold, used by the worksheet only."""

RESIDENCE_WS_MONTHS_OWNED_AFTER_1971 = CATALOG.declare(
    "residence_ws_months_owned_after_1971", int, non_negative=True
)
"""Months owned after 1971 and before March 1994, Form T2091(IND)-WS line 62 "Number of months you
owned the property after 1971 and before March 1994 (do not include any months you or your spouse
or common-law partner designated the property as a principal residence)": a starting count, a field
of each record of the properties sold, used by the worksheet only."""

RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994 = CATALOG.declare(
    "residence_ws_cost_base_adjustments_to_feb_1994", Decimal, non_negative=True
)
"""Adjustments made to the cost base after 1981 and before February 23, 1994, Form T2091(IND)-WS
line 12 "Adjustments made to the cost base after 1981 and before February 23, 1994": a starting
amount, a field of each record of the properties sold, used by Part 2 of the worksheet only (it is
not line 13 of Form T2091(IND), which runs to the disposition)."""

PRINCIPAL_RESIDENCE_PROPERTIES = RecordListKind.declare(
    CATALOG,
    "principal_residence_properties",
    fields=(
        RESIDENCE_YEARS_DESIGNATED_AFTER_1981,
        RESIDENCE_YEARS_DESIGNATED_1972_TO_1981,
        RESIDENCE_YEARS_OWNED_AFTER_1981,
        RESIDENCE_YEARS_OWNED_1972_TO_1981,
        RESIDENCE_PROCEEDS,
        RESIDENCE_OUTLAYS,
        RESIDENCE_ADJUSTED_COST_BASE,
        RESIDENCE_PLUS_ONE_YEAR,
        RESIDENCE_PART_2_APPLIES,
        RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981,
        RESIDENCE_FMV_DEC_31_1981,
        RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981,
        RESIDENCE_T664_FILED,
        RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981,
        RESIDENCE_WS_YEARS_OWNED_AFTER_1981,
        RESIDENCE_WS_DESIGNATED_PROCEEDS,
        RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994,
        RESIDENCE_WS_FMV_FEB_22_1994,
        RESIDENCE_WS_ELECTED_CAPITAL_GAIN,
        RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992,
        RESIDENCE_WS_MONTHS_OWNED_AFTER_1971,
        RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994,
    ),
)
"""Properties sold and designated as a principal residence, Form T2091(IND) "Complete a separate
form for each property you sold.": a starting list with one record for each such property, holding
the form's input lines 1, 2, 5, 6, 8, 9, 10, 11, 12 and 13, whether the "plus one" applies and
whether Part 2 applies (lines 3, 4, 7 and 14 onward are worked out), and the figures of the 1994
election the Form T2091(IND)-WS worksheet takes: whether Form T664 or T664(Seniors) was filed, and
worksheet lines 1, 4, 7, 8, 10, 12, 13, 60 and 62. The caller lists only the properties the form
sends to Section 2 (Schedule 3 box 2 or 3) that are not flipped properties."""

PRINCIPAL_RESIDENCE_GAIN = CATALOG.declare("principal_residence_gain", Decimal, non_negative=True)
"""Capital gain left after the principal residence exemption, Form T2091(IND) Part 3 line 54 "Total
capital gain": "If you completed Part 2, enter whichever amount is less: line 53 above or line 24 of
Part 1. Otherwise, enter the amount from line 24.", each line 24 being "Line 18 minus line 23 (if
negative, enter "0")", totalled over the properties sold."""

PRINCIPAL_RESIDENCE_DESIGNATION_BOX = CATALOG.declare(
    "principal_residence_designation_box", int, non_negative=True
)
"""Principal residence designation box, Form 5000-S3 Part 1 line 17900 "Tick the box that applies to
your designation of the property described on Form T2091(IND) or Form T1255": 1 for the property
designated for all, or all but one, of its years owned, 2 for some but not all of them, 3 for more
than one property; 0 with no property. A conclusion from the properties sold, not a printed line."""

PRINCIPAL_RESIDENCE_LINE_27 = CATALOG.declare("principal_residence_line_27", Decimal)
"""Pre-1982 gain before principal residence exemption, Form T2091(IND) Part 2 line 27 "Line 25 minus
line 26": the total over the properties sold, not floored, so it may be negative; 0 for a property
whose area A is not completed."""

PRINCIPAL_RESIDENCE_LINE_29 = CATALOG.declare(
    "principal_residence_line_29", Decimal, non_negative=True
)
"""Years designated before 1982 plus one, Form T2091(IND) Part 2 line 29 "Line 2 plus 1 (see note on
page 4)": the total over the properties sold; 0 for a property whose area A is not completed."""

PRINCIPAL_RESIDENCE_LINE_30 = CATALOG.declare("principal_residence_line_30", Decimal)
"""Pre-1982 gain multiplied by the years, Form T2091(IND) Part 2 line 30 "Multiply line 28 by line
29.": the total over the properties sold, not floored, so it may be negative."""

PRINCIPAL_RESIDENCE_LINE_32 = CATALOG.declare("principal_residence_line_32", Decimal)
"""Pre-1982 exempt part, Form T2091(IND) Part 2 line 32 "Divide line 30 by line 31.": the total over
the properties sold of each quotient rounded with the dataset's rule; it may be negative."""

PRINCIPAL_RESIDENCE_LINE_33 = CATALOG.declare(
    "principal_residence_line_33", Decimal, non_negative=True
)
"""Pre-1982 gain, Form T2091(IND) Part 2 line 33 "Line 27 minus line 32 (if negative, enter "0")":
the total over the properties sold, each floored at 0."""

PRINCIPAL_RESIDENCE_LINE_38 = CATALOG.declare(
    "principal_residence_line_38", Decimal, non_negative=True
)
"""Post-1981 cost base, outlays and fair market value, Form T2091(IND) Part 2 line 38 "Add lines 35
to 37.": the total over the properties sold; 0 for a property whose area B is not completed."""

PRINCIPAL_RESIDENCE_LINE_39 = CATALOG.declare("principal_residence_line_39", Decimal)
"""Post-1981 gain before principal residence exemption, Form T2091(IND) Part 2 line 39 "Line 34
minus line 38": the total over the properties sold, not floored, so it may be negative."""

PRINCIPAL_RESIDENCE_LINE_42 = CATALOG.declare("principal_residence_line_42", Decimal)
"""Post-1981 gain multiplied by the years designated after 1981, Form T2091(IND) Part 2 line 42
"Multiply line 40 by line 41.": the total over the properties sold, not floored, so it may be
negative."""

PRINCIPAL_RESIDENCE_LINE_44 = CATALOG.declare("principal_residence_line_44", Decimal)
"""Post-1981 exempt part, Form T2091(IND) Part 2 line 44 "Divide line 42 by line 43.": the total
over the properties sold of each quotient rounded with the dataset's rule; it may be negative."""

PRINCIPAL_RESIDENCE_LINE_45 = CATALOG.declare(
    "principal_residence_line_45", Decimal, non_negative=True
)
"""Post-1981 gain, Form T2091(IND) Part 2 line 45 "Line 39 minus line 44 (if negative, enter "0")":
the total over the properties sold, each floored at 0."""

PRINCIPAL_RESIDENCE_LINE_48 = CATALOG.declare(
    "principal_residence_line_48", Decimal, non_negative=True
)
"""Post-1981 loss, Form T2091(IND) Part 2 line 48 "Line 46 minus line 47 (if negative, enter "0")":
the total over the properties sold, each floored at 0; 0 for a property whose area C is not
completed."""

PRINCIPAL_RESIDENCE_LINE_51 = CATALOG.declare(
    "principal_residence_line_51", Decimal, non_negative=True
)
"""Pre-1982 and post-1981 gains together, Form T2091(IND) Part 2 line 51 "Line 49 plus line 50": the
total over the properties sold."""

PRINCIPAL_RESIDENCE_LINE_53 = CATALOG.declare(
    "principal_residence_line_53", Decimal, non_negative=True
)
"""Net capital gain of Part 2, Form T2091(IND) Part 2 line 53 "Line 51 minus line 52 (if negative,
enter "0")": the total over the properties sold, each floored at 0."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_3 = CATALOG.declare(
    "principal_residence_worksheet_line_3", Decimal, non_negative=True
)
"""Total years designated before 1995, Form T2091(IND)-WS line 3 "Total number of years designated
before 1995 (line 1 plus line 2)": the total over the properties sold, each a count of years."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_6 = CATALOG.declare(
    "principal_residence_worksheet_line_6", Decimal, non_negative=True
)
"""Total years owned before 1995, Form T2091(IND)-WS line 6 "Total number of years owned before 1995
(line 4 plus line 5)": the total over the properties sold, each a count of years."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16 = CATALOG.declare(
    "principal_residence_worksheet_line_16", Decimal, non_negative=True
)
"""Line 14 times 1.1, Form T2091(IND)-WS Chart 1 line 16 "Multiply line 14 by 1.1.": the total over
the properties sold of each product rounded with the Chart 1 factor's rule; 0 for a property whose
Chart 1 is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17 = CATALOG.declare(
    "principal_residence_worksheet_line_17", Decimal, non_negative=True
)
"""Chart 1 line 17, Form T2091(IND)-WS "Line 15 minus line 16 (if negative, enter "0")": the total
over the properties sold, each floored at 0; 0 for a property whose Chart 1 is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18 = CATALOG.declare(
    "principal_residence_worksheet_line_18", Decimal
)
"""Chart 1 line 18, Form T2091(IND)-WS "Line 14 minus line 17": the total over the properties sold,
not floored, so it may be negative; 0 for a property whose Chart 1 is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19 = CATALOG.declare(
    "principal_residence_worksheet_line_19", Decimal
)
"""Worksheet line 19, Form T2091(IND)-WS "Enter the amount from line 18 if you completed Chart 1.
Otherwise, enter the amount from line 10.": the total over the properties sold, not floored, so it
may be negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_21 = CATALOG.declare(
    "principal_residence_worksheet_line_21", Decimal
)
"""Adjusted gain before principal residence exemption, Form T2091(IND)-WS line 21 "Line 19 minus
line 20": the total over the properties sold, not floored, so it may be negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_23 = CATALOG.declare(
    "principal_residence_worksheet_line_23", Decimal, non_negative=True
)
"""Years designated plus the "plus one", Form T2091(IND)-WS line 23 "Line 3 plus 1 (see note
below)": the total over the properties sold, each a count of years."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_24 = CATALOG.declare(
    "principal_residence_worksheet_line_24", Decimal
)
"""Adjusted gain multiplied by the years, Form T2091(IND)-WS line 24 "Multiply line 22 by line 23.":
the total over the properties sold, not floored, so it may be negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_26 = CATALOG.declare(
    "principal_residence_worksheet_line_26", Decimal
)
"""Exempt part of the adjusted gain, Form T2091(IND)-WS line 26 "Divide line 24 by line 25.": the
total over the properties sold of each quotient rounded with the worksheet's rounding rule; it may
be negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_27 = CATALOG.declare(
    "principal_residence_worksheet_line_27", Decimal
)
"""Net adjusted gain, Form T2091(IND)-WS line 27 "Line 21 minus line 26": the total over the
properties sold, not floored, so it may be negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59 = CATALOG.declare(
    "principal_residence_worksheet_line_59", Decimal
)
"""Gain carried into Part 3, Form T2091(IND)-WS line 59 "If you completed Part 2, enter the amount
from line 58. Otherwise, enter the amount from line 27.": the total over the properties sold, not
floored, so it may be negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61 = CATALOG.declare(
    "principal_residence_worksheet_line_61", Decimal
)
"""Gain multiplied by the months owned after February 1992, Form T2091(IND)-WS line 61 "Multiply
line 59 by line 60.": the total over the properties sold, not floored, so it may be negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63 = CATALOG.declare(
    "principal_residence_worksheet_line_63", Decimal
)
"""Gain of the months owned after February 1992 over the months owned after 1971, Form T2091(IND)-WS
line 63 "Divide line 61 by line 62.": the total over the properties sold of each quotient rounded
with the worksheet's rounding rule; it may be negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64 = CATALOG.declare(
    "principal_residence_worksheet_line_64", Decimal
)
"""Total adjusted gain, Form T2091(IND)-WS line 64 "Line 59 minus line 63": the total over the
properties sold, not floored, so it may be negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66 = CATALOG.declare(
    "principal_residence_worksheet_line_66", Decimal
)
"""Reduction as a result of the capital gains election, Form T2091(IND)-WS line 66 "Enter whichever
amount is less: line 64 or line 65.": the total over the properties sold, not floored, so it may be
negative."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_30 = CATALOG.declare(
    "principal_residence_worksheet_line_30", Decimal
)
"""Adjusted pre-1982 gain before the exemption, Form T2091(IND)-WS line 30 "Line 28 minus line 29":
the total over the properties sold, not floored, so it may be negative; 0 where area A is not
completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_32 = CATALOG.declare(
    "principal_residence_worksheet_line_32", Decimal, non_negative=True
)
"""Years designated before 1982 plus one, Form T2091(IND)-WS line 32 "Line 2 plus 1 (see note
below)": the total over the properties sold of that count; 0 where area A is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_33 = CATALOG.declare(
    "principal_residence_worksheet_line_33", Decimal
)
"""Pre-1982 gain multiplied by the years, Form T2091(IND)-WS line 33 "Multiply line 31 by line 32.":
the total over the properties sold, not floored, so it may be negative; 0 where area A is not
completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_35 = CATALOG.declare(
    "principal_residence_worksheet_line_35", Decimal
)
"""Exempt part of the pre-1982 gain, Form T2091(IND)-WS line 35 "Divide line 33 by line 34.": the
total over the properties sold of each quotient rounded with the worksheet's rounding rule; it may
be negative; 0 where area A is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_36 = CATALOG.declare(
    "principal_residence_worksheet_line_36", Decimal, non_negative=True
)
"""Adjusted pre-1982 gain, Form T2091(IND)-WS line 36 "Line 30 minus line 35 (if negative, enter
"0")": the total over the properties sold, each floored at 0; 0 where area A is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_40 = CATALOG.declare(
    "principal_residence_worksheet_line_40", Decimal, non_negative=True
)
"""Fair market value 1981 plus adjustments, Form T2091(IND)-WS line 40 "Line 38 plus line 39": the
total over the properties sold; 0 where area B is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_41 = CATALOG.declare(
    "principal_residence_worksheet_line_41", Decimal
)
"""Adjusted post-1981 gain before the exemption, Form T2091(IND)-WS line 41 "Line 37 minus line 40":
the total over the properties sold, not floored, so it may be negative; 0 where area B is not
completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_44 = CATALOG.declare(
    "principal_residence_worksheet_line_44", Decimal
)
"""Post-1981 gain multiplied by the years, Form T2091(IND)-WS line 44 "Multiply line 42 by line
43.": the total over the properties sold, not floored, so it may be negative; 0 where area B is not
completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_46 = CATALOG.declare(
    "principal_residence_worksheet_line_46", Decimal
)
"""Exempt part of the post-1981 gain, Form T2091(IND)-WS line 46 "Divide line 44 by line 45.": the
total over the properties sold of each quotient rounded with the worksheet's rounding rule; it may
be negative; 0 where area B is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47 = CATALOG.declare(
    "principal_residence_worksheet_line_47", Decimal, non_negative=True
)
"""Adjusted post-1981 gain, Form T2091(IND)-WS line 47 "Line 41 minus line 46 (if negative, enter
"0")": the total over the properties sold, each floored at 0; 0 where area B is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50 = CATALOG.declare(
    "principal_residence_worksheet_line_50", Decimal, non_negative=True
)
"""Adjusted post-1981 loss, Form T2091(IND)-WS line 50 "Line 48 minus line 49 (if negative, enter
"0")": the total over the properties sold, each floored at 0; 0 where area C is not completed."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_53 = CATALOG.declare(
    "principal_residence_worksheet_line_53", Decimal, non_negative=True
)
"""Adjusted gains added, Form T2091(IND)-WS line 53 "Line 51 plus line 52": the total over the
properties sold of the adjusted pre-1982 gain and the adjusted post-1981 gain."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_55 = CATALOG.declare(
    "principal_residence_worksheet_line_55", Decimal, non_negative=True
)
"""Net adjusted gain from Part 2, Form T2091(IND)-WS line 55 "Line 53 minus line 54 (if negative,
enter "0")": the total over the properties sold, each floored at 0."""

PRINCIPAL_RESIDENCE_WORKSHEET_LINE_58 = CATALOG.declare(
    "principal_residence_worksheet_line_58", Decimal
)
"""Total adjusted gain before reduction for non-qualifying real or immovable property, Form
T2091(IND)-WS line 58 "Enter whichever amount is less: line 56 or line 57.": the total over the
properties sold of the lesser of line 27 and line 55, not floored, so it may be negative."""

PRINCIPAL_RESIDENCE_LINE_56 = CATALOG.declare("principal_residence_line_56", Decimal)
"""Reduction as a result of the capital gains election, Form T2091(IND) Part 4 line 56 "Reduction as
a result of the capital gains election (line 66 of Form T2091(IND)-WS)": the total over the
properties sold; 0 for a property whose election was not filed. The form prints no floor, so it may
be negative."""

PRINCIPAL_RESIDENCE_LINE_57 = CATALOG.declare(
    "principal_residence_line_57", Decimal, non_negative=True
)
"""Total capital gain after the election, Form T2091(IND) Part 4 line 57 "Line 55 minus line 56 (if
negative, enter "0")": the total over the properties sold, each floored at 0; the amount that
goes to Schedule 3 line 15800 when the election is wired."""

CCA_CLASS_NUMBER = CATALOG.declare("cca_class_number", Decimal, non_negative=True)
"""Class number, T776 and T2125 Area A "Column 1: Class number", and T776 Area B and Area C
"Column 1: Class number": a number such as 8, 10.1 or 43.1, kept exact, a field of each record of
a list of capital cost allowance classes."""

CCA_UCC_AT_START = CATALOG.declare("cca_ucc_at_start", Decimal, non_negative=True)
"""UCC at the start of the year, Area A "Column 2: Undepreciated capital cost (UCC) at the start of
the year": a starting amount, a field of each record of a list of capital cost allowance
classes."""

CCA_ADDITIONS = CATALOG.declare("cca_additions", Decimal, non_negative=True)
"""Cost of additions, Area A "Column 3: Cost of additions in the year (see Areas B and C below)": a
starting amount, a field of each record of a list of capital cost allowance classes."""

CCA_PROCEEDS = CATALOG.declare("cca_proceeds", Decimal, non_negative=True)
"""Proceeds of dispositions, Area A "Column 5: Proceeds of dispositions in the year (see Areas D and
E below)": a starting amount, a field of each record of a list of capital cost allowance
classes."""

CCA_AIIP_ADDITIONS = CATALOG.declare("cca_aiip_additions", Decimal, non_negative=True)
"""AIIP additions, Area A "Column 11: Cost of remaining additions from column 10 that are AIIPs or
ZEVs acquired before 2025": a starting amount, a field of each record of a list of capital cost
allowance classes."""

CCA_RIIP_ADDITIONS = CATALOG.declare("cca_riip_additions", Decimal, non_negative=True)
"""RIIP additions, Area A "Column 12: Cost of remaining additions from column 10 that are RIIPs or
ZEVs acquired after 2024": a starting amount, a field of each record of a list of capital cost
allowance classes."""

CCA_DIEP_ADDITIONS = CATALOG.declare("cca_diep_additions", Decimal, non_negative=True)
"""DIEP additions, Area A "Column 4: Cost of additions from column 3 that are DIEPs (property must
be available for use before 2025)": a starting amount, a field of each record of a list of capital
cost allowance classes."""

CCA_DIEP_PROCEEDS = CATALOG.declare("cca_diep_proceeds", Decimal, non_negative=True)
"""DIEP proceeds, Area A "Column 6: Proceeds of dispositions of DIEP (enter amount from column 5
that relates to DIEP from column 4)": a starting amount, a field of each record of a list of
capital cost allowance classes."""

CCA_IMMEDIATE_EXPENSING = CATALOG.declare("cca_immediate_expensing", Decimal, non_negative=True)
"""Immediate expensing amount, Area A "Column 9: Immediate expensing amount for DIEPs (Note 5)": the
caller's amount for the class, a field of each record of a list of capital cost allowance
classes."""

CCA_CLAIMED = CATALOG.declare("cca_claimed", Decimal, non_negative=True)
"""CCA claimed, T776 Area A "Column 23: CCA claim for the year" (T2125 column 21): the caller's
election, "any amount you like, from zero to the maximum allowed for the year" (Guide T4036), a
field of each record of a list of capital cost allowance classes."""

CCA_NO_PROPERTY_LEFT = CATALOG.declare("cca_no_property_left", int, non_negative=True)
"""No property left in the class, Area A Note 3 "If no property is left in the class and there is a
positive amount in this column, deduct the amount from your income as a terminal loss": 1 if no
property is left in the class at the end of the year, else 0, taken as a count like the forms'
other yes or no questions; a field of each record of a list of capital cost allowance classes."""

CCA_CHANGE_IN_USE = CATALOG.declare("cca_change_in_use", int, non_negative=True)
"""Change in use, Guide T4044 2025, Part A column 3: "If you owned property for personal use and
then started using it for employment in 2025, there is a change in use. In most cases when this
happens, the amount you will enter in this column is the fair market value of the property at the
time you start using the property for employment." 1 if the filer owned the property of the Part A
row (Classes 8, 10, 54 and 55) for personal use and started using it for employment in the tax
year, else 0, taken as a count like the forms' other yes or no questions. A field of each record of
Form T777 Part A."""

CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE = CATALOG.declare(
    "cca_change_in_use_fair_market_value", Decimal, non_negative=True
)
"""Fair market value at a change in use, Guide T4044 2025, Part A column 3: "If you owned property
for personal use and then started using it for employment in 2025, there is a change in use. In
most cases when this happens, the amount you will enter in this column is the fair market value of
the property at the time you start using the property for employment." The filer's figure, read
only when the row is answered as a change in use, else 0. A field of each record of Form T777
Part A."""

CCA_PERSONAL_PART_REMAINING = CATALOG.declare(
    "cca_personal_part_remaining", Decimal, non_negative=True
)
"""Remaining personal part, T776 Area A Note 9 (Column 24): "If, in the year, you disposed of a
property that you used for both personal and rental use, and your rental use of that property
changed from year to year, you must subtract any remaining personal part of this property's cost
from the UCC at the end of the year" (T2125, T2042 and T2121 endnote 9, with "business" for
"rental"): the caller's amount for the class, a field of each record of the lists of capital cost
allowance classes. Not the personal part of line 9936, which is `rental_cca_personal_part`."""

CCA_HALF_YEAR_RULE_DIFFERS = CATALOG.declare("cca_half_year_rule_differs", int, non_negative=True)
"""Half-year rule differs from the class, Guide T4002 2025, "Column 18 - Adjustment for current-year
additions subject to the half-year rule": "some properties are not subject to the half-year rule.
Some examples are those in Classes 13, 14, 23, 24, 27, 34, and 52, as well as most of those in
Class 12, such as small tools"; "in a non-arm's length transaction ... you may buy depreciable
property that the seller continuously owned"; "The half-year rule does not apply when the available
for use rules ... denies a CCA claim until the second tax year after you acquire the property".
1 if the row's additions are treated the opposite way from their class for the half-year rule
(Class 12 dies, jigs, patterns, moulds, lasts, cutting or shaping parts and software are subject
despite an exempt class; additions the Guide's conditions exempt, as a non-arm's length purchase of
property the seller owned continuously for at least 364 days before the end of the fiscal period,
and additions whose CCA is denied until the second year, are exempt despite a subject class), else
0, taken as a count like the forms' other yes or no questions; a field of each record of a list of
capital cost allowance classes. The caller decides whether the Guide's conditions are met. The
columns of a record work on the record alone (proceeds, no property left), so a class whose
additions are treated both ways is entered as several records with its proceeds in one of them."""

CCA_RATE_ELECTION = CATALOG.declare("cca_rate_election", int, non_negative=True)
"""CCA rate election, Guide T4036 2025, "Class 1 (4%)": "Under proposed changes, new buildings or
parts of a building that are built for use as a purpose-built residential rental (see definition on
page 8) may now be eligible for an accelerated CCA rate of 10%"; "The CCA rate for eligible
non-residential buildings acquired by a taxpayer after March 18, 2007, and used in Canada to
manufacture or process goods for sale or lease includes an additional allowance of 6% for a total
rate of 10%. The CCA rate for other eligible non-residential buildings includes an additional
allowance of 2% for a total rate of 6%"; "To be eligible for one of the additional allowances, you
must elect to put a building in a separate class. [...] If you do not file an election to put it in
a separate class, the 4% rate will apply." The code of the election the caller makes for the row:
0 none (the class's own rate), 1 purpose-built residential rental, 2 separate class, other
non-residential building, 3 separate class, building used to manufacture or process goods. The rate
of each code comes from the class-rates dataset, and a code the row's class does not list is
refused. A field of each record of a list of capital cost allowance classes."""

CCA_VEHICLE_ACQUIRED_YEAR = CATALOG.declare("cca_vehicle_acquired_year", int, non_negative=True)
"""Year the vehicle was acquired, T2125 2025 Area A endnote 2 (T776 Column 5 Note 2): "a passenger
vehicle bought after April 18, 2021, that has been included in Class 10.1, and whose cost is more
than the prescribed amount will be adjusted based on a factor equal to its prescribed amount as a
proportion of the actual cost of the vehicle [...] If the passenger vehicle in Class 10.1 is not
designated for immediate expensing treatment, this special rule does not apply", and Guide T4036
"Class 10.1 (30%)": "if you dispose of a passenger vehicle acquired after April 18, 2021, to a
person or partnership with whom you deal at arm's length". The year the vehicle in the row was
acquired, which picks its prescribed amount, or 0 when the rule does not apply to the row (it is
not a Class 10.1 vehicle designated for immediate expensing, or it was not sold at arm's length),
which the caller decides. A field of each record of a list of capital cost allowance classes, of
each record of Form T777 Part B (its "Date acquired (yyyy-mm-dd)", as the year, carried as
entered and required on every row, so never 0; no line of the form reads it) and of each record
of the vehicles sold from a Class 54 row (Guide T4036 "Class 54 (30%)"), where 0 means the rule
does not apply to that vehicle."""

CCA_VEHICLE_COST = CATALOG.declare("cca_vehicle_cost", Decimal, non_negative=True)
"""Actual cost of the vehicle, T2125 2025 Area A endnote 2: "whose cost is more than the prescribed
amount will be adjusted based on a factor equal to its prescribed amount as a proportion of the
actual cost of the vehicle", and Guide T4036 "Class 10.1 (30%)": the prescribed amounts are each
"plus the GST/HST or PST". The cost of the vehicle in the row including the GST/HST or PST. A
field of each record of a list of capital cost allowance classes and of each vehicle sold from a
Class 54 row. On Form T777 Part B it is the printed "Cost of vehicle", carried as entered (0 when
none is entered; no line of the form reads it): Guide T4044 says to leave out the GST and PST or HST
"when calculating the cost of the vehicle", so there it is the price before tax."""

CCA_VEHICLE_FROM_NON_ARMS_LENGTH = CATALOG.declare(
    "cca_vehicle_from_non_arms_length", int, non_negative=True
)
"""Bought from a non-arm's-length person, Guide T4044 2025, Part B column 3: "There is a limit on
the capital cost of a Class 10.1 vehicle you buy from a person with whom you have a non-arm's length
relationship. Generally, such a relationship happens when the person from whom you acquire the
vehicle is a relative. A non-arm's length relationship can also happen in certain business
relationships." 1 if the filer acquired the Class 10.1 vehicle of the row from such a person, else
0, taken as a count like the forms' other yes or no questions. The Guide states the condition and
no test for it, so the filer answers it. A field of each record of Form T777 Part B."""

CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE = CATALOG.declare(
    "cca_vehicle_non_arms_length_fair_market_value", Decimal, non_negative=True
)
"""Fair market value of a vehicle bought from a non-arm's-length person, Guide T4044 2025, Part B
column 3: "the capital cost is the least of the following three amounts: - the fair market value of
the vehicle when you acquired it". The filer's figure, read only when the row is answered as bought
from a non-arm's-length person, else 0. A field of each record of Form T777 Part B."""

CCA_VEHICLE_SELLER_COST = CATALOG.declare("cca_vehicle_seller_cost", Decimal, non_negative=True)
"""Seller's cost of a vehicle bought from a non-arm's-length person, Guide T4044 2025, Part B
column 3: "the seller's cost of the vehicle just before you acquired it. The cost can vary depending
on what the seller used the vehicle for before you acquired it. If the seller used the vehicle to
earn income, the cost will be the UCC of the vehicle just before you acquired it. When the seller
was not using the vehicle to earn income, the cost will usually be the original cost of the
vehicle". The filer's figure, read only when the row is answered as bought from a non-arm's-length
person, else 0. A field of each record of Form T777 Part B."""

CCA_VEHICLE_CHANGE_IN_USE = CATALOG.declare("cca_vehicle_change_in_use", int, non_negative=True)
"""Change in use, Guide T4044 2025, Part B column 3: "If you owned a passenger vehicle for personal
use and then started using it for employment in 2025, there is a change in use." 1 if the filer
owned the Class 10.1 vehicle of the row for personal use and started using it for employment in the
tax year, else 0, taken as a count like the forms' other yes or no questions. A field of each record
of Form T777 Part B."""

CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE = CATALOG.declare(
    "cca_vehicle_change_in_use_fair_market_value", Decimal, non_negative=True
)
"""Fair market value at a change in use, Guide T4044 2025, Part B column 3: "In most cases when
this happens, the amount you will enter in column 3 is the fair market value of the property at the
time you start using the property for employment." The filer's figure, read only when the row is
answered as a change in use, else 0. A field of each record of Form T777 Part B."""

CCA_VEHICLE_GOVERNMENT_ASSISTANCE = CATALOG.declare("cca_vehicle_government_assistance", Decimal)
"""Government assistance for the vehicle, T2125 2025 Area A endnote 2: "For dispositions after July
29, 2019, you will have to adjust the actual cost of the vehicle for any payments or repayments of
government assistance that you may have received or repaid for the vehicle". The assistance
received less the assistance repaid, signed: a repayment is negative. A field of each record of a
list of capital cost allowance classes and of each vehicle sold from a Class 54 row."""

CCA_ZEPV_PROCEEDS = CATALOG.declare("cca_zepv_proceeds", Decimal, non_negative=True)
"""Proceeds of one sold zero-emission passenger vehicle, Guide T4036 2025 "Class 54 (30%)": "If a
zero-emission passenger vehicle is disposed of to a person or partnership with whom you deal at
arm's length, and its cost exceeds the prescribed amount [...], the proceeds of disposition will be
adjusted based on a factor equal to the prescribed amount as a proportion of the actual cost of the
vehicle." The proceeds of the vehicle as entered, before the adjustment. A field of each record of
a Class 54 row's list of sold vehicles."""

CCA_ZEPV_DIEP_PROCEEDS = CATALOG.declare("cca_zepv_diep_proceeds", Decimal, non_negative=True)
"""DIEP part of the proceeds of one sold zero-emission passenger vehicle, Area A column 6 "Proceeds
of dispositions of DIEP (enter amount from col. 5 that relates to DIEP from col. 4)": the part of
the vehicle's proceeds that relates to a DIEP, as entered, before the adjustment. A field of each
record of a Class 54 row's list of sold vehicles."""

CCA_UCC_AT_END = CATALOG.declare("cca_ucc_at_end", Decimal, non_negative=True)
"""UCC at the end of the year, T776 Area A "Column 24: UCC at the end of the year (column 7 minus
column 23)" (T2125 column 22): a field of each record of the closing list of capital cost
allowance classes, for next year."""

INFIRM_CHILDREN = CATALOG.declare("infirm_children", int, non_negative=True)
"""Number of infirm children, T1 line 83 "Number of children you are claiming this amount for Line
30499": a starting count."""

INFIRM_CHILDREN_AMOUNT = CATALOG.declare("infirm_children_amount", Decimal, non_negative=True)
"""Canada caregiver amount for infirm children, T1 line 83 (line 30500) "Canada caregiver amount
for infirm children under 18 years of age (see Schedule 5) Number of children you are claiming
this amount for Line 30499" "multiplied by $2,687", a part of the total of the credit amounts on
the T1 alone (the ON428 caregiver amount, line 58185, is not triggered)."""
