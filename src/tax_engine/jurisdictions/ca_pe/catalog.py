"""The Prince Edward Island artifact catalog: Prince Edward Island's own kinds, named from the
Prince Edward Island forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_pe import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, PE428 line 9 "Line 9 and line 58040: Basic personal amount Claim
$14,650": the printed $14,650, claimed whole and not income-tested."""

PE428_AGE_AMOUNT_CLAIMED_LINE_10 = AmountKind.declare(
    CATALOG, "pe428_age_amount_claimed_line_10", non_negative=True
)
"""Age amount claimed, PE428 line 10 "Line 10 and line 58080: Age amount (if you were born in 1960
or earlier) (use Worksheet PE428) (maximum $6,510)": the amount as the filer gives it, an optional
input; a blank input is read as blank, and the line 10 step checks it against the printed
maximum."""

PE428_AGE_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "pe428_age_amount_maximum", non_negative=True
)
"""Age amount maximum, printed on PE428 line 10 "(maximum $6,510)": the printed maximum, from the
`ca-pe/age_amount_maximum` dataset; the bound line 10 cannot pass."""

PE428_AGE_AMOUNT_LINE_10 = AmountKind.declare(
    CATALOG, "pe428_age_amount_line_10", non_negative=True
)
"""Age amount, PE428 line 10 "Line 10 and line 58080: Age amount (if you were born in 1960 or
earlier) (use Worksheet PE428) (maximum $6,510)": the claimed amount, passed on unchanged when it
is at most the printed maximum, blank when left out; above the maximum it is refused, not capped."""

PE428_SPOUSE_OR_COMMON_LAW_PARTNER_AMOUNT_CLAIMED_LINE_13 = AmountKind.declare(
    CATALOG, "pe428_spouse_or_common_law_partner_amount_claimed_line_13", non_negative=True
)
"""Spouse or common-law partner amount claimed, PE428 line 13 "Line 13 and line 58120: Line 11
minus line 12 (if negative, enter "0") (maximum $12,443)": the amount as the filer gives it, an
optional input; a blank input is read as blank, and the line 13 step checks it against the printed
maximum."""

PE428_SPOUSE_OR_COMMON_LAW_PARTNER_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "pe428_spouse_or_common_law_partner_amount_maximum", non_negative=True
)
"""Spouse or common-law partner amount maximum, printed on PE428 line 13 "(maximum $12,443)": the
printed maximum, from the `ca-pe/spouse_or_common_law_partner_amount_maximum` dataset; the bound
line 13 cannot pass."""

PE428_SPOUSE_OR_COMMON_LAW_PARTNER_AMOUNT_LINE_13 = AmountKind.declare(
    CATALOG, "pe428_spouse_or_common_law_partner_amount_line_13", non_negative=True
)
"""Spouse or common-law partner amount, PE428 line 13 "Line 13 and line 58120: Line 11 minus line
12 (if negative, enter "0") (maximum $12,443)": the claimed amount, passed on unchanged when it is
at most the printed maximum, blank when left out; above the maximum it is refused, not capped."""

PE428_ELIGIBLE_DEPENDANT_AMOUNT_CLAIMED_LINE_16 = AmountKind.declare(
    CATALOG, "pe428_eligible_dependant_amount_claimed_line_16", non_negative=True
)
"""Amount for an eligible dependant claimed, PE428 line 16 "Line 16 and line 58160: Line 14 minus
line 15 (if negative, enter "0") (maximum $12,443)": the amount as the filer gives it, an optional
input; a blank input is read as blank, and the line 16 step checks it against the printed
maximum."""

PE428_ELIGIBLE_DEPENDANT_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "pe428_eligible_dependant_amount_maximum", non_negative=True
)
"""Amount for an eligible dependant maximum, printed on PE428 line 16 "(maximum $12,443)": the
printed maximum, from the `ca-pe/eligible_dependant_amount_maximum` dataset; the bound line 16
cannot pass."""

PE428_ELIGIBLE_DEPENDANT_AMOUNT_LINE_16 = AmountKind.declare(
    CATALOG, "pe428_eligible_dependant_amount_line_16", non_negative=True
)
"""Amount for an eligible dependant, PE428 line 16 "Line 16 and line 58160: Line 14 minus line 15
(if negative, enter "0") (maximum $12,443)": the claimed amount, passed on unchanged when it is at
most the printed maximum, blank when left out; above the maximum it is refused, not capped."""

PE428_INFIRM_DEPENDANTS_AMOUNT_LINE_17 = AmountKind.declare(
    CATALOG, "pe428_infirm_dependants_amount_line_17", non_negative=True
)
"""Amount for infirm dependants age 18 or older (use Worksheet PE428), PE428 line 17 "Line 17 and
line 58200: Amount for infirm dependants age 18 or older (use Worksheet PE428)": the amount as the
filer gives it, an optional input; a blank input is read as blank."""

PE428_YOUNG_CHILDREN_AMOUNT_LINE_18 = AmountKind.declare(
    CATALOG, "pe428_young_children_amount_line_18", non_negative=True
)
"""Amount for young children (complete the chart at the end of page 2), PE428 line 18 "Line 18 and
line 58230: Amount for young children (complete the chart at the end of page 2)": the amount as
the filer gives it, an optional input; a blank input is read as blank."""

PE428_CREDITS_SUBTOTAL_LINE_19 = AmountKind.declare(
    CATALOG, "pe428_credits_subtotal_line_19", non_negative=True
)
"""Prince Edward Island credits subtotal, PE428 line 19 "Line 19: Add lines 9, 10, 13, and 16 to
18. = ^": the sum of the personal amounts claimed, the basic personal amount plus the optional
lines 10, 13, 16, 17 and 18 read as 0 when blank."""

PE428_CPP_CONTRIBUTIONS_LINE_20 = AmountKind.declare(
    CATALOG, "pe428_cpp_contributions_line_20", non_negative=True
)
"""CPP or QPP contributions, PE428 line 20 and line 58240 "Amount from line 30800 of your return":
a copy of Schedule 8 line 25, the CPP base contributions on the return."""

PE428_QPP_CONTRIBUTIONS_LINE_21 = AmountKind.declare(
    CATALOG, "pe428_qpp_contributions_line_21", non_negative=True
)
"""Contributions on self-employment, PE428 line 21 and line 58280 "Amount from line 31000 of your
return": a record total of the T1's export
(`ca/self_employment_cpp_qpp_contributions_line_31000`), 0 for a salary-only caller."""

PE428_EI_PREMIUMS_LINE_22 = AmountKind.declare(
    CATALOG, "pe428_ei_premiums_line_22", non_negative=True
)
"""EI premiums credit amount, PE428 line 22 and line 58300 "Amount from line 31200 of your
return": a copy of T2204 line 16, the EI premiums credit amount."""

PE428_EI_PREMIUMS_LINE_23 = AmountKind.declare(
    CATALOG, "pe428_ei_premiums_line_23", non_negative=True
)
"""Employment insurance premiums, PE428 line 23 and line 58305 "Amount from line 31217 of your
return": a record total of the T1's export (`ca/ei_premiums_on_self_employment_line_31217`), 0 for
a salary-only caller."""

PE428_CPP_EI_AND_OTHER_LINE_24 = AmountKind.declare(
    CATALOG, "pe428_cpp_ei_and_other_line_24", non_negative=True
)
"""CPP or QPP and EI amounts, PE428 line 24 "Line 24: Add lines 20 to 23. = ^": the sum of the CPP
or QPP contributions, the self-employment contributions and the EI premiums on lines 20 to 23."""

PE428_CREDITS_SUBTOTAL_LINE_25 = AmountKind.declare(
    CATALOG, "pe428_credits_subtotal_line_25", non_negative=True
)
"""Prince Edward Island credits subtotal, PE428 line 25 "Line 25: Line 19 plus line 24 = ^": line
19 plus line 24, the amounts of the personal credits and of the CPP and EI credits; line 26 is a
copy of it."""

PE428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "pe428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form PE428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3, 4, 5 and 7."""

PE428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "pe428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, Form PE428 line 3 "Column 1: Line 1 is $33,328.00 or less / Line 3:
0.00" (33,328.00; 64,656.00; 105,000.00; 140,000.00): the printed lower bound of the column of
lines 2 to 8 that line 1 falls in."""

PE428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "pe428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, PE428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative)": line 1 minus line 3, not below zero."""

PE428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "pe428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, Form PE428 line 5 "Column 1: Line 1 is $33,328.00 or less / Line 5: Rate
9.5%" (13.47%; 16.6%; 17.62%; 19%): the printed rate of the column of lines 2 to 8 that line 1
falls in."""

PE428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "pe428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the excess, PE428 line 6 "Line 6: Line 4 multiplied by the percentage from line 5": line 4
times the rate of line 5, rounded to the cent."""

PE428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "pe428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column of lines 2 to 8 (the engine's description; the form prints no
title for line 7), Form PE428 line 7 "Column 1: Line 1 is $33,328.00 or less / Line 7: 0.00"
(3,166.16; 7,386.04; 14,083.15; 20,250.15): the figure printed on line 7 of the column that line 1
falls in."""

PE428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "pe428_tax_on_taxable_income_line_8", non_negative=True
)
"""Prince Edward Island tax on taxable income, PE428 line 8 "Line 8: Line 6 plus line 7 Prince
Edward Island tax on taxable income": line 6 plus line 7, copied to line 55 and read by the lines
after it."""

PE428_PENSION_INCOME_AMOUNT_CLAIMED_LINE_27 = AmountKind.declare(
    CATALOG, "pe428_pension_income_amount_claimed_line_27", non_negative=True
)
"""Pension income amount claimed, PE428 line 27 "Pension income amount (maximum $1,000)": the
amount as the filer gives it, an optional input; a blank input is read as blank, and the line 27
step checks it against the printed maximum."""

PE428_PENSION_INCOME_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "pe428_pension_income_amount_maximum", non_negative=True
)
"""Pension income amount maximum, printed on PE428 line 27 "Pension income amount (maximum
$1,000)": the printed maximum, from the `ca-pe/pension_income_amount_maximum` dataset; the bound
line 27 cannot pass."""

PE428_PENSION_INCOME_AMOUNT_LINE_27 = AmountKind.declare(
    CATALOG, "pe428_pension_income_amount_line_27", non_negative=True
)
"""Pension income amount, PE428 line 27 "Pension income amount (maximum $1,000)": the claimed
amount, passed on unchanged when it is at most the printed maximum, blank when left out; above
the maximum it is refused, not capped."""

PE428_CHILDRENS_WELLNESS_TAX_CREDIT_LINE_28 = AmountKind.declare(
    CATALOG, "pe428_childrens_wellness_tax_credit_line_28", non_negative=True
)
"""Children's wellness tax credit, PE428 line 28 "Line 28 and line 58365: Children's wellness tax
credit": the amount as the filer gives it, an optional input; a blank input is read as blank,
and the sum that reads it reads it as 0."""

PE428_CAREGIVER_AMOUNT_LINE_29 = AmountKind.declare(
    CATALOG, "pe428_caregiver_amount_line_29", non_negative=True
)
"""Caregiver amount (use Worksheet PE428), PE428 line 29 "Line 29 and line 58400: Caregiver amount
(use Worksheet PE428)": the amount as the filer gives it, an optional input; a blank input is
read as blank, and the sum that reads it reads it as 0."""

PE428_CREDITS_SUBTOTAL_LINE_30 = AmountKind.declare(
    CATALOG, "pe428_credits_subtotal_line_30", non_negative=True
)
"""Prince Edward Island credits subtotal, PE428 line 30 "Line 30: Add lines 26 to 29. = ^": line 26
(a copy of line 25) plus the pension income amount, the children's wellness tax credit and the
caregiver amount, the optional lines read as 0 when blank."""

PE428_DISABILITY_AMOUNT_SELF_LINE_31 = AmountKind.declare(
    CATALOG, "pe428_disability_amount_self_line_31", non_negative=True
)
"""Disability amount for self, PE428 line 31 "Line 31 and line 58440: Disability amount for self
(claim $6,890 or, if you were under 18 years of age, use Worksheet PE428)": the amount as the
filer gives it, an optional input; a blank input is read as blank, and the sum that reads it
reads it as 0."""

PE428_DISABILITY_AMOUNT_TRANSFERRED_FROM_A_DEPENDANT_LINE_32 = AmountKind.declare(
    CATALOG, "pe428_disability_amount_transferred_from_a_dependant_line_32", non_negative=True
)
"""Disability amount transferred from a dependant, PE428 line 32 "Line 32 and line 58480:
Disability amount transferred from a dependant (use Worksheet PE428)": the amount as the filer
gives it, an optional input; a blank input is read as blank, and the sum that reads it reads it
as 0."""

PE428_TEACHER_SCHOOL_SUPPLY_AMOUNT_CLAIMED_LINE_33 = AmountKind.declare(
    CATALOG, "pe428_teacher_school_supply_amount_claimed_line_33", non_negative=True
)
"""Teacher school supply amount claimed, PE428 line 33 "Teacher school supply amount (maximum
$500)": the amount as the filer gives it, an optional input; a blank input is read as blank, and
the line 33 step checks it against the printed maximum."""

PE428_TEACHER_SCHOOL_SUPPLY_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "pe428_teacher_school_supply_amount_maximum", non_negative=True
)
"""Teacher school supply amount maximum, printed on PE428 line 33 "Teacher school supply amount
(maximum $500)": the printed maximum, from the `ca-pe/teacher_school_supply_amount_maximum`
dataset; the bound line 33 cannot pass."""

PE428_TEACHER_SCHOOL_SUPPLY_AMOUNT_LINE_33 = AmountKind.declare(
    CATALOG, "pe428_teacher_school_supply_amount_line_33", non_negative=True
)
"""Teacher school supply amount, PE428 line 33 "Teacher school supply amount (maximum $500)": the
claimed amount, passed on unchanged when it is at most the printed maximum, blank when left out;
above the maximum it is refused, not capped."""

PE428_CREDITS_SUBTOTAL_LINE_34 = AmountKind.declare(
    CATALOG, "pe428_credits_subtotal_line_34", non_negative=True
)
"""Prince Edward Island credits subtotal, PE428 line 34 "Line 34: Add lines 30 to 33. = ^": line 30
plus the disability amount for self, the disability amount transferred from a dependant and the
teacher school supply amount, the optional lines read as 0 when blank."""

PE428_STUDENT_LOAN_INTEREST_LINE_35 = AmountKind.declare(
    CATALOG, "pe428_student_loan_interest_line_35", non_negative=True
)
"""Interest paid on your student loans, PE428 line 35 "Line 35 and line 58520: Interest paid on
your student loans (amount from line 31900 of your return)": a record total of the T1's export
(`ca/student_loan_interest_line_31900`), 0 for a salary-only caller."""

PE428_TUITION_AND_EDUCATION_AMOUNTS_LINE_36 = AmountKind.declare(
    CATALOG, "pe428_tuition_and_education_amounts_line_36", non_negative=True
)
"""Your tuition and education amounts, PE428 line 36 "Line 36 and line 58560: Your tuition and
education amounts (attach Schedule PE(S11))": the amount as the filer gives it, an optional
input; a blank input is read as blank, and the sum that reads it reads it as 0."""

PE428_TUITION_TRANSFERRED_FROM_CHILD_OR_GRANDCHILD_LINE_37 = AmountKind.declare(
    CATALOG, "pe428_tuition_transferred_from_child_or_grandchild_line_37", non_negative=True
)
"""Tuition and education amounts transferred from a child or grandchild, PE428 line 37 "Line 37 and
line 58600: Tuition and education amounts transferred from a child or grandchild": the amount as
the filer gives it, an optional input; a blank input is read as blank, and the sum that reads it
reads it as 0."""

PE428_AMOUNTS_TRANSFERRED_FROM_SPOUSE_OR_PARTNER_LINE_38 = AmountKind.declare(
    CATALOG, "pe428_amounts_transferred_from_spouse_or_partner_line_38", non_negative=True
)
"""Amounts transferred from your spouse or common-law partner, PE428 line 38 "Line 38 and line
58640: Amounts transferred from your spouse or common-law partner (attach Schedule PE(S2))": the
amount as the filer gives it, an optional input; a blank input is read as blank, and the sum
that reads it reads it as 0."""

PE428_CREDITS_SUBTOTAL_LINE_39 = AmountKind.declare(
    CATALOG, "pe428_credits_subtotal_line_39", non_negative=True
)
"""Prince Edward Island credits subtotal, PE428 line 39 "Line 39: Add lines 34 to 38. = ^": line 34
plus the student loan interest, the tuition and education amounts, the amounts transferred from
a child or grandchild and the amounts transferred from a spouse or common-law partner, the
optional lines read as 0 when blank."""

PE428_MEDICAL_EXPENSES_LINE_40 = AmountKind.declare(
    CATALOG, "pe428_medical_expenses_line_40", non_negative=True
)
"""Medical expenses, PE428 line 40 and line 58689 "Amount from line 33099 of your return": a record
total of the T1's export (`ca/medical_expenses_line_33099`), 0 for a salary-only caller."""

PE428_NET_INCOME_LINE_41 = AmountKind.declare(
    CATALOG, "pe428_net_income_line_41", non_negative=True
)
"""Net income, PE428 line 41 "Line 41: Amount from line 23600 of your return": a record total of
the T1's net income (line 23600, floored)."""

PE428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_43 = AmountKind.declare(
    CATALOG, "pe428_medical_expenses_rate_amount_line_43", non_negative=True
)
"""Medical expenses rate amount, PE428 line 43 "Line 43: Line 41 multiplied by the percentage from
line 42 = ^": line 41 times the 3% of line 42, rounded to the cent."""

PE428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_44 = AmountKind.declare(
    CATALOG, "pe428_medical_expenses_limited_amount_line_44", non_negative=True
)
"""Medical expenses limited amount, PE428 line 44 "Line 44: Enter whichever is less: $1,678 or the
amount on line 43.": the lesser of the printed $1,678 and line 43."""

PE428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_45 = AmountKind.declare(
    CATALOG, "pe428_medical_expenses_over_limit_line_45", non_negative=True
)
"""Medical expenses over the limit, PE428 line 45 "Line 45: Line 40 minus line 44 (if negative,
enter "0") = ^": line 40 less line 44, not below zero."""

PE428_ALLOWABLE_MEDICAL_EXPENSES_FOR_OTHER_DEPENDANTS_LINE_46 = AmountKind.declare(
    CATALOG, "pe428_allowable_medical_expenses_for_other_dependants_line_46", non_negative=True
)
"""Allowable amount of medical expenses for other dependants, PE428 line 46 "Line 46 and line
58729: Allowable amount of medical expenses for other dependants (use Worksheet PE428)": the
amount as the filer gives it, an optional input; a blank input is read as blank, and the sum
that reads it reads it as 0."""

PE428_MEDICAL_EXPENSES_ALLOWABLE_LINE_47 = AmountKind.declare(
    CATALOG, "pe428_medical_expenses_allowable_line_47", non_negative=True
)
"""Allowable medical expenses, PE428 line 47 "Line 47 and line 58769: Line 45 plus line 46 =": line
45 plus the allowable amount of medical expenses for other dependants, the optional line 46 read
as 0 when blank."""

PE428_CREDITS_TOTAL_LINE_48 = AmountKind.declare(
    CATALOG, "pe428_credits_total_line_48", non_negative=True
)
"""Credits total, PE428 line 48 and line 58800 "Line 48 and line 58800: Line 39 plus line 47 =":
the credits subtotal of line 39 plus the allowable medical expenses of line 47."""

PE428_CREDITS_AT_RATE_LINE_50 = AmountKind.declare(
    CATALOG, "pe428_credits_at_rate_line_50", non_negative=True
)
"""Credits at the credit rate, PE428 line 50 and line 58840 "Line 50 and line 58840: Line 48
multiplied by the percentage from line 49 =": line 48 times the 9.5% of line 49, rounded to the
cent."""

PE428_DONATIONS_AMOUNT_LINE_51 = AmountKind.declare(
    CATALOG, "pe428_donations_amount_line_51", non_negative=True
)
"""Federal Schedule 9 amount, PE428 line 51 box A "Line 51: Amount from line 13 of your federal
Schedule 9": a record total of the Schedule 9 export, 0 for a salary-only caller."""

PE428_DONATIONS_CREDIT_AT_RATE_LINE_51 = AmountKind.declare(
    CATALOG, "pe428_donations_credit_at_rate_line_51", non_negative=True
)
"""Donations credit at the printed rate, PE428 line 51 box B "Line 51: Amount from line 13 of your
federal Schedule 9 multiplied by 9.5% =": the Schedule 9 amount times 9.5%, rounded to the cent."""
