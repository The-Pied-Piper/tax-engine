"""The Nova Scotia artifact catalog: Nova Scotia's own kinds, named
from the Nova Scotia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind, CountKind
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

NS428_NET_INCOME_LINE_65 = AmountKind.declare(
    CATALOG, "ns428_net_income_line_65", non_negative=False
)
"""Net income, NS428 line 65 column 1 "Net income from line 23600 of the return (or the amount you
would have entered if the instructions on line 23600 said "if negative, show in brackets")": a
record total of the T1's net income before its floor, so it can be negative. Column 2 (spouse) is
deferred."""

NS428_UCCB_REPAYMENT_LINE_21300 = AmountKind.declare(
    CATALOG, "ns428_uccb_repayment_line_21300", non_negative=True
)
"""NS428 line 66, the part from T1 line 21300 (UCCB repayment): a record total of the T1's line."""

NS428_RDSP_INCOME_REPAYMENT_LINE_23200 = AmountKind.declare(
    CATALOG, "ns428_rdsp_income_repayment_line_23200", non_negative=True
)
"""NS428 line 66, the RDSP income repayment included on T1 line 23200: a record total of the T1's
line."""

NS428_UCCB_RDSP_REPAYMENTS_LINE_66 = AmountKind.declare(
    CATALOG, "ns428_uccb_rdsp_repayments_line_66", non_negative=True
)
"""UCCB and RDSP repayments, NS428 line 66 "Total of the universal child care benefit (UCCB)
repayment (line 21300 of the return) and the registered disability savings plan (RDSP) income
repayment (included on line 23200 of the return)": the sum of the two T1 lines, 0 for a salary-only
filer."""

NS428_FAMILY_INCOME_LINE_67 = AmountKind.declare(
    CATALOG, "ns428_family_income_line_67", non_negative=False
)
"""NS428 line 67 "Line 65 plus line 66": the net income plus the UCCB and RDSP repayments. Line 65
can be negative, so the kind is signed."""

NS428_UCCB_INCOME_LINE_11700 = AmountKind.declare(
    CATALOG, "ns428_uccb_income_line_11700", non_negative=True
)
"""NS428 line 68, the part from T1 line 11700 (UCCB income): a record total of the T1's line."""

NS428_RDSP_INCOME_LINE_12500 = AmountKind.declare(
    CATALOG, "ns428_rdsp_income_line_12500", non_negative=True
)
"""NS428 line 68, the part from T1 line 12500 (RDSP income): a record total of the T1's line."""

NS428_UCCB_RDSP_INCOME_LINE_68 = AmountKind.declare(
    CATALOG, "ns428_uccb_rdsp_income_line_68", non_negative=True
)
"""UCCB and RDSP income, NS428 line 68 "Total of the UCCB income (line 11700 of the return) and the
RDSP income (line 12500 of the return)": the sum of the two T1 lines, 0 for a salary-only filer."""

NS428_FAMILY_INCOME_LESS_UCCB_RDSP_LINE_69 = AmountKind.declare(
    CATALOG, "ns428_family_income_less_uccb_rdsp_line_69", non_negative=True
)
"""NS428 line 69 "Line 67 minus line 68 (if negative, enter "0")", column 1. Line 70 adds columns 1
and 2; with the spouse column deferred line 70 is this figure and has no step."""

LOW_INCOME_REDUCTION_BASIC = AmountKind.declare(
    CATALOG, "low_income_reduction_basic", non_negative=True
)
"""Basic reduction, NS428 line 71 and line 61950 "Basic reduction Claim $300": the printed $300,
claimed whole."""

NS428_LOW_INCOME_REDUCTION_LINE_74 = AmountKind.declare(
    CATALOG, "ns428_low_income_reduction_line_74", non_negative=True
)
"""NS428 line 74 "Add lines 71 to 73. (maximum $600)": the basic reduction, not more than the
printed $600. Lines 72 and 73 (spouse, eligible dependant) and line 75 are deferred, so lines 76 and
78 are this figure and have no step."""

LOW_INCOME_REDUCTION_BASE_AMOUNT = AmountKind.declare(
    CATALOG, "low_income_reduction_base_amount", non_negative=True
)
"""Base amount, NS428 line 80 "Base amount 15,000.00": the printed figure."""

NS428_LINE_81 = AmountKind.declare(CATALOG, "ns428_line_81", non_negative=True)
"""NS428 line 81 "Line 79 minus line 80 (if negative, enter "0")": the adjusted family income less
the base amount, not below 0."""

NS428_LINE_83 = AmountKind.declare(CATALOG, "ns428_line_83", non_negative=True)
"""NS428 line 83 "Line 81 multiplied by the percentage from line 82": line 81 times the printed 5%,
rounded to the cent."""

NS428_LOW_INCOME_REDUCTION_LINE_84 = AmountKind.declare(
    CATALOG, "ns428_low_income_reduction_line_84", non_negative=True
)
"""Nova Scotia low-income tax reduction, NS428 line 84 "Line 78 minus line 83 (if negative, enter
"0")"."""

NS428_TAX_LINE_85 = AmountKind.declare(CATALOG, "ns428_tax_line_85", non_negative=True)
"""NS428 line 85 "Line 77 minus line 84 (if negative, enter "0")": the tax after the foreign tax
credit (line 64) less the low-income tax reduction, not below 0."""

NS428_POLITICAL_CONTRIBUTIONS_LINE_86 = AmountKind.declare(
    CATALOG, "ns428_political_contributions_line_86", non_negative=True
)
"""NS428 line 86 "Total political contributions made in 2025 ... multiplied by 75% (maximum $750)":
the amount as the filer gives it, an optional input; a blank input is read as 0 by the step that
reads it."""

NS428_POLITICAL_CONTRIBUTION_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "ns428_political_contribution_credit_maximum", non_negative=True
)
"""Political contribution tax credit maximum, printed on NS428 line 86 "(maximum $750)": the
printed maximum, from the `ca-ns/political_contribution_credit_maximum` dataset; the bound line
86 cannot pass."""

NS428_POLITICAL_CONTRIBUTIONS_CREDIT_AT_RATE_LINE_86 = AmountKind.declare(
    CATALOG, "ns428_political_contributions_credit_at_rate_line_86", non_negative=True
)
"""NS428 line 86: the political contributions times the printed 75%, before the maximum check."""

NS428_POLITICAL_CONTRIBUTIONS_CREDIT_LINE_86 = AmountKind.declare(
    CATALOG, "ns428_political_contributions_credit_line_86", non_negative=True
)
"""Nova Scotia political contribution tax credit, NS428 line 86 "Total political contributions made
in 2025 ... multiplied by 75% (maximum $750)": the contributions times 75%, passed on unchanged
when at most the printed maximum; above it is refused, not capped."""

NS428_TAX_LINE_87 = AmountKind.declare(CATALOG, "ns428_tax_line_87", non_negative=True)
"""NS428 line 87 "Line 85 minus line 86 (if negative, enter \"0\")"."""

NS428_FOOD_BANK_DONATIONS_LINE_88 = AmountKind.declare(
    CATALOG, "ns428_food_bank_donations_line_88", non_negative=True
)
"""NS428 line 88 "Food bank tax credit for farmers ... multiplied by 25%": the amount as the filer
gives it, an optional input; a blank input is read as 0 by the step that reads it."""

NS428_FOOD_BANK_CREDIT_LINE_88 = AmountKind.declare(
    CATALOG, "ns428_food_bank_credit_line_88", non_negative=True
)
"""Food bank tax credit for farmers, NS428 line 88 "Food bank tax credit for farmers ... multiplied
by 25%": the entered amount times the printed 25%."""

NS428_TAX_LINE_89 = AmountKind.declare(CATALOG, "ns428_tax_line_89", non_negative=True)
"""NS428 line 89 "Line 87 minus line 88 (if negative, enter \"0\")"."""

NS428_LABOUR_SPONSORED_SHARES_COST_LINE_90 = AmountKind.declare(
    CATALOG, "ns428_labour_sponsored_shares_cost_line_90", non_negative=True
)
"""NS428 line 90 "Labour-sponsored venture capital tax credit: Cost of shares from Form NSLSV ...
multiplied by 20% (maximum $2,000)": the amount as the filer gives it, an optional input; a
blank input is read as 0 by the step that reads it."""

NS428_LABOUR_SPONSORED_CREDIT_MAXIMUM = AmountKind.declare(
    CATALOG, "ns428_labour_sponsored_credit_maximum", non_negative=True
)
"""Labour-sponsored venture capital tax credit maximum, printed on NS428 line 90 "(maximum
$2,000)": the printed maximum, from the `ca-ns/labour_sponsored_credit_maximum` dataset; the
bound line 90 cannot pass."""

NS428_LABOUR_SPONSORED_CREDIT_AT_RATE_LINE_90 = AmountKind.declare(
    CATALOG, "ns428_labour_sponsored_credit_at_rate_line_90", non_negative=True
)
"""NS428 line 90: the cost of shares times the printed 20%, before the maximum check."""

NS428_LABOUR_SPONSORED_CREDIT_LINE_90 = AmountKind.declare(
    CATALOG, "ns428_labour_sponsored_credit_line_90", non_negative=True
)
"""Labour-sponsored venture capital tax credit, NS428 line 90: the cost of shares times 20%, passed
on unchanged when at most the printed maximum; above it is refused, not capped."""

NS428_TAX_LINE_91 = AmountKind.declare(CATALOG, "ns428_tax_line_91", non_negative=True)
"""NS428 line 91 "Line 89 minus line 90 (if negative, enter \"0\")"."""

NS428_EQUITY_TAX_CREDIT_LINE_92 = AmountKind.declare(
    CATALOG, "ns428_equity_tax_credit_line_92", non_negative=True
)
"""NS428 line 92 "Equity tax credit (complete Form T1285)": the amount as the filer gives it, an
optional input; a blank input is read as 0 by the step that reads it."""

NS428_TAX_LINE_93 = AmountKind.declare(CATALOG, "ns428_tax_line_93", non_negative=True)
"""NS428 line 93 "Line 91 minus line 92 (if negative, enter \"0\")"."""

NS428_INNOVATION_EQUITY_TAX_CREDIT_LINE_94 = AmountKind.declare(
    CATALOG, "ns428_innovation_equity_tax_credit_line_94", non_negative=True
)
"""NS428 line 94 "Innovation equity tax credit (complete Form T225)": the amount as the filer gives
it, an optional input; a blank input is read as 0 by the step that reads it."""

NS428_TAX_LINE_95 = AmountKind.declare(CATALOG, "ns428_tax_line_95", non_negative=True)
"""NS428 line 95 "Line 93 minus line 94 (if negative, enter \"0\")"."""

NS428_VENTURE_CAPITAL_TAX_CREDIT_LINE_96 = AmountKind.declare(
    CATALOG, "ns428_venture_capital_tax_credit_line_96", non_negative=True
)
"""NS428 line 96 "Venture capital tax credit (complete Form T224)": the amount as the filer gives
it, an optional input; a blank input is read as 0 by the step that reads it."""

NS428_TAX_LINE_97 = AmountKind.declare(CATALOG, "ns428_tax_line_97", non_negative=True)
"""NS428 line 97 "Line 95 minus line 96 (if negative, enter \"0\")"."""

NS428_AGE_65_OR_OLDER = CountKind.declare(CATALOG, "ns428_age_65_or_older", non_negative=True)
"""Aged 65 or older at the end of the year, read from the T1's `ca/age_65_or_older` (worked out
once there from the year of birth) for NS428 line 10 and line 98: 1 or 0, blank when the year is
blank."""

WORKSHEET_NS428_AGE_AMOUNT_MAXIMUM_LINE_1 = AmountKind.declare(
    CATALOG, "worksheet_ns428_age_amount_maximum_line_1", non_negative=True
)
"""Worksheet NS428 age amount line 1 "Maximum amount 5,734.00"."""

WORKSHEET_NS428_AGE_AMOUNT_NET_INCOME_LINE_2 = AmountKind.declare(
    CATALOG, "worksheet_ns428_age_amount_net_income_line_2", non_negative=True
)
"""Worksheet NS428 age amount line 2 "Amount from line 23600 of your return"."""

WORKSHEET_NS428_AGE_AMOUNT_INCOME_THRESHOLD_LINE_3 = AmountKind.declare(
    CATALOG, "worksheet_ns428_age_amount_income_threshold_line_3", non_negative=True
)
"""Worksheet NS428 age amount line 3 "Income threshold 30,828.00"."""

WORKSHEET_NS428_AGE_AMOUNT_LINE_4 = AmountKind.declare(
    CATALOG, "worksheet_ns428_age_amount_line_4", non_negative=True
)
"""Worksheet NS428 age amount line 4 "Line 2 minus line 3 (if negative, enter \"0\")"."""

WORKSHEET_NS428_AGE_AMOUNT_LINE_6 = AmountKind.declare(
    CATALOG, "worksheet_ns428_age_amount_line_6", non_negative=True
)
"""Worksheet NS428 age amount line 6 "Line 4 multiplied by the percentage from line 5"."""

WORKSHEET_NS428_AGE_AMOUNT_LINE_7 = AmountKind.declare(
    CATALOG, "worksheet_ns428_age_amount_line_7", non_negative=True
)
"""Worksheet NS428 age amount line 7 "Line 1 minus line 6 (if negative, enter \"0\")": the amount
for NS428 line 10 when the filer was born in 1960 or earlier."""

NS428_AGE_AMOUNT_CLAIMED_LINE_10 = AmountKind.declare(
    CATALOG, "ns428_age_amount_claimed_line_10", non_negative=True
)
"""NS428 line 10: worksheet line 7 when born in 1960 or earlier, 0.00 otherwise, before the check
against the printed maximum."""

NS428_AGE_AMOUNT_LINE_10 = AmountKind.declare(
    CATALOG, "ns428_age_amount_line_10", non_negative=True
)
"""NS428 line 10 "Age amount (if you were born in 1960 or earlier) (use Worksheet NS428)
(maximum $5,734)": worksheet line 7 when born in 1960 or earlier, 0.00 otherwise."""

NS428_AGE_TAX_CREDIT_INCOME_LIMIT = AmountKind.declare(
    CATALOG, "ns428_age_tax_credit_income_limit", non_negative=True
)
"""Taxable income limit of the age tax credit, NS428 line 98 "(... your taxable income is less than
$24,000)": the printed limit, from the `ca-ns/age_tax_credit_income_limit` dataset."""

NS428_INCOME_UNDER_AGE_TAX_CREDIT_LIMIT = AmountKind.declare(
    CATALOG, "ns428_income_under_age_tax_credit_limit", non_negative=True
)
"""The age tax credit income limit less taxable income (line 1), not below 0: above 0 exactly when
taxable income is less than the limit. Not a line of the form."""

NS428_AGE_TAX_CREDIT_ELIGIBILITY_GATE = AmountKind.declare(
    CATALOG, "ns428_age_tax_credit_eligibility_gate", non_negative=True
)
"""Switch of the age tax credit's income test, 0 or 1, from the
`ca-ns/age_tax_credit_eligibility_gate` dataset. Not a CRA figure."""

NS428_AGE_TAX_CREDIT_CLAIM = AmountKind.declare(
    CATALOG, "ns428_age_tax_credit_claim", non_negative=True
)
"""Age tax credit claim, NS428 line 98 "Claim $1,000": the printed figure, from the
`ca-ns/age_tax_credit` dataset."""

NS428_AGE_TAX_CREDIT_IF_BORN_IN_1960_OR_EARLIER = AmountKind.declare(
    CATALOG, "ns428_age_tax_credit_if_born_in_1960_or_earlier", non_negative=True
)
"""The age tax credit claim when the filer was born in 1960 or earlier, 0.00 otherwise, before the
income test. Not a line of the form."""

NS428_AGE_TAX_CREDIT_LINE_98 = AmountKind.declare(
    CATALOG, "ns428_age_tax_credit_line_98", non_negative=True
)
"""Age tax credit, NS428 line 98 "Age tax credit (if you were born in 1960 or earlier and your
taxable income is less than $24,000) Claim $1,000": $1,000.00 when both conditions are met, 0.00
otherwise."""

NS428_NOVA_SCOTIA_TAX_LINE_99 = AmountKind.declare(
    CATALOG, "ns428_nova_scotia_tax_line_99", non_negative=True
)
"""Nova Scotia tax, NS428 line 99 "Line 97 minus line 98 (if negative, enter \"0\") Enter this
amount on line 42800 of your return. Nova Scotia tax": line 97 less line 98 (the age tax credit),
not below 0."""

AVERAGE_TAX_RATE = AmountKind.declare(CATALOG, "average_tax_rate", non_negative=True)
"""Average tax rate on the take-home basis, the Nova Scotia return summary's own figure (no form
prints it): the income tax, CPP (Schedule 8 lines 25 and 28), EI (T2204 line 16) together divided
by the salary (`ca/return_employment_income`), as a fraction, so 0.1598 is 15.98%. Paid
credits are not in it. It is 0 when the salary is 0."""

NOVA_SCOTIA_BRACKET_RATE_RETURN = AmountKind.declare(
    CATALOG, "nova_scotia_bracket_rate_return", non_negative=True
)
"""Nova Scotia bracket rate, NS428 line 5 "Rate": the printed rate of the column that line 1 falls
in (8.79% to 21%), read from NS428 into the return summary. Always present."""


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

MARGINAL_NOVA_SCOTIA_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_nova_scotia_credit_rate", non_negative=True
)
"""Nova Scotia non-refundable tax credit rate, NS428 line 47 "Nova Scotia non-refundable tax credit
rate 8.79%": the `ca-ns/credit_rate` dataset as it is, with none of the cent rounding the credit
box applies. A rate, not printed as its own figure."""

MARGINAL_NOVA_SCOTIA_CONTRIBUTION_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_nova_scotia_contribution_credit_rate", non_negative=True
)
"""Nova Scotia credit rate on the CPP base and EI of a further dollar of salary: the
credit-earning contribution rate times the credit rate, the provincial tax the contributions take
off. An exact product, not printed on the form."""

MARGINAL_NOVA_SCOTIA_BRACKET_RATE = AmountKind.declare(
    CATALOG, "marginal_nova_scotia_bracket_rate", non_negative=True
)
"""Nova Scotia bracket rate on a further dollar of salary: the bracket rate of NS428
line 5 times the part left in the net income. An exact product, not printed on the
form."""

MARGINAL_NOVA_SCOTIA_RATE_AFTER_CREDITS = AmountKind.declare(
    CATALOG, "marginal_nova_scotia_rate_after_credits", non_negative=True
)
"""Nova Scotia rate on a further dollar of salary after the CPP base and EI credits,
before the low-income tax reduction. An exact difference, not printed on the form."""

INCOME_OVER_LOW_INCOME_THRESHOLD_RETURN = AmountKind.declare(
    CATALOG, "income_over_low_income_threshold_return", non_negative=True
)
"""NS428 line 81 "Line 79 minus line 80 (if negative, enter "0")", the income over the
base amount of the low-income tax reduction, read into the return summary. The base of the
line 81 gate."""

LOW_INCOME_TAX_REDUCTION_RETURN = AmountKind.declare(
    CATALOG, "low_income_tax_reduction_return", non_negative=True
)
"""NS428 line 84, the Nova Scotia low-income tax reduction, read into the return
summary. The base of the line 84 gate."""

INCOME_OVER_LOW_INCOME_THRESHOLD_GATE = AmountKind.declare(
    CATALOG, "income_over_low_income_threshold_gate", non_negative=True
)
"""0 where NS428 line 81 is 0.00 and 1 where it is at least one cent, from the
`ca-ns/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

LOW_INCOME_TAX_REDUCTION_GATE = AmountKind.declare(
    CATALOG, "low_income_tax_reduction_gate", non_negative=True
)
"""0 where NS428 line 84 is 0.00 and 1 where it is at least one cent, from the
`ca-ns/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

LOW_INCOME_REDUCTION_PHASE_OUT_GATE = AmountKind.declare(
    CATALOG, "low_income_reduction_phase_out_gate", non_negative=True
)
"""1 while the low-income tax reduction is being phased out (NS428 lines 81 and 84 both above
zero), otherwise 0. The product of the two gates, not printed on the form."""

LOW_INCOME_REDUCTION_RATE_FIGURE = AmountKind.declare(
    CATALOG, "low_income_reduction_rate_figure", non_negative=True
)
"""NS428 line 82 "Applicable rate 5%": the `ca-ns/low_income_reduction_rate` dataset as it is. A
rate, not printed as its own figure."""

MARGINAL_LOW_INCOME_REDUCTION_RATE = AmountKind.declare(
    CATALOG, "marginal_low_income_reduction_rate", non_negative=True
)
"""Rate at which a further dollar of net income takes off the low-income tax reduction (NS428
line 82 and line 83): 5% while the reduction is being phased out, 0 elsewhere. Not printed on
the form."""

MARGINAL_LOW_INCOME_PHASE_OUT_RATE = AmountKind.declare(
    CATALOG, "marginal_low_income_phase_out_rate", non_negative=True
)
"""The low-income reduction rate on a further dollar of salary: the reduction rate times the part
left in the net income. An exact product, not printed on the form."""

MARGINAL_NOVA_SCOTIA_RATE_WITH_REDUCTION = AmountKind.declare(
    CATALOG, "marginal_nova_scotia_rate_with_reduction", non_negative=True
)
"""Nova Scotia rate on a further dollar of salary after the credits plus the
low-income reduction phase-out, before the line 99 gate. An exact sum, not printed on the form."""

NOVA_SCOTIA_TAX_RETURN = AmountKind.declare(CATALOG, "nova_scotia_tax_return", non_negative=True)
"""NS428 line 99 "Line 97 minus line 98 (if negative, enter "0")", the tax that goes to T1 line
42800, read into the return summary. The base of the Nova Scotia rate gate."""

NOVA_SCOTIA_RATE_GATE = AmountKind.declare(CATALOG, "nova_scotia_rate_gate", non_negative=True)
"""Nova Scotia rate gate: 0 where the Nova Scotia tax (NS428 line
99) is 0.00 and 1 where it is at least one cent, from the
`ca-ns/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

NOVA_SCOTIA_MARGINAL_RATE = AmountKind.declare(
    CATALOG, "nova_scotia_marginal_rate", non_negative=True
)
"""Nova Scotia marginal rate on the take-home basis: the bracket rate after the CPP
base and EI credits, plus the low-income tax reduction phase-out, counted where the Nova Scotia
tax (NS428 line 99) is above zero and 0 where it is not. Not printed on the form."""

MARGINAL_TAX_RATE = AmountKind.declare(CATALOG, "marginal_tax_rate", non_negative=True)
"""Marginal tax rate on the take-home basis: the change in income tax, CPP, CPP2 and EI on a further
dollar of salary, with no credit paid on filing: the sum of the federal marginal rate, the
Nova Scotia marginal rate (which has no surtax or health premium) and the
contribution rate, on the return summary. Not printed on the form."""
