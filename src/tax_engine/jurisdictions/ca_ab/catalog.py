"""The Alberta artifact catalog: Alberta's own kinds, named from the Alberta forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ab import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

AB428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "ab428_taxable_income_line_1", non_negative=True
)
"""Taxable income, AB428 line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, the base of the bracket columns read by lines 3 and 4."""

AB428_BRACKET_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "ab428_bracket_rate_line_5", non_negative=True
)
"""Bracket column rate, AB428 line 5 (each column prints "Line 5: Rate" with 8%, 10% or 12%): the
printed rate of the column that line 1 falls in, blank when line 1 is outside the lines 2 to 8
table."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, AB428 line 16 (line 58040) "Basic personal amount Claim $22,323": the
amount claimed, the first part of the total of the Alberta credit amounts."""

AB428_CREDITS_SUBTOTAL_LINE_25 = AmountKind.declare(
    CATALOG, "ab428_credits_subtotal_line_25", non_negative=True
)
"""AB428 line 25 "Line 25: Add lines 16, 17, 20, 23, and 24.": the sum of those lines, here the
basic personal amount (line 16) alone."""

AB428_BRACKET_LOWER_BOUND_LINE_10 = AmountKind.declare(
    CATALOG, "ab428_bracket_lower_bound_line_10", non_negative=True
)
"""Lower bound of the column, AB428 line 10 "Line 10: 181,481.00": the printed lower bound of the
column of lines 9 to 15 that line 1 falls in, blank when line 1 is 181,481 or less."""

AB428_BRACKET_TAX_AT_START_LINE_14 = AmountKind.declare(
    CATALOG, "ab428_bracket_tax_at_start_line_14", non_negative=True
)
"""Tax at the start of the column, AB428 line 14 "Line 14: 17,553.04": the printed tax at the start
of the column of lines 9 to 15 that line 1 falls in, blank when line 1 is 181,481 or less."""

AB428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "ab428_tax_on_taxable_income_line_8", non_negative=True
)
"""Alberta tax on taxable income, AB428 line 8 "Line 6 plus line 7 Alberta tax on taxable income =":
line 6 plus line 7 of the column that line 1 falls in, read by line 59 on the tax form."""

AB428_TAX_ON_TAXABLE_INCOME_LINE_15 = AmountKind.declare(
    CATALOG, "ab428_tax_on_taxable_income_line_15", non_negative=True
)
"""Alberta tax on taxable income, AB428 line 15 "Line 13 plus line 14 Alberta tax on taxable income
=": line 13 plus line 14 of the column that line 1 falls in, read by line 59 on the tax form."""

AB428_CPP_CONTRIBUTIONS_LINE_27 = AmountKind.declare(
    CATALOG, "ab428_cpp_contributions_line_27", non_negative=True
)
"""CPP or QPP contributions, AB428 line 27 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

AB428_UNUSED_TUITION_LINE_41 = AmountKind.declare(
    CATALOG, "ab428_unused_tuition_line_41", non_negative=True
)
"""Unused tuition and education amounts, AB428 line 41 (line 58560) "Your unused tuition and
education amounts": the unused tuition and education amounts from Schedule AB(S11), read by line 2
of Worksheet AB428."""

AB428_MEDICAL_EXPENSES_LINE_51 = AmountKind.declare(
    CATALOG, "ab428_medical_expenses_line_51", non_negative=True
)
"""Medical expenses, AB428 line 51 (line 58769) "Line 49 plus line 50 =": line 49 plus line 50, an
optional input; a blank is read as 0 by the line 52 part."""

AB428_CREDITS_TOTAL_LINE_52 = AmountKind.declare(
    CATALOG, "ab428_credits_total_line_52", non_negative=True
)
"""Credit amounts total, AB428 line 52 (line 58800) "Line 43 plus line 51 =": line 43 plus
line 51, read by line 1 of Worksheet AB428."""

AB428_DONATIONS_CREDIT_LINE_57 = AmountKind.declare(
    CATALOG, "ab428_donations_credit_line_57", non_negative=True
)
"""Donations and gifts credit, AB428 line 57 (line 58969) "Line 57 and line 58969: Line 55 plus line
56 =": a caller input, read as 0 when the filer has no donations or gifts."""

AB428_NON_REFUNDABLE_CREDITS_LINE_58 = AmountKind.declare(
    CATALOG, "ab428_non_refundable_credits_line_58", non_negative=True
)
"""Alberta non-refundable tax credits, AB428 line 58 (line 61500) "Line 54 plus line 57 Enter this
amount on line 62. Alberta non-refundable tax credits =": line 54 plus line 57, read by line 62 on
the tax form."""

AB428_TAX_ON_SPLIT_INCOME_LINE_60 = AmountKind.declare(CATALOG, "ab428_tax_on_split_income_line_60")
"""Alberta tax on split income, AB428 line 60 "Line 60 and line 61510: Alberta tax on split income
(complete Form T1206)": the tax from Form T1206, an optional input that a salary-only caller leaves
out."""

AB428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_64 = AmountKind.declare(
    CATALOG, "ab428_minimum_tax_carryover_amount_line_64", non_negative=True
)
"""Alberta minimum tax carryover amount, AB428 line 64 and line 61540 "Amount from line 40427 of
your return": the amount from line 40427 of the T1 return, an optional input, box A of the line,
that a salary-only caller leaves out and is read as 0; the 35% is applied by the next step."""

AB428_MINIMUM_TAX_CARRYOVER_LINE_64 = AmountKind.declare(
    CATALOG, "ab428_minimum_tax_carryover_line_64", non_negative=True
)
"""Alberta minimum tax carryover, AB428 line 64 and line 61540 "Amount from line 40427 of your
return multiplied by 35% =": calculated, the amount from line 40427 multiplied by 35%."""

AB428_MINIMUM_TAX_T691_AMOUNT_LINE_67 = AmountKind.declare(
    CATALOG, "ab428_minimum_tax_t691_amount_line_67"
)
"""Alberta additional tax for minimum tax purposes, AB428 line 67 "Line 67: Form T691: line 1 minus
line 2 of Part 7 multiplied by 35%": the amount from Form T691, an optional input that a salary-only
caller leaves out. The 35% multiply is a separate step."""

AB428_ADDITIONAL_MINIMUM_TAX_LINE_67 = AmountKind.declare(
    CATALOG, "ab428_additional_minimum_tax_line_67"
)
"""Alberta additional tax for minimum tax purposes, AB428 line 67 "Line 67: Form T691: line 1 minus
line 2 of Part 7 multiplied by 35% =": the T691 amount multiplied by 35%, rounded half-up to the
cent."""

AB428_PROVINCIAL_FOREIGN_TAX_CREDIT_LINE_69 = AmountKind.declare(
    CATALOG, "ab428_provincial_foreign_tax_credit_line_69", non_negative=True
)
"""Provincial foreign tax credit, AB428 line 69 "Line 69: Provincial foreign tax credit (complete
Form T2036)": the credit from Form T2036, an optional input that a salary-only caller leaves out."""

AB428_POLITICAL_CONTRIBUTIONS_CREDIT_LINE_72 = AmountKind.declare(
    CATALOG, "ab428_political_contributions_credit_line_72", non_negative=True
)
"""Alberta political contributions tax credit, AB428 line 72 "Line 72: Alberta political
contributions tax credit (use Worksheet AB428) (maximum $1,000)": the credit from the worksheet, an
optional input that a salary-only caller leaves out, read by line 73."""

AB428_ALBERTA_TAX_LINE_75 = AmountKind.declare(
    CATALOG, "ab428_alberta_tax_line_75", non_negative=True
)
"""Alberta tax, AB428 line 75 "Line 75: Line 73 minus line 74 (if negative, enter "0") Enter this
amount on line 42800 of your return. Alberta tax =": line 73 minus line 74, not below 0, entered on
T1 line 42800."""

WORKSHEET_AB428_SUPPLEMENTAL_CREDIT_LINE_9 = AmountKind.declare(
    CATALOG, "worksheet_ab428_supplemental_credit_line_9", non_negative=True
)
"""Alberta supplemental tax credit, Worksheet AB428 line 9 "Line 9: Line 7 multiplied by the
percentage from line 8 enter this amount on line 61545 of your Form AB428.": the credit entered on
line 61545 of Form AB428."""

WORKSHEET_AB428_LINE_6 = AmountKind.declare(CATALOG, "worksheet_ab428_line_6", non_negative=True)
"""Base amount, Worksheet AB428 line 6 "Line 6: Base amount 4,800.00": the base amount of the
Alberta supplemental tax credit."""

WORKSHEET_AB428_LINE_2 = AmountKind.declare(CATALOG, "worksheet_ab428_line_2", non_negative=True)
"""Amount from AB428 line 58560, Worksheet AB428 line 2 "Line 2: Amount from line 58560 of your Form
AB428": the unused tuition amount of Form AB428 line 41, read as the worksheet's second figure."""

AB428_EI_PREMIUMS_LINE_29 = AmountKind.declare(
    CATALOG, "ab428_ei_premiums_line_29", non_negative=True
)
"""EI premiums credit amount, AB428 line 29 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

AB428_CPP_EI_AND_OTHER_LINE_32 = AmountKind.declare(
    CATALOG, "ab428_cpp_ei_and_other_line_32", non_negative=True
)
"""CPP, EI and other credit amounts subtotal, AB428 line 32 "Line 32: Add lines 27 to 31. = ^": the
sum of lines 27 and 29. Lines 28, 30 and 31 are not built: a salary-only filer has none of them."""

AB428_CREDITS_SUBTOTAL_LINE_33 = AmountKind.declare(
    CATALOG, "ab428_credits_subtotal_line_33", non_negative=True
)
"""Credits subtotal, AB428 line 33 "Line 33: Line 26 plus line 32 = ^": line 26 is "Amount from line
25 of the previous page", a copy of line 25, so the sum adds line 25 and line 32."""

AB428_DIVIDEND_TAX_CREDIT_LINE_63 = AmountKind.declare(
    CATALOG, "ab428_dividend_tax_credit_line_63", non_negative=True
)
"""Alberta dividend tax credit, AB428 line 63 (line 61520) "Alberta dividend tax credit (use
Worksheet AB428)": an optional input that a salary-only caller leaves out."""

AB428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "ab428_pension_income_amount", non_negative=True
)
"""Pension income amount, AB428 line 34 "Line 34 and line 58360: Pension income amount (maximum
$1,719)": the amount the filer claims, a caller input that is read as 0 when it is left out."""

AB428_CREDITS_SUBTOTAL_LINE_36 = AmountKind.declare(
    CATALOG, "ab428_credits_subtotal_line_36", non_negative=True
)
"""Credits subtotal, AB428 line 36 "Line 36: Add lines 33 to 35. = ^": line 35 (caregiver amount) is
not built, so the sum adds line 33 and the line 34 pension income amount."""

AB428_CREDITS_SUBTOTAL_LINE_39 = AmountKind.declare(
    CATALOG, "ab428_credits_subtotal_line_39", non_negative=True
)
"""Credits subtotal, AB428 line 39 "Line 39: Add lines 36 to 38. = ^": lines 37 and 38 (the
disability amounts) are not built, so the sum reads line 36 alone."""

AB428_CREDITS_SUBTOTAL_LINE_43 = AmountKind.declare(
    CATALOG, "ab428_credits_subtotal_line_43", non_negative=True
)
"""Credits subtotal, AB428 line 43 "Line 43: Add lines 39 to 42. = ^": lines 40 and 42 are not
built, so the sum adds line 39 and the line 41 unused tuition and education amounts."""

AB428_BRACKET_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "ab428_bracket_lower_bound_line_3", non_negative=True
)
"""Lower bound of the column, AB428 line 3 "Line 3: 0.00" (60,000.00; 151,234.00): the printed lower
bound of the column of lines 2 to 8 that line 1 falls in. It is blank when line 1 is above 181,481,
where lines 9 to 15 apply."""

AB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "ab428_taxable_income_over_lower_bound_line_4", non_negative=True
)
"""Taxable income over the lower bound, AB428 line 4 "Line 4: Line 2 minus line 3 (cannot be
negative) =": line 1 minus line 3, not below zero; blank when line 3 is blank."""

AB428_BRACKET_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "ab428_bracket_tax_at_start_line_7", non_negative=True
)
"""Tax at the start of the column, AB428 line 7 "Line 7: 0.00" (4,800.00; 13,923.40): the printed
tax at the start of the column of lines 2 to 8 that line 1 falls in. It is blank when line 1 is
above 181,481, where lines 9 to 15 apply."""

AB428_BRACKET_RATE_LINE_12 = AmountKind.declare(
    CATALOG, "ab428_bracket_rate_line_12", non_negative=True
)
"""Bracket column rate, AB428 line 12 (the columns print "Line 12: Rate" with 13%, 14% or 15%): the
printed rate of the column that line 1 falls in; blank when line 1 is 181,481.00 or less."""

AB428_ALBERTA_TAX_ON_TAXABLE_INCOME_LINE_59 = AmountKind.declare(
    CATALOG, "ab428_alberta_tax_on_taxable_income_line_59", non_negative=True
)
"""Alberta tax on taxable income, AB428 line 59 "Line 59: Alberta tax on taxable income from line 8
or line 15 ^": the amount of line 8 or of line 15, whichever the taxable income is in; the other is
blank."""

AB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_11 = AmountKind.declare(
    CATALOG, "ab428_taxable_income_over_lower_bound_line_11", non_negative=True
)
"""Taxable income over the lower bound, AB428 line 11 "Line 11: Line 9 minus line 10 (cannot be
negative)": line 1 minus the lower bound of line 10, not below 0; blank when line 1 is 181,481.00
or less, where line 10 is blank."""
