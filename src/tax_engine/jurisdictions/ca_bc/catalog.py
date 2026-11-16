"""The British Columbia artifact catalog: British Columbia's own kinds, named from the British
Columbia forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_bc import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

BC428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "bc428_taxable_income_line_1", non_negative=True
)
"""Taxable income, BC428 line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3, 4, 10 and 11."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, BC428 line 16 (line 58040) "Basic personal amount Claim $12,932": the
amount claimed, the first part of the total of the British Columbia credit amounts."""

BC428_SUBTOTAL_LINE_25 = AmountKind.declare(CATALOG, "bc428_subtotal_line_25", non_negative=True)
"""Subtotal of credit amounts, BC428 line 25 "Line 25: Add lines 16, 17, 20, 23 and 24.": the sum of
those lines, here the basic personal amount (line 16) alone."""

BC428_BRACKET_LOWER_BOUND_LINE_10 = AmountKind.declare(
    CATALOG, "bc428_bracket_lower_bound_line_10", non_negative=True
)
"""Lower bound of the column, BC428 line 10 "Line 10: 137,407.00": the printed lower bound of the
column of lines 9 to 15 that line 1 falls in, blank when line 1 is 137,407 or less."""

BC428_BRACKET_TAX_AT_START_LINE_14 = AmountKind.declare(
    CATALOG, "bc428_bracket_tax_at_start_line_14", non_negative=True
)
"""Tax at the start of the column, BC428 line 14 "Line 14: 10,801.15": the printed tax at the start
of the column of lines 9 to 15 that line 1 falls in, blank when line 1 is 137,407 or less."""

BC428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_11 = AmountKind.declare(
    CATALOG, "bc428_taxable_income_over_lower_bound_line_11", non_negative=True
)
"""Taxable income over the lower bound, BC428 line 11 "Line 11: Line 9 minus line 10 (cannot be
negative)": line 1 minus the lower bound of line 10, not below 0; blank when line 1 is 137,407.00
or less, where line 10 is blank."""

BC428_BRACKET_RATE_LINE_12 = AmountKind.declare(
    CATALOG, "bc428_bracket_rate_line_12", non_negative=True
)
"""Rate, BC428 line 12 "Line 12: Rate 14.7%; 16.8%; 20.5%": the printed rate of the column of lines
9 to 15 that line 1 falls in, blank when line 1 is 137,407 or less."""

BC428_BRACKET_TAX_LINE_13 = AmountKind.declare(
    CATALOG, "bc428_bracket_tax_line_13", non_negative=True
)
"""Tax on the part over the lower bound, BC428 line 13 "Line 13: Line 11 multiplied by the
percentage from line 12 =": line 11 times the line 12 rate, rounded to the cent; blank when line 11
or line 12 is blank, that is when line 1 is 137,407 or less."""

BC428_TAX_ON_TAXABLE_INCOME_LINE_15 = AmountKind.declare(
    CATALOG, "bc428_tax_on_taxable_income_line_15", non_negative=True
)
"""British Columbia tax on taxable income, BC428 line 15 "Line 13 plus line 14 British Columbia tax
on taxable income =": line 13 plus line 14 of the column that line 1 falls in; blank when lines 13
and 14 are blank."""

BC428_BASE_AMOUNT_LINE_75 = AmountKind.declare(
    CATALOG, "bc428_base_amount_line_75", non_negative=True
)
"""Base amount, BC428 line 75 "Line 75: Base amount 25,020.00": the printed amount the British
Columbia tax reduction starts from."""

BC428_CPP_CONTRIBUTIONS_LINE_27 = AmountKind.declare(
    CATALOG, "bc428_cpp_contributions_line_27", non_negative=True
)
"""CPP or QPP contributions, BC428 line 27 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

BC428_BRITISH_COLUMBIA_TAX_LINE_91 = AmountKind.declare(
    CATALOG, "bc428_british_columbia_tax_line_91", non_negative=True
)
"""British Columbia tax, BC428 line 91 "Enter this amount on line 42800 of your return.": the
British Columbia tax, entered on T1 line 42800."""

BC428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "bc428_pension_income_amount", non_negative=True
)
"""Pension income amount, BC428 line 36 "Line 36 and line 58360: Pension income amount (maximum
$1,000)": the amount the filer claims, a caller input that is read as blank when left out."""

BC428_QUALIFYING_GIFTS_LINE_59 = AmountKind.declare(
    CATALOG, "bc428_qualifying_gifts_line_59", non_negative=True
)
"""Amount of qualifying gifts also claimed on line 57, BC428 line 59 "Line 59 and line 58980: Amount
of qualifying gifts also claimed on line 57 multiplied by 25%": the amount the filer also claims on
line 57, a caller input that is read as blank when left out."""

BC428_MINIMUM_TAX_CARRYOVER_AMOUNT = AmountKind.declare(
    CATALOG, "bc428_minimum_tax_carryover_amount", non_negative=True
)
"""Amount from line 40427 of the return, BC428 line 66 "Line 66 and line 61540: Amount from line
40427 of your return": the minimum tax carryover amount, a caller input that is read as 0 when left
out."""

BC428_MINIMUM_TAX_CARRYOVER_LINE_66 = AmountKind.declare(
    CATALOG, "bc428_minimum_tax_carryover_line_66", non_negative=True
)
"""British Columbia minimum tax carryover, BC428 line 66 and line 61540 "Amount from line 40427 of
your return multiplied by 34.9% =": calculated, the amount from line 40427 multiplied by 34.9%."""

BC428_DIVIDEND_TAX_CREDIT_LINE_65 = AmountKind.declare(
    CATALOG, "bc428_dividend_tax_credit_line_65", non_negative=True
)
"""British Columbia dividend tax credit, BC428 line 65 "Line 65 and line 61520: British Columbia
dividend tax credit (use Worksheet BC428)": a caller input that is read as blank when left out."""

BC428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_71 = AmountKind.declare(
    CATALOG, "bc428_provincial_foreign_tax_credit_line_71", non_negative=True
)
"""British Columbia provincial foreign tax credit, BC428 line 71 "Line 71: Provincial foreign tax
credit (complete Form T2036)": a caller input that is read as blank when left out."""

BC428_POLITICAL_CONTRIBUTION_TAX_CREDIT_LINE_84 = AmountKind.declare(
    CATALOG, "bc428_political_contribution_tax_credit_line_84", non_negative=True
)
"""British Columbia political contribution tax credit, BC428 line 84 "Line 84: British Columbia
political contribution tax credit (use Worksheet BC428) (maximum $500)": a caller input that is
read as blank when left out."""

BC428_ESOP_EVCC_CREDITS_LINE_88 = AmountKind.declare(
    CATALOG, "bc428_esop_evcc_credits_line_88", non_negative=True
)
"""British Columbia total ESOP and EVCC credits, BC428 line 88 "Line 88: Line 86 plus line 87
(maximum $2,000)": a caller input that is read as blank when left out."""

BC428_ADDITIONAL_MINIMUM_TAX_AMOUNT_LINE_69 = AmountKind.declare(
    CATALOG, "bc428_additional_minimum_tax_amount_line_69"
)
"""Amount from line 14 of Part 7 of Form T691, BC428 line 69 "Amount from line 14 of Part 7 of Form
T691 multiplied by 34.9% =": the amount from Form T691, an optional input that a caller with no
minimum tax leaves out. The multiply is a separate step."""

BC428_ADDITIONAL_MINIMUM_TAX_LINE_69 = AmountKind.declare(
    CATALOG, "bc428_additional_minimum_tax_line_69", non_negative=True
)
"""British Columbia additional tax for minimum tax purposes, BC428 line 69 "Amount from line 14 of
Part 7 of Form T691 multiplied by 34.9% =": calculated, the Form T691 amount multiplied by 34.9%."""

BC428_DONATIONS_AND_GIFTS_LINE_57 = AmountKind.declare(
    CATALOG, "bc428_donations_and_gifts_line_57", non_negative=True
)
"""Donations and gifts, BC428 line 57 and line 58969 "Donations and gifts (use Worksheet BC428)":
the amount the filer claims, a caller input that is read as blank when left out."""

BC428_EI_PREMIUMS_LINE_29 = AmountKind.declare(
    CATALOG, "bc428_ei_premiums_line_29", non_negative=True
)
"""EI premiums credit amount, BC428 line 29 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

BC428_MEDICAL_EXPENSES_LINE_53 = AmountKind.declare(
    CATALOG, "bc428_medical_expenses_line_53", non_negative=True
)
"""Medical expenses, BC428 line 53 (line 58769) "Line 51 plus line 52 =": line 51 plus line 52, an
optional input; a blank is read as 0 by the step that reads it."""

BC428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "bc428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, BC428 line 3 "Line 3: 0.00" (49,279.00; 98,560.00; 113,158.00): the
printed lower bound of the column of lines 2 to 8 that line 1 falls in. It is blank when line 1 is
above 137,407, where lines 9 to 15 apply."""

BC428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "bc428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column, BC428 line 7 "Line 7: 0.00" (2,493.52; 6,288.15; 7,820.94): the
printed tax at the start of the column of lines 2 to 8 that line 1 falls in. It is blank when line 1
is above 137,407, where lines 9 to 15 apply."""

BC428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "bc428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, BC428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero; blank when line 3 is blank."""

BC428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "bc428_bracket_rate_line_5", non_negative=True
)
"""Rate of the column, BC428 line 5 "Line 5: Rate" (5.06%; 7.7%; 10.5%; 12.29%): the printed rate of
the column of lines 2 to 8 that line 1 falls in. It is blank when line 1 is above 137,407, where
lines 9 to 15 apply."""

BC428_BRACKET_TAX_LINE_6 = AmountKind.declare(
    CATALOG, "bc428_bracket_tax_line_6", non_negative=True
)
"""Tax on the part over the lower bound, BC428 line 6 "Line 6: Line 4 multiplied by the percentage
from line 5 =": line 4 times the line 5 rate, rounded to the cent; blank when line 4 or line 5 is
blank."""

BC428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "bc428_tax_on_taxable_income_line_8", non_negative=True
)
"""British Columbia tax on taxable income, BC428 line 8 "Line 6 plus line 7 British Columbia tax on
taxable income =": line 6 plus line 7 of the column that line 1 falls in; blank when lines 6 and 7
are blank."""

BC428_CPP_EI_AND_OTHER_LINE_33 = AmountKind.declare(
    CATALOG, "bc428_cpp_ei_and_other_line_33", non_negative=True
)
"""BC428 line 33 "Add lines 27 to 32.": the sum of lines
27 and 29. Lines 28, 30, 31 and 32 are not built: a salary-only filer has none of them."""

BC428_SUBTOTAL_LINE_35 = AmountKind.declare(CATALOG, "bc428_subtotal_line_35", non_negative=True)
"""Subtotal, BC428 line 35 "Line 35: Add lines 26, 33 and 34.": the sum of line 26 (a copy of line
25), line 33 and line 34. Line 34 (adoption expenses) is not built: a salary-only filer has none."""

BC428_SUBTOTAL_LINE_37 = AmountKind.declare(CATALOG, "bc428_subtotal_line_37", non_negative=True)
"""Subtotal, BC428 line 37 "Line 37: Line 35 plus line 36 = ^": the sum of line 35 and line 36, the
pension income amount, an optional input read as 0 when the filer has none."""

BC428_SUBTOTAL_LINE_40 = AmountKind.declare(CATALOG, "bc428_subtotal_line_40", non_negative=True)
"""Subtotal, BC428 line 40 "Line 40: Add lines 37 to 39. = ^": the sum of line 37. Lines 38 and 39
are the disability amounts, not built: a salary-only filer has none."""

BC428_SUBTOTAL_LINE_45 = AmountKind.declare(CATALOG, "bc428_subtotal_line_45", non_negative=True)
"""Subtotal, BC428 line 45 "Line 45: Add lines 40 to 44. = ^": the sum of line 40. Lines 41 to 44
are student loan interest, tuition and transfers, not built: a salary-only filer has none."""

BC428_TOTAL_LINE_54 = AmountKind.declare(CATALOG, "bc428_total_line_54", non_negative=True)
"""Total, BC428 line 54 and line 58800 "Line 45 plus line 53 = ^": line 45 plus line 53, the medical
expenses input read as 0 when blank."""

BC428_TAX_ON_SPLIT_INCOME_LINE_62 = AmountKind.declare(CATALOG, "bc428_tax_on_split_income_line_62")
"""British Columbia tax on split income, BC428 line 62 "Line 62 and line 61510: British Columbia tax
on split income (complete Form T1206)": the tax from Form T1206, an optional input that a
salary-only caller leaves out."""

BC428_AT_RATE_LINE_56 = AmountKind.declare(CATALOG, "bc428_at_rate_line_56", non_negative=True)
"""Credit amounts at the credit rate, BC428 line 56 (line 58840) "Line 54 multiplied by the
percentage from line 55 = ^": line 54 multiplied by the 5.06% of line 55, rounded half-up to the
cent."""

BC428_SUBTOTAL_LINE_58 = AmountKind.declare(CATALOG, "bc428_subtotal_line_58", non_negative=True)
"""Subtotal, BC428 line 58 "Line 56 plus line 57 = ^": line 56 plus line 57, the donations and gifts
input read as 0 when blank."""

BC428_FARMERS_FOOD_DONATION_CREDIT_LINE_59 = AmountKind.declare(
    CATALOG, "bc428_farmers_food_donation_credit_line_59", non_negative=True
)
"""Farmers' food donation credit amount, BC428 line 59 "Line 59 and line 58980: Amount of qualifying
gifts also claimed on line 57 multiplied by 25% = ^": the qualifying gifts times the 25% of the
dataset, rounded half-up to the cent; blank gifts are taken as 0."""

BC428_NON_REFUNDABLE_CREDITS_LINE_60 = AmountKind.declare(
    CATALOG, "bc428_non_refundable_credits_line_60", non_negative=True
)
"""Non-refundable tax credits, BC428 line 60 "Line 60 and line 61500: Line 58 plus line 59 Enter
this amount on line 64.": line 58 plus line 59."""

BC428_TOTAL_LINE_67 = AmountKind.declare(CATALOG, "bc428_total_line_67", non_negative=True)
"""Total, BC428 line 67 "Line 67: Add lines 64 to 66. = ^": line 64 (the non-refundable credits, a
copy of line 60) plus line 65 (the dividend tax credit, blank read as 0) plus line 66 (the minimum
tax carryover), rounded to the cent."""

BC428_TAX_AFTER_CREDITS_LINE_68 = AmountKind.declare(
    CATALOG, "bc428_tax_after_credits_line_68", non_negative=True
)
"""Tax after credits, BC428 line 68 "Line 68: Line 63 minus line 67 (if negative, enter "0") = ^":
line 63 (the tax with split income) minus line 67 (the total), not below 0, rounded to the cent."""

BC428_TAX_WITH_MINIMUM_TAX_LINE_70 = AmountKind.declare(
    CATALOG, "bc428_tax_with_minimum_tax_line_70", non_negative=True
)
"""Tax with the additional minimum tax, BC428 line 70 "Line 70: Line 68 plus line 69 = ^": line 68
(the tax after credits) plus line 69 (the additional minimum tax), rounded to the cent."""

BC428_TAX_AFTER_FOREIGN_CREDIT_LINE_72 = AmountKind.declare(
    CATALOG, "bc428_tax_after_foreign_credit_line_72", non_negative=True
)
"""Tax after the foreign tax credit, BC428 line 72 "Line 72: Line 70 minus line 71 (if negative,
enter "0") = ^": line 70 (the tax with the additional minimum tax) minus line 71 (the provincial
foreign tax credit, blank read as 0), not below 0, rounded to the cent."""

BC428_BRITISH_COLUMBIA_TAX_REDUCTION_LINE_79 = AmountKind.declare(
    CATALOG, "bc428_british_columbia_tax_reduction_line_79", non_negative=True
)
"""British Columbia tax reduction, BC428 line 79 "Line 79: Line 73 minus line 78 (if negative, enter
"0") British Columbia tax reduction = ^": line 73 (the basic reduction) minus line 78 (the
reduction clawback), not below 0, rounded to the cent."""

BC428_TAX_AFTER_REDUCTION_LINE_80 = AmountKind.declare(
    CATALOG, "bc428_tax_after_reduction_line_80", non_negative=True
)
"""Tax after the British Columbia tax reduction, BC428 line 80 "Line 80: Line 72 minus line 79 (if
negative, enter "0") = ^": line 72 (the tax after the foreign tax credit) minus line 79 (the British
Columbia tax reduction), not below 0, rounded to the cent."""

BC428_TAX_AFTER_LOGGING_CREDIT_LINE_82 = AmountKind.declare(
    CATALOG, "bc428_tax_after_logging_credit_line_82", non_negative=True
)
"""Tax after the logging tax credit, BC428 line 82 "Line 82: Line 80 minus line 81 (if negative,
enter "0") = ^": line 80 (the tax after the British Columbia tax reduction) minus line 81 (the
logging tax credit, read as 0 when blank), not below 0, rounded to the cent."""

BC479_NET_INCOME_LINE_1 = AmountKind.declare(CATALOG, "bc479_net_income_line_1", non_negative=False)
"""Net income, BC479 line 1 "Net income from line 23600 of the return (or the amount you would have
entered if the instructions on line 23600 said "if negative, show in brackets")": the net income of
the T1 return before its floor, read from the signed T1 net income export (`ca/net_income_signed`,
not the floored `ca/net_income`). Column 1 only. The form asks for the amount with a negative shown
in brackets, so the kind is signed."""

BC428_NET_INCOME_LINE_74 = AmountKind.declare(
    CATALOG, "bc428_net_income_line_74", non_negative=True
)
"""Net income, BC428 line 74 "Enter your net income from line 23600 of your return": the T1 net
income, line 23600 after its floor."""

BC428_NET_INCOME_OVER_BASE_LINE_76 = AmountKind.declare(
    CATALOG, "bc428_net_income_over_base_line_76", non_negative=True
)
"""Net income over the base amount, BC428 line 76 "Line 76: Line 74 minus line 75 (if negative,
enter "0") =": line 74 less line 75, not below zero."""

BC428_REDUCTION_CLAWBACK_LINE_78 = AmountKind.declare(
    CATALOG, "bc428_reduction_clawback_line_78", non_negative=True
)
"""British Columbia tax reduction clawback, BC428 line 78 "Line 76 multiplied by the percentage from
line 77 =": line 76 times the printed rate of line 77."""

BC479_BRITISH_COLUMBIA_CREDITS_LINE_45 = AmountKind.declare(
    CATALOG, "bc479_british_columbia_credits_line_45", non_negative=True
)
"""British Columbia credits, BC479 line 45 "Enter this amount on line 47900 of your return.": the
British Columbia credits, entered on T1 line 47900."""

BC479_UCCB_RDSP_REPAYMENTS_LINE_2 = AmountKind.declare(
    CATALOG, "bc479_uccb_rdsp_repayments_line_2", non_negative=True
)
"""UCCB and RDSP repayments, BC479 line 2 "Total of the universal child care benefit (UCCB)
repayment (line 21300 of the return) and the registered disability savings plan (RDSP) income
repayment (included on line 23200 of the return)": the total of the two repayments, a caller input
that is read as blank when left out, column 1 (you) only."""

BC479_INCOME_WITH_REPAYMENTS_LINE_3 = AmountKind.declare(
    CATALOG, "bc479_income_with_repayments_line_3", non_negative=False
)
"""Income with repayments, BC479 line 3 "Line 1 plus line 2": line 1 plus line 2, the UCCB and RDSP
repayments input read as 0 when blank. The result is signed, because line 1 is signed."""

BC479_ADJUSTED_NET_INCOME_LINE_5 = AmountKind.declare(
    CATALOG, "bc479_adjusted_net_income_line_5", non_negative=True
)
"""Adjusted net income, BC479 line 5 "Line 5: Line 3 minus line 4 (if negative, enter "0")": line 3
(the income with repayments) minus line 4 (the UCCB and RDSP income, read as 0 when blank), floored
at 0 as the form prints, rounded to the cent."""

BC479_ADJUSTED_FAMILY_NET_INCOME_LINE_6 = AmountKind.declare(
    CATALOG, "bc479_adjusted_family_net_income_line_6", non_negative=True
)
"""Adjusted family net income, BC479 line 6 "Line 6: Add the amounts from line 5 of columns 1 and
2.": the sum of line 5 of the two columns; the spouse column is not built, so it is line 5 of column
1 alone."""

BC479_THRESHOLD_LINE_7 = AmountKind.declare(CATALOG, "bc479_threshold_line_7", non_negative=True)
"""Threshold, BC479 line 7 "Line 7: If you had a spouse or common-law partner on December 31, 2025,
enter $18,000. If not, enter $15,000.": the printed amount without a spouse, $15,000; the spouse
amount is not built."""

BC479_INCOME_FOR_SALES_TAX_CREDIT_LINE_8 = AmountKind.declare(
    CATALOG, "bc479_income_for_sales_tax_credit_line_8", non_negative=True
)
"""Income for the sales tax credit, BC479 line 8 "Line 8: Line 6 minus line 7 (if negative, enter
"0") Income for the sales tax credit = ^": line 6 (the adjusted family net income) minus line 7 (the
threshold), not below 0, rounded to the cent."""

BC479_INCOME_REDUCTION_LINE_12 = AmountKind.declare(
    CATALOG, "bc479_income_reduction_line_12", non_negative=True
)
"""Income reduction, BC479 line 12 "Line 12: Amount from line 8 ^ multiplied by 2% = ^": line 8
(the income for the sales tax credit) times the printed 2%, rounded to the cent."""

BC479_BASIC_SALES_TAX_CREDIT_LINE_9 = AmountKind.declare(
    CATALOG, "bc479_basic_sales_tax_credit_line_9", non_negative=True
)
"""Basic sales tax credit, BC479 line 9 (line 60330) "Basic sales tax credit Claim $75": the amount
claimed, the same at every income."""

BC428_BRITISH_COLUMBIA_TAX_ON_TAXABLE_INCOME_LINE_61 = AmountKind.declare(
    CATALOG, "bc428_british_columbia_tax_on_taxable_income_line_61", non_negative=True
)
"""British Columbia tax on taxable income, BC428 line 61 "Line 61: British Columbia tax on taxable
income from line 8 or 15 ^": the amount of line 8 or of line 15, whichever the taxable income is
in; the other is blank."""

BC428_BASIC_REDUCTION_LINE_73 = AmountKind.declare(
    CATALOG, "bc428_basic_reduction_line_73", non_negative=True
)
"""Basic reduction, BC428 line 73 "Basic reduction Claim $562": the amount claimed, the British
Columbia basic tax reduction, claimed whole at every salary (line 79 phases it out)."""

BC428_TAX_WITH_SPLIT_INCOME_LINE_63 = AmountKind.declare(
    CATALOG, "bc428_tax_with_split_income_line_63"
)
"""Tax with split income, BC428 line 63 "Line 63: Line 61 plus line 62 = ^": line 61 plus line 62,
the tax on split income input read as 0 when blank. The form prints no floor for the line, so the
kind is signed."""

BC428_LOGGING_TAX_CREDIT_LINE_81 = AmountKind.declare(
    CATALOG, "bc428_logging_tax_credit_line_81", non_negative=True
)
"""British Columbia logging tax credit, BC428 line 81 "Line 81: British Columbia logging tax credit
from Form FIN 542S or Form FIN 542P": a caller input that is read as blank when left out."""

BC479_UCCB_RDSP_INCOME_LINE_4 = AmountKind.declare(
    CATALOG, "bc479_uccb_rdsp_income_line_4", non_negative=True
)
"""UCCB and RDSP income, BC479 line 4 "Total of the UCCB income (line 11700 of the return) and the
RDSP income (line 12500 of the return)": the total of the two incomes, a caller input that is read
as blank when left out, column 1 (you) only."""

BC479_HOME_RENOVATION_EXPENSES_LINE_14 = AmountKind.declare(
    CATALOG, "bc479_home_renovation_expenses_line_14", non_negative=True
)
"""Home renovation expenses, BC479 line 14 "Enter your home renovation expenses from line 5 of your
Schedule BC(S12). (maximum $10,000)": the amount from line 5 of Schedule BC(S12), a caller input
that is read as blank when left out."""

BC479_CREDIT_BEFORE_REDUCTION_LINE_11 = AmountKind.declare(
    CATALOG, "bc479_credit_before_reduction_line_11", non_negative=True
)
"""Credit before the income reduction, BC479 line 11 "Line 11: Line 9 plus line 10 = ^": the basic
sales tax credit (line 9) plus the spouse or common-law partner additional credit (line 10)."""

BC479_SALES_TAX_CREDIT_LINE_13 = AmountKind.declare(
    CATALOG, "bc479_sales_tax_credit_line_13", non_negative=True
)
"""Sales tax credit, BC479 line 13 "Line 13: Line 11 minus line 12 (if negative, enter "0") Sales
tax credit = ^": line 11 (the credit before the income reduction) minus line 12 (the income
reduction), not below 0, rounded to the cent."""
