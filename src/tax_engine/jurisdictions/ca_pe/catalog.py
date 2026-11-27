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

PE428_DONATIONS_AMOUNT_LINE_52 = AmountKind.declare(
    CATALOG, "pe428_donations_amount_line_52", non_negative=True
)
"""Federal Schedule 9 amount, PE428 line 52 box A "Line 52: Amount from line 14 of your federal
Schedule 9": a record total of the Schedule 9 export, 0 for a salary-only caller."""

PE428_DONATIONS_CREDIT_AT_RATE_LINE_52 = AmountKind.declare(
    CATALOG, "pe428_donations_credit_at_rate_line_52", non_negative=True
)
"""Donations credit at the printed rate, PE428 line 52 box B "Line 52: Amount from line 14 of your
federal Schedule 9 multiplied by 19% =": the Schedule 9 amount times 19%, rounded to the cent."""

PE428_DONATIONS_AND_GIFTS_CREDIT_LINE_53 = AmountKind.declare(
    CATALOG, "pe428_donations_and_gifts_credit_line_53", non_negative=True
)
"""Donations and gifts credit, PE428 line 53 and line 58969 "Line 53 and line 58969: Line 51 plus
line 52 =": the donations credit at 9.5% plus the donations credit at 19%."""

PE428_NON_REFUNDABLE_CREDITS_LINE_54 = AmountKind.declare(
    CATALOG, "pe428_non_refundable_credits_line_54", non_negative=True
)
"""Prince Edward Island non-refundable tax credits, PE428 line 54 and line 61500 "Line 54 and line
61500: Line 50 plus line 53 Enter this amount on line 58. Prince Edward Island non-refundable
tax credits =": the credits at the credit rate plus the donations and gifts credit."""

PE428_ALLOWABLE_MEDICAL_EXPENSES_LINE_47 = AmountKind.declare(
    CATALOG, "pe428_allowable_medical_expenses_line_47", non_negative=True
)
"""Allowable medical expenses, PE428 line 47 and line 58769 "Line 47 and line 58769: Line 45 plus
line 46 =": the amount as the filer gives it, an optional input; a blank input is read as blank,
and the sum that reads it reads it as 0."""

PE428_TAX_ON_SPLIT_INCOME_LINE_56 = AmountKind.declare(
    CATALOG, "pe428_tax_on_split_income_line_56", non_negative=True
)
"""Prince Edward Island tax on split income, PE428 line 56 and line 61510 "Line 56 and line 61510:
Prince Edward Island tax on split income (complete Form T1206)": the amount as the filer gives it,
an optional input; a blank input is read as blank, and the sum that reads it reads it as 0."""

PE428_TAX_LINE_57 = AmountKind.declare(CATALOG, "pe428_tax_line_57", non_negative=True)
"""Prince Edward Island tax before credits, PE428 line 57 "Line 57: Line 55 plus line 56 =": the tax
on taxable income (line 55, a copy of line 8) plus the tax on split income."""

PE428_TAX_LINE_59 = AmountKind.declare(CATALOG, "pe428_tax_line_59", non_negative=True)
"""Prince Edward Island tax after the non-refundable credits, PE428 line 59 "Line 59: Line 57 minus
line 58 (if negative, enter "0") =": the tax before credits less the credits, not below 0."""

PE428_DIVIDEND_TAX_CREDIT_LINE_60 = AmountKind.declare(
    CATALOG, "pe428_dividend_tax_credit_line_60", non_negative=True
)
"""Prince Edward Island dividend tax credit, PE428 line 60 and line 61520 "Line 60 and line 61520:
Prince Edward Island dividend tax credit (use Worksheet PE428)": the amount as the filer gives it,
an optional input; a blank input is read as blank, and the sum that reads it reads it as 0."""

PE428_MINIMUM_TAX_CARRYOVER_LINE_61 = AmountKind.declare(
    CATALOG, "pe428_minimum_tax_carryover_line_61", non_negative=True
)
"""Prince Edward Island minimum tax carryover, PE428 line 61 and line 61540 "Line 61 and line 61540:
Amount from line 40427 of your return multiplied by 57.5% =": the amount as the filer gives it, an
optional input; a blank input is read as blank, and the sum that reads it reads it as 0."""

PE428_CREDITS_TOTAL_LINE_62 = AmountKind.declare(
    CATALOG, "pe428_credits_total_line_62", non_negative=True
)
"""Prince Edward Island dividend and minimum tax credits, PE428 line 62 "Line 62: Line 60 plus
line 61 =": the dividend tax credit plus the minimum tax carryover."""

PE428_TAX_LINE_63 = AmountKind.declare(CATALOG, "pe428_tax_line_63", non_negative=True)
"""Prince Edward Island tax after the dividend and minimum tax credits, PE428 line 63 "Line 63: Line
59 minus line 62 (if negative, enter "0") =": line 59 less line 62, not below 0."""

PE428_ADDITIONAL_TAX_MINIMUM_TAX_LINE_64 = AmountKind.declare(
    CATALOG, "pe428_additional_tax_minimum_tax_line_64", non_negative=True
)
"""Prince Edward Island additional tax for minimum tax purposes, PE428 line 64 "Line 64: Amount from
Line 14 of Part 7 of Form T691 multiplied by 57.5% =": the amount as the filer gives it, an
optional input; a blank input is read as blank, and the sum that reads it reads it as 0."""

PE428_TAX_WITH_MINIMUM_TAX_LINE_65 = AmountKind.declare(
    CATALOG, "pe428_tax_with_minimum_tax_line_65", non_negative=True
)
"""Prince Edward Island tax with the additional minimum tax, PE428 line 65 "Line 65: Line 63 plus
line 64 =": line 63 plus the additional tax for minimum tax purposes."""

PE428_AMOUNT_FROM_SPOUSE_OR_PARTNER_FORM_LINE_66 = AmountKind.declare(
    CATALOG, "pe428_amount_from_spouse_or_partner_form_line_66", non_negative=True
)
"""Spouse or partner Form PE428 amount, PE428 line 66 and line 63360 "Line 66 and line 63360: Amount
from line 101 of your spouse's or common-law partner's Form PE428, if any": the amount as the
filer gives it, an optional input; a blank input is read as blank, and the subtraction that reads
it reads it as 0."""

PE428_TAX_LINE_67 = AmountKind.declare(CATALOG, "pe428_tax_line_67", non_negative=True)
"""Prince Edward Island tax after credits, PE428 line 67 "Line 67: Line 65 minus line 66 (if
negative, enter "0") Enter this amount on line 74. =": line 65 less the amount from the spouse or
common-law partner's form, not below 0."""

PE428_NET_INCOME_LINE_68 = AmountKind.declare(
    CATALOG, "pe428_net_income_line_68", non_negative=False
)
"""Net income, PE428 line 68 column 1 "Line 68: Net income from line 23600 of the return (or the
amount you would have entered if the instructions on line 23600 said "if negative, show in
brackets")": the net income of the T1 return before its floor, read from the signed T1 net income
export (`ca/net_income_signed`). The form shows a negative net income in brackets, so the kind is
signed."""

PE428_UCCB_REPAYMENT_LINE_69 = AmountKind.declare(
    CATALOG, "pe428_uccb_repayment_line_69", non_negative=True
)
"""UCCB repayment, PE428 line 69 column 1 "Line 69: Amount from line 21300 of the return": the T1's
line, read as the T1 form's export."""

PE428_FAMILY_INCOME_LINE_70 = AmountKind.declare(
    CATALOG, "pe428_family_income_line_70", non_negative=False
)
"""Line 68 plus line 69, PE428 line 70 "Line 68 plus line 69", column 1 (you): the net income of
line 68 plus the UCCB repayment of line 69. Line 68 can be negative, so the kind is signed."""

PE428_UCCB_INCOME_LINE_71 = AmountKind.declare(
    CATALOG, "pe428_uccb_income_line_71", non_negative=True
)
"""UCCB income, PE428 line 71 column 1 "Line 71: Amount from line 11700 of the return": the T1's
line, read as the T1 form's export."""

PE428_ADJUSTED_FAMILY_INCOME_LINE_72 = AmountKind.declare(
    CATALOG, "pe428_adjusted_family_income_line_72", non_negative=True
)
"""Line 70 minus line 71, PE428 line 72 "Line 70 minus line 71 (if negative, enter "0")", column 1
(you): the family income of line 70 less the UCCB income of line 71, not below 0. Line 73 ("Adjusted
family income") adds the two columns, and column 2 is not modelled, so this is the adjusted family
income."""

LOW_INCOME_REDUCTION_BASIC = AmountKind.declare(
    CATALOG, "low_income_reduction_basic", non_negative=True
)
"""Basic reduction, PE428 line 75 "Line 75 and line 63370: Basic reduction Claim $350": the printed
$350, claimed whole and not income-tested."""

PE428_AGE_REDUCTION_FOR_SELF_LINE_76 = AmountKind.declare(
    CATALOG, "pe428_age_reduction_for_self_line_76", non_negative=True
)
"""Age reduction for self, PE428 line 76 and line 63380 "Age reduction for self (if you were born in
1960 or earlier) Claim $250": the amount as the filer gives it, an optional input; a blank input is
read as blank, and the sum that reads it reads it as 0."""

PE428_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_LINE_77 = AmountKind.declare(
    CATALOG, "pe428_reduction_for_spouse_or_common_law_partner_line_77", non_negative=True
)
"""Reduction for spouse or common-law partner, PE428 line 77 and line 63390 "Reduction for spouse or
common-law partner (if you had a spouse or common-law partner on December 31, 2025) Claim $350": the
amount as the filer gives it, an optional input; a blank input is read as blank, and the sum that
reads it reads it as 0."""

PE428_AGE_REDUCTION_FOR_SPOUSE_OR_COMMON_LAW_PARTNER_LINE_78 = AmountKind.declare(
    CATALOG, "pe428_age_reduction_for_spouse_or_common_law_partner_line_78", non_negative=True
)
"""Age reduction for spouse or common-law partner, PE428 line 78 and line 63400 "Age reduction for
spouse or common-law partner (if they were born in 1960 or earlier) Claim $250": the amount as the
filer gives it, an optional input; a blank input is read as blank, and the sum that reads it reads
it as 0."""

PE428_REDUCTION_FOR_ELIGIBLE_DEPENDANT_LINE_79 = AmountKind.declare(
    CATALOG, "pe428_reduction_for_eligible_dependant_line_79", non_negative=True
)
"""Reduction for an eligible dependant, PE428 line 79 and line 63410 "Reduction for an eligible
dependant claimed on line 58160 Claim $350": the amount as the filer gives it, an optional input; a
blank input is read as blank, and the sum that reads it reads it as 0."""

PE428_REDUCTION_FOR_DEPENDENT_CHILDREN_LINE_80 = AmountKind.declare(
    CATALOG, "pe428_reduction_for_dependent_children_line_80", non_negative=True
)
"""Reduction for dependent children born in 2007 or later, PE428 line 80 "Number of dependent
children (do not include a child on line 63410) Line 60999 multiplied by $300 =": the amount as the
filer gives it, an optional input; a blank input is read as blank, and the sum that reads it reads
it as 0."""

PE428_LOW_INCOME_REDUCTIONS_TOTAL_LINE_81 = AmountKind.declare(
    CATALOG, "pe428_low_income_reductions_total_line_81", non_negative=True
)
"""Reductions added, PE428 line 81 "Line 81: Add lines 75 to 80 =": the basic reduction and the
claims of lines 76 to 80 added."""

LOW_INCOME_REDUCTION_BASE_AMOUNT = AmountKind.declare(
    CATALOG, "low_income_reduction_base_amount", non_negative=True
)
"""Base amount, PE428 line 83 "Line 83: Base amount 22,650.00": the printed $22,650.00, the family
income above which the reduction fades."""

PE428_INCOME_OVER_BASE_AMOUNT_LINE_84 = AmountKind.declare(
    CATALOG, "pe428_income_over_base_amount_line_84", non_negative=True
)
"""PE428 line 84 "Line 84: Line 82 minus line 83 (if negative, enter "0") =": the adjusted family
income (line 82, a copy of line 73) less the base amount of line 83, not below 0, rounded half-up
to the cent."""

PE428_REDUCTION_PHASE_OUT_LINE_86 = AmountKind.declare(
    CATALOG, "pe428_reduction_phase_out_line_86", non_negative=True
)
"""PE428 line 86 "Line 86: Line 84 multiplied by the percentage from line 85 =": line 84 times the
printed line 85 rate of 5%, rounded half-up to the cent."""

PE428_LOW_INCOME_TAX_REDUCTION_LINE_87 = AmountKind.declare(
    CATALOG, "pe428_low_income_tax_reduction_line_87", non_negative=True
)
"""Prince Edward Island low-income tax reduction, PE428 line 87 "Line 87: Line 81 minus line 86 (if
negative, enter "0") Prince Edward Island low-income tax reduction =": line 81 less line 86, not
below 0, rounded half-up to the cent."""

PE428_TAX_LINE_88 = AmountKind.declare(CATALOG, "pe428_tax_line_88", non_negative=True)
"""PE428 line 88 "Line 88: Line 74 minus line 87 (if negative, enter "0") =": line 74 (a copy of
line 67, the tax after credits) less the low-income tax reduction of line 87, not below 0, rounded
half-up to the cent."""

PE428_LOW_INCOME_TAX_REDUCTION_BEFORE_LINE_66_CHECK = AmountKind.declare(
    CATALOG, "pe428_low_income_tax_reduction_before_line_66_check", non_negative=True
)
"""Line 81 less line 86, not below 0, rounded half-up to the cent: the low-income tax reduction
before the instruction under line 67 ("If you are claiming an amount on line 66, enter "0" on line
87") is applied. Not printed on the form."""

PE428_AMOUNT_FROM_SPOUSE_FORM_CLAIMED_LINE_66 = AmountKind.declare(
    CATALOG, "pe428_amount_from_spouse_form_claimed_line_66", non_negative=True
)
"""The amount claimed on PE428 line 66, a blank line 66 read as 0.00, so the line 66 gate can read
it. Not printed on the form."""

PE428_LINE_87_LINE_66_GATE = AmountKind.declare(
    CATALOG, "pe428_line_87_line_66_gate", non_negative=True
)
"""The line 66 gate of PE428 line 87: 1 where line 66 is 0.00 and 0 where an amount is claimed on
line 66. A switch, not printed on the form."""

PE428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_89 = AmountKind.declare(
    CATALOG, "pe428_provincial_foreign_tax_credit_line_89", non_negative=True
)
"""Provincial foreign tax credit, PE428 line 89 "Provincial foreign tax credit (complete Form
T2036)": the amount as the filer gives it, an optional input; a blank input is read as blank, and
the step that reads it reads it as 0."""

PE428_TAX_LINE_90 = AmountKind.declare(CATALOG, "pe428_tax_line_90", non_negative=True)
"""PE428 line 90 "Line 90: Line 88 minus line 89 (if negative, enter "0") =": line 88 less the
provincial foreign tax credit of line 89, not below 0, rounded half-up to the cent."""

PE428_POLITICAL_CONTRIBUTION_TAX_CREDIT_CLAIMED_LINE_92 = AmountKind.declare(
    CATALOG, "pe428_political_contribution_tax_credit_claimed_line_92", non_negative=True
)
"""The political contribution tax credit of PE428 line 92 as the filer gives it, an optional input
(the worksheet is not built); a blank input is read as blank, and line 92 checks it against the
printed maximum. Not printed as a separate line."""

PE428_POLITICAL_CONTRIBUTION_TAX_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "pe428_political_contribution_tax_credit_maximum", non_negative=True
)
"""The printed maximum of PE428 line 92 ($500), from the
`ca-pe/political_contribution_tax_credit_maximum` dataset; the bound line 92 checks against. Not
printed as a separate line."""

PE428_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_92 = AmountKind.declare(
    CATALOG, "pe428_political_contribution_tax_credit_line_92", non_negative=True
)
"""Prince Edward Island political contribution tax credit, PE428 line 92 "(use Worksheet PE428)
(maximum $500)": the credit as the filer gives it, an optional input (the worksheet is not built);
a blank input is read as blank, and the step that reads it reads it as 0."""

PE428_TAX_LINE_93 = AmountKind.declare(CATALOG, "pe428_tax_line_93", non_negative=True)
"""PE428 line 93 "Line 93: Line 90 minus line 92 (if negative, enter "0") =": line 90 less the
political contribution tax credit of line 92, not below 0, rounded half-up to the cent."""

PE428_EQUITY_TAX_CREDIT_LINE_94 = AmountKind.declare(
    CATALOG, "pe428_equity_tax_credit_line_94", non_negative=True
)
"""Equity tax credit from Certificate PE-ETC, PE428 line 94 and line 63500: the amount as the
filer gives it, an optional input; a blank input is read as blank, and the sum that reads it
reads it as 0."""

PE428_UNUSED_EQUITY_TAX_CREDIT_LINE_95 = AmountKind.declare(
    CATALOG, "pe428_unused_equity_tax_credit_line_95", non_negative=True
)
"""Unused Prince Edward Island equity tax credit from the most recent notice of assessment or
reassessment, PE428 line 95: the amount as the filer gives it, an optional input; a blank input is
read as blank, and the sum that reads it reads it as 0."""

PE428_EQUITY_TAX_CREDIT_BEFORE_MAXIMUM_LINE_96 = AmountKind.declare(
    CATALOG, "pe428_equity_tax_credit_before_maximum_line_96", non_negative=True
)
"""Line 94 plus line 95, before the printed maximum of line 96 is applied, rounded half-up to the
cent. Not printed on the form."""

PE428_EQUITY_TAX_CREDIT_LINE_96 = AmountKind.declare(
    CATALOG, "pe428_equity_tax_credit_line_96", non_negative=True
)
"""PE428 line 96 "Line 94 plus line 95 (maximum $7,000) =": the sum of lines 94 and 95, at most the
printed maximum of $7,000."""

PE428_PRINCE_EDWARD_ISLAND_TAX_LINE_97 = AmountKind.declare(
    CATALOG, "pe428_prince_edward_island_tax_line_97", non_negative=True
)
"""Prince Edward Island tax, PE428 line 97 "Line 93 minus line 96 (if negative, enter "0") Enter
this amount on line 42800 of your return. Prince Edward Island tax =": line 93 less the equity tax
credit of line 96, not below 0, rounded half-up to the cent."""

AVERAGE_TAX_RATE = AmountKind.declare(CATALOG, "average_tax_rate", non_negative=True)
"""Average tax rate on the take-home basis, the Prince Edward Island return
summary's own figure
(no form prints it): the income tax, CPP (Schedule 8 lines 25 and 28), EI (T2204 line 16) together
divided by the salary (`ca/return_employment_income`), as a fraction, so 0.1598 is 15.98%. Paid
credits are not in it. It is 0 when the salary is 0."""

PRINCE_EDWARD_ISLAND_BRACKET_RATE_RETURN = AmountKind.declare(
    CATALOG, "prince_edward_island_bracket_rate_return", non_negative=True
)
"""Prince Edward Island bracket rate, PE428 line 5 "Line 5: Rate": the printed rate of the column of
the five that line 1 falls in, read from PE428 into the return summary. Not printed on the form
as its own figure."""

MARGINAL_NET_INCOME_RATE = AmountKind.declare(
    CATALOG, "marginal_net_income_rate", non_negative=True
)
"""Part of a further dollar of salary left in the net income (T1 line 23600) and the taxable
income: 1 less the CPP first additional rate and the CPP second additional rate, which T1 line
22215 takes off the income. The federal form's export
`ca/take_home_marginal_rates.marginal_net_income_rate`, totalled into the return summary's own
artifact. Not printed on the form."""

MARGINAL_CREDIT_CONTRIBUTION_RATE = AmountKind.declare(
    CATALOG, "marginal_credit_contribution_rate", non_negative=True
)
"""Credit-earning contribution rate on a further dollar of salary: the CPP base rate (T1 line
30800) plus the EI rate (T1 line 31200). The federal form's export
`ca/take_home_marginal_rates.marginal_credit_contribution_rate`, totalled into the return
summary's own artifact. Not printed on the form."""

MARGINAL_FEDERAL_RATE = AmountKind.declare(CATALOG, "marginal_federal_rate", non_negative=True)
"""Federal marginal rate on the take-home basis: the federal rate on a further dollar of salary
after the credits, where the basic federal tax (T1 line 42900) is above zero, and 0 where it is
not. The federal form's export `ca/take_home_marginal_rates.marginal_federal_rate`, totalled into
the return summary's own artifact. Not printed on the form."""

MARGINAL_CONTRIBUTION_RATE = AmountKind.declare(
    CATALOG, "marginal_contribution_rate", non_negative=True
)
"""Contribution rate on a further dollar of salary: the CPP base, first additional and second
additional rates plus the EI rate (T2204 line 16). The federal form's export
`ca/take_home_marginal_rates.marginal_contribution_rate`, totalled into the return summary's own
artifact. Not printed on the form."""

MARGINAL_PRINCE_EDWARD_ISLAND_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_prince_edward_island_credit_rate", non_negative=True
)
"""The PE428 credit rate (the printed "Prince Edward Island non-refundable tax credit rate"): the
`ca-pe/credit_rate` dataset as it is, with none of the cent rounding the credit box applies. A
rate, not printed as its own figure."""

MARGINAL_PRINCE_EDWARD_ISLAND_CONTRIBUTION_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_prince_edward_island_contribution_credit_rate", non_negative=True
)
"""Prince Edward Island credit rate on the CPP base and EI of a further dollar of salary: the
credit-earning contribution rate times the credit rate, the provincial tax the contributions take
off. An exact product, not printed on the form."""

MARGINAL_PRINCE_EDWARD_ISLAND_BRACKET_RATE = AmountKind.declare(
    CATALOG, "marginal_prince_edward_island_bracket_rate", non_negative=True
)
"""Prince Edward Island bracket rate on a further dollar of salary: the bracket rate of PE428
line 5 times the part left in the net income. An exact product, not printed on the
form."""

MARGINAL_PRINCE_EDWARD_ISLAND_RATE_AFTER_CREDITS = AmountKind.declare(
    CATALOG, "marginal_prince_edward_island_rate_after_credits", non_negative=True
)
"""Prince Edward Island rate on a further dollar of salary after the CPP base and EI credits,
before the low-income tax reduction. An exact difference, not printed on the form."""

INCOME_OVER_BASE_AMOUNT_RETURN = AmountKind.declare(
    CATALOG, "income_over_base_amount_return", non_negative=True
)
"""PE428 line 84 "Line 82 minus line 83 (if negative, enter "0")", the income over the base
amount, read into the return summary. The base of the line 84 gate."""

LOW_INCOME_TAX_REDUCTION_RETURN = AmountKind.declare(
    CATALOG, "low_income_tax_reduction_return", non_negative=True
)
"""PE428 line 87, the Prince Edward Island low-income tax reduction, read into the return
summary. The base of the line 87 gate."""

INCOME_OVER_BASE_AMOUNT_GATE = AmountKind.declare(
    CATALOG, "income_over_base_amount_gate", non_negative=True
)
"""0 where PE428 line 84 is 0.00 and 1 where it is at least one cent, from the
`ca-pe/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

LOW_INCOME_TAX_REDUCTION_GATE = AmountKind.declare(
    CATALOG, "low_income_tax_reduction_gate", non_negative=True
)
"""0 where PE428 line 87 is 0.00 and 1 where it is at least one cent, from the
`ca-pe/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

LOW_INCOME_REDUCTION_PHASE_OUT_GATE = AmountKind.declare(
    CATALOG, "low_income_reduction_phase_out_gate", non_negative=True
)
"""1 while the low-income tax reduction is being phased out (PE428 lines 84 and 87 both above
zero), otherwise 0. The product of the two gates, not printed on the form."""

LOW_INCOME_REDUCTION_RATE_FIGURE = AmountKind.declare(
    CATALOG, "low_income_reduction_rate_figure", non_negative=True
)
"""PE428 line 85 "Applicable rate 5%": the `ca-pe/low_income_reduction_rate` dataset as it is. A
rate, not printed as its own figure."""

MARGINAL_LOW_INCOME_REDUCTION_RATE = AmountKind.declare(
    CATALOG, "marginal_low_income_reduction_rate", non_negative=True
)
"""Rate at which a further dollar of net income takes off the low-income tax reduction (PE428
line 85 and line 86): 5% while the reduction is being phased out, 0 elsewhere. Not printed on
the form."""

MARGINAL_LOW_INCOME_PHASE_OUT_RATE = AmountKind.declare(
    CATALOG, "marginal_low_income_phase_out_rate", non_negative=True
)
"""The low-income reduction rate on a further dollar of salary: the reduction rate times the part
left in the net income. An exact product, not printed on the form."""

MARGINAL_PRINCE_EDWARD_ISLAND_RATE_WITH_REDUCTION = AmountKind.declare(
    CATALOG, "marginal_prince_edward_island_rate_with_reduction", non_negative=True
)
"""Prince Edward Island rate on a further dollar of salary after the credits plus the
low-income reduction phase-out, before the line 97 gate. An exact sum, not printed on the form."""

PRINCE_EDWARD_ISLAND_TAX_RETURN = AmountKind.declare(
    CATALOG, "prince_edward_island_tax_return", non_negative=True
)
"""PE428 line 97 "Line 93 minus line 96 (if negative, enter "0")", the tax that goes to T1 line
42800, read into the return summary. The base of the Prince Edward Island rate gate."""

PRINCE_EDWARD_ISLAND_RATE_GATE = AmountKind.declare(
    CATALOG, "prince_edward_island_rate_gate", non_negative=True
)
"""Prince Edward Island rate gate: 0 where the Prince Edward Island tax (PE428 line
97) is 0.00 and 1 where it is at least one cent, from the
`ca-pe/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

PRINCE_EDWARD_ISLAND_MARGINAL_RATE = AmountKind.declare(
    CATALOG, "prince_edward_island_marginal_rate", non_negative=True
)
"""Prince Edward Island marginal rate on the take-home basis: the bracket rate after the CPP
base and EI credits, plus the low-income tax reduction phase-out, counted where the Prince Edward
Island tax (PE428 line 97) is above zero and 0 where it is not. Not printed on the form."""

MARGINAL_TAX_RATE = AmountKind.declare(CATALOG, "marginal_tax_rate", non_negative=True)
"""Marginal tax rate on the take-home basis: the change in income tax, CPP, CPP2 and EI on a further
dollar of salary, with no credit paid on filing: the sum of the federal marginal rate, the
Prince Edward Island marginal rate (which has no surtax or health premium) and the
contribution rate, on the return summary. Not printed on the form."""
