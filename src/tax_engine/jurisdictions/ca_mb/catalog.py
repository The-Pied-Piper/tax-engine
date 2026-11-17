"""The Manitoba artifact catalog: Manitoba's own kinds, named from the Manitoba forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_mb import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

MB428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "mb428_tax_on_taxable_income_line_8", non_negative=True
)
"""Manitoba tax on taxable income, MB428 line 8 "Line 6 plus line 7 Manitoba tax on taxable income
=": line 6 plus line 7 of the column that line 1 falls in, read by line 58 on the tax form."""

MB428_BASIC_PERSONAL_AMOUNT_LINE_9 = AmountKind.declare(
    CATALOG, "mb428_basic_personal_amount_line_9", non_negative=True
)
"""Basic personal amount, MB428 line 9 and line 58040 "Basic personal amount (use Worksheet MB428)":
the amount of Worksheet MB428 line 9, which says to enter it on line 58040."""

MB428_CREDITS_SUBTOTAL_LINE_18 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_18", non_negative=True
)
"""Credits subtotal, MB428 line 18 "Line 18: Add lines 9, 10, 13, 16, and 17. = ^": only the basic
personal amount, line 9, is summed here, because a salary-only single filer has no age, spouse,
eligible dependant or infirm dependant amount."""

MB428_CPP_CONTRIBUTIONS_LINE_19 = AmountKind.declare(
    CATALOG, "mb428_cpp_contributions_line_19", non_negative=True
)
"""CPP or QPP contributions, MB428 line 19 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

MB428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "mb428_pension_income_amount", non_negative=True
)
"""Pension income amount, MB428 line 31 "Line 31 and line 58360: Pension income amount (maximum
$1,000)": the amount the filer claims, a caller input that is read as blank when left out; the
line 31 step checks it against the printed maximum."""

MB428_PENSION_INCOME_AMOUNT_MAXIMUM = AmountKind.declare(
    CATALOG, "mb428_pension_income_amount_maximum", non_negative=True
)
"""Pension income amount maximum, printed on MB428 line 31 "(maximum $1,000)": the printed
maximum, from the `ca-mb/pension_income_amount_maximum` dataset; the bound line 31 cannot pass."""

MB428_PENSION_INCOME_AMOUNT_LINE_31 = AmountKind.declare(
    CATALOG, "mb428_pension_income_amount_line_31", non_negative=True
)
"""Pension income amount, MB428 line 31 "Line 31 and line 58360: Pension income amount (maximum
$1,000)": the entered amount, passed on unchanged when it is at most the printed maximum, blank when
left out; above the maximum it is refused, not capped."""

MB428_MEDICAL_EXPENSES_LINE_50 = AmountKind.declare(
    CATALOG, "mb428_medical_expenses_line_50", non_negative=True
)
"""Medical expenses, MB428 line 50 (line 58769) "Line 48 plus line 49 =": line 48 plus line 49, an
optional input; a blank is read as 0 by the line 51 step."""

MB428_DONATIONS_CREDIT_LINE_56 = AmountKind.declare(
    CATALOG, "mb428_donations_credit_line_56", non_negative=True
)
"""Donations and gifts credit, MB428 line 56 (line 58969) "Line 56 and line 58969: Line 54 plus line
55 =": a caller input, read as blank when left out; line 57 reads it."""

MB428_NON_REFUNDABLE_CREDITS_LINE_57 = AmountKind.declare(
    CATALOG, "mb428_non_refundable_credits_line_57", non_negative=True
)
"""Manitoba non-refundable tax credits, MB428 line 57 "Line 57 and line 61500: Line 53 plus line 56
Enter this amount on line 61. Manitoba non-refundable tax credits =": line 53 plus line 56, read by
line 61 on the tax form."""

MB428_MANITOBA_TAX_ON_TAXABLE_INCOME_LINE_58 = AmountKind.declare(
    CATALOG, "mb428_manitoba_tax_on_taxable_income_line_58", non_negative=True
)
"""Manitoba tax on taxable income, MB428 line 58 "Line 58: Manitoba tax on taxable income from
line 8": line 8 of the Manitoba tax form's Part A, read across the forms."""

MB428_TAX_ON_SPLIT_INCOME_LINE_59 = AmountKind.declare(
    CATALOG, "mb428_tax_on_split_income_line_59", non_negative=True
)
"""Manitoba tax on split income, MB428 line 59 (line 61510) "Line 59 and line 61510: Manitoba tax on
split income (complete Form T1206)": a caller input, read as blank when left out; line 60 reads
it."""

MB428_TAX_BEFORE_CREDITS_LINE_60 = AmountKind.declare(
    CATALOG, "mb428_tax_before_credits_line_60", non_negative=True
)
"""MB428 line 60 "Line 60: Line 58 plus line 59 =": the sum of line 58 and line 59, where a blank
line 59 is read as 0."""

MB428_NON_REFUNDABLE_CREDITS_LINE_61 = AmountKind.declare(
    CATALOG, "mb428_non_refundable_credits_line_61", non_negative=True
)
"""Manitoba non-refundable tax credits, MB428 line 61 "Line 61: Manitoba non-refundable tax credits
from line 57 ^": line 57 of the credits form, read across the forms."""

MB428_MINIMUM_TAX_CARRYOVER_LINE_63 = AmountKind.declare(
    CATALOG, "mb428_minimum_tax_carryover_line_63", non_negative=True
)
"""Minimum tax carryover amount, MB428 line 63 (line 40427) "Line 63 and line 61540: Amount from
line 40427 of your return": a caller input, read as blank when left out; the carryover credit step
reads it."""

MB428_MINIMUM_TAX_CARRYOVER_CREDIT_LINE_63 = AmountKind.declare(
    CATALOG, "mb428_minimum_tax_carryover_credit_line_63", non_negative=True
)
"""Manitoba minimum tax carryover, MB428 line 63 and line 61540 "Amount from line 40427 of your
return multiplied by 50% =": calculated, the amount from line 40427 multiplied by 50%."""

MB428_ADDITIONAL_TAX_MINIMUM_TAX_LINE_66 = AmountKind.declare(
    CATALOG, "mb428_additional_tax_minimum_tax_line_66", non_negative=True
)
"""Manitoba additional tax for minimum tax purposes, MB428 line 66 "Line 66: Form T691: line 1 minus
line 2 of Part 7 multiplied by 50% =": calculated, the Form T691 amount multiplied by 50%."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_9 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_9", non_negative=True
)
"""Manitoba basic personal amount, Worksheet MB428 line 9 "Line 9: Line 1 minus line 8 (if negative,
enter "0") Enter this amount on line 58040 of your Form MB428.": the basic personal amount entered
on line 58040 of Form MB428."""

MB479_MANITOBA_CREDITS_LINE_81 = AmountKind.declare(
    CATALOG, "mb479_manitoba_credits_line_81", non_negative=True
)
"""Manitoba credits, MB479 line 81 "Add lines 78 to 80. Enter this amount on line 47900 of your
return.": the Manitoba credits, entered on T1 line 47900."""

MB428_DIVIDEND_TAX_CREDIT_LINE_62 = AmountKind.declare(
    CATALOG, "mb428_dividend_tax_credit_line_62", non_negative=True
)
"""Manitoba dividend tax credit, MB428 line 62 (line 61520) "Line 62 and line 61520: Manitoba
dividend tax credit (use Worksheet MB428)": a caller input, read as blank when left out."""

MB428_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_69 = AmountKind.declare(
    CATALOG, "mb428_political_contribution_tax_credit_line_69", non_negative=True
)
"""Manitoba political contribution tax credit, MB428 line 69 "Line 69: Manitoba political
contribution tax credit (use Worksheet MB428) (maximum $1,000)": a caller input, read as blank
when left out."""

MB428_LABOUR_SPONSORED_FUNDS_CREDIT_LINE_71 = AmountKind.declare(
    CATALOG, "mb428_labour_sponsored_funds_credit_line_71", non_negative=True
)
"""Labour-sponsored funds tax credit, MB428 line 71 (line 60800) "Enter your labour-sponsored funds
tax credit from Slip T2C (MAN.).": a caller input, read as blank when left out."""

MB428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_73 = AmountKind.declare(
    CATALOG, "mb428_provincial_foreign_tax_credit_line_73", non_negative=True
)
"""Provincial foreign tax credit, MB428 line 73 "Line 73: Provincial foreign tax credit (complete
Form T2036)": a caller input, read as blank when left out."""

MB428_MANITOBA_TAX_LINE_82 = AmountKind.declare(
    CATALOG, "mb428_manitoba_tax_line_82", non_negative=True
)
"""Manitoba tax, MB428 line 82 "Enter this amount on line 42800 of your return.": the Manitoba
tax, entered on T1 line 42800."""

MB428_A_FAMILY_TAX_BENEFIT_LINE_12 = AmountKind.declare(
    CATALOG, "mb428_a_family_tax_benefit_line_12", non_negative=True
)
"""Family tax benefit, Schedule MB428-A line 12 "Line 12: Line 10 minus line 11 (if negative, enter
"0") Enter this amount on line 61470 of your Form MB428.": the family tax benefit entered on line
61470 of Form MB428."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_3 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_3", non_negative=True
)
"""Income threshold, Worksheet MB428 line 3 "Line 3: Income threshold 200,000.00": the income
threshold of the basic personal amount section."""

WORKSHEET_MB428_LINE_2 = AmountKind.declare(CATALOG, "worksheet_mb428_line_2", non_negative=True)
"""Net income, Worksheet MB428 line 2 "Line 2: Amount from line 23600 of your return": the T1 net
income, line 23600 after its floor."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_1 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_1", non_negative=True
)
"""Base amount, Worksheet MB428 line 1 "Line 1: Base amount 15,780.00": the base amount of the
basic personal amount section."""

MB428_EI_PREMIUMS_LINE_21 = AmountKind.declare(
    CATALOG, "mb428_ei_premiums_line_21", non_negative=True
)
"""EI premiums credit amount, MB428 line 21 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_5 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_5", non_negative=True
)
"""Income threshold, Worksheet MB428 line 5 "Line 5: Income threshold 200,000.00": the income
threshold of the basic personal amount section."""

WORKSHEET_MB428_LINE_4 = AmountKind.declare(CATALOG, "worksheet_mb428_line_4", non_negative=True)
"""Net income over the threshold, Worksheet MB428 line 4 "Line 4: Line 2 minus line 3 (if negative,
enter "0")": line 2 minus line 3, not below zero."""

WORKSHEET_MB428_BASIC_PERSONAL_AMOUNT_LINE_7 = AmountKind.declare(
    CATALOG, "worksheet_mb428_basic_personal_amount_line_7", non_negative=True
)
"""Base amount, Worksheet MB428 line 7 "Line 7: Base amount 15,780.00": the base amount of the
basic personal amount section."""

MB428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "mb428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form MB428 Line 1 "Enter your taxable income from line 26000 of your return":
the T1 taxable income, read directly by lines 3 and 4."""

WORKSHEET_MB428_LINE_6 = AmountKind.declare(CATALOG, "worksheet_mb428_line_6", non_negative=True)
"""Net income over the threshold as a share of the threshold, Worksheet MB428 line 6 "Line 6: Line 4
divided by line 5 = ^": the ratio of line 4 to line 5, a fraction (0.25 is a quarter), not money."""

MB428_A_BASIC_AMOUNT_LINE_1 = AmountKind.declare(
    CATALOG, "mb428_a_basic_amount_line_1", non_negative=True
)
"""Basic amount, Schedule MB428-A line 1 "Line 1: Basic amount 2,065.00": the basic amount of the
family tax benefit."""

MB428_A_NET_INCOME_LINE_11 = AmountKind.declare(
    CATALOG, "mb428_a_net_income_line_11", non_negative=True
)
"""Net income, Schedule MB428-A (CRA 5007-A) line 11 "Line 11: Net income from line 23600 of your
return": the first box of the line, the net income read from the T1, before the multiplication
by 9%."""

MB479_NET_INCOME_LINE_1 = AmountKind.declare(CATALOG, "mb479_net_income_line_1", non_negative=False)
"""Net income, MB479 line 1 "Line 1: Net income from line 23600 of the return (or the amount you
would have entered if the instructions on line 23600 said "if negative, show in brackets")": the
net income of the T1 return before its floor, read from the signed T1 net income export
(`ca/net_income_signed`, not the floored `ca/net_income`). Column 1 only. The form shows a negative
net income in brackets, so the kind is signed."""

MB479_UCCB_RDSP_REPAYMENTS_LINE_2 = AmountKind.declare(
    CATALOG, "mb479_uccb_rdsp_repayments_line_2", non_negative=True
)
"""UCCB and RDSP repayments, MB479 line 2 "Total of the universal child care benefit (UCCB)
repayment (line 21300 of the return) and the registered disability savings plan (RDSP) income
repayment (included on line 23200 of the return)": the total of the two repayments, a caller input
that is read as blank when left out, column 1 (you) only."""

WORKSHEET_MB428_LINE_8 = AmountKind.declare(CATALOG, "worksheet_mb428_line_8", non_negative=True)
"""Worksheet MB428 line 8 "Line 8: Line 6 multiplied by line 7 = ^": line 6 times line 7, money."""

MB428_A_LINE_10 = AmountKind.declare(CATALOG, "mb428_a_line_10", non_negative=True)
"""Sum of lines 1 to 9, Schedule MB428-A line 10 "Line 10: Add lines 1 to 9.": the basic amount of
the family tax benefit, the only line of the block that is built."""

MB428_A_LINE_11 = AmountKind.declare(CATALOG, "mb428_a_line_11", non_negative=True)
"""Net income multiplied by 9%, Schedule MB428-A (CRA 5007-A) line 11 "Line 11: Net income from line
23600 of your return multiplied by 9%": the net income of the first box times the printed rate."""

MB479_UCCB_RDSP_INCOME_LINE_4 = AmountKind.declare(
    CATALOG, "mb479_uccb_rdsp_income_line_4", non_negative=True
)
"""UCCB and RDSP income, MB479 line 4 "Total of the UCCB income (line 11700 of the return) and RDSP
income (line 12500 of the return)": the total of the two incomes, a caller input that is read as
blank when left out, column 1 (you) only."""

MB479_FAMILY_INCOME_COLUMN_2_LINE_5 = AmountKind.declare(
    CATALOG, "mb479_family_income_column_2_line_5", non_negative=True
)
"""Family income of your spouse or common-law partner, MB479 line 5 "Line 3 minus line 4 (if
negative, enter "0")": column 2 (your spouse or common-law partner), taken as one figure because the
spouse's own lines 1 to 4 are not modelled, a caller input that is read as blank when left out."""

MB479_FAMILY_INCOME_BEFORE_BENEFITS_LINE_3 = AmountKind.declare(
    CATALOG, "mb479_family_income_before_benefits_line_3", non_negative=False
)
"""Family income before benefits, MB479 line 3 "Line 3: Line 1 plus line 2": the net income of
line 1 plus the UCCB and RDSP repayments of line 2, column 1 (you) only. Line 1 can be negative, so
the kind is signed."""

MB479_BASIC_CREDIT_LINE_7 = AmountKind.declare(
    CATALOG, "mb479_basic_credit_line_7", non_negative=True
)
"""Basic credit, MB479 line 7 "Line 7: Basic credit 195.00": the basic credit of the Manitoba
personal tax credits."""

MB479_PRIMARY_CAREGIVER_CREDIT_LINE_59 = AmountKind.declare(
    CATALOG, "mb479_primary_caregiver_credit_line_59", non_negative=True
)
"""Primary caregiver tax credit, MB479 line 59 "Line 59 and line 61260: Primary caregiver tax
credit": a caller input that is read as blank when left out."""

MB479_ODOUR_CONTROL_CREDIT_LINE_65 = AmountKind.declare(
    CATALOG, "mb479_odour_control_credit_line_65", non_negative=True
)
"""Unused odour-control tax credit, MB479 line 65 "Line 65 and line 61340: Enter your unused
odour-control tax credit from your 2024 notice of assessment or reassessment.": a caller input that
is read as blank when left out."""

MB428_CPP_EI_AND_OTHER_LINE_28 = AmountKind.declare(
    CATALOG, "mb428_cpp_ei_and_other_line_28", non_negative=True
)
"""CPP, EI and other credit amounts subtotal, MB428 line 28 "Line 28: Add lines 19 to 27. = ^": the
sum of lines 19 and 21. Lines 20 and 22 to 27 are not built: a salary-only filer has none."""

MB428_FAMILY_TAX_BENEFIT_LINE_41 = AmountKind.declare(
    CATALOG, "mb428_family_tax_benefit_line_41", non_negative=True
)
"""Family tax benefit, MB428 line 41 and line 61470 "Line 41 and line 61470: Family tax benefit
(attach Schedule MB428-A)": the amount of Schedule MB428-A line 12, which says to enter it on line
61470 of Form MB428."""

MB428_CREDITS_SUBTOTAL_LINE_29 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_29", non_negative=True
)
"""Credits subtotal, MB428 line 29 "Line 29: Line 18 plus line 28.": the sum of line 18 and line
28."""

MB428_CREDITS_SUBTOTAL_LINE_33 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_33", non_negative=True
)
"""Credits subtotal, MB428 line 33 "Line 33: Add lines 30 to 32. = ^": the sum of line 30 (a copy of
line 29) and the line 31 pension income amount; line 32, the caregiver amount, is not built."""

MB428_CREDITS_SUBTOTAL_LINE_36 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_36", non_negative=True
)
"""Credits subtotal, MB428 line 36 "Line 36: Add lines 33 to 35. = ^": lines 34 and 35, the
disability amounts, are not built, so the sum reads line 33 alone."""

MB428_CREDITS_SUBTOTAL_LINE_42 = AmountKind.declare(
    CATALOG, "mb428_credits_subtotal_line_42", non_negative=True
)
"""Credits subtotal, MB428 line 42 "Line 42: Add lines 36 to 41. = ^": the sum of line 36 and the
line 41 family tax benefit; lines 37 to 40, the optional student loan, tuition and transfer amounts,
are left blank and not built."""

MB428_CREDITS_TOTAL_LINE_51 = AmountKind.declare(
    CATALOG, "mb428_credits_total_line_51", non_negative=True
)
"""MB428 line 51 "Line 51 and line 58800: Line 42 plus line 50 = ^": the sum of line 42 and the
line 50 medical expense amount; lines 43 to 49, the medical expense working, are not built."""

MB428_CREDITS_AT_RATE_LINE_53 = AmountKind.declare(
    CATALOG, "mb428_credits_at_rate_line_53", non_negative=True
)
"""MB428 line 53 (line 58840) "Line 51 multiplied by the percentage from line 52 = ^": line 51
multiplied by the 10.8% of line 52, rounded half-up to the cent."""

MB479_FAMILY_INCOME_COLUMN_1_LINE_5 = AmountKind.declare(
    CATALOG, "mb479_family_income_column_1_line_5", non_negative=True
)
"""Family income, MB479 line 5 "Line 3 minus line 4 (if negative, enter "0")": line 3 less the UCCB
and RDSP income of line 4, floored at 0, column 1 (you) only."""

MB428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "mb428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, MB428 line 3 "Line 3: 0.00" (47,000.00; 100,000.00): the printed lower
bound of the column of lines 2 to 8 that line 1 falls in."""

MB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "mb428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, MB428 line 4 "Line 4: Line 2 minus line 3 (can not be
negative) =": line 1 minus line 3, not below zero."""

MB428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "mb428_bracket_rate_line_5", non_negative=True
)
"""Bracket column rate, MB428 line 5 (each column prints "Line 5: Rate" with 10.8%, 12.75% or
17.4%): the printed rate of the column of lines 2 to 8 that line 1 falls in."""

MB428_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "mb428_tax_on_excess_line_6", non_negative=True
)
"""Tax on the taxable income over the lower bound, MB428 line 6 "Line 6: Line 4 multiplied by the
percentage from line 5 =": line 4 times the line 5 rate, rounded half-up to the cent."""

MB479_AGE_CREDIT_LINE_8 = AmountKind.declare(CATALOG, "mb479_age_credit_line_8", non_negative=True)
"""Age credit for self, MB479 line 8 "Age credit for self (if you were born in 1960 or earlier)
Claim $113": the credit of the first box, a caller input that is read as blank when left out."""

MB479_SPOUSE_CREDITS_LINE_12 = AmountKind.declare(
    CATALOG, "mb479_spouse_credits_line_12", non_negative=True
)
"""Spouse or common-law partner credits, MB479 line 12 "Line 12 and line 60900: Add lines 9 to 11.":
the printed sum of lines 9 to 11, taken as one figure because those lines are not modelled, a caller
input that is read as blank when left out."""

MB479_ELIGIBLE_DEPENDANT_CREDIT_LINE_13 = AmountKind.declare(
    CATALOG, "mb479_eligible_dependant_credit_line_13", non_negative=True
)
"""Eligible dependant credit, MB479 line 13 "Credit for an eligible dependant claimed on line 58160
of your Form MB428 Claim $195": the credit of the box, a caller input that is read as blank when
left out."""

MB479_DISABILITY_CREDIT_LINE_14 = AmountKind.declare(
    CATALOG, "mb479_disability_credit_line_14", non_negative=True
)
"""Disability credit, MB479 line 14 "Number of disability claims Line 60950 multiplied by $113": the
product box, taken as one figure because the count above it is not modelled, a caller input that is
read as blank when left out."""

MB479_DISABLED_DEPENDANTS_CREDIT_LINE_15 = AmountKind.declare(
    CATALOG, "mb479_disabled_dependants_credit_line_15", non_negative=True
)
"""Disabled dependants credit, MB479 line 15 "Number of disabled dependants Line 60970 multiplied by
$62": the product box, taken as one figure because the count above it is not modelled, a caller
input that is read as blank when left out."""

MB479_DEPENDENT_CHILDREN_CREDIT_LINE_16 = AmountKind.declare(
    CATALOG, "mb479_dependent_children_credit_line_16", non_negative=True
)
"""Dependent children credit, MB479 line 16 "Number of dependent children Line 60999 multiplied by
$26": the product box, taken as one figure because the count above it is not modelled, a caller
input that is read as blank when left out."""

MB479_TOTAL_CREDITS_LINE_17 = AmountKind.declare(
    CATALOG, "mb479_total_credits_line_17", non_negative=True
)
"""Total credits, MB479 line 17 "Line 17 and line 61050: Add lines 7, 8, and 12 to 16. Total
credits": the basic credit of line 7 plus the credits of lines 8 and 12 to 16, each blank one taken
as 0."""

MB479_HOMEOWNER_RENTER_SENIOR_CREDITS_LINE_53 = AmountKind.declare(
    CATALOG, "mb479_homeowner_renter_senior_credits_line_53", non_negative=True
)
"""Homeowners, renters and seniors credits, MB479 line 53 "Line 53: Line 41 plus line 52 = ^": the
printed collecting sum of the skipped block of lines 20 to 52 (homeowners affordability, renters
affordability, seniors school tax rebate), a caller input that is read as blank when left out."""

MB479_EIA_MSPD_NUMBER_LINE_56 = AmountKind.declare(
    CATALOG, "mb479_eia_mspd_number_line_56", non_negative=True
)
"""EIA or MSPD number, MB479 line 56 "Line 56 and line 61255: If you (or your spouse or common-law
partner) did receive EIA or MSPD payments from Manitoba in 2025, enter the number from box 14 of
your (or your spouse's or common-law partner's) Form T5007, Statement of Benefits (even if it is
0.00)": the number from box 14 of Form T5007, a caller input that is read as 1 when left out."""

MB479_GREEN_ENERGY_PURCHASER_CREDIT_LINE_67 = AmountKind.declare(
    CATALOG, "mb479_green_energy_purchaser_credit_line_67", non_negative=True
)
"""Green energy equipment tax credit (purchaser), MB479 line 67 "Line 67 and line 61380: Complete
Form T1294": the credit worked out on Form T1294, which is not built, a caller input that is read
as blank when left out."""

MB479_GEOTHERMAL_HEAT_PUMP_COST_LINE_68 = AmountKind.declare(
    CATALOG, "mb479_geothermal_heat_pump_cost_line_68", non_negative=True
)
"""Geothermal heat pump cost, MB479 line 68 "Line 68 and line 61390: 7.5% of the adjusted cost of
geothermal heat pumps": the adjusted cost of geothermal heat pumps the 7.5% is taken of, a caller
input that is read as blank when left out."""

MB479_GEOTHERMAL_HEAT_PUMP_CREDIT_LINE_68 = AmountKind.declare(
    CATALOG, "mb479_geothermal_heat_pump_credit_line_68", non_negative=True
)
"""Green energy equipment tax credit (manufacturer), MB479 line 68 "Line 68 and line 61390: 7.5% of
the adjusted cost of geothermal heat pumps": calculated, 7.5% of the adjusted cost of geothermal
heat pumps, rounded half-up to the cent."""

MB428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "mb428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column, MB428 line 7 "Line 7: 0.00" (5,076.00; 11,833.50): the printed
tax at the start of the column of lines 2 to 8 that line 1 falls in. Column 3 is unbounded, so it is
never blank."""

MB479_FAMILY_INCOME_LINE_6 = AmountKind.declare(
    CATALOG, "mb479_family_income_line_6", non_negative=True
)
"""Family income, MB479 line 6: line 5 of column 1 (you) plus line 5 of column 2 (your spouse or
common-law partner), the amount that later lines refer to as "Amount from line 6". Column 2 is taken
as 0 when left out."""

MB479_REDUCTION_LINE_18 = AmountKind.declare(CATALOG, "mb479_reduction_line_18", non_negative=True)
"""Reduction, MB479 line 18: the amount from line 6 multiplied by 1%, the printed rate held in the
`ca-mb/personal_tax_credit_reduction_rate` dataset, rounded half-up to the cent."""

MB479_FERTILITY_TREATMENT_EXPENSES_LINE_61 = AmountKind.declare(
    CATALOG, "mb479_fertility_treatment_expenses_line_61", non_negative=True
)
"""Fertility treatment expenses, MB479 line 61 "Line 61: Eligible medical expenses for fertility
treatments Line 61268 multiplied by 40% (maximum $16,000)": the eligible medical expenses of the
first box, a caller input that is read as blank when left out."""

MB428_T691_AMOUNT_LINE_66 = AmountKind.declare(
    CATALOG, "mb428_t691_amount_line_66", non_negative=True
)
"""Form T691 amount, MB428 line 66 "Line 66: Form T691: line 1 minus line 2 of Part 7": a caller
input, read as blank when left out; the 50% multiplication step reads it."""

MB479_PAID_WORK_EXPERIENCE_CREDIT_LINE_63 = AmountKind.declare(
    CATALOG, "mb479_paid_work_experience_credit_line_63", non_negative=True
)
"""Paid work experience tax credit, MB479 line 63 "Line 63 and line 61310: Paid work experience tax
credit": the credit of the line, a caller input that is read as blank when left out."""

MB479_PERSONAL_TAX_CREDIT_LINE_19 = AmountKind.declare(
    CATALOG, "mb479_personal_tax_credit_line_19", non_negative=True
)
"""Personal tax credit, MB479 line 19 "Line 19: Line 17 minus line 18 (if negative, enter "0")
Enter this amount on line 54. Personal tax credit =": line 17 and line 18 (total credits less the
reduction, not below 0), rounded to the cent."""

MB479_FERTILITY_TREATMENT_CREDIT_BEFORE_MAXIMUM_LINE_61 = AmountKind.declare(
    CATALOG, "mb479_fertility_treatment_credit_before_maximum_line_61", non_negative=True
)
"""Fertility treatment tax credit before its maximum, MB479 line 61 "Line 61: Eligible medical
expenses for fertility treatments Line 61268 multiplied by 40% (maximum $16,000) =" before the
maximum: the eligible medical expenses multiplied by 40%."""

MB479_FERTILITY_TREATMENT_CREDIT_LINE_61 = AmountKind.declare(
    CATALOG, "mb479_fertility_treatment_credit_line_61", non_negative=True
)
"""Fertility treatment tax credit, MB479 line 61 "Line 61: Eligible medical expenses for fertility
treatments Line 61268 multiplied by 40% (maximum $16,000) =": calculated, the eligible medical
expenses multiplied by 40%, then at most the printed maximum of $16,000."""
