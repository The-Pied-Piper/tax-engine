"""The Nova Scotia artifact catalog: Nova Scotia's own kinds, named
from the Nova Scotia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ns import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

NS428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "ns428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form NS428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3 and 4."""

NS428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "ns428_tax_on_taxable_income_line_8", non_negative=True
)
"""Nova Scotia tax on taxable income, NS428 line 8 "Line 6 plus line 7 Nova Scotia tax on taxable
income =": line 6 plus line 7, copied to line 53 and read by the tax after credits."""

NS428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "ns428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, Form NS428 line 3 "Column 1: Line 1 is $30,507 or less / Line 3: 0.00"
(30,507.00; 61,015.00; 95,883.00; 154,650.00): the printed lower bound of the column of lines 2 to
8 that line 1 falls in."""

NS428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "ns428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, NS428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero."""

NS428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "ns428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, Form NS428 line 5 "Column 1: Line 1 is $30,507 or less / Line 5: Rate 8.79%"
(14.95%; 16.67%; 17.5%; 21%): the printed rate of the column of lines 2 to 8 that line 1 falls
in."""

NS428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "ns428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the excess, NS428 line 6 "Line 6: Line 4 multiplied by the percentage from line 5 =":
line 4 times the rate of line 5, rounded to the cent."""

NS428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "ns428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column of lines 2 to 8 (the engine's description; the form prints no
title for line 7), Form NS428 line 7 "Column 1: Line 1 is $30,507 or less / Line 7: 0.00"
(2,681.57; 7,242.51; 13,055.01; 23,339.23): the figure printed on line 7 of the column that line 1
falls in."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, NS428 line 9 "Line 9 and line 58040: Basic personal amount Claim
$11,744": the printed $11,744, claimed whole and not income-tested."""

NS428_CREDITS_SUBTOTAL_LINE_19 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_19", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 19 "Add lines 9 to 18.": the sum of the personal amounts
claimed, here the basic personal amount alone."""

NS428_CPP_CONTRIBUTIONS_LINE_21 = AmountKind.declare(
    CATALOG, "ns428_cpp_contributions_line_21", non_negative=True
)
"""CPP or QPP contributions, NS428 line 21 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

NS428_QPP_CONTRIBUTIONS_LINE_22 = AmountKind.declare(
    CATALOG, "ns428_qpp_contributions_line_22", non_negative=True
)
"""Quebec Pension Plan contributions, NS428 line 22 "Amount from line 31000 of your return": a
record total of the T1's export (`ca/self_employment_cpp_qpp_contributions_line_31000`), 0 for a
salary-only caller."""

NS428_EI_PREMIUMS_LINE_23 = AmountKind.declare(
    CATALOG, "ns428_ei_premiums_line_23", non_negative=True
)
"""EI premiums credit amount, NS428 line 23 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

NS428_EI_PREMIUMS_LINE_24 = AmountKind.declare(
    CATALOG, "ns428_ei_premiums_line_24", non_negative=True
)
"""Employment insurance premiums, NS428 line 24 "Amount from line 31217 of your return": a record
total of the T1's export (`ca/ei_premiums_on_self_employment_line_31217`), 0 for a salary-only
caller."""

NS428_CPP_EI_AND_OTHER_LINE_25 = AmountKind.declare(
    CATALOG, "ns428_cpp_ei_and_other_line_25", non_negative=True
)
"""CPP or QPP, EI and other credit amounts, NS428 line 25 "Add lines 21 to 24.": the sum of the CPP
or QPP contributions, the QPP contributions and the EI premiums on lines 21 to 24."""

NS428_CREDITS_SUBTOTAL_LINE_26 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_26", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 26 "Line 20 plus line 25": line 20, a copy of line 19,
plus line 25, read by the next line of the credits."""

NS428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "ns428_pension_income_amount", non_negative=True
)
"""Pension income amount, NS428 line 27 "Line 27 and line 58360: Pension income amount (maximum
$1,173)": the amount the filer claims, a caller input that is read as 0 when it is left out; the
line 27 step checks it against the printed maximum."""

NS428_PENSION_INCOME_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "ns428_pension_income_amount_maximum", non_negative=True
)
"""Pension income amount maximum, printed on NS428 line 27 "(maximum $1,173)": the printed maximum,
from the `ca-ns/pension_income_amount_maximum` dataset; the bound line 27 cannot pass."""

NS428_PENSION_INCOME_AMOUNT_CHECKED_LINE_27 = AmountKind.declare(
    CATALOG, "ns428_pension_income_amount_checked_line_27", non_negative=True
)
"""Pension income amount, NS428 line 27 "Line 27 and line 58360: Pension income amount (maximum
$1,173)": the entered amount, passed on unchanged when it is at most the printed maximum, read as 0
when left out; above the maximum it is refused, not capped."""

NS428_CREDITS_SUBTOTAL_LINE_29 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_29", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 29 "Add lines 26 to 28.": line 26 plus the checked
pension income amount of line 27, line 28 (the caregiver amount) not being built."""

NS428_CREDITS_SUBTOTAL_LINE_32 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_32", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 32 "Add lines 29 to 31.": line 29, lines 30 and 31 (the
disability amounts) not being built."""

NS428_STUDENT_LOAN_INTEREST_LINE_33 = AmountKind.declare(
    CATALOG, "ns428_student_loan_interest_line_33", non_negative=True
)
"""Interest paid on student loans, NS428 line 33 (line 58520) "Interest paid on your student loans
(amount from line 31900 of your return)": a record total of the T1's export
(`ca/student_loan_interest_line_31900`), 0 for a salary-only caller."""

NS428_CREDITS_SUBTOTAL_LINE_37 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_37", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 37 "Add lines 32 to 36.": line 32 plus line 33, lines 34
to 36 (tuition and transfers) not being built."""

NS428_MEDICAL_EXPENSES_LINE_38 = AmountKind.declare(
    CATALOG, "ns428_medical_expenses_line_38", non_negative=True
)
"""Medical expenses, NS428 line 38 (line 58689) "Amount from line 33099 of your return": a record
total of the T1's export (`ca/medical_expenses_line_33099`), 0 for a salary-only caller."""

NS428_NET_INCOME_LINE_39 = AmountKind.declare(
    CATALOG, "ns428_net_income_line_39", non_negative=True
)
"""Net income, NS428 line 39 "Amount from line 23600 of your return": a record total of the T1's
net income, line 23600 as the T1 floors it."""

NS428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_41 = AmountKind.declare(
    CATALOG, "ns428_medical_expenses_rate_amount_line_41", non_negative=True
)
"""Medical expenses threshold, NS428 line 41 "Line 39 multiplied by the percentage from line 40 =":
line 39 times the 3% of line 40."""

NS428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_42 = AmountKind.declare(
    CATALOG, "ns428_medical_expenses_limited_amount_line_42", non_negative=True
)
"""Medical expenses threshold, limited, NS428 line 42 "Enter whichever is less: $1,637 or the amount
on line 41.": the lesser of the printed ceiling and line 41."""

NS428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_43 = AmountKind.declare(
    CATALOG, "ns428_medical_expenses_over_limit_line_43", non_negative=True
)
"""Medical expenses over the limit, NS428 line 43 "Line 38 minus line 42 (if negative, enter "0")
=": line 38 minus line 42, never below 0; a blank line 38 is read as 0."""

NS428_MEDICAL_EXPENSES_LINE_45 = AmountKind.declare(
    CATALOG, "ns428_medical_expenses_line_45", non_negative=True
)
"""Medical expenses, NS428 line 45 (line 58769) "Line 43 plus line 44 =": line 43, line 44 (the
allowable amount for other dependants) not being built."""

NS428_CREDITS_TOTAL_LINE_46 = AmountKind.declare(
    CATALOG, "ns428_credits_total_line_46", non_negative=True
)
"""Nova Scotia credits total, NS428 line 46 (line 58800) "Line 37 plus line 45 =": the credits
subtotal of line 37 plus the medical expense amount of line 45."""

NS428_CREDITS_AT_RATE_LINE_48 = AmountKind.declare(
    CATALOG, "ns428_credits_at_rate_line_48", non_negative=True
)
"""Nova Scotia credits at the credit rate, NS428 line 48 (line 58840) "Line 46 multiplied by the
percentage from line 47 =": line 46 multiplied by the 8.79% of line 47, rounded half-up to the
cent."""

NS428_DONATIONS_AMOUNT_LINE_49 = AmountKind.declare(
    CATALOG, "ns428_donations_amount_line_49", non_negative=True
)
"""Donations amount, NS428 line 49 box A "Amount from line 13 of your federal Schedule 9": the
amount, a record total of Schedule 9's export (`ca/schedule_9.donations_and_gifts_line_13`), 0 for a
salary-only caller."""

NS428_DONATIONS_CREDIT_AT_RATE_LINE_49 = AmountKind.declare(
    CATALOG, "ns428_donations_credit_at_rate_line_49", non_negative=True
)
"""Donations credit at 8.79%, NS428 line 49 box B "Amount from line 13 of your federal Schedule 9
multiplied by 8.79% =": the Schedule 9 amount times 8.79%; a blank amount is read as 0."""

NS428_DONATIONS_AMOUNT_LINE_50 = AmountKind.declare(
    CATALOG, "ns428_donations_amount_line_50", non_negative=True
)
"""Donations amount, NS428 line 50 box A "Amount from line 14 of your federal Schedule 9": the
amount, a record total of Schedule 9's export (`ca/schedule_9.donations_and_gifts_line_14`), 0 for a
salary-only caller."""

NS428_DONATIONS_CREDIT_AT_RATE_LINE_50 = AmountKind.declare(
    CATALOG, "ns428_donations_credit_at_rate_line_50", non_negative=True
)
"""Donations credit at 21%, NS428 line 50 box B "Amount from line 14 of your federal Schedule 9
multiplied by 21% =": the Schedule 9 amount times 21%; a blank amount is read as 0."""

NS428_DONATIONS_CREDIT_LINE_51 = AmountKind.declare(
    CATALOG, "ns428_donations_credit_line_51", non_negative=True
)
"""Donations and gifts credit, NS428 line 51 (58969) "Line 51 and 58969: Line 49 plus line 50 =":
line 49 plus line 50; line 52 reads it."""

NS428_NON_REFUNDABLE_CREDITS_LINE_52 = AmountKind.declare(
    CATALOG, "ns428_non_refundable_credits_line_52", non_negative=True
)
"""Nova Scotia non-refundable tax credits, NS428 line 52 (line 61500) "Line 48 plus line 51 Enter
this amount on line 56. Nova Scotia non-refundable tax credits =" (as CRA's PDF prints it; its text
version misprints the line): line 48 plus line 51, read by line 56."""

NS428_TAX_ON_SPLIT_INCOME_LINE_54 = AmountKind.declare(
    CATALOG, "ns428_tax_on_split_income_line_54", non_negative=True
)
"""Nova Scotia tax on split income, NS428 line 54 and line 61510 "Nova Scotia tax on split income
(complete Form T1206)": an optional input that a salary-only caller leaves out, read as blank."""

NS428_TAX_LINE_55 = AmountKind.declare(CATALOG, "ns428_tax_line_55", non_negative=True)
"""Nova Scotia tax, NS428 line 55 "Line 53 plus line 54": the tax on taxable income (line 53, a copy
of line 8) plus the tax on split income, a blank line 54 read as 0."""

NS428_DIVIDEND_TAX_CREDIT_LINE_57 = AmountKind.declare(
    CATALOG, "ns428_dividend_tax_credit_line_57", non_negative=True
)
"""Nova Scotia dividend tax credit, NS428 line 57 and line 61520 "Nova Scotia dividend tax credit
(use Worksheet NS428)": one optional input, as the filer gives it; Worksheet NS428 is not built."""

NS428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_58 = AmountKind.declare(
    CATALOG, "ns428_minimum_tax_carryover_amount_line_58", non_negative=True
)
"""Nova Scotia minimum tax carryover amount, NS428 line 58 (line 61540) "Amount from line 40427 of
your return": the amount from line 40427 of the T1 return, a record total of the T1's export
(`ca/minimum_tax_carryover_line_40427`), 0 for a salary-only caller."""

NS428_MINIMUM_TAX_CARRYOVER_LINE_58 = AmountKind.declare(
    CATALOG, "ns428_minimum_tax_carryover_line_58", non_negative=True
)
"""Nova Scotia minimum tax carryover, NS428 line 58 "Amount from line 40427 of your return
multiplied by 57.5% =": the amount from line 40427 multiplied by 57.5%."""

NS428_CREDITS_SUBTOTAL_LINE_59 = AmountKind.declare(
    CATALOG, "ns428_credits_subtotal_line_59", non_negative=True
)
"""Nova Scotia credits subtotal, NS428 line 59 "Add lines 56 to 58.": line 56 (a copy of line 52)
plus the dividend tax credit (line 57, a blank read as 0) plus the minimum tax carryover (line
58)."""

NS428_TAX_LINE_60 = AmountKind.declare(CATALOG, "ns428_tax_line_60", non_negative=True)
"""Nova Scotia tax after the credits, NS428 line 60 "Line 55 minus line 59 (if negative, enter
"0")": line 55 less line 59, not below zero."""

NS428_MINIMUM_TAX_T691_AMOUNT_LINE_61 = AmountKind.declare(
    CATALOG, "ns428_minimum_tax_t691_amount_line_61", non_negative=True
)
"""Nova Scotia additional tax amount, NS428 line 61 "Amount from line 14 of Part 7 of Form T691":
the amount from Form T691, a record total of the T691's export
(`ca/t691_additional_taxes_for_minimum_tax_carryover_line_14`), 0 for a salary-only caller."""

NS428_MINIMUM_TAX_ADDITIONAL_LINE_61 = AmountKind.declare(
    CATALOG, "ns428_minimum_tax_additional_line_61", non_negative=True
)
"""Nova Scotia additional tax for minimum tax purposes, NS428 line 61 "Amount from line 14 of Part 7
of Form T691 multiplied by 57.5%": the amount from Form T691 multiplied by 57.5%."""

NS428_TAX_LINE_62 = AmountKind.declare(CATALOG, "ns428_tax_line_62", non_negative=True)
"""Nova Scotia tax, NS428 line 62 "Line 60 plus line 61": line 60 plus the additional tax for
minimum tax purposes."""

NS428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_63 = AmountKind.declare(
    CATALOG, "ns428_provincial_foreign_tax_credit_line_63", non_negative=True
)
"""Provincial foreign tax credit, NS428 line 63 "Provincial foreign tax credit (complete Form
T2036)": an optional input that a salary-only caller leaves out, read as blank."""

NS428_TAX_AFTER_CREDITS_LINE_64 = AmountKind.declare(
    CATALOG, "ns428_tax_after_credits_line_64", non_negative=True
)
"""Nova Scotia tax after the foreign tax credit, NS428 line 64 "Line 62 minus line 63 (if negative,
enter "0")": line 62 less the provincial foreign tax credit, not below zero; line 77 reads it."""
