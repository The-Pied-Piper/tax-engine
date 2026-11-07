"""The federal catalog: federal tax payable.

Special taxes, Form RC359 (tax on excess employees profit sharing plan amounts, one copy for each
employer), net federal tax, total payable and income tax deducted.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind, CountKind, RecordListKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

RC359_EPSP_CONTRIBUTIONS = AmountKind.declare(
    CATALOG, "rc359_epsp_contributions", non_negative=True
)
"""Employer contributions to an employees profit sharing plan, Form RC359 line 1 "If you are a
specified employee, enter the amount of contributions from box 41 of your T4PS slip.": the
contributions of the employer's T4PS slips, totalled."""

RC359_EMPLOYMENT_INCOME = AmountKind.declare(CATALOG, "rc359_employment_income", non_negative=True)
"""Employment income from the employer, Form RC359 line 2 "Enter the employment income reported on
your T4 slip(s) from the employer who made the EPSP contributions. Also include wage loss
replacement benefits received related to this employment.": the employment income of the T4 slips
from the employer, the base of the 20 percent."""

RC359_OTHER_EMPLOYMENT_INCOME = AmountKind.declare(
    CATALOG, "rc359_other_employment_income", non_negative=True
)
"""Security options benefits and other employment income, Form RC359 line 3 "Enter the security
options benefits (boxes 38 and 90 of your T4 slip) and other employment income (box 35 of your T4PS
slip) related to the employment income reported on line 2.": the security options and other
employment income that line 4 takes off the employment income."""

RC359_PROVINCE = CountKind.declare(CATALOG, "rc359_province", non_negative=True)
"""Province or territory of residence at the end of the year, Form RC359 line 8 "Enter the rate for
your province or territory of residence at the end of the year using the charts below. (If you were
not a resident of a province or territory in Canada, enter the rate for "Other".)": the code of the
chart, 1 Newfoundland and Labrador to 14 Other (non-resident); a code the chart does not list is
refused."""

RC359_LINE_4 = AmountKind.declare(CATALOG, "rc359_line_4")
"""Employment income less the other employment income, Form RC359 line 4 "Line 2 minus line 3": line
2 less line 3.

The form prints no "(if negative, enter "0")", so the kind is signed.
"""

RC359_LINE_6 = AmountKind.declare(CATALOG, "rc359_line_6")
"""Employment income at 20 percent, Form RC359 line 6 "Line 4 multiplied by the percentage from line
5": line 4 at the rate of line 5 "Rate × 20%", rounded half-up to the cent.

The form prints no "(if negative, enter "0")", so the kind is signed, as line 4 is.
"""

RC359_EXCESS_EPSP_AMOUNT = AmountKind.declare(
    CATALOG, "rc359_excess_epsp_amount", non_negative=True
)
"""Excess EPSP amount, Form RC359 line 7 "Line 1 minus line 6 (if negative, enter "0")": the
contributions less line 6, not below zero, "Excess EPSP amount", of each copy of the form. The
return's line 22900 reads the total of these over the copies (`rc359_excess_epsp_total`)."""

RC359_EXCESS_EPSP_TOTAL = AmountKind.declare(CATALOG, "rc359_excess_epsp_total", non_negative=True)
"""Excess EPSP amounts, the total of Form RC359 line 7 "Excess EPSP amount" over the copies of the
form, one for each employer (0 with none): T1 line 22900 "Other employment expenses (see Guide
T4044)" adds it to Form T777 line 17 (`other_employment_expenses`)."""

RC359_LINE_8 = AmountKind.declare(CATALOG, "rc359_line_8", non_negative=True)
"""Province percentage, Form RC359 line 8 "Enter the rate for your province or territory of
residence at the end of the year using the charts below": the printed percentage of the province
code (`rc359_province`), as a percentage and not a rate."""

RC359_TAX_ON_EXCESS_EPSP = AmountKind.declare(
    CATALOG, "rc359_tax_on_excess_epsp", non_negative=True
)
"""Tax on excess EPSP amount, Form RC359 line 9 "Line 7 multiplied by the percentage from line 8.
Include this amount on line 41800 of your return.": the excess EPSP amount at the province
percentage, rounded half-up to the cent once, for each copy of the form."""

RC359_EMPLOYERS = RecordListKind.declare(
    CATALOG,
    "rc359_employers",
    fields=(
        RC359_EPSP_CONTRIBUTIONS,
        RC359_EMPLOYMENT_INCOME,
        RC359_OTHER_EMPLOYMENT_INCOME,
        RC359_PROVINCE,
    ),
)
"""Form RC359, Tax on Excess Employees Profit Sharing Plan Amounts, "If you have EPSPs from
different employers, complete a separate form for each employer": one record for each employer, in
the order the filer gives them (any number, none included), holding the inputs of lines 1, 2, 3 and
8 of its copy."""

SPECIAL_TAXES = AmountKind.declare(CATALOG, "special_taxes", non_negative=True)
"""Special taxes, T1 line 141 (line 41800) "Special taxes": the additional tax on RESP accumulated
income payments (`resp_aips_additional_tax`, Form T1172), the tax for not purchasing replacement
shares in a Quebec labour-sponsored fund (`rl_10_labour_sponsored_fund_amount`) and the tax on
excess employees profit sharing plan amounts (`rc359_tax_total`, Form RC359 line 9 of each copy)."""

RC359_TAX_TOTAL = AmountKind.declare(CATALOG, "rc359_tax_total", non_negative=True)
"""Tax on excess EPSP amounts, T1 line 41800 "Special taxes": the total of Form RC359 line 9 "Tax on
excess EPSP amount" over the copies of the form, one for each employer (0 with none). Added into
`special_taxes`."""

SPLIT_INCOME_LINE_10 = AmountKind.declare(CATALOG, "split_income_line_10", non_negative=True)
"""Tax on split income with the advanced Canada workers benefit, Form T1206 Part 2 line 10 "Line 8
plus line 9", line 9 being "Amount from line 41500 of your return": the federal tax on split income
plus the advanced Canada workers benefit."""

SPLIT_INCOME_LINE_13 = AmountKind.declare(CATALOG, "split_income_line_13", non_negative=True)
"""Disability amounts on split income, Form T1206 Part 2 line 13 "Line 11 plus line 12", line 11
being "Amount from line 31600 of your return" and line 12 "Amount from line 31800 of your return":
the disability amount for self plus the disability amount transferred from a dependant, under
"Federal disability tax credit"."""

SPLIT_INCOME_LINE_14 = AmountKind.declare(CATALOG, "split_income_line_14", non_negative=True)
"""Disability tax credit on split income, Form T1206 Part 2 line 14, line 13 "× 14.5%": the
disability amounts at the credit rate."""

SPLIT_INCOME_LINE_15 = AmountKind.declare(CATALOG, "split_income_line_15")
"""Tax on split income less the disability credit, Form T1206 Part 2 line 15 "Line 10 minus line
14": line 10 less the disability credit.

The form prints no "(if negative, enter "0")", so the kind is signed.
"""

SPLIT_INCOME_LINE_18 = AmountKind.declare(CATALOG, "split_income_line_18", non_negative=True)
"""Eligible dividends on split income, Form T1206 Part 2 line 18 "Line 16 minus line 17 (if
negative, enter "0")": line 16 (the dividends of line 1 of Part 1) less line 17 (the dividends other
than eligible of line 2), not below zero, under "Federal dividend tax credit on split income"."""

SPLIT_INCOME_LINE_19 = AmountKind.declare(CATALOG, "split_income_line_19", non_negative=True)
"""Dividend tax credit on split income, other than eligible, Form T1206 Part 2 line 19, line 17 "×
9.0301%": line 17 at the dividend tax credit rate for dividends other than eligible."""

SPLIT_INCOME_LINE_20 = AmountKind.declare(CATALOG, "split_income_line_20", non_negative=True)
"""Dividend tax credit on split income, eligible, Form T1206 Part 2 line 20, line 18 "× 15.0198%":
line 18 at the dividend tax credit rate for eligible dividends."""

SPLIT_INCOME_LINE_21 = AmountKind.declare(CATALOG, "split_income_line_21", non_negative=True)
"""Dividend tax credit on split income, Form T1206 Part 2 line 21 "Line 19 plus line 20": the
federal dividend tax credit on split income."""

SPLIT_INCOME_LINE_22 = AmountKind.declare(CATALOG, "split_income_line_22")
"""Tax on split income after the credits, Form T1206 Part 2 line 22 "Line 15 minus line 21": line 15
less the dividend tax credit.

The form prints no "(if negative, enter "0")", so the kind is signed.
"""

SPLIT_INCOME_LINE_23 = AmountKind.declare(CATALOG, "split_income_line_23", non_negative=True)
"""Federal foreign tax credit on split income, Form T1206 Part 2 line 23 "Part of the amount on
line 3 that is from foreign sources" (68370) over "Total income from foreign sources" (68380),
"× Amount from line 40500 of your return": the federal foreign tax credit times the share of the
split income that is from foreign sources, 0 when there is no income from foreign sources."""

SPLIT_INCOME_LINE_24 = AmountKind.declare(CATALOG, "split_income_line_24", non_negative=True)
"""Tax on split income after the credits, not below zero, Form T1206 Part 2 line 24 "Line 22 minus
line 23 (if negative, enter "0")": line 22 less line 23, the federal foreign tax credit on split
income."""

SPLIT_INCOME_LINE_29 = AmountKind.declare(CATALOG, "split_income_line_29", non_negative=True)
"""Federal tax less credits with the advanced Canada workers benefit, Form T1206 Part 2 line 29
"Line 27 plus line 28": the federal tax less credits (lines 25 to 27, the T1 line 139) plus the
advanced Canada workers benefit of line 28."""

SPLIT_INCOME_LINE_30 = AmountKind.declare(CATALOG, "split_income_line_30", non_negative=True)
"""Federal tax on split income floor, Form T1206 Part 2 line 30 "Enter whichever is more: the amount
from line 24 or line 29.": the greater of line 24 and line 29, the floor under the federal tax on
split income."""

NET_FEDERAL_TAX = AmountKind.declare(CATALOG, "net_federal_tax", non_negative=True)
"""Net federal tax, T1 line 142 (line 42000) "Add lines 139 to 141. Net federal tax", as built for
the take-home return: the sum of one part, line 139 (`federal_tax_less_credits`, line 41700). Lines
140 (41500) and 141 (41800) are absent for the take-home filer and are left out.
"""

CPP_PAYABLE_ON_SELF_EMPLOYMENT = AmountKind.declare(
    CATALOG, "cpp_payable_on_self_employment", non_negative=True
)
"""CPP contributions payable on self-employment income and other earnings, T1 line 144 and line
42100 "CPP contributions payable on self-employment income and other earnings (complete Schedule 8
or Form RC381, whichever applies)": Schedule 8 Part 4 line 14, entered once for each Part 4
completed (1 or 0). The Part 5 amount and Form RC381 are added in separate steps."""

EI_PAYABLE_ON_SELF_EMPLOYMENT = AmountKind.declare(
    CATALOG, "ei_payable_on_self_employment", non_negative=True
)
"""EI premiums payable on self-employment and other eligible earnings, T1 line 145 and line 42120
"Employment insurance premiums payable on self-employment and other eligible earnings (complete
Schedule 13)": Schedule 13 line 9, entered once for each agreement with the Commission (1 or 0)."""

SOCIAL_BENEFITS_REPAYMENT_PAYABLE = AmountKind.declare(
    CATALOG, "social_benefits_repayment_payable", non_negative=True
)
"""Social benefits repayment, T1 line 146 and line 42200 "Social benefits repayment (amount from
line 23500)": the amount of line 23500, carried."""

TOTAL_PAYABLE = AmountKind.declare(CATALOG, "total_payable", non_negative=True)
"""Total payable, T1 line 148 (line 43500) "Add lines 143 to 147. Total payable", as built for the
take-home return: the sum of two parts, line 143 (`net_federal_tax`, line 42000) and line 147
(`provincial_tax_line_42800`, the Ontario tax from ON428 line 90, entered on line 42800). Lines 144
(42100), 145 (42120) and 146 (42200) are absent for the take-home filer and are left out.
"""

PROVINCIAL_TAX_LINE_42800 = AmountKind.declare(
    CATALOG, "provincial_tax_line_42800", non_negative=True
)
"""Provincial or territorial tax, T1 line 147 and line 42800 "Provincial or territorial tax
(complete and attach your provincial or territorial Form 428, even if the result is "0")": the
Ontario tax of Form ON428 line 90 (`ca-on/on428_ontario_tax_line_90`), entered on line 42800 of
the return."""

INCOME_TAX_DEDUCTED = AmountKind.declare(CATALOG, "income_tax_deducted", non_negative=True)
"""Income tax deducted, T1 line 150 (line 43700) "Total income tax deducted (amounts from all
Canadian slips)": a starting amount."""

NET_RENTAL_INCOME_NOT_BELOW_ZERO = AmountKind.declare(
    CATALOG, "net_rental_income_not_below_zero", non_negative=True
)
"""Net rental income, T1 line 12600, not below zero, not a form line: a rental loss counts 0 in the
income before losses (`ca/income_before_losses`)."""

BUSINESS_INCOME_NOT_BELOW_ZERO = AmountKind.declare(
    CATALOG, "business_income_not_below_zero", non_negative=True
)
"""Net business income, T1 line 13500, not below zero, not a form line: a business loss counts 0 in
the income before losses (`ca/income_before_losses`)."""

PROFESSIONAL_INCOME_NOT_BELOW_ZERO = AmountKind.declare(
    CATALOG, "professional_income_not_below_zero", non_negative=True
)
"""Net professional income, T1 line 13700, not below zero, not a form line: a professional loss
counts 0 in the income before losses (`ca/income_before_losses`)."""

COMMISSION_INCOME_NOT_BELOW_ZERO = AmountKind.declare(
    CATALOG, "commission_income_not_below_zero", non_negative=True
)
"""Net commission income, T1 line 13900, not below zero, not a form line: a commission loss counts 0
in the income before losses (`ca/income_before_losses`)."""

FARMING_INCOME_NOT_BELOW_ZERO = AmountKind.declare(
    CATALOG, "farming_income_not_below_zero", non_negative=True
)
"""Net farming income, T1 line 14100, not below zero, not a form line: a farming loss counts 0 in
the income before losses (`ca/income_before_losses`)."""

FISHING_INCOME_NOT_BELOW_ZERO = AmountKind.declare(
    CATALOG, "fishing_income_not_below_zero", non_negative=True
)
"""Net fishing income, T1 line 14300, not below zero, not a form line: a fishing loss counts 0 in
the income before losses (`ca/income_before_losses`)."""

INCOME_BEFORE_LOSSES = AmountKind.declare(CATALOG, "income_before_losses", non_negative=True)
"""Income before losses, not a form line: the income lines of T1 Step 2 (lines 10100 to 14700) added
as in total income (line 15000), except that the net rental, business, professional, commission,
farming and fishing lines, which print a loss, each count 0 when they are a loss. It is the bound of
the amount that is part of the income it comes out of: T1206 line 3. Total income itself shows a
loss in brackets, which would bound that amount at 0 for a filer with a loss."""

INCOME_TAX_DEDUCTED_AFTER_ELECTION = AmountKind.declare(
    CATALOG, "income_tax_deducted_after_election", non_negative=True
)
"""Income tax deducted on T1 line 150 (line 43700) after the Form T1032 election: when the election
applies (line 22 of the form is above 0), line 39 of the form on the transferring spouse's return
and line 42 on the receiving spouse's ("Enter the result on line 43700 of the transferring spouse's
... return" and "... of the receiving spouse's ... return"); otherwise
`ca/income_tax_deducted`.
The total credits sum reads this amount."""

CPP_PART_5_PAYABLE_ON_SELF_EMPLOYMENT = AmountKind.declare(
    CATALOG, "cpp_part_5_payable_on_self_employment", non_negative=True
)
"""T1 line 42100 from Part 5 line 49 if positive, once for each Part 5
completed (1 or 0)."""

CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS = AmountKind.declare(
    CATALOG, "cpp_payable_on_self_employment_and_other_earnings", non_negative=True
)
"""T1 line 42100: the Part 4 amount (cpp_payable_on_self_employment) plus the Part 5 amount,
added into the total payable by 11_net_tax."""
