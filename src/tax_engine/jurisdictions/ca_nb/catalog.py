"""The New Brunswick artifact catalog: New Brunswick's own kinds, named from its forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_nb import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, NB428 line 9 and line 58040 "Basic personal amount Claim $13,396": the
amount claimed, one of the credit amounts that the New Brunswick credits subtotal is built from."""

NB428_CREDITS_SUBTOTAL_LINE_18 = AmountKind.declare(
    CATALOG, "nb428_credits_subtotal_line_18", non_negative=True
)
"""New Brunswick credits subtotal, NB428 line 18 "Add lines 9, 10, 13, 16, and 17.": the sum of the
personal amounts claimed, here the basic personal amount alone."""

NB428_CPP_CONTRIBUTIONS_LINE_19 = AmountKind.declare(
    CATALOG, "nb428_cpp_contributions_line_19", non_negative=True
)
"""CPP or QPP contributions, NB428 line 19 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

NB428_EI_PREMIUMS_LINE_21 = AmountKind.declare(
    CATALOG, "nb428_ei_premiums_line_21", non_negative=True
)
"""EI premiums credit amount, NB428 line 21 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

NB428_CPP_EI_AND_OTHER_LINE_25 = AmountKind.declare(
    CATALOG, "nb428_cpp_ei_and_other_line_25", non_negative=True
)
"""CPP or QPP, EI and other credit amounts, NB428 line 25 "Add lines 19 to 24.": the sum of the CPP
or QPP contributions on line 19 and the EI premiums on line 21, the other lines being blank
optional lines."""

NB428_CREDITS_SUBTOTAL_LINE_26 = AmountKind.declare(
    CATALOG, "nb428_credits_subtotal_line_26", non_negative=True
)
"""New Brunswick credit amounts subtotal, NB428 line 26 "Line 26: Line 18 plus line 25": the
personal amounts plus the CPP or QPP and EI credit amounts, read by the lines that follow."""

NB428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "nb428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form NB428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3, 4, 5 and 7."""

NB428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "nb428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, Form NB428 line 3 "Column 1: Line 1 is $51,306 or less / Line 3: 0.00"
(51,306.00; 102,614.00; 190,060.00): the printed lower bound of the column of lines 2 to 8 that
line 1 falls in."""

NB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "nb428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, NB428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero."""

NB428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "nb428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, Form NB428 line 5 "Column 1: Line 1 is $51,306 or less / Line 5: Rate 9.4%"
(14%; 16%; 19.5%): the printed rate of the column of lines 2 to 8 that line 1 falls in."""

NB428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "nb428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the excess, NB428 line 6 "Line 6: Line 4 multiplied by the percentage from line 5 =":
line 4 times the rate of line 5, rounded to the cent."""

NB428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "nb428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column of lines 2 to 8 (the engine's description; the form prints no
title for line 7), Form NB428 line 7 "Column 1: Line 1 is $51,306 or less / Line 7: 0.00" (4,822.76;
12,005.88; 25,997.24): the figure printed on line 7 of the column that line 1 falls in."""

NB428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "nb428_tax_on_taxable_income_line_8", non_negative=True
)
"""New Brunswick tax on taxable income, NB428 line 8 "Line 8: Line 6 plus line 7 New Brunswick tax
on taxable income =": line 6 plus line 7, read by line 54 on the tax form."""

NB428_CREDITS_SUBTOTAL_LINE_30 = AmountKind.declare(
    CATALOG, "nb428_credits_subtotal_line_30", non_negative=True
)
"""New Brunswick credits subtotal, NB428 line 30 "Add lines 27 to 29.": line 27 (a copy of line 26),
the pension and caregiver amounts being blank claims."""

NB428_CREDITS_SUBTOTAL_LINE_33 = AmountKind.declare(
    CATALOG, "nb428_credits_subtotal_line_33", non_negative=True
)
"""New Brunswick credits subtotal, NB428 line 33 "Add lines 30 to 32.": line 30, the disability
amounts being blank claims."""

NB428_CREDITS_SUBTOTAL_LINE_38 = AmountKind.declare(
    CATALOG, "nb428_credits_subtotal_line_38", non_negative=True
)
"""New Brunswick credits subtotal, NB428 line 38 "Add lines 33 to 37.": line 33, lines 34 to 37
being blank claims."""

NB428_MEDICAL_EXPENSES_LINE_46 = AmountKind.declare(
    CATALOG, "nb428_medical_expenses_line_46", non_negative=True
)
"""Medical expenses, NB428 line 46 and line 58769 "Line 44 plus line 45": the amount as the filer
gives it, an optional input; a blank input is read as blank."""

NB428_CREDITS_TOTAL_LINE_47 = AmountKind.declare(
    CATALOG, "nb428_credits_total_line_47", non_negative=True
)
"""New Brunswick credits total, NB428 line 47 and line 58800 "Line 38 plus line 46": the credits
subtotal plus the medical expenses."""

NB428_CREDITS_AT_RATE_LINE_49 = AmountKind.declare(
    CATALOG, "nb428_credits_at_rate_line_49", non_negative=True
)
"""Credits at the credit rate, NB428 line 49 and line 58840 "Line 47 multiplied by the percentage
from line 48": line 47 times 9.4%."""

NB428_DONATIONS_AMOUNT_LINE_50 = AmountKind.declare(
    CATALOG, "nb428_donations_amount_line_50", non_negative=True
)
"""Donations amount, NB428 line 50 box A "Amount from line 13 of your federal Schedule 9": a record
total of Schedule 9's export (`ca/schedule_9.donations_and_gifts_line_13`), 0 for a salary-only
caller."""

NB428_DONATIONS_CREDIT_AT_RATE_LINE_50 = AmountKind.declare(
    CATALOG, "nb428_donations_credit_at_rate_line_50", non_negative=True
)
"""Donations credit at 9.4%, NB428 line 50 box B "Amount from line 13 of your federal Schedule 9
multiplied by 9.4% =": the Schedule 9 amount times 9.4%; a blank amount is read as 0."""

NB428_DONATIONS_AMOUNT_LINE_51 = AmountKind.declare(
    CATALOG, "nb428_donations_amount_line_51", non_negative=True
)
"""Donations amount, NB428 line 51 box A "Amount from line 14 of your federal Schedule 9": a record
total of Schedule 9's export (`ca/schedule_9.donations_and_gifts_line_14`), 0 for a salary-only
caller."""

NB428_DONATIONS_CREDIT_AT_RATE_LINE_51 = AmountKind.declare(
    CATALOG, "nb428_donations_credit_at_rate_line_51", non_negative=True
)
"""Donations credit at 17.95%, NB428 line 51 box B "Amount from line 14 of your federal Schedule 9
multiplied by 17.95% =": the Schedule 9 amount times 17.95%; a blank amount is read as 0."""

NB428_DONATIONS_CREDIT_LINE_52 = AmountKind.declare(
    CATALOG, "nb428_donations_credit_line_52", non_negative=True
)
"""Donations and gifts credit, NB428 line 52 and line 58969 "Line 50 plus line 51": line 50 plus
line 51."""

NB428_NON_REFUNDABLE_CREDITS_LINE_53 = AmountKind.declare(
    CATALOG, "nb428_non_refundable_credits_line_53", non_negative=True
)
"""New Brunswick non-refundable tax credits, NB428 line 53 and line 61500 "Line 49 plus line 52":
the credits at the printed rate plus the donations credit; line 57 reads it."""

NB428_TAX_ON_SPLIT_INCOME_LINE_55 = AmountKind.declare(
    CATALOG, "nb428_tax_on_split_income_line_55", non_negative=True
)
"""NB428 line 55 and line 61510 "New Brunswick tax on split income (complete Form T1206)": the
amount as the filer gives it, an optional input; a blank input is read as blank."""

NB428_TAX_BEFORE_CREDITS_LINE_56 = AmountKind.declare(
    CATALOG, "nb428_tax_before_credits_line_56", non_negative=True
)
"""NB428 line 56 "Line 54 plus line 55": the tax on taxable income plus the tax on split income,
line 54 being a copy of line 8."""

NB428_TAX_AFTER_NON_REFUNDABLE_CREDITS_LINE_58 = AmountKind.declare(
    CATALOG, "nb428_tax_after_non_refundable_credits_line_58", non_negative=True
)
"""NB428 line 58 "Line 56 minus line 57 (if negative, enter "0")": line 56 less the non-refundable
credits of line 53, not below zero."""

NB428_DIVIDEND_TAX_CREDIT_LINE_60 = AmountKind.declare(
    CATALOG, "nb428_dividend_tax_credit_line_60", non_negative=True
)
"""NB428 line 60 and line 61520 "New Brunswick dividend tax credit (use Worksheet NB428)": the
amount as the filer gives it, an optional input; a blank input is read as blank."""

NB428_MINIMUM_TAX_CARRYOVER_LINE_61 = AmountKind.declare(
    CATALOG, "nb428_minimum_tax_carryover_line_61", non_negative=True
)
"""NB428 line 61 and line 61540 "Amount from line 40427 of your return multiplied by 57%": the
amount as the filer gives it, an optional input; a blank input is read as blank."""

NB428_DIVIDEND_CREDIT_AND_CARRYOVER_LINE_62 = AmountKind.declare(
    CATALOG, "nb428_dividend_credit_and_carryover_line_62", non_negative=True
)
"""NB428 line 62 "Line 60 plus line 61": the dividend tax credit plus the minimum tax carryover."""

NB428_TAX_LINE_63 = AmountKind.declare(CATALOG, "nb428_tax_line_63", non_negative=True)
"""NB428 line 63 "Line 59 minus line 62 (if negative, enter "0")": line 59, a copy of line 58,
less line 62, not below zero."""

NB428_ADDITIONAL_TAX_MINIMUM_TAX_LINE_64 = AmountKind.declare(
    CATALOG, "nb428_additional_tax_minimum_tax_line_64", non_negative=True
)
"""NB428 line 64 "Form T691: line 1 minus line 2 of Part 7 multiplied by 57%": the amount as the
filer gives it, an optional input; a blank input is read as blank."""

NB428_TAX_WITH_MINIMUM_TAX_LINE_65 = AmountKind.declare(
    CATALOG, "nb428_tax_with_minimum_tax_line_65", non_negative=True
)
"""NB428 line 65 "Line 63 plus line 64": the tax after the dividend credit plus the additional tax
for minimum tax purposes."""

NB428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_66 = AmountKind.declare(
    CATALOG, "nb428_provincial_foreign_tax_credit_line_66", non_negative=True
)
"""NB428 line 66 "Provincial foreign tax credit (complete Form T2036)": the amount as the filer
gives it, an optional input; a blank input is read as blank."""

NB428_TAX_LINE_67 = AmountKind.declare(CATALOG, "nb428_tax_line_67", non_negative=True)
"""NB428 line 67 "Line 65 minus line 66 (if negative, enter "0")": line 65 less the provincial
foreign tax credit, not below zero; line 69 reads it."""

NB428_NET_INCOME_LINE_70 = AmountKind.declare(
    CATALOG, "nb428_net_income_line_70", non_negative=True
)
"""Net income, NB428 line 70 "Net income from line 23600": the T1 net income, read for the
adjusted family income and for the low-income reduction's printed eligibility test."""

NB428_UCCB_REPAYMENT_LINE_21300 = AmountKind.declare(
    CATALOG, "nb428_uccb_repayment_line_21300", non_negative=True
)
"""UCCB repayment, line 21300 of the return, one of the two figures NB428 line 71 totals."""

NB428_RDSP_INCOME_REPAYMENT_LINE_23200 = AmountKind.declare(
    CATALOG, "nb428_rdsp_income_repayment_line_23200", non_negative=True
)
"""RDSP income repayment included on line 23200 of the return, the other figure NB428 line 71
totals."""

NB428_UCCB_RDSP_REPAYMENTS_LINE_71 = AmountKind.declare(
    CATALOG, "nb428_uccb_rdsp_repayments_line_71", non_negative=True
)
"""NB428 line 71 "UCCB repayment (line 21300) and RDSP income repayment (in line 23200)": the two
repayments added."""

NB428_FAMILY_INCOME_LINE_72 = AmountKind.declare(
    CATALOG, "nb428_family_income_line_72", non_negative=True
)
"""NB428 line 72 "Line 70 plus line 71": the net income plus the UCCB and RDSP repayments."""

NB428_UCCB_INCOME_LINE_11700 = AmountKind.declare(
    CATALOG, "nb428_uccb_income_line_11700", non_negative=True
)
"""UCCB income, line 11700 of the return, one of the two figures NB428 line 73 totals."""

NB428_RDSP_INCOME_LINE_12500 = AmountKind.declare(
    CATALOG, "nb428_rdsp_income_line_12500", non_negative=True
)
"""RDSP income, line 12500 of the return, the other figure NB428 line 73 totals."""

NB428_UCCB_RDSP_INCOME_LINE_73 = AmountKind.declare(
    CATALOG, "nb428_uccb_rdsp_income_line_73", non_negative=True
)
"""NB428 line 73 "UCCB income (line 11700) and RDSP income (line 12500)": the two incomes added."""

NB428_ADJUSTED_FAMILY_INCOME_LINE_74 = AmountKind.declare(
    CATALOG, "nb428_adjusted_family_income_line_74", non_negative=True
)
"""NB428 line 74 "Line 72 minus line 73 (if negative, enter "0")", column 1: the adjusted family
income. Column 2 is not modelled, so line 75 (the two columns added) is this figure."""

LOW_INCOME_REDUCTION_BASIC = AmountKind.declare(
    CATALOG, "low_income_reduction_basic", non_negative=True
)
"""Basic reduction, NB428 line 77 and line 61570 "Basic reduction Claim $802": the printed $802,
claimed whole and not income-tested."""

NB428_LOW_INCOME_REDUCTION_LINE_80 = AmountKind.declare(
    CATALOG, "nb428_low_income_reduction_line_80", non_negative=True
)
"""NB428 line 80 "Add lines 77 to 79 (maximum $1,604)": the basic reduction, not more than the
printed $1,604. Lines 78 and 79 (the spouse and the eligible dependant) are not modelled."""

LOW_INCOME_REDUCTION_BASE_AMOUNT = AmountKind.declare(
    CATALOG, "low_income_reduction_base_amount", non_negative=True
)
"""Base amount, NB428 line 82 "Base amount 21,920.00": the printed figure, the same at every
salary."""

NB428_LINE_83 = AmountKind.declare(CATALOG, "nb428_line_83", non_negative=True)
"""NB428 line 83 "Line 81 minus line 82 (if negative, enter "0")": the adjusted family income over
the base amount, line 81 being a copy of line 75."""

NB428_LINE_85 = AmountKind.declare(CATALOG, "nb428_line_85", non_negative=True)
"""NB428 line 85 "Line 83 multiplied by the percentage from line 84": line 83 at the printed 3%."""

NB428_LINE_86_BEFORE_ELIGIBILITY_TEST = AmountKind.declare(
    CATALOG, "nb428_line_86_before_eligibility_test", non_negative=True
)
"""NB428 line 86 "Line 80 minus line 85 (if negative, enter "0")", before the printed eligibility
test sets it to 0. Not printed as a line of its own."""

LOW_INCOME_REDUCTION_SINGLE_INCOME_LIMIT = AmountKind.declare(
    CATALOG, "low_income_reduction_single_income_limit", non_negative=True
)
"""Single income limit, the NB428 eligibility test "You are single and your net income from line
23600 of your return is less than $48,653": the printed figure."""

NB428_INCOME_UNDER_SINGLE_LIMIT = AmountKind.declare(
    CATALOG, "nb428_income_under_single_limit", non_negative=True
)
"""The single income limit less the net income of line 70, not below 0: above 0 exactly when the
net income is under the limit. Not printed on the form."""

NB428_LINE_86_ELIGIBILITY_GATE = AmountKind.declare(
    CATALOG, "nb428_line_86_eligibility_gate", non_negative=True
)
"""1 where the printed eligibility test is met (net income under the single limit), else 0, from
the `ca-nb/low_income_reduction_eligibility_gate` dataset. A plain figure, not printed."""

NB428_LINE_86 = AmountKind.declare(CATALOG, "nb428_line_86", non_negative=True)
"""NB428 line 86 "Line 80 minus line 85 (if negative, enter "0")", New Brunswick low-income tax
reduction: 0 where the eligibility test is not met."""

NB428_TAX_LINE_87 = AmountKind.declare(CATALOG, "nb428_tax_line_87", non_negative=True)
"""NB428 line 87 "Line 76 minus line 86 (if negative, enter "0")": the New Brunswick tax after the
low-income tax reduction, line 76 being line 69, which is line 67 (line 68 is not modelled)."""

NB428_POLITICAL_CONTRIBUTION_CREDIT_LINE_92 = AmountKind.declare(
    CATALOG, "nb428_political_contribution_credit_line_92", non_negative=True
)
"""NB428 line 92 "New Brunswick political contribution tax credit (use Worksheet NB428) (maximum
$500)": the amount as the filer enters it, one optional input; the worksheet is not built."""

NB428_TAX_LINE_93 = AmountKind.declare(CATALOG, "nb428_tax_line_93", non_negative=True)
"""NB428 line 93 "Line 87 minus line 92 (if negative, enter "0")": the New Brunswick tax after the
political contribution tax credit."""

NB428_LABOUR_SPONSORED_CREDIT_LINE_94 = AmountKind.declare(
    CATALOG, "nb428_labour_sponsored_credit_line_94", non_negative=True
)
"""NB428 line 94 "Labour-sponsored venture capital fund tax credit from NB-LSVC-1 certificate(s)
(maximum $2,000)": the amount as the filer enters it, one optional input."""

NB428_TAX_LINE_95 = AmountKind.declare(CATALOG, "nb428_tax_line_95", non_negative=True)
"""NB428 line 95 "Line 93 minus line 94 (if negative, enter "0")": the New Brunswick tax after the
labour-sponsored venture capital fund tax credit."""

NB428_SMALL_BUSINESS_INVESTOR_CREDIT_LINE_96 = AmountKind.declare(
    CATALOG, "nb428_small_business_investor_credit_line_96", non_negative=True
)
"""NB428 line 96 "Small business investor tax credit (complete Form T1258) (maximum $125,000)": the
amount as the filer enters it, one optional input; Form T1258 is not built."""

NB428_NEW_BRUNSWICK_TAX_LINE_97 = AmountKind.declare(
    CATALOG, "nb428_new_brunswick_tax_line_97", non_negative=True
)
"""NB428 line 97 "Line 95 minus line 96 (if negative, enter "0")": the New Brunswick tax, entered on
line 42800 of the return."""
