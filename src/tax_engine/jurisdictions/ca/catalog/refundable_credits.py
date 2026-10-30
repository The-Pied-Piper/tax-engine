"""The federal catalog: refundable credits and payments.

Provincial credits, the multigenerational home renovation credit, the GST/HST rebate, the educator
and journalism credits, instalments and the refundable medical expense supplement.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

PROVINCIAL_CREDITS = CATALOG.declare("provincial_credits", Decimal, non_negative=True)
"""Provincial or territorial credits, T1 line 165 and line 47900 "Provincial or territorial credits
(complete Form 479, if it applies)": the Ontario credits, Form ON479 line 21."""

CANADA_TRAINING_CREDIT = CATALOG.declare("canada_training_credit", Decimal, non_negative=True)
"""Canada training credit, Schedule 11 line 5 "Enter this amount on line 45350 of your return. Your
Canada training credit", T1 line 156 and line 45350 "Canada training credit (CTC) (complete
Schedule 11)": the amount claimed, at most line 4 (the lesser of 50% of the Canadian tuition fees
and the limit on the notice)."""

HOME_RENOVATION_EXPENDITURES = CATALOG.declare(
    "home_renovation_expenditures", Decimal, non_negative=True
)
"""Total qualifying expenditures of a renovation, Schedule 12 Step 1 line 1 "Total amount paid from
all sales slips and contracts included in the table above and any additional sheets of paper Total
qualifying expenditures": the amount paid for one qualifying renovation, a field of each record of
`ca/home_renovations`."""

HOME_RENOVATION_REIMBURSED = CATALOG.declare(
    "home_renovation_reimbursed", Decimal, non_negative=True
)
"""Amount reimbursed for a renovation, Schedule 12 Step 1 line 2 "Any amount that can reasonably be
considered to be reimbursed (including government assistance received or receivable) included in
the amount on line 1": a field of each record of `ca/home_renovations`."""

HOME_RENOVATION_CLAIMED_BY_OTHERS = CATALOG.declare(
    "home_renovation_claimed_by_others", Decimal, non_negative=True
)
"""Amount claimed by other eligible individuals for a renovation, Schedule 12 Step 1 line 5 "Amount
of eligible expenses being claimed by other eligible individuals": a field of each record of
`ca/home_renovations`."""

HOME_RENOVATIONS = RecordListKind.declare(
    CATALOG,
    "home_renovations",
    fields=(
        HOME_RENOVATION_EXPENDITURES,
        HOME_RENOVATION_REIMBURSED,
        HOME_RENOVATION_CLAIMED_BY_OTHERS,
    ),
)
"""Qualifying renovations, Schedule 12 Step 1 "If you paid qualifying expenditures for more than one
qualifying renovation, complete this step for each qualifying renovation using an additional sheet
of paper": a starting list with one record for each qualifying renovation, holding lines 1, 2 and 5.
The caller lists only the renovations that qualify, and the expenses claimed for the medical expense
or home accessibility credit are left out of line 1."""

HOME_RENOVATION_LINE_3 = CATALOG.declare("home_renovation_line_3", Decimal, non_negative=True)
"""Schedule 12 Step 1 line 3 "Line 1 minus line 2 (maximum $50,000 per qualifying renovation)": the
total over the renovations of the renovation's line 1 less its line 2, at most the line 4 maximum,
a part of line 7 and line 8. The caller keeps line 2 within line 1, so it is not below 0."""

HOME_RENOVATION_LINE_6 = CATALOG.declare("home_renovation_line_6", Decimal, non_negative=True)
"""Schedule 12 Step 1 line 6 "Line 4 minus line 5": the total over the renovations of the maximum
per qualifying renovation less line 5. The caller keeps line 5 within the maximum, so it is not
below 0."""

HOME_RENOVATION_LINE_8 = CATALOG.declare("home_renovation_line_8", Decimal, non_negative=True)
"""Schedule 12 Step 2 line 8 and line 45354 "Add the amounts from line 7 for each qualifying
renovation. Your total qualifying expenditures": the total over the renovations of the lesser of
line 3 and line 6 (line 7, "Enter whichever is less: amount from line 3 or line 6. Your qualifying
expenditures for the qualifying renovation")."""

MULTIGENERATIONAL_HOME_RENOVATION_CREDIT = CATALOG.declare(
    "multigenerational_home_renovation_credit", Decimal, non_negative=True
)
"""Multigenerational home renovation tax credit, T1 line 157 and line 45355 "Multigenerational home
renovation tax credit (MHRTC) (complete Schedule 12)": Schedule 12 line 10 "Line 8 multiplied by the
percentage from line 9 Enter this amount on line 45355 of your return", line 9 being the applicable
rate of 14.5%, rounded to the cent."""

PART_XII_2_TAX_CREDIT = CATALOG.declare("part_xii_2_tax_credit", Decimal, non_negative=True)
"""Part XII.2 tax credit, T1 line 159 (45600) "Part XII.2 tax credit (box 38 of all T3 slips and
box 209 of all T5013 slips)": the amount of those boxes, added by the filer."""

EMPLOYEE_AND_PARTNER_GST_HST_REBATE = CATALOG.declare(
    "employee_and_partner_gst_hst_rebate", Decimal, non_negative=True
)
"""Employee and partner GST/HST rebate, T1 line 160 (45700) "Employee and partner GST/HST rebate
(complete Form GST370)": the rebate of Form GST370, taken as entered."""

EDUCATOR_SUPPLIES_EXPENSES = CATALOG.declare(
    "educator_supplies_expenses", Decimal, non_negative=True
)
"""Educator supplies expenses, T1 line 46800 on the eligible educator school supply tax credit
"Supplies expenses (maximum $1,000) Line 46800": the eligible supplies paid, before the maximum."""

EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM = CATALOG.declare(
    "educator_supplies_expenses_at_most_maximum", Decimal, non_negative=True
)
"""Educator supplies expenses that count, T1 line 161 and line 46900 "Supplies expenses (maximum
$1,000) Line 46800": line 46800 up to the printed maximum of $1,000, which sits before the
percentage, so it caps the supplies expenses and not the credit."""

EDUCATOR_SCHOOL_SUPPLY_CREDIT = CATALOG.declare(
    "educator_school_supply_credit", Decimal, non_negative=True
)
"""Eligible educator school supply tax credit, T1 line 161 and line 46900 "Supplies expenses
(maximum $1,000) Line 46800 multiplied by 25% =": the supplies expenses that count, at 25%."""

JOURNALISM_LABOUR_TAX_CREDIT = CATALOG.declare(
    "journalism_labour_tax_credit", Decimal, non_negative=True
)
"""Canadian journalism labour tax credit, T1 line 162 (47555) "Canadian journalism labour tax
credit (box 236 of all T5013 slips)": the total of amount 5B of Form T2125 over the statements."""

TAX_PAID_BY_INSTALMENTS = CATALOG.declare("tax_paid_by_instalments", Decimal, non_negative=True)
"""Tax paid by instalments, T1 line 164 (47600) "Tax paid by instalments": the instalments paid
for the year, as entered."""

NET_BUSINESS_INCOME = CATALOG.declare("net_business_income", Decimal, non_negative=True)
"""Net business income, line 13500 "Business income": the profits only of the Form T2125 statements,
the positive net income of each statement added, so a loss counts 0."""

NET_PROFESSIONAL_INCOME = CATALOG.declare("net_professional_income", Decimal, non_negative=True)
"""Net professional income, line 13700 "Professional income": the professional income of T1
line 13700 not below zero, so a loss counts 0."""

NET_COMMISSION_INCOME = CATALOG.declare("net_commission_income", Decimal, non_negative=True)
"""Net commission income, line 13900 "Commission income": the commission income of T1 line 13900
not below zero, so a loss counts 0."""

NET_FARMING_INCOME = CATALOG.declare("net_farming_income", Decimal, non_negative=True)
"""Net farming income, line 14100 "Farming income": the profits only of the Form T2042 statements,
the positive net income of each statement added, so a loss counts 0."""

NET_FISHING_INCOME = CATALOG.declare("net_fishing_income", Decimal, non_negative=True)
"""Net fishing income, line 14300 "Fishing income": the profits only of the Form T2121 statements,
the positive net income of each statement added, so a loss counts 0."""

MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME = CATALOG.declare(
    "medical_supplement_employment_income", Decimal, non_negative=True
)
"""Employment income for the supplement, Federal Worksheet "Line 45200 - Refundable medical expense
supplement" "your employment income from lines 10100 and 10400 of your return": employment income
(line 10100) plus other employment income (line 10400)."""

MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS = CATALOG.declare(
    "medical_supplement_employment_income_less_wage_loss", Decimal
)
"""Employment income other than wage-loss replacement plan amounts, Federal Worksheet "Line 45200 -
Refundable medical expense supplement" "(other than amounts received from a wage-loss replacement
plan)": the employment income less those amounts. The worksheet floors only the result after the
deductions ("if the result is negative, consider it as "0""), so the kind is signed."""

MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS = CATALOG.declare(
    "medical_supplement_employment_deductions", Decimal, non_negative=True
)
"""Employment deductions for the supplement, Federal Worksheet "Line 45200 - Refundable medical
expense supplement" "minus the amounts from lines 20700, 21200, 22900, and 23100 of your return":
the registered pension plan deduction, the union dues, the other employment expenses and the clergy
residence deduction, in line order."""

MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME = CATALOG.declare(
    "medical_supplement_employment_working_income", Decimal, non_negative=True
)
"""Employment part of the working income, Federal Worksheet "Line 45200 - Refundable medical expense
supplement" "your employment income ... minus the amounts from lines 20700, 21200, 22900, and 23100
of your return (if the result is negative, consider it as "0")"."""

MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME = CATALOG.declare(
    "medical_supplement_self_employment_income", Decimal, non_negative=True
)
"""Net self-employment income for the supplement, Federal Worksheet "Line 45200 - Refundable medical
expense supplement" "your net self-employment income (not including losses) from lines 13500,
13700, 13900, 14100, and 14300 of your return": the five lines, in line order."""

MEDICAL_SUPPLEMENT_WORKING_INCOME = CATALOG.declare(
    "medical_supplement_working_income", Decimal, non_negative=True
)
"""Working income for the supplement, Federal Worksheet "Line 45200 - Refundable medical expense
supplement" "In addition, the total of the following two amounts must be $4,390 or more": the
employment part and the net self-employment income. It is the gate of the supplement."""

MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3 = CATALOG.declare("medical_supplement_column_1_line_3", Decimal)
"""Your column, Federal Worksheet "Line 45200 - Refundable medical expense supplement" line 3
"Line 1 plus line 2": line 1 is the TOSI-adjusted net income of Form T1206 Part 1 line 6, whose
line 5 is the "amount you would have entered if the instructions on line 23600 said "if negative,
show in brackets"" (line 23400 less line 23500), and line 2 the UCCB and RDSP income
repayments. The form prints no
"(if negative, enter "0")" on line 3, so the kind is signed."""

MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5 = CATALOG.declare(
    "medical_supplement_column_1_line_5", Decimal, non_negative=True
)
"""Your column, Federal Worksheet "Line 45200 - Refundable medical expense supplement" line 5
"Line 3 minus line 4 (if negative, enter "0")": line 4 is the UCCB income and RDSP income."""

MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2 = CATALOG.declare(
    "medical_supplement_column_2_line_2", Decimal, non_negative=True
)
"""Your spouse or common-law partner's column, Federal Worksheet "Line 45200 - Refundable medical
expense supplement" line 2: the total of their UCCB repayment and RDSP income repayment."""

MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3 = CATALOG.declare("medical_supplement_column_2_line_3", Decimal)
"""Your spouse or common-law partner's column, Federal Worksheet "Line 45200 - Refundable medical
expense supplement" line 3 "Line 1 plus line 2". The form prints no "(if negative, enter "0")" on
line 3, so the kind is signed."""

MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4 = CATALOG.declare(
    "medical_supplement_column_2_line_4", Decimal, non_negative=True
)
"""Your spouse or common-law partner's column, Federal Worksheet "Line 45200 - Refundable medical
expense supplement" line 4 "Total of the UCCB income (line 11700 of the return) and the RDSP income
(line 12500 of the return)"."""

MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5 = CATALOG.declare(
    "medical_supplement_column_2_line_5", Decimal, non_negative=True
)
"""Your spouse or common-law partner's column, Federal Worksheet "Line 45200 - Refundable medical
expense supplement" line 5 "Line 3 minus line 4 (if negative, enter "0")"."""

MEDICAL_SUPPLEMENT_LINE_6 = CATALOG.declare("medical_supplement_line_6", Decimal, non_negative=True)
"""Adjusted family net income, Federal Worksheet "Line 45200 - Refundable medical expense
supplement" line 6 "Add the amounts from line 5 of columns 1 and 2. Adjusted family net income"."""

MEDICAL_SUPPLEMENT_INCOME_THRESHOLD = CATALOG.declare(
    "medical_supplement_income_threshold", Decimal, non_negative=True
)
"""Income threshold, Federal Worksheet "Line 45200 - Refundable medical expense supplement" line 7
"Income threshold 33,294.00": the printed constant, claimed whole."""

MEDICAL_SUPPLEMENT_LINE_8 = CATALOG.declare("medical_supplement_line_8", Decimal, non_negative=True)
"""Refundable medical expense supplement line 8, Federal Worksheet "Line 45200 - Refundable
medical expense supplement" line 8 "Line 6 minus line
7 (if negative, enter "0") =": the adjusted family net income over the income threshold."""

MEDICAL_SUPPLEMENT_LINE_11 = CATALOG.declare(
    "medical_supplement_line_11", Decimal, non_negative=True
)
"""Refundable medical expense supplement line 11, Federal Worksheet "Line 45200 - Refundable
medical expense supplement" line 11 "Line 9 plus line
10": the amount from line 21500 (line 9) plus the amount from line 33200 (line 10). It is 0 when
neither line has an amount, which is the worksheet's "You entered an amount on line 21500 or line
33200 of your return"."""

MEDICAL_SUPPLEMENT_LINE_13 = CATALOG.declare(
    "medical_supplement_line_13", Decimal, non_negative=True
)
"""Refundable medical expense supplement line 13, Federal Worksheet "Line 45200 - Refundable
medical expense supplement" line 13 "Line 11
multiplied by the percentage from line 12 =", line 12 being "Applicable rate 25%"."""

MEDICAL_SUPPLEMENT_LINE_14 = CATALOG.declare(
    "medical_supplement_line_14", Decimal, non_negative=True
)
"""Refundable medical expense supplement line 14, Federal Worksheet "Line 45200 - Refundable
medical expense supplement" line 14 "Enter whichever
is less: amount from line 13 or $1,504"."""

MEDICAL_SUPPLEMENT_LINE_15 = CATALOG.declare(
    "medical_supplement_line_15", Decimal, non_negative=True
)
"""Refundable medical expense supplement line 15, Federal Worksheet "Line 45200 - Refundable
medical expense supplement" line 15 "Amount from line
8 multiplied by 5% =": the reduction for the income over the threshold."""

MEDICAL_SUPPLEMENT_LINE_16 = CATALOG.declare(
    "medical_supplement_line_16", Decimal, non_negative=True
)
"""Refundable medical expense supplement line 16, Federal Worksheet "Line 45200 - Refundable
medical expense supplement" line 16 "Line 14 minus
line 15 (if negative, enter "0") Enter this amount on line 45200 of your return. =", before the
conditions the worksheet states.

"Your adjusted family net income is less than $63,374" has no step of its own: at $63,374 line 15
is 5% of 30,080, which is $1,504, so line 16 is already 0 there."""

MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET = CATALOG.declare(
    "medical_supplement_if_working_income_met", Decimal, non_negative=True
)
"""Line 16 when the working income is enough, Federal Worksheet "Line 45200 - Refundable medical
expense supplement" "In addition, the total of the following two amounts must be $4,390 or more":
line 16 when the working income is $4,390 or more, else 0."""

MEDICAL_SUPPLEMENT_IF_RESIDENT = CATALOG.declare(
    "medical_supplement_if_resident", Decimal, non_negative=True
)
"""Line 16 when the filer was resident, Federal Worksheet "Line 45200 - Refundable medical expense
supplement" "You were resident in Canada throughout 2025": the amount of the working income
condition times the caller's count of 0 or 1."""

REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT = CATALOG.declare(
    "refundable_medical_expense_supplement", Decimal, non_negative=True
)
"""Refundable medical expense supplement, T1 line 154 and line 45200 "Refundable medical expense
supplement (use Federal Worksheet)": line 16 of the Federal Worksheet "Line 45200 - Refundable
medical expense supplement" when every condition it states holds, else 0: the working income of
$4,390 or more, "You were resident in Canada throughout 2025" and "You were 18 years of age or older
at the end of 2025" (each a caller's count of 0 or 1). "You entered an amount on line 21500 or line
33200 of your return" and "Your adjusted family net income is less than $63,374" take no step, as
lines 11 and 16 are already 0 there."""
